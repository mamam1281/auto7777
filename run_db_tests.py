#!/usr/bin/env python
"""
PostgreSQL 데이터베이스 무결성 테스트를 실행하는 스크립트
"""
import os
import sys
import subprocess
import argparse

# 현재 디렉토리를 설정
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
TEST_DIR = os.path.join(SCRIPT_DIR, "cc-webapp", "backend", "tests", "db_integrity")

def run_tests(test_type=None, verbose=False):
    """
    특정 유형의 테스트 또는 모든 테스트를 실행합니다.
    
    Args:
        test_type: 'referential', 'acid', 'data' 중 하나 또는 None (모든 테스트)
        verbose: 상세 출력 여부
    """
    # 테스트 명령 구성
    # venv_311 환경의 pytest 사용
    pytest_path = os.path.join(SCRIPT_DIR, "venv_311", "Scripts", "pytest.exe")
    if not os.path.exists(pytest_path):
        print(f"가상환경 pytest를 찾을 수 없습니다. 경로: {pytest_path}")
        pytest_path = "pytest"  # 시스템 설치된 pytest 사용
    
    cmd = [pytest_path]
    
    if verbose:
        cmd.append("-v")
    
    # 테스트 타입에 따라 파일 선택
    if test_type == "referential":
        cmd.append(os.path.join(TEST_DIR, "test_referential_integrity.py"))
        print("참조 무결성 테스트 실행 중...")
    elif test_type == "acid":
        cmd.append(os.path.join(TEST_DIR, "test_acid_transactions.py"))
        print("ACID 트랜잭션 테스트 실행 중...")
    elif test_type == "data":
        cmd.append(os.path.join(TEST_DIR, "test_data_integrity.py"))
        print("데이터 무결성 테스트 실행 중...")
    else:
        cmd.append(TEST_DIR)
        print("모든 데이터베이스 무결성 테스트 실행 중...")
    
    # 테스트 실행
    try:
        result = subprocess.run(cmd, check=True)
        print(f"테스트 완료. 종료 코드: {result.returncode}")
        return result.returncode
    except subprocess.CalledProcessError as e:
        print(f"테스트 실패. 종료 코드: {e.returncode}")
        return e.returncode

if __name__ == "__main__":
    # 명령줄 인수 파싱
    parser = argparse.ArgumentParser(description="PostgreSQL 데이터베이스 무결성 테스트 실행")
    parser.add_argument("--type", choices=["referential", "acid", "data"], 
                        help="실행할 테스트 유형 (referential=참조 무결성, acid=트랜잭션, data=데이터 무결성)")
    parser.add_argument("-v", "--verbose", action="store_true", help="상세 출력 활성화")
    
    args = parser.parse_args()
    
    # 테스트 실행
    sys.exit(run_tests(args.type, args.verbose))
