"""
게임 API 인증 통합 테스트 스크립트
- 로그인해서 토큰 발급
- 토큰으로 게임 API 호출
- 토큰 없이 시도하여 인증 실패 확인

사용 방법:
1. 필요한 패키지 설치: pip install requests
2. 서버 실행: python run_server.py
3. 테스트 실행: python test_game_api_auth.py
"""

import requests
import json
import sys
from datetime import datetime

# 서버 URL 설정
BASE_URL = "http://localhost:8000"
AUTH_URL = f"{BASE_URL}/api/auth/login"
SLOT_URL = f"{BASE_URL}/api/games/slot/spin"
ROULETTE_URL = f"{BASE_URL}/api/games/roulette/spin"
GACHA_URL = f"{BASE_URL}/api/games/gacha/pull"
STATS_URL = f"{BASE_URL}/api/games/stats"

# 테스트 사용자 정보
TEST_USER = {
    "site_id": "test_user",
    "password": "test_password"
}

def log(message):
    """로그 출력 함수"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{timestamp}] {message}")

def login_and_get_token():
    """로그인해서 토큰 발급"""
    log("로그인 시도...")
    try:
        response = requests.post(AUTH_URL, json=TEST_USER)
        response.raise_for_status()
        token_data = response.json()
        token = token_data.get("access_token")
        if not token:
            log("오류: 토큰을 받지 못했습니다.")
            return None
        log("로그인 성공! 토큰 발급 완료.")
        return token
    except requests.exceptions.RequestException as e:
        log(f"로그인 오류: {str(e)}")
        if hasattr(response, 'text'):
            log(f"서버 응답: {response.text}")
        return None

def test_game_api_with_token(token):
    """토큰으로 게임 API 호출 테스트"""
    headers = {"Authorization": f"Bearer {token}"}
    
    # 1. 슬롯 머신 테스트
    log("슬롯 머신 API 호출 테스트...")
    try:
        response = requests.post(SLOT_URL, headers=headers)
        response.raise_for_status()
        log(f"슬롯 머신 응답: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
    except requests.exceptions.RequestException as e:
        log(f"슬롯 머신 API 오류: {str(e)}")
        if hasattr(response, 'text'):
            log(f"서버 응답: {response.text}")
    
    # 2. 룰렛 테스트
    log("룰렛 API 호출 테스트...")
    try:
        response = requests.post(ROULETTE_URL, headers=headers)
        response.raise_for_status()
        log(f"룰렛 응답: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
    except requests.exceptions.RequestException as e:
        log(f"룰렛 API 오류: {str(e)}")
        if hasattr(response, 'text'):
            log(f"서버 응답: {response.text}")
    
    # 3. 가챠 테스트
    log("가챠 API 호출 테스트...")
    try:
        response = requests.post(GACHA_URL, json={"count": 1}, headers=headers)
        response.raise_for_status()
        log(f"가챠 응답: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
    except requests.exceptions.RequestException as e:
        log(f"가챠 API 오류: {str(e)}")
        if hasattr(response, 'text'):
            log(f"서버 응답: {response.text}")
    
    # 4. 게임 통계 테스트 (V2 API)
    log("게임 통계 API 호출 테스트...")
    try:
        response = requests.get(STATS_URL, headers=headers)
        response.raise_for_status()
        log(f"게임 통계 응답: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
    except requests.exceptions.RequestException as e:
        log(f"게임 통계 API 오류: {str(e)}")
        if hasattr(response, 'text'):
            log(f"서버 응답: {response.text}")

def test_game_api_without_token():
    """토큰 없이 게임 API 호출해서 인증 실패 확인"""
    log("토큰 없이 슬롯 머신 API 호출 테스트...")
    try:
        response = requests.post(SLOT_URL)
        if response.status_code == 401:
            log("예상대로 401 Unauthorized 오류 발생 (정상)")
        else:
            log(f"예상과 다른 응답 코드: {response.status_code}")
            log(f"응답: {response.text}")
    except requests.exceptions.RequestException as e:
        log(f"요청 오류: {str(e)}")

if __name__ == "__main__":
    log("게임 API 인증 통합 테스트 시작")
    
    # 1. 토큰 발급
    token = login_and_get_token()
    if not token:
        log("토큰 발급 실패로 테스트 종료")
        sys.exit(1)
    
    # 2. 토큰으로 게임 API 호출
    test_game_api_with_token(token)
    
    # 3. 토큰 없이 시도하여 인증 실패 확인
    test_game_api_without_token()
    
    log("게임 API 인증 통합 테스트 완료")
