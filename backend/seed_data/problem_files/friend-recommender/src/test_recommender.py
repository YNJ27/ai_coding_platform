"""Tests for Recommender — Implementation phase."""

import unittest

from social_network import SocialNetwork
from recommender import Recommender


def _build_small_network() -> SocialNetwork:
    net = SocialNetwork()
    for a, b in [
        ("Alice", "Bob"), ("Alice", "Charlie"), ("Alice", "Diana"),
        ("Bob", "Charlie"), ("Bob", "Eve"),
        ("Charlie", "Diana"), ("Charlie", "Eve"), ("Charlie", "Frank"),
        ("Diana", "Frank"), ("Diana", "Grace"),
        ("Eve", "Frank"), ("Eve", "Heidi"),
        ("Frank", "Grace"), ("Frank", "Heidi"),
        ("Grace", "Ivan"), ("Grace", "Judy"),
        ("Heidi", "Ivan"),
        ("Ivan", "Judy"),
        ("Judy", "Karl"),
        ("Karl", "Liam"),
    ]:
        net.add_friendship(a, b)
    return net


class RecommenderTest(unittest.TestCase):

    def test_basic_recommendation_order(self) -> None:
        net = _build_small_network()
        rec = Recommender(net)
        results = rec.recommend("Alice")
        self.assertGreater(len(results), 0, "should return at least one recommendation")
        self.assertEqual(results[0], "Eve")

    def test_excludes_self_and_existing_friends(self) -> None:
        net = _build_small_network()
        rec = Recommender(net)
        results = rec.recommend("Alice")
        self.assertNotIn("Alice", results)
        self.assertNotIn("Bob", results)
        self.assertNotIn("Charlie", results)
        self.assertNotIn("Diana", results)

    def test_limit_to_five(self) -> None:
        net = _build_small_network()
        rec = Recommender(net)
        results = rec.recommend("Alice")
        self.assertLessEqual(len(results), 5, "should return at most 5 recommendations")

    def test_no_valid_candidates(self) -> None:
        net = SocialNetwork()
        net.add_user("Alice")
        rec = Recommender(net)
        results = rec.recommend("Alice")
        self.assertEqual(results, [])


if __name__ == "__main__":
    unittest.main()
