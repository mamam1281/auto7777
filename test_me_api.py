#!/usr/bin/env python3

import requests
import json

# 먼저 로그인해서 토큰 얻기
login_data = {
    "site_id": "admin",
    "password": "admin123"
}

try:
    # 로그인
    login_response = requests.post("http://localhost:8000/api/auth/login", json=login_data)
    print(f"로그인 응답 상태: {login_response.status_code}")
    
    if login_response.status_code == 200:
        login_result = login_response.json()
        token = login_result.get("access_token")
        print(f"토큰 획득: {token[:20]}...")
        
        # /api/auth/me 호출
        headers = {"Authorization": f"Bearer {token}"}
        me_response = requests.get("http://localhost:8000/api/auth/me", headers=headers)
        print(f"\n/api/auth/me 응답 상태: {me_response.status_code}")
        
        if me_response.status_code == 200:
            me_data = me_response.json()
            print(f"사용자 데이터: {json.dumps(me_data, indent=2, ensure_ascii=False)}")
        else:
            print(f"/api/auth/me 오류: {me_response.text}")
    else:
        print(f"로그인 실패: {login_response.text}")

except Exception as e:
    print(f"API 테스트 오류: {e}")
