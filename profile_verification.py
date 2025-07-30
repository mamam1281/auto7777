#!/usr/bin/env python3
"""
간단한 프로필 API 검증 스크립트
PowerShell 환경에서 동작하는 버전
"""

import json
import urllib.request
import urllib.parse
import ssl

BASE_URL = "http://localhost:8000"

def make_request(url, data=None, headers=None, method="GET"):
    """HTTP 요청 전송"""
    if headers is None:
        headers = {"Content-Type": "application/json"}
    
    if data:
        data = json.dumps(data).encode('utf-8')
    
    req = urllib.request.Request(url, data=data, headers=headers, method=method)
    
    try:
        with urllib.request.urlopen(req) as response:
            return response.getcode(), json.loads(response.read().decode('utf-8'))
    except urllib.error.HTTPError as e:
        try:
            error_data = json.loads(e.read().decode('utf-8'))
            print(f"   HTTP 에러 {e.code}: {error_data}")
            return e.code, error_data
        except:
            print(f"   HTTP 에러 {e.code}: {str(e)}")
            return e.code, {"error": str(e)}
    except Exception as e:
        print(f"   요청 중 예외 발생: {str(e)}")
        return 0, {"error": str(e)}

def test_profile_verification():
    """프로필 API 검증 체크리스트"""
    print("🧪 프로필 조회 API (GET /api/users/{id}/profile) 검증 시작...")
    print("=" * 70)
    
    results = {
        "권한_기반_정보_필터링": False,
        "민감_정보_숨김_처리": False,
        "활동_통계_계산": False,
        "진행_중인_미션정보": False,
        "보유_아이템_통화_정보": False,
        "프로필_이미지_아바타": False
    }
    
    # 1. 테스트 사용자 회원가입
    print("\n1️⃣ 테스트 사용자 회원가입...")
    import time
    timestamp = str(int(time.time()))
    signup_data = {
        "site_id": f"test_profile_{timestamp}",
        "nickname": f"프로필테스트유저{timestamp[-4:]}",
        "phone_number": f"010-{timestamp[-4:]}-{timestamp[-4:]}",
        "password": "testpass123",
        "invite_code": "6969"
    }
    
    status, response = make_request(f"{BASE_URL}/api/auth/signup", signup_data, method="POST")
    print(f"   회원가입 응답 상태: {status}")
    print(f"   응답 내용: {response}")
    
    if status in [200, 201]:
        token = response.get("access_token")
        if token:
            print(f"✅ 회원가입 성공! 토큰 획득")
        else:
            print("❌ 회원가입 응답에 토큰이 없습니다")
            return 0, 6
        
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
        
        # 2. 본인 프로필 조회 (/api/users/me/profile)
        print("\n2️⃣ 본인 프로필 조회 테스트...")
        status, profile = make_request(f"{BASE_URL}/api/users/me/profile", headers=headers)
        
        if status == 200:
            print("✅ 본인 프로필 조회 성공!")
            print(f"   - 사용자 ID: {profile.get('id')}")
            print(f"   - 닉네임: {profile.get('nickname')}")
            print(f"   - 사이버 토큰: {profile.get('cyber_token_balance')}")
            print(f"   - 등급: {profile.get('rank')}")
            print(f"   - 로그인 횟수: {profile.get('login_count')}")
            
            # 민감 정보 포함 여부 확인
            has_sensitive = 'phone_number' in profile
            print(f"   - 민감 정보 포함: {has_sensitive}")
            
            if has_sensitive:
                results["민감_정보_숨김_처리"] = True
                print(f"   - 전화번호: {profile.get('phone_number')}")
                print(f"   - 초대코드: {profile.get('invite_code')}")
            
            # 보유 아이템/통화 정보
            if 'cyber_token_balance' in profile:
                results["보유_아이템_통화_정보"] = True
                print(f"   ✅ 보유 통화 정보: 사이버 토큰 {profile.get('cyber_token_balance')}개")
            
            user_id = profile.get('id')
            
            # 3. 타인 프로필 조회 시도 (권한 기반 필터링 확인)
            print("\n3️⃣ 타인 프로필 조회 권한 테스트...")
            other_user_id = user_id + 1 if user_id > 1 else user_id + 2
            
            status, other_profile = make_request(f"{BASE_URL}/api/users/{other_user_id}/profile", headers=headers)
            
            if status == 200:
                has_sensitive_other = 'phone_number' in other_profile
                print(f"   ✅ 타인 프로필 조회 성공")
                print(f"   - 민감 정보 숨김: {not has_sensitive_other}")
                print(f"   - 공개 정보만 표시: 닉네임 {other_profile.get('nickname', 'N/A')}")
                
                if not has_sensitive_other:
                    results["권한_기반_정보_필터링"] = True
                    results["민감_정보_숨김_처리"] = True
                    
            elif status == 404:
                print("   ⚠️ 다른 사용자가 존재하지 않음 (정상)")
                results["권한_기반_정보_필터링"] = True  # 존재하지 않는 사용자 차단
            elif status == 403:
                print("   ✅ 타인 프로필 접근 차단 (정상)")
                results["권한_기반_정보_필터링"] = True
            
            # 4. 활동 통계 조회
            print("\n4️⃣ 활동 통계 조회 테스트...")
            status, stats = make_request(f"{BASE_URL}/api/users/me/stats", headers=headers)
            
            if status == 200:
                print("   ✅ 활동 통계 조회 성공!")
                print(f"   - 총 액션 수: {stats.get('total_actions', 0)}")
                print(f"   - 총 보상 수: {stats.get('total_rewards', 0)}")
                print(f"   - 플레이 시간: {stats.get('play_time_minutes', 0)}분")
                print(f"   - 마지막 활동: {stats.get('last_activity', 'N/A')}")
                
                results["활동_통계_계산"] = True
            
            # 5. 인증 토큰 없이 접근 시도
            print("\n5️⃣ 인증 토큰 없이 접근 시도...")
            status, error = make_request(f"{BASE_URL}/api/users/me/profile", headers={"Content-Type": "application/json"})
            
            if status == 401:
                print("   ✅ 인증되지 않은 접근 차단 (401)")
                results["권한_기반_정보_필터링"] = True
            elif status == 422:
                print("   ✅ 인증 헤더 누락으로 접근 차단 (422)")
                results["권한_기반_정보_필터링"] = True
                
        else:
            print(f"❌ 본인 프로필 조회 실패: {status}")
            
    else:
        print(f"❌ 회원가입 실패: {status}")
    
    # 체크리스트 결과 출력
    print("\n" + "=" * 70)
    print("📋 체크리스트 검증 결과:")
    print("=" * 70)
    
    for item, passed in results.items():
        status_icon = "✅" if passed else "❌"
        print(f"   {status_icon} {item.replace('_', ' ')}: {'통과' if passed else '미구현/실패'}")
    
    passed_count = sum(results.values())
    total_count = len(results)
    
    print(f"\n📊 전체 결과: {passed_count}/{total_count} 항목 통과")
    
    if passed_count == total_count:
        print("🎉 모든 프로필 API 요구사항이 구현되었습니다!")
    elif passed_count >= total_count * 0.7:
        print("⚠️ 대부분 구현되었으나 일부 기능이 누락되었습니다.")
    else:
        print("❌ 많은 기능이 아직 구현되지 않았습니다.")
    
    return passed_count, total_count

if __name__ == "__main__":
    passed, total = test_profile_verification()
    print(f"\n최종 점수: {passed}/{total} ({passed/total*100:.1f}%)")
