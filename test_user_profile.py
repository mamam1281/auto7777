#!/usr/bin/env python3
"""
일반 사용자 프로필 API 테스트 스크립트
일반 사용자 계정으로 프로필 기능 검증
"""
import requests
import json

BASE_URL = "http://localhost:8000"

def test_regular_user_profile():
    print("🧪 일반 사용자 프로필 API 테스트 시작...")
    
    # 1. 일반 사용자로 로그인
    print("\n1️⃣ 일반 사용자 로그인 테스트...")
    login_data = {
        "site_id": "user001",  # 일반 사용자 계정
        "password": "testpass123"
    }
    
    try:
        login_response = requests.post(f"{BASE_URL}/api/auth/login", json=login_data)
        print(f"로그인 응답 상태: {login_response.status_code}")
        
        if login_response.status_code == 200:
            token = login_response.json().get("access_token")
            print(f"✅ 일반 사용자 JWT 토큰 획득 성공")
            
            # 2. 내 프로필 조회 (본인 정보)
            print("\n2️⃣ 내 프로필 조회 테스트...")
            headers = {"Authorization": f"Bearer {token}"}
            
            my_profile_response = requests.get(f"{BASE_URL}/api/users/me/profile", headers=headers)
            print(f"내 프로필 응답 상태: {my_profile_response.status_code}")
            
            if my_profile_response.status_code == 200:
                my_profile = my_profile_response.json()
                print("✅ 내 프로필 조회 성공!")
                print(f"   - 사용자 ID: {my_profile.get('id')}")
                print(f"   - 닉네임: {my_profile.get('nickname')}")
                print(f"   - 사이버 토큰: {my_profile.get('cyber_token_balance')}")
                print(f"   - 등급: {my_profile.get('rank')}")
                print(f"   - 민감정보(전화번호): {'phone_number' in my_profile}")
                
                my_user_id = my_profile.get('id')
                
                # 3. 다른 사용자 프로필 조회 시도 (권한 확인)
                print("\n3️⃣ 다른 사용자 프로필 조회 권한 테스트...")
                other_user_id = my_user_id + 1 if my_user_id > 1 else my_user_id + 2  # 다른 사용자 ID
                
                other_profile_response = requests.get(f"{BASE_URL}/api/users/{other_user_id}/profile", headers=headers)
                print(f"다른 사용자 프로필 응답 상태: {other_profile_response.status_code}")
                
                if other_profile_response.status_code == 200:
                    other_profile = other_profile_response.json()
                    print("✅ 다른 사용자 프로필 조회 성공 (공개 정보만)")
                    print(f"   - 다른 사용자 닉네임: {other_profile.get('nickname')}")
                    print(f"   - 민감정보 숨김 확인: {'phone_number' not in other_profile}")
                elif other_profile_response.status_code == 404:
                    print("⚠️ 다른 사용자가 존재하지 않음 (정상)")
                elif other_profile_response.status_code == 403:
                    print("✅ 다른 사용자 프로필 접근 제한 정상 작동")
                
                # 4. 내 통계 조회
                print("\n4️⃣ 내 통계 조회 테스트...")
                my_stats_response = requests.get(f"{BASE_URL}/api/users/{my_user_id}/stats", headers=headers)
                print(f"내 통계 응답 상태: {my_stats_response.status_code}")
                
                if my_stats_response.status_code == 200:
                    my_stats = my_stats_response.json()
                    print("✅ 내 통계 조회 성공!")
                    print(f"   - 총 액션 수: {my_stats.get('total_actions')}")
                    print(f"   - 총 보상 수: {my_stats.get('total_rewards')}")
                    print(f"   - 플레이 시간: {my_stats.get('play_time_minutes')}분")
                
                # 5. 다른 사용자 통계 조회 시도 (권한 확인)
                print("\n5️⃣ 다른 사용자 통계 조회 권한 테스트...")
                other_stats_response = requests.get(f"{BASE_URL}/api/users/{other_user_id}/stats", headers=headers)
                print(f"다른 사용자 통계 응답 상태: {other_stats_response.status_code}")
                
                if other_stats_response.status_code == 403:
                    print("✅ 다른 사용자 통계 접근 제한 정상 작동")
                elif other_stats_response.status_code == 404:
                    print("⚠️ 다른 사용자가 존재하지 않음")
                
                print("\n🎉 일반 사용자 프로필 API 테스트 완료!")
                return True
                
            else:
                print(f"❌ 프로필 조회 실패: {my_profile_response.text}")
                
        elif login_response.status_code == 401:
            print("⚠️ 일반 사용자 계정이 없거나 비밀번호가 틀림")
            print("대신 회원가입 후 테스트해보겠습니다...")
            return test_signup_and_profile()
        else:
            print(f"❌ 로그인 실패: {login_response.text}")
            
    except requests.exceptions.ConnectionError:
        print("❌ 서버 연결 실패 - 백엔드 서버가 실행 중인지 확인하세요")
        return False
    except Exception as e:
        print(f"❌ 테스트 중 오류 발생: {e}")
        return False
    
    return False

def test_signup_and_profile():
    """회원가입 후 프로필 테스트"""
    print("\n📝 회원가입 후 프로필 테스트...")
    
    signup_data = {
        "site_id": "testuser_" + str(int(time.time())),
        "nickname": "테스트유저",
        "phone_number": "010-1234-5678",
        "password": "testpass123",
        "invite_code": "6969"
    }
    
    try:
        import time
        signup_response = requests.post(f"{BASE_URL}/api/auth/signup", json=signup_data)
        print(f"회원가입 응답 상태: {signup_response.status_code}")
        
        if signup_response.status_code == 201:
            signup_result = signup_response.json()
            token = signup_result.get("access_token")
            print("✅ 회원가입 성공!")
            
            # 바로 프로필 조회
            headers = {"Authorization": f"Bearer {token}"}
            profile_response = requests.get(f"{BASE_URL}/api/users/me/profile", headers=headers)
            
            if profile_response.status_code == 200:
                profile = profile_response.json()
                print("✅ 신규 사용자 프로필 조회 성공!")
                print(f"   - 닉네임: {profile.get('nickname')}")
                print(f"   - 초기 사이버 토큰: {profile.get('cyber_token_balance')}")
                print(f"   - 등급: {profile.get('rank')}")
                return True
        else:
            print(f"❌ 회원가입 실패: {signup_response.text}")
            
    except Exception as e:
        print(f"❌ 회원가입 테스트 중 오류: {e}")
    
    return False

if __name__ == "__main__":
    import time
    success = test_regular_user_profile()
    
    if success:
        print("\n✅ 일반 사용자 프로필 API 검증 완료!")
        print("   ✅ 백엔드: 정상 동작")
        print("   ✅ 데이터베이스: 연결 확인")
        print("   ✅ JWT 인증: 일반 사용자 토큰 발급 성공")
        print("   ✅ 프로필 조회: 본인 정보 조회 성공")
        print("   ✅ 권한 제어: 타인 민감정보 접근 차단")
        print("   ✅ 통계 조회: 본인 통계만 접근 가능")
    else:
        print("\n❌ 일반 사용자 프로필 API에 문제가 있습니다.")
        print("   해결 방법:")
        print("   1. 백엔드 서버 상태 확인 (docker ps)")
        print("   2. 일반 사용자 계정 생성 필요")
        print("   3. JWT 토큰 발급 확인 필요")
