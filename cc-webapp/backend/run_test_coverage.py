"""
테스트 커버리지 실행 스크립트
"""

import os
import sys
import subprocess
from pathlib import Path


def run_tests_with_coverage():
    """테스트 실행 및 커버리지 보고서 생성"""
    # 프로젝트 루트 디렉토리 확인
    current_dir = Path(__file__).parent.resolve()
    
    # 테스트 실행 명령어
    cmd = [
        "pytest",
        "-v",  # 상세 출력
        "--cov=app",  # 'app' 디렉토리 커버리지 확인
        "--cov-report=term",  # 터미널에 보고서 출력
        "--cov-report=html:coverage_html",  # HTML 형식 보고서 생성
        "--cov-report=xml:coverage.xml",  # XML 형식 보고서 생성 (CI/CD 통합용)
        "tests/"  # 테스트 디렉토리
    ]
    
    print("테스트 실행 및 커버리지 분석 중...")
    try:
        # 테스트 실행
        result = subprocess.run(cmd, cwd=current_dir, check=False)
        
        # 종료 코드 출력
        if result.returncode == 0:
            print("\n✅ 모든 테스트가 성공적으로 완료되었습니다.")
            print(f"   커버리지 보고서는 {current_dir}/coverage_html/index.html 에서 확인할 수 있습니다.")
        else:
            print(f"\n❌ 테스트 실행 중 오류가 발생했습니다. 종료 코드: {result.returncode}")
        
        return result.returncode
    
    except Exception as e:
        print(f"테스트 실행 중 예외가 발생했습니다: {str(e)}")
        return 1


def main():
    """메인 함수"""
    sys.exit(run_tests_with_coverage())


if __name__ == "__main__":
    main()
