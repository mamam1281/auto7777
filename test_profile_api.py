"""
프로필 API 테스트 스크립트
"""
import requests
import json

# API 설정
BASE_URL = "http://localhost:8000"
HEADERS = {
    "Content-Type": "application/json",
    "Accept": "application/json"
}

def test_profile_api():
    """프로필 API 테스트"""
    
    print("🔍 프로필 API 테스트 시작...")
    
    # 1. 사용자 프로필 조회 테스트 (ID=1)
    try:
        profile_url = f"{BASE_URL}/api/users/1/profile"
        print(f"\n📡 GET {profile_url}")
        
        response = requests.get(profile_url, headers=HEADERS, timeout=10)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            profile_data = response.json()
            print("✅ 프로필 조회 성공!")
            print(json.dumps(profile_data, indent=2, ensure_ascii=False))
        else:
            print(f"❌ 프로필 조회 실패: {response.text}")
            
    except requests.exceptions.RequestException as e:
        print(f"❌ 네트워크 오류: {e}")
    
    # 2. API 문서 확인
    try:
        docs_url = f"{BASE_URL}/docs"
        print(f"\n📖 API 문서 확인: {docs_url}")
        
        response = requests.get(docs_url, timeout=10)
        if response.status_code == 200:
            print("✅ API 문서 접근 가능")
        else:
            print(f"❌ API 문서 접근 실패: {response.status_code}")
            
    except requests.exceptions.RequestException as e:
        print(f"❌ API 문서 접근 오류: {e}")

if __name__ == "__main__":
    test_profile_api()
