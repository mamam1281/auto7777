"""최종 인증 시스템 테스트"""
import requests
import json
from datetime import datetime

def test_final_auth():
    """최종 인증 시스템 테스트"""
    base_url = "http://localhost:8000"
    
    print("🎯 최종 인증 시스템 테스트")
    print("=" * 50)
    
    # 회원가입 테스트 (필수 5개 입력: 사이트아이디, 닉네임, 전화번호, 초대코드, 비밀번호)
    timestamp = datetime.now().strftime('%H%M%S')
    signup_data = {
        "site_id": f"finaltest{timestamp}",
        "nickname": f"최종테스터{timestamp}",
        "phone_number": f"010{timestamp}0000",
        "invite_code": "5858",
        "password": "finaltest123"
    }
    
    print("1️⃣ 회원가입 테스트 (필수 5개 입력)")
    print(f"   데이터: {json.dumps(signup_data, ensure_ascii=False, indent=2)}")
    
    try:
        response = requests.post(
            f"{base_url}/auth/signup",
            json=signup_data,
            headers={"Content-Type": "application/json"},
            timeout=10
        )
        print(f"   상태코드: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ 회원가입 성공!")
            print(f"   사용자 ID: {result['user']['id']}")
            print(f"   사이트 ID: {result['user']['site_id']}")
            print(f"   닉네임: {result['user']['nickname']}")
            print(f"   전화번호: {result['user']['phone_number']}")
            print(f"   토큰: {result['access_token'][:30]}...")
            
            # 로그인 테스트
            print("\n2️⃣ 로그인 테스트")
            login_data = {
                "site_id": signup_data["site_id"],
                "password": signup_data["password"]
            }
            
            login_response = requests.post(
                f"{base_url}/auth/login",
                json=login_data,
                headers={"Content-Type": "application/json"},
                timeout=10
            )
            
            if login_response.status_code == 200:
                login_result = login_response.json()
                print("✅ 로그인 성공!")
                print(f"   토큰: {login_result['access_token'][:30]}...")
            else:
                print(f"❌ 로그인 실패: {login_response.status_code}")
                print(f"   응답: {login_response.text}")
        else:
            print(f"❌ 회원가입 실패: {response.status_code}")
            print(f"   응답: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print("❌ 백엔드 서버에 연결할 수 없습니다. 서버가 실행 중인지 확인하세요.")
    except Exception as e:
        print(f"❌ 오류 발생: {e}")

if __name__ == "__main__":
    test_final_auth()
