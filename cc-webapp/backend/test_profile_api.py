#!/usr/bin/env python3
"""
프로필 API 완성도 테스트 스크립트
목표: 4/6 → 6/6 완성도 달성 확인

새로 추가된 기능:
- ❌ → ✅ 진행 중인 미션정보 (미션 시스템 구현)
- ❌ → ✅ 프로필 이미지/아바타 (이미지 업로드 시스템 구현)
"""

import requests
import json
import sys
from datetime import datetime

API_BASE = "http://localhost:8000"

def test_enhanced_profile_api():
    """개선된 프로필 API 테스트"""
    print("🔍 프로필 API 완성도 테스트 시작...")
    print("=" * 60)
    
    # 1. 로그인해서 JWT 토큰 받기 (기존 사용자 사용)
    login_data = {
        "site_id": "testuser123",  # 기존 사용자 사용
        "password": "password123"
    }
    
    try:
        login_response = requests.post(f"{API_BASE}/api/auth/login", json=login_data)
        print(f"🔍 로그인 응답 상태: {login_response.status_code}")
        if login_response.status_code == 200:
            login_result = login_response.json()
            print(f"🔍 로그인 응답 데이터: {login_result}")
        
        if login_response.status_code != 200:
            print("❌ 기존 사용자로 로그인 실패, 새 사용자 생성 시도...")
            
            # 현재 시간을 포함한 고유한 사용자 생성
            import time
            timestamp = str(int(time.time()))
            
            # 회원가입 시도
            signup_data = {
                "site_id": f"test_profile_{timestamp}",
                "nickname": f"프로필테스트유저{timestamp[-4:]}",
                "phone_number": f"010-{timestamp[-4:]}-{timestamp[-8:-4]}",
                "password": "password123",
                "invite_code": "6969"
            }
            signup_response = requests.post(f"{API_BASE}/api/auth/signup", json=signup_data)
            if signup_response.status_code != 200:
                print(f"❌ 회원가입 실패: {signup_response.text}")
                return False
            print("✅ 회원가입 성공")
            
            # 다시 로그인
            login_data["site_id"] = signup_data["site_id"]  # 새로 생성한 사용자 ID 사용
            login_response = requests.post(f"{API_BASE}/api/auth/login", json=login_data)
        
        if login_response.status_code != 200:
            print(f"❌ 로그인 실패: {login_response.text}")
            return False
            
        if login_response.status_code != 200:
            print(f"❌ 로그인 실패: {login_response.text}")
            return False
            
        login_result = login_response.json()
        token = login_result["access_token"]
        
        # user_id가 없으면 /api/auth/me를 통해 가져오기
        if "user_id" in login_result:
            user_id = login_result["user_id"]
        else:
            # 토큰으로 사용자 정보 조회
            headers = {"Authorization": f"Bearer {token}"}
            me_response = requests.get(f"{API_BASE}/api/auth/me", headers=headers)
            if me_response.status_code == 200:
                me_data = me_response.json()
                user_id = me_data["id"]
            else:
                print(f"❌ 사용자 정보 조회 실패: {me_response.text}")
                return False
        
        print(f"✅ 로그인 성공, 사용자 ID: {user_id}")
        
        headers = {"Authorization": f"Bearer {token}"}
        
    except Exception as e:
        print(f"❌ 인증 과정에서 오류: {e}")
        return False
    
    # 2. 개선된 프로필 API 호출
    try:
        profile_response = requests.get(f"{API_BASE}/api/users/{user_id}/profile", headers=headers)
        
        if profile_response.status_code != 200:
            print(f"❌ 프로필 조회 실패: {profile_response.text}")
            return False
            
        profile_data = profile_response.json()
        print("✅ 프로필 조회 성공")
        print(f"📊 응답 데이터: {json.dumps(profile_data, indent=2, ensure_ascii=False)}")
        
    except Exception as e:
        print(f"❌ 프로필 조회 중 오류: {e}")
        return False
    
    # 3. 완성도 체크리스트 검증
    print("\n" + "=" * 60)
    print("📋 프로필 API 완성도 체크리스트")
    print("=" * 60)
    
    checklist = {
        "권한 기반 정보 필터링": "basic_info" in profile_data,
        "민감 정보 숨김 처리": "phone_number" not in str(profile_data) or profile_data.get("phone_number", "").startswith("***"),
        "활동 통계 계산": "activity_stats" in profile_data,
        "진행 중인 미션정보": "mission_progress" in profile_data,
        "보유 아이템/통화 정보": "cyber_tokens" in profile_data or "currency" in profile_data,
        "프로필 이미지/아바타": "profile_image" in profile_data or "avatar" in profile_data
    }
    
    completed_count = 0
    total_count = len(checklist)
    
    for item, status in checklist.items():
        status_icon = "✅" if status else "❌"
        print(f"  {status_icon} {item}")
        if status:
            completed_count += 1
    
    print("\n" + "=" * 60)
    completion_rate = (completed_count / total_count) * 100
    print(f"🎯 완성도: {completed_count}/{total_count} ({completion_rate:.1f}%)")
    
    if completed_count == total_count:
        print("🎉 목표 달성! 6/6 완성도 100% 달성!")
        return True
    elif completed_count >= 4:
        print(f"⚠️ 부분 완성: {completed_count}/6, 추가 구현 필요")
        return False
    else:
        print("❌ 기본 기능 부족, 추가 개발 필요")
        return False

if __name__ == "__main__":
    print(f"🚀 테스트 시작 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"🐍 Python 환경: Docker 컨테이너 (Python 3.11)")
    print(f"🎯 목표: 프로필 API 4/6 → 6/6 완성도 달성 확인")
    print()
    
    success = test_enhanced_profile_api()
    exit_code = 0 if success else 1
    
    print(f"\n🏁 테스트 완료 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"📝 결과: {'성공' if success else '실패'}")
    
    sys.exit(exit_code)
