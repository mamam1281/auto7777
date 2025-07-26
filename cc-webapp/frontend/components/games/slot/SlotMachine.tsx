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
  const [error, setError] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  
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
    setBalance(prev => prev - betAmount); // 즉시 UI에 반영
    setWinResult(null);
    setShake(false);
    setNearMiss(false);
    setError(null);
    setIsLoading(true);

    // 스핀 결과 생성 
    const newReels = generateSpinResult();
    const localResult = checkWinCondition(newReels, betAmount);
    
    // 프론트엔드 로직으로 게임 진행하면서도 API 호출 형식 유지
    gameAPI.mockSpinSlot(betAmount, newReels, localResult)
      .then(response => {
        const apiResult = response.data;
        
        // 근접 실패 체크 (2개 일치 시)
        const isNearMiss = !localResult.isWin && (
          (newReels[0] === newReels[1] && newReels[0] === '⭐') ||
          (newReels[1] === newReels[2] && newReels[1] === '⭐') ||
          (newReels[0] === newReels[1] && newReels[0] === '💎')
        );
        
        if (isNearMiss || apiResult.animation === 'near_miss') {
          setNearMiss(true);
        }
        
        setTimeout(() => {
          setReels(newReels);
          setWinResult(localResult);
          
          if (localResult.isWin) {
            setBalance(prev => prev + localResult.payout);
            setDisplayBalance(prev => prev + localResult.payout); // 승리 시 즉시 업데이트
            if (localResult.type === "jackpot") {
              setShake(true);
            }
          } else {
            setBalanceUpdateDelay(true); // 패배 시 지연 업데이트
            // 패배 시 잔액 업데이트 지연
            setTimeout(() => {
              setDisplayBalance(prev => prev - betAmount);
              setBalanceUpdateDelay(false);
            }, 1500);
          }
          
          setIsSpinning(false);
          setGameState('result');
          setIsLoading(false);
          
          // 일정 시간 후 대기 상태로 되돌리기
          setTimeout(() => {
            setGameState('idle');
            setNearMiss(false);
          }, 3000);
        }, 2000);
      })
      .catch(err => {
        console.error('슬롯 스핀 에러:', err);
        setError('슬롯 머신 스핀 중 오류가 발생했습니다.');
        setIsSpinning(false);
        setGameState('idle');
        setIsLoading(false);
        // 에러 시 차감된 잔액 복구
        setBalance(prev => prev + betAmount);
        setDisplayBalance(prev => prev + betAmount);
      });
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
        <div className="w-full bg-red-600 text-white p-2 mb-2 rounded text-center">
          {error}
        </div>
      )}
      
      {/* 로딩 인디케이터 */}
      {isLoading && (
        <div className="absolute top-2 right-2 bg-blue-500 text-white px-2 py-1 rounded-full text-sm z-10">
          로딩 중...
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
          className="absolute top-4 right-4 bg-red-500/80 text-white px-3 py-1 rounded text-sm"
        >
          💰 계산 중...
        </motion.div>
      )}
    </motion.div>
  );
};

export default SlotMachine;
