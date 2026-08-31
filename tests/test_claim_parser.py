import unittest

from patentscribe.claim_parser import (
    analyze_claims,
    build_graph,
    parse_claims,
)


CLAIMS_OK = """1. 一种数据处理方法，其特征在于，包括：
获取待处理数据；
对所述待处理数据执行第一处理，得到中间结果；
对所述中间结果执行第二处理，得到输出结果。
2. 根据权利要求1所述的方法，其特征在于，所述第一处理包括滤波步骤。
3. 根据权利要求1或2所述的方法，其特征在于，所述第二处理为加权融合。
4. 一种数据处理装置，其特征在于，包括获取模块100、处理模块200和输出模块300。
"""


class TestParseClaims(unittest.TestCase):
    def test_numbering_and_count(self):
        claims = parse_claims(CLAIMS_OK)
        self.assertEqual([c.number for c in claims], [1, 2, 3, 4])

    def test_independent_dependent(self):
        claims = parse_claims(CLAIMS_OK)
        kinds = {c.number: c.kind for c in claims}
        self.assertEqual(kinds[1], "independent")
        self.assertEqual(kinds[2], "dependent")
        self.assertEqual(kinds[4], "independent")

    def test_refs_list(self):
        claims = parse_claims(CLAIMS_OK)
        self.assertEqual(claims[1].refs, [1])
        self.assertEqual(claims[2].refs, [1, 2])

    def test_range_expansion(self):
        text = "1. 一种方法，其特征在于，包括步骤A。\n2. 根据权利要求1所述的方法，其特征在于，还包括B。\n3. 根据权利要求1-2任一项所述的方法，其特征在于，还包括C。"
        claims = parse_claims(text)
        self.assertEqual(claims[2].refs, [1, 2])

    def test_subject_extraction(self):
        claims = parse_claims(CLAIMS_OK)
        self.assertIn("数据处理方法", claims[0].subject)
        self.assertIn("数据处理装置", claims[3].subject)

    def test_features_split(self):
        claims = parse_claims(CLAIMS_OK)
        # 独权 1 应切出 3 个特征片段
        self.assertGreaterEqual(len(claims[0].features), 3)

    def test_alternate_markers(self):
        text = "【1】一种装置，其特征在于，包括部件A。\n【2】根据权利要求1所述的装置，其特征在于，还包括部件B。"
        claims = parse_claims(text)
        self.assertEqual(len(claims), 2)
        self.assertEqual(claims[1].refs, [1])

    def test_empty(self):
        self.assertEqual(parse_claims(""), [])


class TestAnalyzeClaims(unittest.TestCase):
    def _codes(self, issues):
        return {i.code for i in issues}

    def test_clean_case_has_no_errors(self):
        claims = parse_claims(CLAIMS_OK)
        _, issues = analyze_claims(claims)
        errors = [i for i in issues if i.severity.value == "error"]
        self.assertEqual(errors, [])

    def test_dangling_reference(self):
        text = "1. 一种方法，其特征在于，包括A。\n2. 根据权利要求3所述的方法，其特征在于，包括B。"
        claims = parse_claims(text)
        _, issues = analyze_claims(claims)
        self.assertIn("C003", self._codes(issues))

    def test_forward_reference(self):
        # 权2引用编号更大的权3 → 前引限制错误
        bad = "1. 一种方法，其特征在于，包括A。\n2. 根据权利要求3所述的方法，其特征在于，包括B。\n3. 一种装置，其特征在于，包括C。"
        claims = parse_claims(bad)
        _, issues = analyze_claims(claims)
        self.assertIn("C004", self._codes(issues))

    def test_missing_independent(self):
        text = "1. 根据权利要求2所述的方法，其特征在于，包括A。\n2. 根据权利要求1所述的方法，其特征在于，包括B。"
        claims = parse_claims(text)
        _, issues = analyze_claims(claims)
        self.assertIn("C002", self._codes(issues))

    def test_multi_ref_multi_forbidden(self):
        # 权2 引用 1（单项）；权3 引用 1、2（多项）；权4 引用 2、3（其中3为多项）→ 触发 C008
        text = (
            "1. 一种方法，其特征在于，包括A。\n"
            "2. 根据权利要求1所述的方法，其特征在于，包括B。\n"
            "3. 根据权利要求1或2所述的方法，其特征在于，包括C。\n"
            "4. 根据权利要求2或3所述的方法，其特征在于，包括D。"
        )
        claims = parse_claims(text)
        _, issues = analyze_claims(claims)
        self.assertIn("C008", self._codes(issues))

    def test_numbering_gap(self):
        text = "1. 一种方法，其特征在于，包括A。\n3. 根据权利要求1所述的方法，其特征在于，包括B。"
        claims = parse_claims(text)
        _, issues = analyze_claims(claims)
        self.assertIn("C001", self._codes(issues))

    def test_inner_period(self):
        text = "1. 一种方法，其特征在于，包括A。还包括B。\n2. 根据权利要求1所述的方法，其特征在于，包括C。"
        claims = parse_claims(text)
        _, issues = analyze_claims(claims)
        self.assertIn("C006", self._codes(issues))

    def test_graph_ancestors_and_tree(self):
        claims = parse_claims(CLAIMS_OK)
        graph = build_graph(claims)
        self.assertEqual(graph.roots, [1, 4])
        self.assertIn(1, graph.ancestors_of(3))
        tree = graph.render_tree()
        self.assertIn("独权", tree)
        self.assertIn("从权", tree)


if __name__ == "__main__":
    unittest.main()
