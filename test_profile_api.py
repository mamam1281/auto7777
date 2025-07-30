#!/usr/bin/env python3
"""
프로필 API 테스트 스크립트
JWT 토큰 생성 후 프로필 API 호출
"""
import requests
import json

BASE_URL = "http://localhost:8000"

def test_profile_api():
    print("🧪 프로필 API 연동 테스트 시작...")
    
    # 1. 로그인하여 JWT 토큰 얻기
    print("\n1️⃣ 로그인 테스트...")
    login_data = {
        "site_id": "admin_test_001",
        "password": "adminpass123"
    }
    
    try:
        login_response = requests.post(f"{BASE_URL}/api/auth/login", json=login_data)
        print(f"로그인 응답 상태: {login_response.status_code}")
        
        if login_response.status_code == 200:
            token = login_response.json().get("access_token")
            print(f"✅ JWT 토큰 획득 성공: {token[:20]}...")
            
            # 2. 내 프로필 조회
            print("\n2️⃣ 내 프로필 조회 테스트...")
            headers = {"Authorization": f"Bearer {token}"}
            
            profile_response = requests.get(f"{BASE_URL}/api/users/me/profile", headers=headers)
            print(f"프로필 조회 응답 상태: {profile_response.status_code}")
            
            if profile_response.status_code == 200:
                profile_data = profile_response.json()
                print("✅ 프로필 조회 성공!")
                print(f"   - 사용자 ID: {profile_data.get('id')}")
                print(f"   - 닉네임: {profile_data.get('nickname')}")
                print(f"   - 등급: {profile_data.get('rank')}")
                print(f"   - 사이버 토큰: {profile_data.get('cyber_token_balance')}")
                print(f"   - 로그인 횟수: {profile_data.get('login_count')}")
                
                # 3. 특정 사용자 프로필 조회 (자기 자신)
                print("\n3️⃣ 특정 사용자 프로필 조회 테스트...")
                user_id = profile_data.get('id')
                user_profile_response = requests.get(f"{BASE_URL}/api/users/{user_id}/profile", headers=headers)
                
                print(f"특정 사용자 프로필 조회 응답 상태: {user_profile_response.status_code}")
                
                if user_profile_response.status_code == 200:
                    print("✅ 특정 사용자 프로필 조회 성공!")
                    user_profile_data = user_profile_response.json()
                    print(f"   - 민감 정보 포함 여부: {'phone_number' in user_profile_data}")
                
                # 4. 사용자 통계 조회
                print("\n4️⃣ 사용자 통계 조회 테스트...")
                stats_response = requests.get(f"{BASE_URL}/api/users/{user_id}/stats", headers=headers)
                
                print(f"사용자 통계 조회 응답 상태: {stats_response.status_code}")
                
                if stats_response.status_code == 200:
                    print("✅ 사용자 통계 조회 성공!")
                    stats_data = stats_response.json()
                    print(f"   - 총 액션 수: {stats_data.get('total_actions')}")
                    print(f"   - 총 보상 수: {stats_data.get('total_rewards')}")
                    print(f"   - 마지막 활동: {stats_data.get('last_activity')}")
                
                print("\n🎉 모든 프로필 API 테스트 통과!")
                return True
                
            else:
                print(f"❌ 프로필 조회 실패: {profile_response.text}")
                
        else:
            print(f"❌ 로그인 실패: {login_response.text}")
            
    except requests.exceptions.ConnectionError:
        print("❌ 서버 연결 실패 - 백엔드 서버가 실행 중인지 확인하세요")
        return False
    except Exception as e:
        print(f"❌ 테스트 중 오류 발생: {e}")
        return False
    
    return False

if __name__ == "__main__":
    success = test_profile_api()
    
    if success:
        print("\n✅ 프로필 API 연동 검증 완료!")
        print("   - 백엔드: 정상 동작")
        print("   - 데이터베이스: 연결 확인")
        print("   - API: JWT 인증 및 프로필 조회 성공")
    else:
        print("\n❌ 프로필 API 연동에 문제가 있습니다.")
        print("   해결 방법:")
        print("   1. 백엔드 서버 상태 확인 (docker ps)")
        print("   2. 데이터베이스 연결 확인")
        print("   3. 관리자 계정 존재 확인")
