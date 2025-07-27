'use client';

import React, { useState, useCallback, useEffect } from 'react';
import { motion } from 'framer-motion';
import SlotMachineHeader1 from './SlotMachineHeader1';
import SlotMachineHeader2 from './SlotMachineHeader2';
import { SlotMachineMain } from './SlotMachineReels';
import BetControl from './BetControl';
import SlotMachineButton from './SlotMachineButton';
import WinParticleEffect from './WinParticleEffect';
import { gameAPI } from '../../../utils/api';

// SYMBOLS은 실제 게임에서 사용할 심볼입니다
const SYMBOLS = ['🍒', '🔔', '💎', '7️⃣', '⭐'];

// 스핀 결과 생성
const generateSpinResult = (): string[] => {
  return [
    SYMBOLS[Math.floor(Math.random() * SYMBOLS.length)],
    SYMBOLS[Math.floor(Math.random() * SYMBOLS.length)],
    SYMBOLS[Math.floor(Math.random() * SYMBOLS.length)]
  ];
};

// 승리 결과 타입 정의
interface WinResult {
  isWin: boolean;
  payout: number;
  multiplier: number;
  winningPositions: number[];
  type: string;
}

// 승리 조건 확인 및 배당 계산 (게임 앱 수준 배당!)
const checkWinCondition = (reels: string[], betAmount: number): WinResult => {
  const symbolMap: { [key: string]: number } = {};
  let allSame = true;
  
  // 카운팅 및 모두 같은지 확인
  for (let i = 0; i < reels.length; i++) {
    symbolMap[reels[i]] = (symbolMap[reels[i]] || 0) + 1;
    if (i > 0 && reels[i] !== reels[0]) {
      allSame = false;
    }
  }

  // 🎰 승리 조건 확인 (더 재미있는 배당!)
  if (allSame) {
    // 🌟 잭팟 - 3개의 별 (200배 배당!)
    if (reels[0] === '⭐') {
      return {
        isWin: true,
        payout: betAmount * 200,
        multiplier: 200,
        winningPositions: [0, 1, 2],
        type: "jackpot"
      };
    }
    
    // 💎 다이아몬드 3개 (50배 배당)
    if (reels[0] === '💎') {
      return {
        isWin: true,
        payout: betAmount * 50,
        multiplier: 50,
        winningPositions: [0, 1, 2],
        type: "diamond_win"
      };
    }
    
    // 7️⃣ 세븐 3개 (30배 배당)
    if (reels[0] === '7️⃣') {
      return {
        isWin: true,
        payout: betAmount * 30,
        multiplier: 30,
        winningPositions: [0, 1, 2],
        type: "seven_win"
      };
    }
    
    // 🔔 벨 3개 (15배 배당)
    if (reels[0] === '🔔') {
      return {
        isWin: true,
        payout: betAmount * 15,
        multiplier: 15,
        winningPositions: [0, 1, 2],
        type: "bell_win"
      };
    }
    
    // 🍒 체리 3개 (5배 배당)
    if (reels[0] === '🍒') {
      return {
        isWin: true,
        payout: betAmount * 5,
        multiplier: 5,
        winningPositions: [0, 1, 2],
        type: "cherry_win"
      };
    }
  }

  // 🎯 2개 매치 보너스 (작은 승리)
  for (const symbol of Object.keys(symbolMap)) {
    if (symbolMap[symbol] === 2) {
      const winningPositions: number[] = [];
      for (let i = 0; i < reels.length; i++) {
        if (reels[i] === symbol) {
          winningPositions.push(i);
        }
      }
      
      let multiplier = 1.5;
      if (symbol === '⭐') multiplier = 5;      // 별 2개
      else if (symbol === '💎') multiplier = 3; // 다이아 2개
      else if (symbol === '7️⃣') multiplier = 2.5; // 세븐 2개
      
      return {
        isWin: true,
        payout: Math.floor(betAmount * multiplier),
        multiplier,
        winningPositions,
        type: "double_match"
      };
    }
  }

  // 💸 패배
  // 💸 패배
  return {
    isWin: false,
    payout: 0,
    multiplier: 0,
    winningPositions: [],
    type: "loss"
  };
};

export type GameState = 'idle' | 'spinning' | 'result';

interface SlotMachineProps {
  className?: string;
}

