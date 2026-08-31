import unittest

from patentscribe.builder import dump_template
from patentscribe.linter import lint_disclosure, _cn_len
from patentscribe.models import Disclosure, Severity


def good_disclosure(**overrides):
    d = Disclosure.from_dict(dump_template("发明"))
    for k, v in overrides.items():
        setattr(d, k, v)
    return d


class TestCnLen(unittest.TestCase):
    def test_mixed_count(self):
        self.assertEqual(_cn_len("数据处理ABC"), 4 + 1)


class TestLinter(unittest.TestCase):
    def _codes(self, report, severity=None):
        return {
            i.code for i in report.issues
            if severity is None or i.severity == severity
        }

    def test_template_has_no_errors(self):
        report = lint_disclosure(good_disclosure())
        self.assertEqual(report.errors, [], msg=[i.message for i in report.errors])
        self.assertTrue(report.passed)

    def test_missing_section_error(self):
        d = good_disclosure(solution="")
        report = lint_disclosure(d)
        self.assertIn("L101", self._codes(report, Severity.ERROR))

    def test_bad_patent_type(self):
        d = good_disclosure(patent_type="玄学")
        report = lint_disclosure(d)
        self.assertIn("L104", self._codes(report, Severity.ERROR))

    def test_title_too_long(self):
        d = good_disclosure(title="一种" + "非常" * 20 + "复杂的数据处理方法与装置系统")
        report = lint_disclosure(d)
        self.assertIn("L201", self._codes(report))

    def test_abstract_too_long(self):
        d = good_disclosure(abstract="技" * 320)
        report = lint_disclosure(d)
        self.assertIn("L301", self._codes(report))

    def test_abstract_marketing(self):
        d = good_disclosure(abstract="本方案性能优异、业界领先，具有巨大效益。" + "技术内容" * 5)
        report = lint_disclosure(d)
        self.assertIn("L302", self._codes(report))

    def test_vague_word_in_claims(self):
        claims = (
            "1. 一种数据处理方法，其特征在于，采用最好的滤波策略对信号进行处理。\n"
            "2. 根据权利要求1所述的方法，其特征在于，滤波窗口大约为5毫秒左右。"
        )
        d = good_disclosure(claims_text=claims)
        report = lint_disclosure(d)
        codes = self._codes(report)
        self.assertIn("L401", codes)

    def test_single_claim_info(self):
        d = good_disclosure(claims_text="1. 一种数据处理方法，其特征在于，执行处理步骤。")
        report = lint_disclosure(d)
        self.assertIn("L403", self._codes(report))

    def test_missing_keywords_info(self):
        d = good_disclosure(keywords=[])
        report = lint_disclosure(d)
        self.assertIn("L701", self._codes(report))

    def test_drawing_mark_consistency(self):
        # 权要中出现 999，但实施方式没有该标记
        claims = (
            "1. 一种数据处理装置，其特征在于，包括部件999。\n"
            "2. 根据权利要求1所述的装置，其特征在于，还包括辅助件。"
        )
        d = good_disclosure(claims_text=claims, embodiments="本实施例仅描述部件100的结构。")
        report = lint_disclosure(d)
        self.assertIn("L601", self._codes(report))

    def test_report_sort_stable(self):
        d = good_disclosure(solution="", abstract="技" * 320)
        report = lint_disclosure(d)
        severities = [i.severity for i in report.issues]
        self.assertEqual(severities, sorted(severities, key=lambda s: {
            Severity.ERROR: 0, Severity.WARN: 1, Severity.INFO: 2}[s]))


if __name__ == "__main__":
    unittest.main()
