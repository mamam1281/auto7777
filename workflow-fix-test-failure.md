# 테스트 실패 자동 분석 및 수정 워크플로

1. read_file: c:\Users\task2\OneDrive\문서\GitHub\2025-2\auto202506-a\cc-webapp\backend\tests\unit\test_advanced_emotion.py
2. ask_followup_question: 최근 테스트 실패 로그를 분석해 원인과 관련 코드를 요약해줘.
3. read_file: c:\Users\task2\OneDrive\문서\GitHub\2025-2\auto202506-a\cc-webapp\backend\app\emotion_models.py
4. read_file: c:\Users\task2\OneDrive\문서\GitHub\2025-2\auto202506-a\cc-webapp\backend\app\utils\sentiment_analyzer.py
5. run_command: cd "cc-webapp/backend"; pytest --maxfail=3 --disable-warnings
6. ask_followup_question: 테스트 결과를 요약하고, 실패가 있으면 자동으로 고칠 수 있는 부분을 제안해줘.