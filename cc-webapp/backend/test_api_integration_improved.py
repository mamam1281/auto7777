#!/usr/bin/env python3
"""
Phase D: 백엔드+프론트엔드 통합 테스트 (개선된 버전)
- 고유한 테스트 데이터 사용
- 전체 회원가입 → 로그인 플로우 테스트
- 에러 케이스 검증
"""

import requests
import json
import time
import random
import string
from datetime import datetime

# 서버 설정
BASE_URL = "http://127.0.0.1:8001"

def generate_unique_id(prefix="test"):
    """고유한 테스트 ID 생성"""
    timestamp = int(time.time() * 1000)  # 밀리초
    random_suffix = ''.join(random.choices(string.ascii_lowercase, k=4))
    return f"{prefix}{timestamp}{random_suffix}"

def test_health_check():
    """서버 상태 확인"""
    print("🔍 서버 상태 확인...")
    try:
        response = requests.get(f"{BASE_URL}/api/health", timeout=5)
        if response.status_code == 200:
            print("✅ 서버 상태: 정상")
            return True
        else:
            print(f"❌ 서버 상태: 오류 {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ 서버 연결 실패: {e}")
        return False

def test_invite_code_generation():
    """초대코드 생성 테스트"""
    print("\n🎫 초대코드 생성 테스트...")
    try:
        response = requests.post(f"{BASE_URL}/api/admin/invite-codes", 
                                json={"count": 1}, timeout=10)
        if response.status_code == 200:
            data = response.json()
            invite_code = data["codes"][0]
            print(f"✅ 초대코드 생성: {invite_code}")
            return invite_code
        else:
            print(f"❌ 초대코드 생성 실패: {response.status_code}")
            return None
    except Exception as e:
        print(f"❌ 초대코드 생성 오류: {e}")
        return None

def test_complete_user_flow():
    """완전한 사용자 플로우 테스트: 초대코드 → 회원가입 → 로그인"""
    print("\n🚀 완전한 사용자 플로우 테스트 시작...")
    
    # 1. 초대코드 생성
    invite_code = test_invite_code_generation()
    if not invite_code:
        return False
    
    # 2. 고유한 테스트 데이터 생성
    unique_site_id = generate_unique_id("user")
    test_data = {
        "site_id": unique_site_id,
        "nickname": f"테스트유저_{int(time.time())}",
        "phone_number": f"010-{random.randint(1000,9999)}-{random.randint(1000,9999)}",
        "password": "test123!@#",
        "invite_code": invite_code
    }
    
    print(f"📝 테스트 데이터: {test_data['site_id']}, {test_data['nickname']}, {test_data['phone_number']}")
    
    # 3. 회원가입 테스트
    print("\n👤 회원가입 테스트...")
    try:
        response = requests.post(f"{BASE_URL}/api/auth/signup", 
                                json=test_data, timeout=10)
        if response.status_code == 200:
            signup_data = response.json()
            print(f"✅ 회원가입 성공: {signup_data.get('message', '성공')}")
            user_id = signup_data.get('user_id')
            print(f"   사용자 ID: {user_id}")
        else:
            error_data = response.json()
            print(f"❌ 회원가입 실패: {response.status_code}")
            print(f"   오류 내용: {error_data.get('detail', '알 수 없음')}")
            return False
    except Exception as e:
        print(f"❌ 회원가입 오류: {e}")
        return False
    
    # 4. 로그인 테스트
    print("\n🔐 로그인 테스트...")
    login_data = {
        "site_id": test_data["site_id"],
        "password": test_data["password"]
    }
    
    try:
        response = requests.post(f"{BASE_URL}/api/auth/login", 
                                json=login_data, timeout=10)
        if response.status_code == 200:
            login_response = response.json()
            print(f"✅ 로그인 성공: {login_response.get('user', {}).get('nickname', 'Unknown')}")
            print(f"   토큰 타입: {login_response.get('token_type', 'Unknown')}")
            return True
        else:
            error_data = response.json()
            print(f"❌ 로그인 실패: {response.status_code}")
            print(f"   오류 내용: {error_data.get('detail', '알 수 없음')}")
            return False
    except Exception as e:
        print(f"❌ 로그인 오류: {e}")
        return False

def test_error_cases():
    """에러 케이스 테스트"""
    print("\n🚨 에러 케이스 테스트...")
    
    # 1. 잘못된 초대코드로 회원가입
    print("1️⃣ 잘못된 초대코드 테스트...")
    invalid_signup = {
        "site_id": generate_unique_id("invalid"),
        "nickname": "잘못된초대코드",
        "phone_number": "010-0000-0000",
        "password": "test123",
        "invite_code": "INVALID123"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/api/auth/signup", 
                                json=invalid_signup, timeout=10)
        if response.status_code == 400:
            print("✅ 잘못된 초대코드 거부됨")
        else:
            print(f"❌ 예상과 다른 응답: {response.status_code}")
    except Exception as e:
        print(f"❌ 테스트 오류: {e}")
    
    # 2. 존재하지 않는 사용자 로그인
    print("2️⃣ 존재하지 않는 사용자 로그인 테스트...")
    invalid_login = {
        "site_id": "nonexistent_user_12345",
        "password": "anypassword"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/api/auth/login", 
                                json=invalid_login, timeout=10)
        if response.status_code == 401:
            print("✅ 존재하지 않는 사용자 로그인 거부됨")
        else:
            print(f"❌ 예상과 다른 응답: {response.status_code}")
    except Exception as e:
        print(f"❌ 테스트 오류: {e}")

def main():
    """메인 테스트 실행"""
    print("🧪 Phase D: 백엔드+프론트엔드 통합 테스트 (개선된 버전)")
    print("=" * 60)
    print(f"⏰ 테스트 시작 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # 서버 상태 확인
    if not test_health_check():
        print("❌ 서버가 실행되지 않았습니다. test_server_phase_d.py를 먼저 실행하세요.")
        return
    
    # 완전한 사용자 플로우 테스트
    flow_success = test_complete_user_flow()
    
    # 에러 케이스 테스트
    test_error_cases()
    
    # 결과 요약
    print("\n" + "=" * 60)
    print("📊 테스트 결과 요약")
    print("=" * 60)
    if flow_success:
        print("✅ 전체 사용자 플로우: 성공")
        print("✅ Phase D 통합 테스트: 완료")
        print("\n🎉 모든 테스트가 성공했습니다!")
        print("🔜 다음 단계: 프론트엔드 폼과 백엔드 API 연동 테스트")
    else:
        print("❌ 전체 사용자 플로우: 실패")
        print("❌ Phase D 통합 테스트: 미완료")
        print("\n🔧 문제를 해결한 후 다시 테스트하세요.")
    
    print(f"⏰ 테스트 완료 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

if __name__ == "__main__":
    main()
