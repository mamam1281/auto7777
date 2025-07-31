#!/usr/bin/env python3

import requests
import json

# WLTN002 계정으로 로그인
login_data = {
    "site_id": "WLTN002",
    "password": "1234"
}

try:
    # 로그인
    login_response = requests.post("http://localhost:8000/api/auth/login", json=login_data)
    print(f"로그인 응답 상태: {login_response.status_code}")
    
    if login_response.status_code == 200:
        login_result = login_response.json()
        token = login_result.get("access_token")
        print(f"토큰 획득: {token[:20]}...")
        
        # /api/auth/me 호출해서 사용자 ID 확인
        headers = {"Authorization": f"Bearer {token}"}
        me_response = requests.get("http://localhost:8000/api/auth/me", headers=headers)
        print(f"\n/api/auth/me 응답 상태: {me_response.status_code}")
        
        if me_response.status_code == 200:
            me_data = me_response.json()
            print(f"사용자 데이터: {json.dumps(me_data, indent=2, ensure_ascii=False)}")
            
            user_id = me_data.get("id")
            print(f"\n사용자 ID: {user_id}")
            
            # 해당 사용자 ID로 프로필 API 테스트
            profile_response = requests.get(f"http://localhost:8000/api/users/{user_id}/profile", headers=headers)
            print(f"\n프로필 API 응답 상태: {profile_response.status_code}")
            print(f"프로필 API 응답: {profile_response.text}")
            
        else:
            print(f"/api/auth/me 오류: {me_response.text}")
    else:
        print(f"로그인 실패: {login_response.text}")

except Exception as e:
    print(f"API 테스트 오류: {e}")
