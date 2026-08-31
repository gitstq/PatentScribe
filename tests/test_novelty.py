import unittest

from patentscribe.builder import dump_template
from patentscribe.models import Disclosure
from patentscribe.novelty import compare_prior_art, disclosure_corpus


def make():
    return Disclosure.from_dict(dump_template("发明"))


class TestNovelty(unittest.TestCase):
    def test_identical_text_full_containment(self):
        d = make()
        same = disclosure_corpus(d)
        result = compare_prior_art(d, [("same.txt", same)])
        self.assertEqual(result.matches[0].containment, 1.0)
        self.assertEqual(result.matches[0].level, "高")
        self.assertEqual(result.riskiest.name, "same.txt")

    def test_disjoint_text_low(self):
        d = make()
        result = compare_prior_art(d, [("other.txt", "烹饪菜谱：番茄炒蛋需要鸡蛋和食盐，热锅冷油翻炒均匀即可出锅。")])
        m = result.matches[0]
        self.assertLess(m.containment, 0.3)
        self.assertEqual(m.level, "低")

    def test_partial_overlap_mid(self):
        d = make()
        # 复制一半本申请语料 + 无关内容
        corpus = disclosure_corpus(d)
        half = corpus[: len(corpus) // 2] + "\n" + "完全无关的农业种植内容，灌溉施肥修剪枝条。" * 3
        result = compare_prior_art(d, [("p.txt", half)])
        self.assertIn(result.matches[0].level, ("中", "高"))

    def test_multiple_prior_sorted(self):
        d = make()
        same = disclosure_corpus(d)
        result = compare_prior_art(d, [
            ("far.txt", "养花浇水晒太阳松土修剪。"),
            ("near.txt", same),
        ])
        self.assertEqual(result.matches[0].name, "near.txt")

    def test_empty_corpus_raises(self):
        with self.assertRaises(ValueError):
            compare_prior_art(Disclosure(), [("x.txt", "内容")])

    def test_serializable(self):
        d = make()
        result = compare_prior_art(d, [("p.txt", disclosure_corpus(d))])
        payload = result.to_dict()
        self.assertIn("matches", payload)
        self.assertIn("note", payload)


if __name__ == "__main__":
    unittest.main()
