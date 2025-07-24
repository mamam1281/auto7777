#!/bin/bash

echo "🧹 피그마 컴포넌트 파일 정리 스크립트"
echo "======================================"

# 백업 디렉토리 생성
mkdir -p backup_old_components

echo "📂 기존 파일들 백업 중..."

# 기존 파일들 백업
cp cc-webapp/frontend/components/ui/basic/Button.tsx backup_old_components/ 2>/dev/null
cp cc-webapp/frontend/components/ui/data-display/Card.tsx backup_old_components/ 2>/dev/null

echo "🗑️ 중복/충돌 파일들 삭제 중..."

# 충돌하는 소문자 card 파일 삭제
rm -f cc-webapp/frontend/components/ui/card.tsx

# 잘못된 위치의 스토리 파일들 삭제 (올바른 위치로 이동 후)
# rm -f cc-webapp/frontend/components/ui/Button.stories.tsx
# rm -f cc-webapp/frontend/components/ui/Card.stories.tsx

# 중복된 Button 파일들 삭제
rm -f cc-webapp/frontend/components/ui/basic/Button_new.tsx

# 중복된 SlotMachine 파일들 삭제 (game 폴더에 이미 있음)
rm -f cc-webapp/frontend/components/ui/SlotMachine.module.css
rm -f cc-webapp/frontend/components/ui/SlotMachine.tsx

# 기타 중복 파일들
rm -f cc-webapp/frontend/components/ui/MotionCard.tsx

echo "📁 파일들을 올바른 위치로 이동 중..."

# Button 파일들을 올바른 위치로 이동
mv cc-webapp/frontend/components/ui/Button.tsx cc-webapp/frontend/components/ui/basic/Button.tsx
mv cc-webapp/frontend/components/ui/Button.stories.tsx cc-webapp/frontend/components/ui/basic/Button.stories.tsx

# Card 파일들을 올바른 위치로 이동 (덮어쓰기)
mv cc-webapp/frontend/components/ui/Card.tsx cc-webapp/frontend/components/ui/data-display/Card.tsx
mv cc-webapp/frontend/components/ui/Card.stories.tsx cc-webapp/frontend/components/ui/data-display/Card.stories.tsx

echo "✅ 파일 정리 완료!"
echo ""
echo "📋 정리된 구조:"
echo "- Button: cc-webapp/frontend/components/ui/basic/"
echo "- Card: cc-webapp/frontend/components/ui/data-display/" 
echo "- SlotMachine: cc-webapp/frontend/components/ui/game/slot-machine/"
echo ""
echo "📦 백업된 파일들: backup_old_components/"
