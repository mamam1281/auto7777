# 🎮 게임 팝업 시스템

## 개요
사진에서 보신 "Globo Run"과 같은 독립적인 고정 크기 팝업 창으로 게임을 실행하는 시스템입니다.

## 구현된 기능

### 1. 팝업 유틸리티 (`utils/gamePopup.ts`)
- `openGamePopup(gameId)`: 게임 팝업 창 열기
- `closeGamePopup()`: 팝업 창 닫기
- `isPopupWindow()`: 현재 창이 팝업인지 확인

### 2. 게임별 팝업 설정
```javascript
const GAME_POPUP_CONFIGS = {
  slots: {
    width: 420,
    height: 680,
    title: '코스믹 포츈 - 슬롯 머신',
    url: '/games/slots/popup'
  },
  rps: {
    width: 400,
    height: 600,
    title: 'RPS Battle',
    url: '/games/rps/popup'
  },
  gacha: {
    width: 450,
    height: 700,
    title: 'Lucky Gacha',
    url: '/gacha/popup'
  },
  'slot-simple': {
    width: 400,
    height: 650,
    title: '슬롯 머신',
    url: '/slot/popup'
  }
};
```

### 3. 팝업 레이아웃 (`components/GamePopupLayout.tsx`)
- 팝업 창 전용 레이아웃 컴포넌트
- 자동 제목 설정
- ESC 키로 창 닫기
- 상단 닫기 버튼

### 4. 팝업 페이지들
- `/games/slots/popup/page.tsx` - 코스믹 포츈 슬롯
- `/gacha/popup/page.tsx` - 가챠 시스템  
- `/games/rps/popup/page.tsx` - RPS 배틀
- `/slot/popup/page.tsx` - 심플 슬롯

## 사용 방법

### 메인 페이지에서 게임 시작
1. 메인 페이지의 게임 카드 클릭
2. "게임 플레이" 버튼 클릭
3. "보너스 받기" 버튼 클릭 (가챠)

### 프로그래밍적으로 팝업 열기
```javascript
import { openGamePopup } from '../utils/gamePopup';

// 슬롯 게임 팝업 열기
openGamePopup('slots');

// 가챠 게임 팝업 열기
openGamePopup('gacha');

// RPS 게임 팝업 열기
openGamePopup('rps');
```

## 팝업 창 특징

### 🎯 고정 크기
- 각 게임마다 최적화된 고정 크기
- 브라우저 창 크기에 관계없이 일관된 경험

### 📱 텔레그램 미니앱 스타일
- 420px 내외의 모바일 친화적 너비
- 세로형 레이아웃 최적화

### ⚡ 독립적 실행
- 메인 앱과 완전히 분리된 창
- 게임 중에도 메인 앱 사용 가능

### 🎮 게임 최적화
- 헤더/네비게이션 없는 깔끔한 인터페이스
- 게임에만 집중할 수 있는 환경

## 팝업 차단 대응
브라우저에서 팝업이 차단된 경우:
1. 사용자에게 팝업 허용 안내
2. 브라우저 설정에서 사이트 팝업 허용 필요

## 향후 개선사항
- [ ] 팝업 위치 기억 기능
- [ ] 멀티 게임 팝업 관리
- [ ] 팝업 간 데이터 동기화
- [ ] 게임 상태 자동 저장/복원

## 테스트
1. 개발 서버 실행: `npm run dev`
2. http://localhost:3000 접속
3. 게임 카드 클릭하여 팝업 테스트

**완전히 독립적인 게임 창으로 실행됩니다! 🚀**
