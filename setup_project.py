#!/usr/bin/env python3
"""
Casino-Club F2P 시스템 초기화 스크립트
- 데이터베이스 생성
- 기본 테스트 데이터 추가
- 고정 초대코드 생성
"""

import os
import sys
import subprocess
from pathlib import Path

# 현재 디렉토리를 스크립트 위치로 변경
os.chdir(os.path.dirname(os.path.abspath(__file__)))

def run_command(command):
    """명령어 실행 및 결과 출력"""
    print(f"실행: {command}")
    result = subprocess.run(command, shell=True, text=True)
    if result.returncode != 0:
        print(f"명령어 실행 중 오류 발생: {command}")
        sys.exit(1)
    return result

def main():
    """메인 실행 함수"""
    print("🚀 Casino-Club F2P 시스템 초기화를 시작합니다...")
    
    # 작업 디렉토리를 cc-webapp/backend로 변경
    backend_path = Path("cc-webapp/backend")
    os.chdir(backend_path)
    
    # 필요한 패키지 설치
    print("\n📦 필요한 패키지를 설치합니다...")
    run_command("pip install -r ../../requirements.txt")
    
    # 데이터베이스 생성
    print("\n🗄️ 데이터베이스를 초기화합니다...")
    run_command("python create_new_db.py")
    
    # 고정 초대코드 생성
    print("\n🎫 고정 초대코드를 생성합니다...")
    run_command("python create_fixed_invites.py")
    
    print("\n✅ 초기화가 완료되었습니다!")
    print("🎮 FastAPI 서버를 시작하려면 다음 명령을 실행하세요:")
    print("   cd cc-webapp/backend && uvicorn app.main:app --reload")
    print("\n🌟 즐거운 개발되세요!")
    os.chdir('c:\\Users\\bdbd\\Downloads\\auto202506-a-main\\auto202506-a-main')
    run_command("python setup_project.py")

if __name__ == "__main__":
    main()
