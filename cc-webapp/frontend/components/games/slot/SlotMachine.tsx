'use client';

import React, { useState, useCallback, useEffect } from 'react';
import { motion } from 'framer-motion';
import SlotMachineHeader1 from './SlotMachineHeader1';
import SlotMachineHeader2 from './SlotMachineHeader2';
import { SlotMachineMain } from './SlotMachineReels';
import BetControl from './BetControl';
import SlotMachineButton from './SlotMachineButton';
import WinParticleEffect from './WinParticleEffect';

// SYMBOLS은 실제 게임에서 사용할 심볼입니다
const SYMBOLS = ['🍒', '🔔', '💎', '7️⃣', '⭐'];

// 승리 결과 타입 정의
interface WinResult {
  isWin: boolean;
  payout: number;
  multiplier: number;
  winningPositions: number[];
  type: string;
}

// 스핀 결과 생성
const generateSpinResult = (): string[] => {
  return [
    SYMBOLS[Math.floor(Math.random() * SYMBOLS.length)],
    SYMBOLS[Math.floor(Math.random() * SYMBOLS.length)],
    SYMBOLS[Math.floor(Math.random() * SYMBOLS.length)]
  ];
};

// 승리 조건 확인 및 배당 계산
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

  // 승리 조건 확인
  if (allSame) {
    // 잭팟 - 3개의 별
    if (reels[0] === '⭐') {
      return {
        isWin: true,
        payout: betAmount * 100,
        multiplier: 100,
        winningPositions: [0, 1, 2],
        type: "jackpot"
      };
    }
    // 일반 3개 매치
    const multipliers: { [key: string]: number } = {
      '7️⃣': 50,
      '💎': 20,
      '🔔': 10,
      '🍒': 5
    };
    const multiplier = multipliers[reels[0]] || 5;
    return {
      isWin: true,
      payout: betAmount * multiplier,
      multiplier: multiplier,
      winningPositions: [0, 1, 2],
      type: "triple"
    };
  } 
  else {
    // 2개 매칭 확인
    for (const symbol in symbolMap) {
      if (symbolMap[symbol] === 2) {
        const winningPositions: number[] = [];
        for (let i = 0; i < reels.length; i++) {
          if (reels[i] === symbol) {
            winningPositions.push(i);
          }
        }
        return {
          isWin: true,
          payout: Math.floor(betAmount * 1.5),
          multiplier: 1.5,
          winningPositions,
          type: "double"
        };
      }
    }
  }

  // 패배
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
  const [isSoundEnabled, setIsSoundEnabled] = useState(true);
  const [shake, setShake] = useState(false);

  // 잭팟 애니메이션 효과
  useEffect(() => {
    const interval = setInterval(() => {
      setJackpot(prev => prev + Math.floor(Math.random() * 10) + 1);
    }, 2500);
    return () => clearInterval(interval);
  }, []);
  
  const handleSpin = useCallback(() => {
    if (balance < betAmount || isSpinning) {
      return;
    }

    setIsSpinning(true);
    setGameState('spinning');
    setBalance(prev => prev - betAmount);
    setWinResult(null);
    setShake(false);

    // 스핀 결과 생성 및 적용
    setTimeout(() => {
      const newReels = generateSpinResult();
      const result = checkWinCondition(newReels, betAmount);
      
      setReels(newReels);
      setWinResult(result);
      
      if (result.isWin) {
        setBalance(prev => prev + result.payout);
        if (result.type === "jackpot") {
          setShake(true);
        }
      }
      
      setIsSpinning(false);
      setGameState('result');
      
      // 일정 시간 후 대기 상태로 되돌리기
      setTimeout(() => {
        setGameState('idle');
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

      {/* Header 2 - Balance & Sound (압축된 여백) */}
      <div className="w-full" style={{ marginTop: '8px' }}>
        <SlotMachineHeader2 
          balance={balance}
          isSoundEnabled={isSoundEnabled}
          setIsSoundEnabled={setIsSoundEnabled}
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
    </motion.div>
  );
};

export default SlotMachine;
