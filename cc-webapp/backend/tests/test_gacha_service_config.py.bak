"""GachaService 설정 관련 테스트."""

import json
from unittest.mock import MagicMock, patch
from sqlalchemy.orm import Session
from app.services.gacha_service import GachaService, GachaPullResult
from app.repositories.game_repository import GameRepository


def test_load_rarity_table_from_env(monkeypatch):
    """환경 변수에서 확률 테이블을 로드하는지 검증."""
    table = [["Legendary", 1.0]]
    monkeypatch.setenv("GACHA_RARITY_TABLE", json.dumps(table))
    service = GachaService(repository=MagicMock(spec=GameRepository))
    assert service.rarity_table == [("Legendary", 1.0)]


def test_reward_pool(monkeypatch):
    """보상 풀이 소진되면 Common으로 대체되는지 확인."""
    monkeypatch.setenv("GACHA_RARITY_TABLE", json.dumps([["Legendary", 1.0]]))
    monkeypatch.setenv("GACHA_REWARD_POOL", json.dumps({"Legendary": 1}))
    repo = MagicMock(spec=GameRepository)
    repo.get_gacha_count.return_value = 0
    repo.get_gacha_history.return_value = []
    service = GachaService(repository=repo)
    with patch("app.services.gacha_service.deduct_tokens"), patch(
        "app.services.gacha_service.get_balance", return_value=0
    ):
        result1 = service.pull(1, 1, MagicMock(spec=Session))
        result2 = service.pull(1, 1, MagicMock(spec=Session))
    assert result1.results[0] == "Legendary"
    assert result2.results[0] == "Common"


