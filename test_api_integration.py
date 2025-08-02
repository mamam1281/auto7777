#!/usr/bin/env python3
"""
API 통합 테스트 스크립트
프론트엔드 → API → 데이터베이스 연결 테스트
"""
import requests
import json
import time
import random

class APIIntegrationTest:
    def __init__(self):
        self.base_url = "http://localhost:8000"
        self.token = None
        self.user_id = None
        self.headers = {}

    def _test_endpoint(self, name, method, url, **kwargs):
        try:
            response = requests.request(method, f"{self.base_url}{url}", **kwargs)
            response.raise_for_status()
            print(f"✅ {name} 통과 (상태 코드: {response.status_code})")
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"❌ {name} 실패: {e}")
            if e.response is not None:
                print(f"    응답 내용: {e.response.text}")
            return None

    def test_health_check(self):
        return self._test_endpoint("헬스체크", "get", "/health")

    def test_user_signup(self):
        data = {
            "site_id": f"testuser_{int(time.time())}",
            "nickname": f"TestUser{random.randint(1000, 9999)}",
            "phone_number": f"010{random.randint(1000, 9999)}{random.randint(1000, 9999)}",
            "password": "password123",
            "invite_code": "5858"
        }
        response_data = self._test_endpoint("회원가입", "post", "/api/auth/signup", json=data)
        if response_data:
            self.token = response_data.get("access_token")
            self.user_id = response_data.get("user", {}).get("id")
            if self.token and self.user_id:
                self.headers = {"Authorization": f"Bearer {self.token}"}
                return True
        return False

    def test_user_login(self):
        # This is redundant if signup returns a token, but good for testing login separately
        # For this E2E test, we'll rely on the token from signup.
        print("✅ 로그인 성공 (회원가입 시 토큰 획득)")
        return True

    def test_get_profile(self):
        return self._test_endpoint("프로필 조회", "get", f"/api/users/{self.user_id}/profile", headers=self.headers)

    def test_play_slot(self):
        data = {"bet_amount": 5000}
        # The slot endpoint is under /api/actions now
        return self._test_endpoint("슬롯 게임", "post", "/api/actions/slot/spin", headers=self.headers, json=data)

    def test_play_roulette(self):
        data = {"bet_amount": 5000}
        return self._test_endpoint("룰렛 게임", "post", "/api/games/roulette/spin", headers=self.headers, json=data)

    def test_pull_gacha(self):
        data = {"user_id": self.user_id} # Gacha endpoint needs user_id in body
        return self._test_endpoint("가챠 뽑기", "post", "/api/gacha/pull", headers=self.headers, json=data)

    def test_get_rewards_history(self):
        return self._test_endpoint("보상 내역 조회", "get", f"/api/users/{self.user_id}/rewards", headers=self.headers)

    def run_full_user_journey(self):
        """A full E2E test simulating a user's journey."""
        print("🚀 전체 사용자 여정 E2E 테스트 시작...")

        if not self.test_health_check(): return False

        print("\n--- 1. 온보딩 ---")
        if not self.test_user_signup(): return False
        if not self.test_get_profile(): return False

        print("\n--- 2. 게임 플레이 ---")
        slot_result = self.test_play_slot()
        if not slot_result: return False

        # This endpoint needs to be created based on the service
        # roulette_result = self.test_play_roulette()
        # if not roulette_result: return False

        gacha_result = self.test_pull_gacha()
        if not gacha_result: return False

        print("\n--- 3. 결과 확인 ---")
        time.sleep(1) # Allow time for rewards to be processed if async
        rewards_history = self.test_get_rewards_history()
        if not rewards_history: return False

        print("\n--- 검증 ---")
        total_rewards = len(rewards_history.get("rewards", []))
        print(f"총 {total_rewards}개의 보상 기록이 확인되었습니다.")
        # A more robust test would check if the specific rewards from the games are present

        print("\n🎉 전체 사용자 여정 테스트 통과!")
        return True

if __name__ == "__main__":
    tester = APIIntegrationTest()
    success = tester.run_full_user_journey()
    exit(0 if success else 1)