export const SlotMachine = ({ className }: SlotMachineProps) => {
  const [gameState, setGameState] = useState<GameState>('idle');
  const [reels, setReels] = useState<string[]>(['💎', '🔔', '🍒']);
  const [betAmount, setBetAmount] = useState(10);
  const [winResult, setWinResult] = useState<WinResult | null>(null);
  const [isSpinning, setIsSpinning] = useState(false);
  const [jackpot, setJackpot] = useState(125780);
  const [balance, setBalance] = useState(1000);
  const [shake, setShake] = useState(false);
  const [error, setError] = useState<string | null>(null);
  
  // 근접 실패 및 심리적 효과 상태
  const [nearMiss, setNearMiss] = useState(false);
  const [displayBalance, setDisplayBalance] = useState(1000);
  const [balanceUpdateDelay, setBalanceUpdateDelay] = useState(false);

  // 잭팟 애니메이션 효과
  useEffect(() => {
    const interval = setInterval(() => {
      setJackpot(prev => prev + Math.floor(Math.random() * 10) + 1);
    }, 2500);
    return () => clearInterval(interval);
  }, []);

  // 잔액 표시 지연 효과 (손실 시)
  useEffect(() => {
    if (balanceUpdateDelay && !winResult?.isWin) {
      const timer = setTimeout(() => {
        setDisplayBalance(balance);
        setBalanceUpdateDelay(false);
      }, 1500); // 1.5초 지연
      return () => clearTimeout(timer);
    } else {
      setDisplayBalance(balance);
    }
  }, [balance, balanceUpdateDelay, winResult]);
  
  const handleSpin = useCallback(() => {
    if (balance < betAmount || isSpinning) {
      return;
    }

    setIsSpinning(true);
    setGameState('spinning');
    setWinResult(null);
    setShake(false);
    setNearMiss(false);
    setError(null);

    // 프론트엔드에서 스핀 결과 생성
    const spinResults = generateSpinResult();
    const winCheck = checkWinCondition(spinResults, betAmount);
    
    // 근접 실패 감지 (2개 매치하지만 3개 아닌 경우)
    const isNearMiss = !winCheck.isWin && (
      (spinResults[0] === spinResults[1] && spinResults[0] !== spinResults[2]) ||
      (spinResults[0] === spinResults[2] && spinResults[0] !== spinResults[1]) ||
      (spinResults[1] === spinResults[2] && spinResults[1] !== spinResults[0])
    );

    if (isNearMiss) {
      setNearMiss(true);
    }

    // 먼저 잔액 차감 (즉시 UI 반영)
    setBalance(prev => prev - betAmount);
    
    // 스핀 애니메이션
    setTimeout(() => {
      setReels(spinResults);
      setWinResult(winCheck);
      
      // 승리 시 잔액 증가
      if (winCheck.isWin) {
        setBalance(prev => prev + winCheck.payout);
        setDisplayBalance(prev => prev + winCheck.payout);
        if (winCheck.type === "jackpot") {
          setShake(true);
        }
      } else {
        // 패배 시 잔액 업데이트 지연 효과
        setBalanceUpdateDelay(true);
      }
      
      setIsSpinning(false);
      setGameState('result');
      
      // 백엔드에 결과만 전송 (코인 동기화용)
      const finalBalance = winCheck.isWin ? 
        balance - betAmount + winCheck.payout : 
        balance - betAmount;
        
      gameAPI.syncBalance(finalBalance)
        .catch(err => {
          console.warn('잔액 동기화 실패:', err);
          // 실패해도 게임 계속 진행 (프론트엔드 우선)
        });
      
      // 일정 시간 후 대기 상태로 되돌리기
      setTimeout(() => {
        setGameState('idle');
        setNearMiss(false);
      }, 3000);
    }, 2000);
  }, [betAmount, balance, isSpinning]);

  const canSpin = balance >= betAmount && !isSpinning;

  return (
    <motion.div
      className={`w-full mx-auto flex flex-col items-center ${className}`}
      animate={shake ? { x: [-5, 5, -5, 5, 0] } : {}}
      transition={{ duration: 0.5 }}
      style={{ pointerEvents: 'auto' }} // CSS 강제 활성화
    >
      {/* 에러 메시지 표시 */}
      {error && (
        <div className="w-full bg-red-600 text-white p-4 mb-2 rounded text-center">
          {error}
        </div>
      )}
      
      {/* Main - Slot Reels (압축된 여백) */}
      <div className="w-full" style={{ marginBottom: '8px' }}>
        <SlotMachineMain 
          reels={reels}
          isSpinning={isSpinning}
          winResult={winResult}
          className="w-full"
        />
      </div>

      {/* Control - Bet Controls (압축된 여백) */}
      <div className="w-full" style={{ marginBottom: '8px' }}>
        <BetControl
          betAmount={betAmount}
          setBetAmount={setBetAmount}
          maxBet={Math.min(balance, 100)}
          disabled={isSpinning}
          className="w-full"
        />
      </div>

      {/* Button - Spin Button (압축된 여백) */}
      <SlotMachineButton
        onSpin={handleSpin}
        canSpin={canSpin}
        isSpinning={isSpinning}
        gameState={gameState}
        winResult={winResult}
        balance={balance}
        betAmount={betAmount}
        className="w-full"
      />

      {/* Header 2 - Balance (압축된 여백) */}
      <div className="w-full" style={{ marginTop: '8px' }}>
        <SlotMachineHeader2 
          balance={displayBalance}
          className="w-full"
        />
      </div>

      {/* Win Particle Effect - 당첨 시 파티클 효과 */}
      {winResult?.isWin && (
        <WinParticleEffect 
          isWin={winResult.isWin}
          winType={winResult.type}
          onComplete={() => setWinResult(null)}
        />
      )}

      {/* Near Miss Effect - 근접 실패 시 심리적 효과 */}
      {nearMiss && (
        <motion.div
          initial={{ opacity: 0, scale: 0.8 }}
          animate={{ opacity: 1, scale: 1 }}
          exit={{ opacity: 0, scale: 0.8 }}
          className="absolute inset-0 flex items-center justify-center bg-black/50 pointer-events-none"
        >
          <motion.div
            animate={{ 
              y: [0, -10, 0],
              scale: [1, 1.1, 1]
            }}
            transition={{ 
              duration: 0.8,
              repeat: 2,
              ease: "easeInOut"
            }}
            className="bg-gradient-to-r from-yellow-400 to-orange-500 text-black px-6 py-3 rounded-lg font-bold text-lg shadow-lg"
          >
            💫 아쉬워! 거의 다 왔는데! 💫
          </motion.div>
        </motion.div>
      )}

      {/* Balance Update Delay Indicator - 잔액 업데이트 지연 표시 */}
      {balanceUpdateDelay && (
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          className="fixed top-4 right-4 bg-gradient-to-r from-[var(--color-accent-amber)]/90 to-[var(--color-accent-yellow)]/90 text-[var(--color-surface-primary)] px-3 py-1 rounded-lg text-sm font-medium shadow-md z-50"
        >
          💰 계산 중...
        </motion.div>
      )}
    </motion.div>
  );
};

export default SlotMachine;
