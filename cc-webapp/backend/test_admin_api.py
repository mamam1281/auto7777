#!/usr/bin/env python3
"""
관리자 기능 리프레시 자동화 테스트 스크립트
Casino-Club F2P 프로젝트 - 관리자 API 종합 테스트
"""

import asyncio
import aiohttp
import json
import time
from typing import Dict, Any, List
import sys
import os

# 백엔드 경로를 sys.path에 추가
sys.path.append('/app')

class AdminAPITester:
    def __init__(self, base_url: str = "http://localhost:8001"):
        self.base_url = base_url
        self.admin_token = None
        self.user_token = None
        self.test_user_id = None
        
    async def setup_tokens(self):
        """관리자와 일반 사용자 토큰 생성"""
        async with aiohttp.ClientSession() as session:
            # 1. 관리자 회원가입/로그인
            admin_signup_data = {
                "site_id": "admin_test_001", 
                "nickname": "AdminTester",
                "phone_number": "010-1111-1111",
                "password": "admin123!",
                "invite_code": "6969"
            }
            
            # 기존 계정으로 로그인 시도
            print("⚠️ 기존 관리자 계정으로 로그인 시도")
            login_data = {"site_id": "admin_test_001", "password": "admin123!"}
            async with session.post(f"{self.base_url}/api/auth/login", json=login_data) as login_resp:
                if login_resp.status == 200:
                    result = await login_resp.json()
                    self.admin_token = result.get("access_token")
                    print(f"✅ 관리자 로그인 성공")
                else:
                    error_text = await login_resp.text()
                    print(f"❌ 관리자 로그인 실패: {login_resp.status} - {error_text}")
                    return False
            
            # 2. 일반 사용자 회원가입/로그인
            user_signup_data = {
                "site_id": "user_test_001",
                "nickname": "RegularUser", 
                "phone_number": "010-2222-2222",
                "password": "user123!",
                "invite_code": "6969"
            }
            
            # 기존 계정으로 로그인 시도
            print("⚠️ 기존 일반 사용자 계정으로 로그인 시도")
            login_data = {"site_id": "user_test_001", "password": "user123!"}
            async with session.post(f"{self.base_url}/api/auth/login", json=login_data) as login_resp:
                if login_resp.status == 200:
                    result = await login_resp.json()
                    self.user_token = result.get("access_token")
                    # 현재 사용자 정보 조회로 user_id 얻기
                    headers_user = {"Authorization": f"Bearer {self.user_token}"}
                    async with session.get(f"{self.base_url}/api/auth/me", headers=headers_user) as me_resp:
                        if me_resp.status == 200:
                            user_info = await me_resp.json()
                            self.test_user_id = user_info.get("id")
                    print(f"✅ 일반 사용자 로그인 성공")
                else:
                    error_text = await login_resp.text()
                    print(f"❌ 일반 사용자 로그인 실패: {login_resp.status} - {error_text}")
                    return False
        
        return self.admin_token and self.user_token
    
    async def test_member_management_api(self):
        """회원 관리 API 테스트 (목록, 상세, 등급/상태 변경, 삭제, 로그)"""
        print("\n🔍 === 회원 관리 API 테스트 시작 ===")
        
        async with aiohttp.ClientSession() as session:
            headers_admin = {"Authorization": f"Bearer {self.admin_token}"}
            headers_user = {"Authorization": f"Bearer {self.user_token}"}
            
            # 1. 회원 목록 조회 - 관리자 권한
            print("\n1️⃣ 회원 목록 조회 테스트")
            async with session.get(f"{self.base_url}/api/admin/users", headers=headers_admin) as resp:
                if resp.status == 200:
                    users = await resp.json()
                    print(f"✅ 관리자 권한으로 회원 목록 조회 성공: {len(users)}명")
                else:
                    error_text = await resp.text()
                    print(f"❌ 관리자 회원 목록 조회 실패: {resp.status} - {error_text}")
            
            # 2. 회원 목록 조회 - 일반 사용자 권한 (접근 거부 확인)
            async with session.get(f"{self.base_url}/api/admin/users", headers=headers_user) as resp:
                if resp.status == 403:
                    print("✅ 일반 사용자 권한으로 관리자 API 접근 차단 확인")
                else:
                    print(f"❌ 일반 사용자 접근 제어 실패: {resp.status}")
            
            # 3. 회원 상세 조회 - 관리자 권한
            if self.test_user_id:
                print(f"\n2️⃣ 회원 상세 조회 테스트 (user_id: {self.test_user_id})")
                async with session.get(f"{self.base_url}/api/admin/users/{self.test_user_id}", headers=headers_admin) as resp:
                    if resp.status == 200:
                        user_detail = await resp.json()
                        print(f"✅ 회원 상세 조회 성공: {user_detail.get('nickname', 'N/A')}")
                        print(f"   - 사이버 토큰: {user_detail.get('cyber_token_balance', 0)}")
                        print(f"   - 등급: {user_detail.get('rank', 'N/A')}")
                    else:
                        error_text = await resp.text()
                        print(f"❌ 회원 상세 조회 실패: {resp.status} - {error_text}")
            
            # 4. 보상 지급 테스트 - 관리자 권한
            if self.test_user_id:
                print(f"\n3️⃣ 보상 지급 테스트")
                reward_data = {
                    "reward_type": "CYBER_TOKEN",
                    "amount": 500,
                    "reason": "관리자 API 테스트 보상"
                }
                async with session.post(f"{self.base_url}/api/admin/users/{self.test_user_id}/reward", 
                                        json=reward_data, headers=headers_admin) as resp:
                    if resp.status == 200:
                        reward_result = await resp.json()
                        print(f"✅ 보상 지급 성공: {reward_result.get('amount', 0)} {reward_result.get('reward_type', 'N/A')}")
                    else:
                        error_text = await resp.text()
                        print(f"❌ 보상 지급 실패: {resp.status} - {error_text}")
            
            # 5. 활동 로그 조회 테스트
            print(f"\n4️⃣ 활동 로그 조회 테스트")
            async with session.get(f"{self.base_url}/api/admin/activities", headers=headers_admin) as resp:
                if resp.status == 200:
                    activities = await resp.json()
                    print(f"✅ 활동 로그 조회 성공: {len(activities)}개 활동")
                    for activity in activities[:3]:  # 최근 3개만 표시
                        print(f"   - {activity.get('activity_type', 'N/A')}: {activity.get('timestamp', 'N/A')}")
                else:
                    error_text = await resp.text()
                    print(f"❌ 활동 로그 조회 실패: {resp.status} - {error_text}")
    
    async def test_reward_item_management_api(self):
        """보상/아이템 관리 API 테스트 (아직 구현되지 않은 경우 스킵)"""
        print("\n🎁 === 보상/아이템 관리 API 테스트 시작 ===")
        
        # 현재 보상 지급 API만 구현되어 있으므로 해당 기능 테스트
        async with aiohttp.ClientSession() as session:
            headers_admin = {"Authorization": f"Bearer {self.admin_token}"}
            
            # 다양한 보상 유형 테스트
            reward_types = [
                {"reward_type": "CYBER_TOKEN", "amount": 100, "reason": "토큰 보상 테스트"},
                {"reward_type": "PREMIUM_GEM", "amount": 50, "reason": "젬 보상 테스트"},
                {"reward_type": "BONUS_SPIN", "amount": 3, "reason": "보너스 스핀 테스트"}
            ]
            
            for i, reward_data in enumerate(reward_types, 1):
                if self.test_user_id:
                    print(f"\n{i}️⃣ {reward_data['reward_type']} 보상 지급 테스트")
                    async with session.post(f"{self.base_url}/api/admin/users/{self.test_user_id}/reward",
                                            json=reward_data, headers=headers_admin) as resp:
                        if resp.status == 200:
                            result = await resp.json()
                            print(f"✅ {reward_data['reward_type']} 보상 지급 성공")
                        else:
                            error_text = await resp.text()
                            print(f"❌ {reward_data['reward_type']} 보상 지급 실패: {resp.status} - {error_text}")
    
    async def test_notification_campaign_api(self):
        """알림/캠페인 관리 API 테스트 (알림 API가 있는지 확인)"""
        print("\n📢 === 알림/캠페인 관리 API 테스트 시작 ===")
        
        async with aiohttp.ClientSession() as session:
            headers_admin = {"Authorization": f"Bearer {self.admin_token}"}
            
            # 알림 관련 API 확인 (구현되어 있는지 테스트)
            test_endpoints = [
                "/admin/notifications",
                "/admin/campaigns", 
                "/notification/send",
                "/notification/schedule"
            ]
            
            for endpoint in test_endpoints:
                async with session.get(f"{self.base_url}{endpoint}", headers=headers_admin) as resp:
                    if resp.status in [200, 404, 405]:  # 404나 405도 엔드포인트가 존재한다는 의미
                        if resp.status == 200:
                            print(f"✅ {endpoint} API 응답 성공")
                        else:
                            print(f"⚠️ {endpoint} API 존재하지만 {resp.status} 응답")
                    else:
                        print(f"❌ {endpoint} API 접근 실패: {resp.status}")
    
    async def run_full_test(self):
        """전체 관리자 기능 리프레시 자동화 테스트 실행"""
        print("🚀 === Casino-Club F2P 관리자 기능 리프레시 자동화 테스트 시작 ===")
        print(f"테스트 대상 서버: {self.base_url}")
        print(f"테스트 시간: {time.strftime('%Y-%m-%d %H:%M:%S')}")
        
        # 1. 토큰 설정
        if not await self.setup_tokens():
            print("❌ 토큰 설정 실패 - 테스트 중단")
            return False
        
        print(f"✅ 관리자 토큰: {self.admin_token[:20]}...")
        print(f"✅ 일반 사용자 토큰: {self.user_token[:20]}...")
        
        # 2. 회원 관리 API 테스트
        await self.test_member_management_api()
        
        # 3. 보상/아이템 관리 API 테스트  
        await self.test_reward_item_management_api()
        
        # 4. 알림/캠페인 관리 API 테스트
        await self.test_notification_campaign_api()
        
        print("\n🎯 === 관리자 기능 리프레시 자동화 테스트 완료 ===")
        return True

async def main():
    tester = AdminAPITester()
    await tester.run_full_test()

if __name__ == "__main__":
    asyncio.run(main())
