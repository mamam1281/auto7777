"""
Phase D: API 엔드포인트 통합 테스트
"""
import requests
import json

BASE_URL = "http://127.0.0.1:8001"

def test_server_health():
    """서버 상태 확인"""
    print("🏥 서버 헬스체크")
    try:
        response = requests.get(f"{BASE_URL}/api/health")
        if response.status_code == 200:
            print("✅ 서버 정상 동작")
            return True
        else:
            print(f"❌ 서버 응답 오류: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ 서버 연결 실패: {e}")
        return False

def create_test_invite_code():
    """테스트용 초대코드 생성"""
    print("\n🎫 초대코드 생성")
    try:
        response = requests.post(f"{BASE_URL}/api/admin/invite-codes", json={"count": 1})
        if response.status_code == 200:
            data = response.json()
            invite_code = data["codes"][0]
            print(f"✅ 초대코드 생성 성공: {invite_code}")
            return invite_code
        else:
            print(f"❌ 초대코드 생성 실패: {response.status_code}")
            print(response.text)
            return None
    except Exception as e:
        print(f"❌ 초대코드 생성 오류: {e}")
        return None

def test_signup_api(invite_code):
    """회원가입 API 테스트"""
    print("\n📝 회원가입 API 테스트")
    
    signup_data = {
        "site_id": "testuser123",
        "nickname": "테스트유저",
        "phone_number": "010-1234-5678",
        "password": "testpass123",
        "invite_code": invite_code
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/auth/signup",
            headers={"Content-Type": "application/json"},
            json=signup_data
        )
        
        print(f"상태 코드: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("✅ 회원가입 성공!")
            print(f"   메시지: {data.get('message')}")
            print(f"   토큰: {data.get('access_token')[:20]}...")
            return True
        else:
            print("❌ 회원가입 실패")
            print(f"   오류: {response.json()}")
            return False
            
    except Exception as e:
        print(f"❌ 회원가입 API 오류: {e}")
        return False

def test_login_api():
    """로그인 API 테스트"""
    print("\n🔐 로그인 API 테스트")
    
    login_data = {
        "site_id": "testuser123",
        "password": "testpass123"
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/auth/login",
            headers={"Content-Type": "application/json"},
            json=login_data
        )
        
        print(f"상태 코드: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("✅ 로그인 성공!")
            print(f"   메시지: {data.get('message')}")
            print(f"   토큰: {data.get('access_token')[:20]}...")
            return True
        else:
            print("❌ 로그인 실패")
            print(f"   오류: {response.json()}")
            return False
            
    except Exception as e:
        print(f"❌ 로그인 API 오류: {e}")
        return False

def test_invalid_login():
    """잘못된 로그인 테스트"""
    print("\n🚫 잘못된 로그인 테스트")
    
    login_data = {
        "site_id": "testuser123",
        "password": "wrongpassword"
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/auth/login",
            headers={"Content-Type": "application/json"},
            json=login_data
        )
        
        if response.status_code == 401:
            print("✅ 잘못된 비밀번호 차단 성공")
            return True
        else:
            print(f"❌ 예상과 다른 응답: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ 테스트 오류: {e}")
        return False

def test_duplicate_signup(invite_code):
    """중복 회원가입 테스트"""
    print("\n🚫 중복 회원가입 테스트")
    
    signup_data = {
        "site_id": "testuser123",  # 이미 존재하는 사이트ID
        "nickname": "다른닉네임",
        "phone_number": "010-9999-8888",
        "password": "testpass123",
        "invite_code": invite_code
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/auth/signup",
            headers={"Content-Type": "application/json"},
            json=signup_data
        )
        
        if response.status_code == 400:
            error_data = response.json()
            print("✅ 중복 사이트ID 차단 성공")
            print(f"   오류 메시지: {error_data.get('detail')}")
            return True
        else:
            print(f"❌ 예상과 다른 응답: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ 테스트 오류: {e}")
        return False

def main():
    print("🧪 Phase D: API 통합 테스트 시작")
    print("=" * 60)
    
    # 1. 서버 상태 확인
    if not test_server_health():
        print("\n❌ 서버가 실행되지 않았습니다!")
        return
    
    # 2. 초대코드 생성
    invite_code = create_test_invite_code()
    if not invite_code:
        print("\n❌ 초대코드 생성 실패!")
        return
    
    # 3. 회원가입 테스트
    signup_success = test_signup_api(invite_code)
    
    # 4. 로그인 테스트
    login_success = test_login_api()
    
    # 5. 잘못된 로그인 테스트
    invalid_login_success = test_invalid_login()
    
    # 6. 다른 초대코드로 중복 테스트
    invite_code2 = create_test_invite_code()
    duplicate_success = test_duplicate_signup(invite_code2) if invite_code2 else False
    
    # 결과 요약
    print("\n" + "=" * 60)
    print("🎯 테스트 결과 요약:")
    print(f"✅ 서버 상태: 정상")
    print(f"{'✅' if signup_success else '❌'} 회원가입: {'성공' if signup_success else '실패'}")
    print(f"{'✅' if login_success else '❌'} 로그인: {'성공' if login_success else '실패'}")
    print(f"{'✅' if invalid_login_success else '❌'} 잘못된 로그인 차단: {'성공' if invalid_login_success else '실패'}")
    print(f"{'✅' if duplicate_success else '❌'} 중복 가입 차단: {'성공' if duplicate_success else '실패'}")
    
    all_success = all([signup_success, login_success, invalid_login_success, duplicate_success])
    
    if all_success:
        print("\n🎉 모든 API 테스트 성공!")
        print("✅ 백엔드 API가 완벽하게 동작합니다!")
    else:
        print("\n❌ 일부 테스트 실패")
        print("❗ 백엔드 API에 문제가 있습니다.")

if __name__ == "__main__":
    main()
