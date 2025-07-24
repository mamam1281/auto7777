import unittest
from unittest.mock import MagicMock, patch
from sqlalchemy.orm import Session

from app.services.gacha_service import GachaService, GachaPullResult
from app.repositories.game_repository import GameRepository


class TestGachaService(unittest.TestCase):
    def setUp(self):
        self.mock_db = MagicMock(spec=Session)
        self.repo = MagicMock(spec=GameRepository)
        self.service = GachaService(repository=self.repo)

    @patch("app.services.gacha_service.deduct_tokens")
    @patch("app.services.gacha_service.get_balance", return_value=80)
    @patch("app.services.gacha_service.random.random", return_value=0.001)
    def test_pull_legendary(self, m_rand, m_balance, m_deduct):
        self.repo.get_gacha_count.return_value = 0
        self.repo.get_gacha_history.return_value = []

        result = self.service.pull(1, 1, self.mock_db)

        self.assertIsInstance(result, GachaPullResult)
        self.assertIn(result.results[0], {"Legendary", "Epic", "Rare", "Common"})
        self.repo.record_action.assert_called_once()

    @patch("app.services.gacha_service.deduct_tokens", side_effect=ValueError)
    def test_pull_insufficient_tokens(self, m_deduct):
        with self.assertRaises(ValueError):
            self.service.pull(1, 1, self.mock_db)


if __name__ == "__main__":
    unittest.main()
