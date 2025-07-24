# 가챠시스템 CSS 값 종합 정리

## 1. CSS 파일별 분류

### A. `gacha-popup.css` (현재 사용중)
**컬러 시스템 (CSS Variables)**
```css
:root {
  --gacha-cyan-main: #069487;
  --gacha-cyan-dark: #0a5c53;
  --gacha-cyan-light: #23aa8f;
  --gacha-cyan-gradient: linear-gradient(135deg, #069487 0%, #117c55 100%);
  --gacha-cyan-gradient-dark: linear-gradient(135deg, #0a5c53 0%, #117c55 100%);
  --gacha-cyan-border: #117c55;
}
```

**전체 배경 (.gacha-popup-colorful)**
```css
background: var(--gacha-cyan-gradient) !important;
min-height: 100vh !important;
width: 100vw !important;
overflow-x: hidden !important;
overflow-y: auto !important;
display: flex !important;
flex-direction: column !important;
align-items: center !important;
justify-content: flex-start !important;
padding-top: 64px !important;
padding-bottom: 64px !important;
```

**Glassmorphism 카드 효과**
```css
background: rgba(255,255,255,0.13) !important;
backdrop-filter: blur(16px) !important;
-webkit-backdrop-filter: blur(16px) !important;
border-radius: 18px !important;
border: 1.5px solid #fff3 !important;
box-shadow: 0 8px 32px rgba(0,0,0,0.12), 0 1.5px 0 rgba(255,255,255,0.08) inset !important;
transition: background 0.2s, box-shadow 0.2s;
```

**버튼 스타일 (가챠뽑기/충전)**
```css
display: flex !important;
align-items: center !important;
justify-content: center !important;
gap: 0.5rem !important;
font-weight: 700 !important;
font-size: 1.15rem !important;
border: none !important;
border-radius: 14px !important;
background: linear-gradient(90deg, #23aa8f 0%, #117c55 100%) !important;
color: #fff !important;
box-shadow: 0 4px 24px #117c5533 !important;
padding: 0.9rem 2.2rem !important;
min-height: 48px !important;
max-height: 56px !important;
transition: background 0.18s, box-shadow 0.18s !important;
```

**티켓 디스플레이**
```css
min-width: 110px !important;
max-width: 180px !important;
padding: 0.7rem 1.5rem !important;
font-size: 1.08rem !important;
margin-bottom: 0.5rem !important;
border-radius: 14px !important;
display: flex !important;
align-items: center !important;
justify-content: center !important;
gap: 0.5rem !important;
```

**가챠 박스 카드**
```css
width: 100% !important;
max-width: 420px !important;
min-width: 320px !important;
margin: 0 auto 1.5rem auto !important;
padding: 1.5rem 1.5rem 1.2rem 1.5rem !important;
border-radius: 18px !important;
```

**가챠 결과 모달**
```css
border-radius: 20px !important;
border: 2.5px solid var(--gacha-cyan-border) !important;
background: linear-gradient(135deg, #e0fdfa 0%, #a7f3d0 100%) !important;
box-shadow: 0 8px 32px #117c5522, 0 2px 16px #0002 !important;
color: #117c55 !important;
z-index: 9999 !important;
position: relative !important;
```

### B. `gacha-popup-backup.css` (백업/구버전)
**전체 배경 (.gacha-popup-colorful)**
```css
background: linear-gradient(135deg, 
  rgba(6, 134, 119, 0.95) 0%,    /* 청록 */
  rgba(17, 124, 85, 0.726) 100%   /* 민트 */
) !important;
height: 100vh !important;
min-height: 100vh !important;
max-height: 100vh !important;
overflow: hidden !important;
display: flex !important;
align-items: flex-start !important;
justify-content: center !important;
padding-top: 90px !important;
padding-bottom: 100px !important;
padding-left: 16px !important;
padding-right: 16px !important;
```

**가챠 박스 카드**
```css
background: linear-gradient(135deg, 
  rgba(164, 212, 208, 0.25) 0%,   /* 밝은 화이트 글래스 */
  rgba(35, 170, 143, 0.2) 100%   /* 라이트 민트 */
) !important;
border: 2px solid rgba(6, 63, 56, 0.6) !important;
box-shadow: 
  0 0 40px rgba(12, 5, 53, 0.4),
  0 0 80px rgba(52, 211, 153, 0.3),
  0 12px 40px rgba(0, 0, 0, 0.3),
  inset 0 2px 0 rgba(255, 255, 255, 0.144) !important;
padding: 8px 12px !important;
height: auto !important;
max-height: calc(100vh - 220px) !important;
overflow: hidden !important;
```

