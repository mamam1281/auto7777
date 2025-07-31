"""
간단한 프로필 API 디버깅 스크립트
"""
import requests
import json

# API 설정
BASE_URL = "http://localhost:8000"

def test_simple_endpoints():
    """간단한 엔드포인트들 테스트"""
    
    print("🔍 간단한 API 엔드포인트 테스트...")
    
    # 1. 헬스체크
    try:
        response = requests.get(f"{BASE_URL}/", timeout=5)
        print(f"Root: {response.status_code}")
    except Exception as e:
        print(f"Root 오류: {e}")
    
    # 2. 인증 관련 엔드포인트 확인
    try:
        response = requests.get(f"{BASE_URL}/api/auth/me", timeout=5)
        print(f"Auth Me (no token): {response.status_code}")
    except Exception as e:
        print(f"Auth Me 오류: {e}")
    
    # 3. 사용자 라우터가 등록되어 있는지 확인
    try:
        response = requests.get(f"{BASE_URL}/api/users", timeout=5)
        print(f"Users endpoint: {response.status_code} - {response.text[:100]}")
    except Exception as e:
        print(f"Users 오류: {e}")
    
    # 4. OpenAPI 스키마에서 users 엔드포인트 확인
    try:
        response = requests.get(f"{BASE_URL}/openapi.json", timeout=5)
        if response.status_code == 200:
            openapi = response.json()
            paths = openapi.get("paths", {})
            user_paths = [path for path in paths.keys() if "users" in path]
            print(f"사용자 관련 경로들: {user_paths}")
        else:
            print(f"OpenAPI 스키마 조회 실패: {response.status_code}")
    except Exception as e:
        print(f"OpenAPI 스키마 오류: {e}")

if __name__ == "__main__":
    test_simple_endpoints()
