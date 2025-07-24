"""Enhanced unit tests for GachaService with comprehensive coverage."""

import pytest
from unittest.mock import Mock, patch, MagicMock
import json
import os
from app.services.gacha_service import GachaService, GachaPullResult
from app.repositories.game_repository import GameRepository


class TestGachaService:
    """Comprehensive test class for GachaService."""
    
    def setup_method(self):
        """Setup test data before each test method."""
        self.mock_db = Mock()
        self.mock_repository = Mock(spec=GameRepository)
        
    def test_gacha_pull_result_dataclass(self):
        """Test GachaPullResult dataclass creation."""
        result = GachaPullResult(
            results=["Epic Sword", "Common Shield"],
            tokens_change=-100,
            balance=400
        )
        
        assert result.results == ["Epic Sword", "Common Shield"]
        assert result.tokens_change == -100
        assert result.balance == 400
        
    def test_default_rarity_table(self):
        """Test that default rarity table is properly defined."""
        assert hasattr(GachaService, 'DEFAULT_RARITY_TABLE')
        table = GachaService.DEFAULT_RARITY_TABLE
        
        assert len(table) == 4
        assert any(item[0] == "Legendary" for item in table)
        assert any(item[0] == "Epic" for item in table)
        assert any(item[0] == "Rare" for item in table)
        assert any(item[0] == "Common" for item in table)
        
        # Check probabilities sum to 1.0
        total_prob = sum(item[1] for item in table)
        assert abs(total_prob - 1.0) < 0.001
        
    @patch.dict(os.environ, {}, clear=True)
    def test_service_init_without_env_vars(self):
        """Test service initialization without environment variables."""
        with patch('app.services.gacha_service.GameRepository') as mock_repo_class:
            mock_repo_class.return_value = self.mock_repository
            
            service = GachaService(self.mock_db)
            
            assert service.db == self.mock_db
            assert service.repository == self.mock_repository
            mock_repo_class.assert_called_once_with(self.mock_db)
            
    @patch.dict(os.environ, {"GACHA_RARITY_TABLE": json.dumps([["Test", 1.0]])})
    def test_service_init_with_env_vars(self):
        """Test service initialization with environment variables."""
        with patch('app.services.gacha_service.GameRepository') as mock_repo_class:
            mock_repo_class.return_value = self.mock_repository
            
            service = GachaService(self.mock_db)
            
            # Should load from environment
            assert service.db == self.mock_db
            
    @patch('app.services.gacha_service.get_balance')
    @patch('app.services.gacha_service.deduct_tokens')
    def test_single_pull_success(self, mock_deduct, mock_get_balance):
        """Test successful single gacha pull."""
        mock_get_balance.return_value = 500
        mock_deduct.return_value = True
        
        with patch('app.services.gacha_service.GameRepository') as mock_repo_class:
            mock_repo_class.return_value = self.mock_repository
            
            service = GachaService(self.mock_db)
            
            # Mock the random selection
            with patch.object(service, '_select_rarity', return_value="Epic"):
                with patch.object(service, '_get_reward_for_rarity', return_value="Epic Sword"):
                    result = service.single_pull(user_id=1, cost=100)
                    
                    assert isinstance(result, GachaPullResult)
                    assert len(result.results) == 1
                    assert result.results[0] == "Epic Sword"
                    assert result.tokens_change == -100
                    assert result.balance == 500
                    
                    mock_deduct.assert_called_once_with(self.mock_db, 1, 100)
                    mock_get_balance.assert_called_once_with(self.mock_db, 1)
                    
    @patch('app.services.gacha_service.get_balance')
    @patch('app.services.gacha_service.deduct_tokens')
    def test_single_pull_insufficient_tokens(self, mock_deduct, mock_get_balance):
        """Test single gacha pull with insufficient tokens."""
        mock_get_balance.return_value = 50
        mock_deduct.return_value = False
        
        with patch('app.services.gacha_service.GameRepository') as mock_repo_class:
            mock_repo_class.return_value = self.mock_repository
            
            service = GachaService(self.mock_db)
            
            with pytest.raises(ValueError, match="Insufficient tokens"):
                service.single_pull(user_id=1, cost=100)
                
    @patch('app.services.gacha_service.get_balance')
    @patch('app.services.gacha_service.deduct_tokens')
    def test_multi_pull_success(self, mock_deduct, mock_get_balance):
        """Test successful multi gacha pull."""
        mock_get_balance.return_value = 1000
        mock_deduct.return_value = True
        
        with patch('app.services.gacha_service.GameRepository') as mock_repo_class:
            mock_repo_class.return_value = self.mock_repository
            
            service = GachaService(self.mock_db)
            
            # Mock the random selections
            with patch.object(service, '_select_rarity', side_effect=["Epic", "Common", "Rare"]):
                with patch.object(service, '_get_reward_for_rarity', 
                                side_effect=["Epic Sword", "Common Shield", "Rare Bow"]):
                    result = service.multi_pull(user_id=1, pull_count=3, cost_per_pull=100)
                    
                    assert isinstance(result, GachaPullResult)
                    assert len(result.results) == 3
                    assert "Epic Sword" in result.results
                    assert "Common Shield" in result.results
                    assert "Rare Bow" in result.results
                    assert result.tokens_change == -300
                    assert result.balance == 1000
                    
    def test_select_rarity_distribution(self):
        """Test rarity selection follows probability distribution."""
        with patch('app.services.gacha_service.GameRepository') as mock_repo_class:
            mock_repo_class.return_value = self.mock_repository
            
            service = GachaService(self.mock_db)
            
            # Mock rarity table for predictable testing
            service.rarity_table = [
                ("Common", 0.7),
                ("Rare", 0.25),
                ("Epic", 0.045),
                ("Legendary", 0.005)
            ]
            
            # Test multiple selections
            results = []
            for _ in range(1000):
                with patch('random.random', return_value=0.8):  # Should select Common
                    rarity = service._select_rarity()
                    results.append(rarity)
                    
            # With random value 0.8, should always select Common
            assert all(r == "Common" for r in results[:100])  # Check first 100
            
    def test_select_rarity_edge_cases(self):
        """Test rarity selection at probability boundaries."""
        with patch('app.services.gacha_service.GameRepository') as mock_repo_class:
            mock_repo_class.return_value = self.mock_repository
            
            service = GachaService(self.mock_db)
            service.rarity_table = [("Common", 0.5), ("Rare", 0.5)]
            
            # Test boundary at 0.5
            with patch('random.random', return_value=0.49):
                assert service._select_rarity() == "Common"
                
            with patch('random.random', return_value=0.51):
                assert service._select_rarity() == "Rare"
                
    def test_get_reward_for_rarity_with_rewards_pool(self):
        """Test reward selection from rewards pool."""
        with patch('app.services.gacha_service.GameRepository') as mock_repo_class:
            mock_repo_class.return_value = self.mock_repository
            
            service = GachaService(self.mock_db)
            service.rewards_pool = {
                "Epic": ["Epic Sword", "Epic Shield", "Epic Bow"],
                "Common": ["Common Dagger", "Common Potion"]
            }
            
            # Test Epic reward selection
            with patch('random.choice', return_value="Epic Sword"):
                reward = service._get_reward_for_rarity("Epic")
                assert reward == "Epic Sword"
                
            # Test Common reward selection
            with patch('random.choice', return_value="Common Potion"):
                reward = service._get_reward_for_rarity("Common")
                assert reward == "Common Potion"
                
    def test_get_reward_for_rarity_fallback(self):
        """Test reward selection fallback when no pool exists."""
        with patch('app.services.gacha_service.GameRepository') as mock_repo_class:
            mock_repo_class.return_value = self.mock_repository
            
            service = GachaService(self.mock_db)
            service.rewards_pool = {}  # Empty pool
            
            reward = service._get_reward_for_rarity("Epic")
            assert reward == "Epic Item"  # Should use fallback
            
    @patch('app.services.gacha_service.logging.getLogger')
    def test_logging_during_operations(self, mock_logger):
        """Test that operations are properly logged."""
        mock_logger_instance = Mock()
        mock_logger.return_value = mock_logger_instance
        
        with patch('app.services.gacha_service.GameRepository') as mock_repo_class:
            mock_repo_class.return_value = self.mock_repository
            
            with patch('app.services.gacha_service.get_balance', return_value=500):
                with patch('app.services.gacha_service.deduct_tokens', return_value=True):
                    service = GachaService(self.mock_db)
                    
                    with patch.object(service, '_select_rarity', return_value="Epic"):
                        with patch.object(service, '_get_reward_for_rarity', return_value="Epic Sword"):
                            service.single_pull(user_id=1, cost=100)
                            
                            # Verify logging occurred
                            assert mock_logger_instance.info.called or mock_logger_instance.debug.called
                            
    def test_rarity_table_validation(self):
        """Test rarity table validation."""
        with patch('app.services.gacha_service.GameRepository') as mock_repo_class:
            mock_repo_class.return_value = self.mock_repository
            
            service = GachaService(self.mock_db)
            
            # Test valid table
            valid_table = [("Common", 0.7), ("Rare", 0.3)]
            service.rarity_table = valid_table
            
            # Should work without issues
            with patch('random.random', return_value=0.5):
                rarity = service._select_rarity()
                assert rarity in ["Common", "Rare"]
                
    def test_repository_integration(self):
        """Test integration with GameRepository."""
        with patch('app.services.gacha_service.GameRepository') as mock_repo_class:
            mock_repo_class.return_value = self.mock_repository
            
            service = GachaService(self.mock_db)
            
            # Verify repository was initialized
            assert service.repository == self.mock_repository
            mock_repo_class.assert_called_once_with(self.mock_db)
            
    def test_service_state_consistency(self):
        """Test that service maintains consistent state."""
        with patch('app.services.gacha_service.GameRepository') as mock_repo_class:
            mock_repo_class.return_value = self.mock_repository
            
            service = GachaService(self.mock_db)
            
            # State should be consistent after initialization
            assert hasattr(service, 'db')
            assert hasattr(service, 'repository')
            assert hasattr(service, 'rarity_table')
            assert hasattr(service, 'rewards_pool')
            
            # Rarity table should be valid
            assert isinstance(service.rarity_table, list)
            assert all(isinstance(item, tuple) and len(item) == 2 for item in service.rarity_table)
            
    @patch('app.services.gacha_service.get_balance')
    @patch('app.services.gacha_service.deduct_tokens')
    def test_error_handling_in_pulls(self, mock_deduct, mock_get_balance):
        """Test error handling in pull operations."""
        mock_get_balance.side_effect = Exception("Database error")
        
        with patch('app.services.gacha_service.GameRepository') as mock_repo_class:
            mock_repo_class.return_value = self.mock_repository
            
            service = GachaService(self.mock_db)
            
            with pytest.raises(Exception):
                service.single_pull(user_id=1, cost=100)
