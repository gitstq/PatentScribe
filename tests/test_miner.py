import unittest

from patentscribe.miner import extract_keywords, mine_text, split_sentences

NOTES = """现有技术在高并发场景下存在请求排队时间长、资源利用率低的问题。
本发明通过引入动态权重调度器对请求进行实时分流。
本方案采用滑动窗口统计各节点的负载。
从而将平均响应延迟降低了40%，并显著提升了系统吞吐量。
"""


class TestMiner(unittest.TestCase):
    def test_split_sentences(self):
        sents = split_sentences(NOTES)
        self.assertGreaterEqual(len(sents), 4)

    def test_classify(self):
        r = mine_text(NOTES)
        self.assertTrue(any("现有技术" in s for s in r.problems))
        self.assertTrue(any("本发明" in s for s in r.solutions))
        self.assertTrue(any("降低" in s for s in r.effects))

    def test_means_extraction(self):
        r = mine_text(NOTES)
        joined = "|".join(r.means)
        self.assertIn("动态权重调度器", joined)

    def test_inventive_points_structure(self):
        r = mine_text(NOTES)
        self.assertTrue(r.inventive_points)
        point = r.inventive_points[0]
        self.assertTrue(point["id"].startswith("IP"))
        self.assertIn("technical_means", point)

    def test_keywords_deterministic(self):
        k1 = extract_keywords(NOTES)
        k2 = extract_keywords(NOTES)
        self.assertEqual(k1, k2)
        # “请求”在语料中出现两次，高频词必须排在前列
        self.assertIn("请求", k1)
        self.assertEqual(k1[0], "请求")

    def test_skeleton_keys(self):
        r = mine_text(NOTES)
        for key in ("title", "problems", "solution", "effects", "keywords", "claims_text"):
            self.assertIn(key, r.skeleton)


if __name__ == "__main__":
    unittest.main()
