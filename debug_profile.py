"""
프로필 API 상세 테스트
"""
import requests
import json

BASE_URL = "http://localhost:8000"

def test_profile_api_detailed():
    """프로필 API 상세 테스트"""
    
    print("🔍 프로필 API 상세 테스트...")
    
    # 1. 프로필 API 호출 (더 자세한 에러 정보)
    try:
        profile_url = f"{BASE_URL}/api/users/1/profile"
        print(f"\n📡 GET {profile_url}")
        
        response = requests.get(profile_url, timeout=10)
        print(f"Status Code: {response.status_code}")
        print(f"Headers: {dict(response.headers)}")
        print(f"Response: {response.text}")
        
        if response.status_code != 200:
            # 다른 사용자 ID로도 테스트
            for user_id in [0, 2, 999]:
                test_url = f"{BASE_URL}/api/users/{user_id}/profile"
                test_response = requests.get(test_url, timeout=5)
                print(f"User {user_id}: {test_response.status_code}")
        
    except Exception as e:
        print(f"❌ 프로필 API 오류: {e}")
    
    # 2. 인증 토큰 있이 테스트 (임시 토큰으로)
    try:
        headers = {
            "Authorization": "Bearer fake_token",
            "Content-Type": "application/json"
        }
        
        profile_url = f"{BASE_URL}/api/users/1/profile"
        response = requests.get(profile_url, headers=headers, timeout=10)
        print(f"\n🔐 인증 헤더 포함: {response.status_code}")
        print(f"Response: {response.text}")
        
    except Exception as e:
        print(f"❌ 인증 토큰 테스트 오류: {e}")

if __name__ == "__main__":
    test_profile_api_detailed()
