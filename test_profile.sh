#!/bin/bash
# 일반 사용자 프로필 API 테스트 스크립트

echo "🧪 일반 사용자 프로필 API 테스트 시작..."

BASE_URL="http://localhost:8000"

echo ""
echo "1️⃣ 먼저 회원가입 테스트..."

# 회원가입 데이터
SIGNUP_DATA='{
  "site_id": "testuser123",
  "nickname": "테스트유저123",
  "phone_number": "010-9999-8888",
  "password": "testpass123",
  "invite_code": "6969"
}'

echo "회원가입 요청 중..."
SIGNUP_RESPONSE=$(curl -s -X POST "$BASE_URL/api/auth/signup" \
  -H "Content-Type: application/json" \
  -d "$SIGNUP_DATA")

echo "회원가입 응답: $SIGNUP_RESPONSE"

# 토큰 추출 시도
TOKEN=$(echo "$SIGNUP_RESPONSE" | grep -o '"access_token":"[^"]*"' | cut -d'"' -f4)

if [ -n "$TOKEN" ]; then
    echo "✅ 회원가입 성공! 토큰 획득: ${TOKEN:0:20}..."
    
    echo ""
    echo "2️⃣ 내 프로필 조회 테스트..."
    
    PROFILE_RESPONSE=$(curl -s -X GET "$BASE_URL/api/users/me/profile" \
      -H "Authorization: Bearer $TOKEN")
    
    echo "내 프로필 응답: $PROFILE_RESPONSE"
    
    # 사용자 ID 추출
    USER_ID=$(echo "$PROFILE_RESPONSE" | grep -o '"id":[0-9]*' | cut -d':' -f2)
    
    if [ -n "$USER_ID" ]; then
        echo "✅ 프로필 조회 성공! 사용자 ID: $USER_ID"
        
        echo ""
        echo "3️⃣ 특정 사용자 프로필 조회 테스트..."
        
        USER_PROFILE_RESPONSE=$(curl -s -X GET "$BASE_URL/api/users/$USER_ID/profile" \
          -H "Authorization: Bearer $TOKEN")
        
        echo "특정 사용자 프로필 응답: $USER_PROFILE_RESPONSE"
        
        echo ""
        echo "4️⃣ 사용자 통계 조회 테스트..."
        
        STATS_RESPONSE=$(curl -s -X GET "$BASE_URL/api/users/$USER_ID/stats" \
          -H "Authorization: Bearer $TOKEN")
        
        echo "사용자 통계 응답: $STATS_RESPONSE"
        
        echo ""
        echo "🎉 일반 사용자 프로필 API 테스트 완료!"
        
    else
        echo "❌ 프로필 조회 실패"
    fi
    
else
    echo "회원가입 실패 또는 토큰 추출 실패"
    echo "기존 사용자로 로그인 시도..."
    
    # 기존 사용자 로그인 시도
    LOGIN_DATA='{
      "site_id": "user001",
      "password": "testpass123"
    }'
    
    LOGIN_RESPONSE=$(curl -s -X POST "$BASE_URL/api/auth/login" \
      -H "Content-Type: application/json" \
      -d "$LOGIN_DATA")
    
    echo "로그인 응답: $LOGIN_RESPONSE"
fi

echo ""
echo "✅ 테스트 완료!"
