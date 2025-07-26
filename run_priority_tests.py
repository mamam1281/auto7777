#!/usr/bin/env python3
"""
우선순위 테스트만 실행하는 스크립트
- 인증, 사용자 관리 등 기본 기능 테스트만 실행
"""
import os
import subprocess
import sys
from pathlib import Path

# 우선순위 테스트 파일 패턴
PRIORITY_TEST_PATTERNS = [
    "test_auth_simple.py",      # 단순 인증 테스트
    "test_auth.py",             # 기본 인증 테스트
    "test_user_segments.py",    # 사용자 세그먼트 테스트
    "test_slot_service.py",     # 슬롯 서비스 테스트
    "test_token_service.py"     # 토큰 서비스 테스트
]

def main():
    """메인 함수"""
    # 현재 디렉토리를 스크립트 위치로 변경
    script_dir = Path(os.path.dirname(os.path.abspath(__file__)))
    os.chdir(script_dir)
    
    # 백엔드 디렉토리 경로
    backend_dir = script_dir / "cc-webapp" / "backend"
    
    if not backend_dir.exists():
        print(f"❌ 백엔드 디렉토리를 찾을 수 없습니다: {backend_dir}")
        return
    
    # 테스트 디렉토리로 이동
    os.chdir(backend_dir)
    
    # 우선순위 테스트 패턴으로 pytest 명령 구성
    patterns = " or ".join([f"test_file={pattern}" for pattern in PRIORITY_TEST_PATTERNS])
    command = f"pytest tests/ -v -k \"{patterns}\""
    
    print(f"🧪 우선순위 테스트 실행: {command}")
    try:
        # 테스트 실행
        subprocess.run(command, shell=True, check=True)
        print("\n✅ 우선순위 테스트 실행 완료")
    except subprocess.CalledProcessError:
        print("\n❌ 일부 테스트가 실패했습니다")
    except Exception as e:
        print(f"\n❌ 테스트 실행 중 오류 발생: {e}")

if __name__ == "__main__":
    main()
