"""You'll implement this."""

from typing import List

from social_network import SocialNetwork


class Recommender:
    """Recommends friends based on mutual connections."""

    def __init__(self, network: SocialNetwork):
        self.network = network

    def recommend(self, user: str, max_recommendations: int = 5) -> List[str]:
        pass
