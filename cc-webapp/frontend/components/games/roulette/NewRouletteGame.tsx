'use client';

import React, { useState, useCallback } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { 
  ROULETTE_NUMBERS, 
  getNumberColor, 
  checkWin,
  getPayout,
  calculateWinnings,
  calculateWheelRotation,
  getPointerNumber,
  CHIP_VALUES,
  type Bet,
  type GameState
} from './SimpleRoulette';

export default function NewRouletteGame() {
  const [gameState, setGameState] = useState<GameState>({
    balance: 1000,
    isSpinning: false,
    winningNumber: null,
    bets: [],
    history: []
  });

  const [selectedChip, setSelectedChip] = useState(10);
  const [wheelRotation, setWheelRotation] = useState(0);
  const [resultModal, setResultModal] = useState({
    isOpen: false,
    winningNumber: null as number | null,
    winAmount: 0,
  });

  const closeModal = () => {
    setResultModal({ isOpen: false, winningNumber: null, winAmount: 0 });
  };

  // 베팅 추가
  const addBet = useCallback((type: 'number' | 'color', value: number | 'red' | 'black') => {
    if (gameState.isSpinning || gameState.balance < selectedChip) return;

    setGameState(prev => ({
      ...prev,
      balance: prev.balance - selectedChip,
      bets: [...prev.bets, { type, value, amount: selectedChip }]
    }));
  }, [gameState.isSpinning, gameState.balance, selectedChip]);

  // 베팅 초기화
  const clearBets = useCallback(() => {
    if (gameState.isSpinning) return;
    
    const totalBets = gameState.bets.reduce((sum, bet) => sum + bet.amount, 0);
    setGameState(prev => ({
      ...prev,
      balance: prev.balance + totalBets,
      bets: []
    }));
  }, [gameState.isSpinning, gameState.bets]);

  // 스핀 시작
  const spin = useCallback(async () => {
    if (gameState.isSpinning || gameState.bets.length === 0) return;

    console.log('🎲 스핀 시작!');
    setGameState(prev => ({ ...prev, isSpinning: true, winningNumber: null }));

    // 1. 결과 미리 생성
    let result = ROULETTE_NUMBERS[Math.floor(Math.random() * ROULETTE_NUMBERS.length)];
    console.log(`🎯 당첨 번호 생성: ${result}`);

    // 2. 최종 회전 각도 계산 (수정된 로직)
    const targetAngle = calculateWheelRotation(result); // 목표 각도 (0~359)
    const extraSpins = 360 * 5; // 최소 5바퀴 회전
    
    const currentAngle = wheelRotation % 360; // 현재 각도
    const rotationDiff = (targetAngle - currentAngle + 360) % 360; // 현재 위치에서 목표까지의 최단 회전(시계방향)
    
    const newRotation = wheelRotation + extraSpins + rotationDiff;

    console.log(`🔄 휠 회전 계산: 현재 ${Math.round(currentAngle)}deg -> 목표 ${targetAngle}deg. 최종 회전: ${newRotation}deg`);

    setWheelRotation(newRotation);

    // 3. 애니메이션 대기 (5초)
    await new Promise(resolve => setTimeout(resolve, 5000));

    // 4. 최종 포인터 위치 검증 및 보정 (안전 장치)
    const finalPointerNumber = getPointerNumber(newRotation);
    console.log(`[검증] 최종 각도: ${newRotation % 360}deg -> 포인터 번호: ${finalPointerNumber} | 생성된 당첨 번호: ${result}`);
    
    if (finalPointerNumber !== result) {
      console.warn(`🚨 포인터와 결과 불일치! 생성된 결과(${result})를 포인터 위치(${finalPointerNumber})로 보정합니다.`);
      result = finalPointerNumber; // UI와 일치하도록 결과를 보정
    }

    // 5. 승리 계산
    const winnings = calculateWinnings(gameState.bets, result);
    console.log(`💰 승리 금액: ${winnings}`);

    // 6. 상태 업데이트
    setGameState(prev => ({
      ...prev,
      isSpinning: false,
      winningNumber: result,
      balance: prev.balance + winnings,
      history: [result, ...prev.history.slice(0, 9)],
      bets: [] // 베팅 초기화
    }));

    // 7. 결과 모달 표시
    setResultModal({
      isOpen: true,
      winningNumber: result,
      winAmount: winnings,
    });
  }, [gameState.isSpinning, gameState.bets, gameState.balance, wheelRotation]);

  return (
    <div style={{
      width: '100%',
      maxWidth: '600px',
      margin: '0 auto',
      padding: '8px', // 패딩 축소
      background: 'linear-gradient(135deg, #1e293b 0%, #0f172a 100%)',
      borderRadius: '20px',
      color: 'white',
      fontFamily: 'Arial, sans-serif'
    }}>
      
      {/* 상단 정보 */}
      <div style={{
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'center',
        marginBottom: '8px', // 마진 축소
        padding: '8px', // 패딩 축소
        background: 'rgba(30, 41, 59, 0.8)',
        borderRadius: '12px',
        backdropFilter: 'blur(10px)'
      }}>
        <div style={{ fontSize: '18px', fontWeight: 'bold' }}>
          💰 잔액: ${gameState.balance}
        </div>
        <div style={{ fontSize: '16px' }}>
          🎯 베팅: ${gameState.bets.reduce((sum, bet) => sum + bet.amount, 0)}
        </div>
      </div>

      {/* 룰렛 휠 */}
      <div style={{
        display: 'flex',
        justifyContent: 'center',
        alignItems: 'center',
        marginBottom: '10px', // 마진 축소
        padding: '8px', // 패딩 축소
        background: 'rgba(30, 41, 59, 0.8)',
        borderRadius: '12px'
      }}>
        <div style={{ 
          position: 'relative', 
          width: '260px', 
          height: '260px', 
          // 팝업/모바일 환경에 맞게 크기 최적화
          margin: '0 auto'
        }}>
          
          {/* 휠 */}
          <motion.div
            style={{
              width: '100%',
              height: '100%',
              borderRadius: '50%',
              border: '6px solid #fbbf24',
              position: 'relative',
              background: `conic-gradient(
                from 0deg,
                #059669 0deg 30deg,
                #dc2626 30deg 60deg,
                #374151 60deg 90deg,
                #dc2626 90deg 120deg,
                #374151 120deg 150deg,
                #dc2626 150deg 180deg,
                #374151 180deg 210deg,
                #dc2626 210deg 240deg,
                #374151 240deg 270deg,
                #dc2626 270deg 300deg,
                #374151 300deg 330deg,
                #dc2626 330deg 360deg
              )`,
              boxShadow: '0 8px 30px rgba(0, 0, 0, 0.3)'
            }}
            animate={{ rotate: wheelRotation }}
            transition={{ 
              duration: 5,  // 애니메이션 시간 5초로 증가
              ease: [0.25, 1, 0.5, 1]  // 자연스러운 감속 효과 (Cubic Bezier)
            }}
          >
            {/* 숫자들 */}
            {ROULETTE_NUMBERS.map((num, index) => {
              const angle = index * 30;
              return (
                <div
                  key={num}
                  style={{
                    position: 'absolute',
                    left: '50%',
                    top: '50%',
                    transform: `rotate(${angle}deg) translateY(-110px) rotate(-${angle}deg)`,
                    marginLeft: '-15px',
                    marginTop: '-15px',
                    width: '30px',
                    height: '30px',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    color: 'white',
                    fontSize: '18px',
                    fontWeight: 'bold',
                    textShadow: '2px 2px 4px rgba(0, 0, 0, 0.8)',
                    backgroundColor: num === 0 ? '#059669' : (num % 2 === 1 ? '#dc2626' : '#374151'),
                    borderRadius: '50%',
                    border: '2px solid white'
                  }}
                >
                  {num}
                </div>
              );
            })}
          </motion.div>

          {/* 포인터 */}
          <div style={{
            position: 'absolute',
            top: '10px',
            left: '50%',
            transform: 'translateX(-50%)',
            zIndex: 10
          }}>
            <div style={{
              width: '0',
              height: '0',
              borderLeft: '12px solid transparent',
              borderRight: '12px solid transparent',
              borderTop: '30px solid #fbbf24',
              filter: 'drop-shadow(0 4px 8px rgba(0, 0, 0, 0.5))'
            }} />
          </div>
        </div>
      </div>

      {/* 칩 선택 */}
      <div style={{
        marginBottom: '10px', // 마진 축소
        padding: '8px', // 패딩 축소
        background: 'rgba(30, 41, 59, 0.8)',
        borderRadius: '12px'
      }}>
        <h3 style={{ margin: '0 0 8px 0', fontSize: '16px' }}>💎 칩 선택</h3>
        <div style={{ display: 'flex', gap: '8px' }}>
          {CHIP_VALUES.map((value, index) => (
            <button
              key={value}
              onClick={() => setSelectedChip(value)}
              disabled={gameState.isSpinning}
              style={{
                flex: 1,
                padding: '10px',
                fontSize: '14px',
                fontWeight: 'bold',
                color: 'white',
                background: index === 0 ? '#059669' : 
                          index === 1 ? '#0ea5e9' : 
                          index === 2 ? '#f59e0b' : '#dc2626',
                border: selectedChip === value ? '3px solid #fbbf24' : 'none',
                borderRadius: '8px',
                cursor: gameState.isSpinning ? 'not-allowed' : 'pointer',
                opacity: gameState.isSpinning ? 0.5 : 1,
                transition: 'all 0.2s ease'
              }}
            >
              ${value}
            </button>
          ))}
        </div>
      </div>

      {/* 베팅 영역 */}
      <div style={{
        marginBottom: '10px', // 마진 축소
        padding: '8px', // 패딩 축소
        background: 'rgba(30, 41, 59, 0.8)',
        borderRadius: '12px'
      }}>
        <h3 style={{ margin: '0 0 10px 0', fontSize: '16px' }}>🎯 베팅 영역</h3>
        
        {/* 숫자 베팅 */}
        <div style={{ marginBottom: '8px' }}>
          <h4 style={{ margin: '0 0 8px 0', fontSize: '14px', color: '#cbd5e1' }}>숫자 베팅 (12배)</h4>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(6, 1fr)', gap: '6px' }}>
            {ROULETTE_NUMBERS.map((num) => (
              <button
                key={num}
                onClick={() => addBet('number', num)}
                disabled={gameState.isSpinning || gameState.balance < selectedChip}
                style={{
                  padding: '8px',
                  fontSize: '14px',
                  fontWeight: 'bold',
                  color: 'white',
                  background: num === 0 ? '#059669' : (num % 2 === 1 ? '#dc2626' : '#374151'),
                  border: 'none',
                  borderRadius: '6px',
                  cursor: (gameState.isSpinning || gameState.balance < selectedChip) ? 'not-allowed' : 'pointer',
                  opacity: (gameState.isSpinning || gameState.balance < selectedChip) ? 0.5 : 1,
                  transition: 'all 0.2s ease'
                }}
              >
                {num}
              </button>
            ))}
          </div>
        </div>

        {/* 색상 베팅 */}
        <div>
          <h4 style={{ margin: '0 0 8px 0', fontSize: '14px', color: '#cbd5e1' }}>색상 베팅 (2배)</h4>
          <div style={{ display: 'flex', gap: '8px' }}>
            <button
              onClick={() => addBet('color', 'red')}
              disabled={gameState.isSpinning || gameState.balance < selectedChip}
              style={{
                flex: 1,
                padding: '12px',
                fontSize: '14px',
                fontWeight: 'bold',
                color: 'white',
                background: '#dc2626',
                border: 'none',
                borderRadius: '8px',
                cursor: (gameState.isSpinning || gameState.balance < selectedChip) ? 'not-allowed' : 'pointer',
                opacity: (gameState.isSpinning || gameState.balance < selectedChip) ? 0.5 : 1,
                transition: 'all 0.2s ease'
              }}
            >
              🔴 빨강
            </button>
            <button
              onClick={() => addBet('color', 'black')}
              disabled={gameState.isSpinning || gameState.balance < selectedChip}
              style={{
                flex: 1,
                padding: '12px',
                fontSize: '14px',
                fontWeight: 'bold',
                color: 'white',
                background: '#374151',
                border: 'none',
                borderRadius: '8px',
                cursor: (gameState.isSpinning || gameState.balance < selectedChip) ? 'not-allowed' : 'pointer',
                opacity: (gameState.isSpinning || gameState.balance < selectedChip) ? 0.5 : 1,
                transition: 'all 0.2s ease'
              }}
            >
              ⚫ 검정
            </button>
          </div>
        </div>
      </div>

      {/* 게임 컨트롤 */}
      <div style={{
        display: 'flex',
        gap: '8px',
        marginBottom: '10px' // 마진 축소
      }}>
        <button
          onClick={spin}
          disabled={gameState.isSpinning || gameState.bets.length === 0}
          style={{
            flex: 2,
            padding: '15px',
            fontSize: '18px',
            fontWeight: 'bold',
            color: 'white',
            background: 'linear-gradient(135deg, #10b981 0%, #059669 100%)',
            border: 'none',
            borderRadius: '10px',
            cursor: (gameState.isSpinning || gameState.bets.length === 0) ? 'not-allowed' : 'pointer',
            opacity: (gameState.isSpinning || gameState.bets.length === 0) ? 0.5 : 1,
            transition: 'all 0.2s ease',
            boxShadow: '0 4px 15px rgba(0, 0, 0, 0.2)'
          }}
        >
          🎡 스핀!
        </button>
        <button
          onClick={clearBets}
          disabled={gameState.isSpinning || gameState.bets.length === 0}
          style={{
            flex: 1,
            padding: '15px',
            fontSize: '16px',
            color: '#e5e7eb',
            background: '#4b5563',
            border: 'none',
            borderRadius: '10px',
            cursor: (gameState.isSpinning || gameState.bets.length === 0) ? 'not-allowed' : 'pointer',
            opacity: (gameState.isSpinning || gameState.bets.length === 0) ? 0.5 : 1,
            transition: 'all 0.2s ease'
          }}
        >
          초기화
        </button>
      </div>

      {/* 베팅 내역 */}
      {gameState.bets.length > 0 && (
        <div style={{
          padding: '8px', // 패딩 축소
          background: 'rgba(30, 41, 59, 0.8)',
          borderRadius: '12px',
          marginBottom: '8px' // 마진 추가
        }}>
          <h3 style={{ margin: '0 0 8px 0', fontSize: '16px' }}>베팅 내역</h3>
          <div style={{ 
            maxHeight: '100px', 
            overflowY: 'auto',
            paddingRight: '5px'
          }}>
            {gameState.bets.map((bet, index) => (
              <div key={index} style={{ 
                display: 'flex', 
                justifyContent: 'space-between', 
                alignItems: 'center',
                padding: '6px',
                borderRadius: '8px',
                background: 'rgba(255, 255, 255, 0.1)',
                marginBottom: '4px'
              }}>
                <div style={{ 
                  fontSize: '14px', 
                  fontWeight: 'bold',
                  color: bet.type === 'color' ? (bet.value === 'red' ? '#dc2626' : '#374151') : 'white'
                }}>
                  {bet.type === 'color' ? (bet.value === 'red' ? '🔴 빨강' : '⚫ 검정') : bet.value}
                </div>
                <div style={{ 
                  fontSize: '14px', 
                  fontWeight: 'bold',
                  color: 'white'
                }}>
                  ${bet.amount}
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* 결과 모달 */}
      <AnimatePresence>
        {resultModal.isOpen && (
          <div style={{
            position: 'fixed',
            top: 0,
            left: 0,
            right: 0,
            bottom: 0,
            backgroundColor: 'rgba(0, 0, 0, 0.7)',
            display: 'flex',
            alignItems: 'flex-end', // 하단 정렬
            justifyContent: 'center',
            zIndex: 1000
          }}>
            <motion.div
              initial={{ y: '100%' }}
              animate={{ y: 0 }}
              exit={{ y: '100%' }}
              transition={{ type: 'spring', stiffness: 300, damping: 30 }}
              style={{
                width: '100%',
                maxWidth: '400px',
                background: 'linear-gradient(180deg, #2d3748 0%, #1a202c 100%)',
                borderTopLeftRadius: '20px',
                borderTopRightRadius: '20px',
                padding: '12px', // 패딩 축소
                boxShadow: '0 -4px 20px rgba(0,0,0,0.3)',
                color: 'white'
              }}
            >
              <div style={{ textAlign: 'center', paddingBottom: '10px' }}>
                <h2 style={{ 
                  fontSize: '22px', // 폰트 크기 조정
                  fontWeight: 'bold', 
                  margin: '0 0 8px 0', // 마진 축소
                  color: resultModal.winAmount > 0 ? '#4ade80' : '#f87171' 
                }}>
                  {resultModal.winAmount > 0 ? '🎉 축하합니다! 🎉' : '아쉽네요... 😥'}
                </h2>
                <p style={{ fontSize: '16px', margin: '0 0 12px 0' }}>
                  당첨 번호: <span style={{ fontWeight: 'bold', fontSize: '18px' }}>{resultModal.winningNumber}</span>
                </p>
                <p style={{ fontSize: '18px', fontWeight: 'bold', margin: '0 0 16px 0' }}>
                  획득 금액: <span style={{ color: '#fbbf24' }}>${resultModal.winAmount}</span>
                </p>
                <button
                  onClick={closeModal}
                  style={{
                    width: '100%',
                    padding: '12px',
                    fontSize: '16px',
                    fontWeight: 'bold',
                    color: 'white',
                    background: 'linear-gradient(135deg, #10b981 0%, #059669 100%)',
                    border: 'none',
                    borderRadius: '10px',
                    cursor: 'pointer',
                    transition: 'background 0.2s ease'
                  }}
                >
                  확인
                </button>
              </div>
            </motion.div>
          </div>
        )}
      </AnimatePresence>

      {/* 최근 기록 */}
      <div style={{
        marginTop: '12px',
        padding: '8px',
        background: 'rgba(30, 41, 59, 0.8)',
        borderRadius: '12px',
        color: 'white',
        fontSize: '14px'
      }}>
        <h3 style={{ margin: '0 0 8px 0', fontSize: '16px' }}>📈 최근 기록</h3>
        <div style={{ 
          display: 'grid', 
          gridTemplateColumns: 'repeat(3, 1fr)', 
          gap: '8px',
          maxHeight: '150px',
          overflowY: 'auto'
        }}>
          {gameState.history.map((num, index) => (
            <div
              key={index}
              style={{
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                flexDirection: 'column',
                padding: '8px',
                borderRadius: '8px',
                background: 'rgba(255, 255, 255, 0.1)',
                color: 'white',
                fontWeight: 'bold',
                textShadow: '1px 1px 2px rgba(0, 0, 0, 0.7)',
                border: '2px solid',
                borderColor: num === 0 ? '#059669' : (num % 2 === 1 ? '#dc2626' : '#374151')
              }}
            >
              <div style={{ fontSize: '18px' }}>
                {num}
              </div>
              <div style={{ 
                fontSize: '12px', 
                marginTop: '4px',
                color: num === 0 ? '#059669' : (num % 2 === 1 ? '#dc2626' : '#374151')
              }}>
                {num === 0 ? '0' : (num % 2 === 1 ? '홀' : '짝')}
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