**티켓 카운터 글래스**
```css
background: rgba(255, 255, 255, 0.089) !important;
border: 1px solid rgba(20, 184, 166, 0.5) !important;
border-radius: 16px !important;
backdrop-filter: blur(15px) !important;
box-shadow: 
  0 8px 32px rgba(20, 184, 166, 0.3),
  0 4px 12px rgba(52, 211, 153, 0.2),
  inset 0 2px 0 rgba(255, 255, 255, 0.4) !important;
padding: 8px 16px !important;
min-width: 120px !important;
```

**가챠 컨테이너 글래스**
```css
background: rgba(255, 255, 255, 0.2) !important;
border: 1px solid rgba(43, 219, 154, 0.4) !important;
border-radius: 20px !important;
backdrop-filter: blur(15px) !important;
box-shadow: 
  0 8px 32px rgba(52, 211, 153, 0.25),
  0 4px 16px rgba(20, 184, 166, 0.2),
  inset 0 2px 0 rgba(255, 255, 255, 0.3) !important;
width: 200px !important;
padding: 16px !important;
min-height: 120px !important;
max-height: 150px !important;
```

**버튼 스타일**
```css
background: linear-gradient(135deg, #14b8a6 0%, #34d399 100%) !important;
border: 1px solid #5eead4 !important;
border-radius: 6px !important;
color: #ffffff !important;
font-weight: 500 !important;
box-shadow: 0 1px 3px rgba(0, 0, 0, 0.2) !important;
padding: 4px 8px !important;
min-height: 28px !important;
max-height: 32px !important;
font-size: 11px !important;
max-width: 100px !important;
```

## 2. 컴포넌트별 인라인 CSS

### A. GachaContainer.tsx
**박스 크기 (1.5배 확대)**
```typescript
const boxSizeClasses = "w-[264px] h-[264px] sm:w-[312px] sm:h-[312px] md:w-[360px] md:h-[360px]";
```

**동적 배경 그라데이션**
```typescript
background: state === 'reveal'
  ? `linear-gradient(145deg, ${tierConfig.gradientFrom}40, ${tierConfig.gradientTo}60)`
  : state === 'pulling'
    ? `linear-gradient(145deg, rgba(var(--color-accent-red-rgb),0.3), rgba(var(--color-accent-amber-rgb),0.4))`
    : `linear-gradient(145deg, rgba(var(--card-rgb),0.5), rgba(var(--background-rgb),0.3))`
```

**애니메이션 CSS**
```typescript
animate={{
  rotateY: state === 'pulling' ? [0, 360] : 0,
  scale: state === 'reveal' ? 1.1 : state === 'pulling' ? 1.02 : 1,
  y: state === 'pulling' ? [0, -15, 0] : 0,
}}
transition={{
  duration: state === 'pulling' ? 2.0 : 0.8,
  ease: state === 'pulling' ? 'easeInOut' : 'backOut',
  repeat: state === 'pulling' ? Infinity : 0,
}}
```

### B. PullButton.tsx
**버튼 CSS 클래스**
```typescript
className={cn(
  'gacha-play-btn flex items-center justify-center gap-1 px-2 py-1.25 rounded-xl font-bold text-base bg-gradient-to-br from-[#23aa8f] to-[#117c55] hover:from-[#117c55] hover:to-[#23aa8f] transition-colors text-white shadow-xl',
  isDisabled ? 'cursor-not-allowed opacity-60' : 'cursor-pointer'
)}
```

**인라인 스타일**
```typescript
style={{
  border: 'none',
  width: 'auto',
  minWidth: '0',
  maxWidth: '100%',
}}
```

### C. ChargeButton.tsx
**버튼 CSS 클래스**
```typescript
className={cn(
  "gacha-charge-btn flex items-center justify-center gap-1 w-full min-h-[32px] max-h-[32px] px-3 py-1 rounded-xl font-bold text-base bg-gradient-to-br from-[#23aa8f] to-[#117c55] hover:from-[#117c55] hover:to-[#23aa8f] transition-colors text-white shadow-lg mt-1",
  className
)}
```

