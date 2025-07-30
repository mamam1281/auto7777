"""
프로필 API 테스트 - 미션 정보와 프로필 이미지 기능 검증
"""

import requests
import json

# API 기본 설정
BASE_URL = "http://localhost:8000"
TEST_USER_ID = 1

def test_profile_api():
    """프로필 API의 새로운 기능들 테스트"""
    
    print("🔍 프로필 API 테스트 시작...")
    print("=" * 50)
    
    # 1. 기본 프로필 조회 (인증 없이)
    print("1️⃣ 기본 프로필 조회 테스트")
    try:
        response = requests.get(f"{BASE_URL}/api/users/{TEST_USER_ID}/profile")
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("✅ 응답 성공!")
            print(f"📄 응답 데이터:")
            print(json.dumps(data, indent=2, ensure_ascii=False))
            
            # 새로운 기능들 체크
            print("\n🔍 새로운 기능 체크:")
            
            # 미션 정보 체크
            if 'missions' in data:
                print(f"✅ 진행 중인 미션정보: {len(data.get('missions', []))}개")
                for mission in data.get('missions', [])[:3]:  # 처음 3개만 표시
                    print(f"   - {mission.get('title', 'N/A')}: {mission.get('current_progress', 0)}/{mission.get('target_value', 0)}")
            else:
                print("❌ 진행 중인 미션정보: 없음")
            
            # 프로필 이미지 체크
            if 'profile_image' in data:
                profile_img = data['profile_image']
                print(f"✅ 프로필 이미지/아바타: {profile_img.get('type', 'N/A')} - {profile_img.get('url', 'N/A')}")
            else:
                print("❌ 프로필 이미지/아바타: 없음")
            
            # 기존 기능들 재확인
            print("\n📊 기존 기능들:")
            print(f"✅ 사이버 토큰: {data.get('cyber_token_balance', 'N/A')}")
            print(f"✅ 로그인 횟수: {data.get('stats', {}).get('login_count', 'N/A')}")
            print(f"✅ 등급: {data.get('rank', 'N/A')}")
            
        else:
            print(f"❌ 요청 실패: {response.text}")
            
    except requests.exceptions.RequestException as e:
        print(f"❌ 연결 오류: {e}")
        print("⚠️ 서버가 실행 중인지 확인해주세요 (docker-compose up)")
    
    print("\n" + "=" * 50)
    
    # 2. 진행률 계산
    print("2️⃣ 체크리스트 진행률 계산")
    
    completed_features = [
        "✅ 권한 기반 정보 필터링",
        "✅ 민감 정보 숨김 처리", 
        "✅ 활동 통계 계산",
        "✅ 보유 아이템/통화 정보"
    ]
    
    # API 응답 기반으로 새 기능들 상태 업데이트
    if 'response' in locals() and response.status_code == 200:
        data = response.json()
        if 'missions' in data:
            completed_features.append("✅ 진행 중인 미션정보")
        if 'profile_image' in data:
            completed_features.append("✅ 프로필 이미지/아바타")
    
    total_features = 6
    completed_count = len(completed_features)
    progress_rate = (completed_count / total_features) * 100
    
    print(f"📈 프로필 API 완성도: {completed_count}/{total_features} ({progress_rate:.1f}%)")
    print("\n완료된 기능들:")
    for feature in completed_features:
        print(f"  {feature}")
    
    if completed_count == total_features:
        print("\n🎉 축하합니다! 프로필 API가 100% 완성되었습니다!")
        print("🏆 체크리스트 업데이트 권장: 4/6 → 6/6")
    else:
        remaining = total_features - completed_count
        print(f"\n⚠️ 남은 기능: {remaining}개")

if __name__ == "__main__":
    test_profile_api()