### D. TicketCounter.tsx
**카운터 CSS 클래스**
```typescript
className={cn(
  "gacha-ticket-display flex items-center gap-2 px-4 py-2 rounded-xl min-h-[36px] max-h-[40px] bg-gradient-to-r from-[#e0fdfa] to-[#a7f3d0] border border-[#117c55] shadow",
  "font-semibold text-[16px] text-[#117c55] select-none"
)}
```

**텍스트 스타일**
```typescript
<span className="font-bold text-[20px] text-[#117c55] tabular-nums">{state.count}</span>
<span className="text-xs font-semibold text-[#117c55] opacity-80">티켓</span>
```

### E. ResultModal.tsx
**모달 인라인 스타일**
```typescript
style={{
  borderRadius: 20,
  border: `2.5px solid ${tierConfig.glowColor}`,
  background: `linear-gradient(135deg, #e0fdfa 0%, #a7f3d0 100%)`,
  boxShadow: `0 8px 32px #117c5522, 0 2px 16px #0002`,
  color: '#117c55',
  maxWidth: 420,
  width: '100%',
  position: 'relative',
  pointerEvents: 'auto',
  overflow: 'hidden',
  zIndex: 9999,
}}
```

**애니메이션 테두리**
```typescript
background: `conic-gradient(from var(--angle), transparent 20%, ${tierConfig.glowColor}, transparent 80%)`
```

**파티클 스타일**
```typescript
style={{
  position: 'absolute',
  borderRadius: '50%',
  left: '50%', top: '40%',
  width: Math.random() * 6 + 4, 
  height: Math.random() * 6 + 4,
  backgroundColor: c.color,
  boxShadow: `0 0 5px ${c.color}`,
}}
```

## 3. 색상 값 정리

### 주요 컬러 팔레트
- **청록 메인**: `#069487`
- **청록 어두운**: `#0a5c53`
- **청록 밝은**: `#23aa8f`
- **민트**: `#117c55`
- **테두리**: `#117c55`
- **배경 그라데이션**: `linear-gradient(135deg, #069487 0%, #117c55 100%)`
- **모달 배경**: `linear-gradient(135deg, #e0fdfa 0%, #a7f3d0 100%)`

### 반투명 값
- **글래스 배경**: `rgba(255,255,255,0.13)`
- **테두리**: `#fff3` (rgba(255,255,255,0.2))
- **그림자**: `rgba(0,0,0,0.12)`

### 백업 파일 색상
- **청록**: `rgba(6, 134, 119, 0.95)`
- **민트**: `rgba(17, 124, 85, 0.726)`
- **글래스 백그라운드**: `rgba(164, 212, 208, 0.25)`
- **글래스 민트**: `rgba(35, 170, 143, 0.2)`

## 4. 크기/간격 값

### 패딩/마진
- **전체 패딩**: `padding-top: 64px`, `padding-bottom: 64px`
- **카드 패딩**: `1.5rem 1.5rem 1.2rem 1.5rem`
- **버튼 패딩**: `0.9rem 2.2rem`
- **티켓 패딩**: `0.7rem 1.5rem`

### 크기
- **박스 최대폭**: `420px`
- **박스 최소폭**: `320px`
- **티켓 최대폭**: `180px`
- **티켓 최소폭**: `110px`
- **버튼 최소높이**: `48px`
- **버튼 최대높이**: `56px`

### 테두리 반경
- **카드**: `18px`
- **버튼**: `14px`
- **모달**: `20px`

## 5. 그림자/효과 값

### Box Shadow
- **카드 글래스**: `0 8px 32px rgba(0,0,0,0.12), 0 1.5px 0 rgba(255,255,255,0.08) inset`
- **버튼**: `0 4px 24px #117c5533`
- **모달**: `0 8px 32px #117c5522, 0 2px 16px #0002`

### Backdrop Filter
- **글래스 효과**: `blur(16px)`
- **웹킷 지원**: `-webkit-backdrop-filter: blur(16px)`

### Transition
- **기본**: `background 0.2s, box-shadow 0.2s`
- **버튼**: `background 0.18s, box-shadow 0.18s`

## 6. z-index 값
- **모달**: `z-index: 9999`
- **백드롭**: `z-index: 50`
- **콘텐츠**: `z-index: 10`

이 정리는 가챠시스템에서 실제 사용되고 있는 모든 CSS 값들을 포함합니다.
