'use client';

import React, { useState, useEffect, useCallback } from 'react';
import { motion, AnimatePresence } from 'framer-motion';

interface Prize {
  id: string;
  name: string;
  value: number;
  color: string;
  probability: number;
  icon?: string;
}

interface PrizeRouletteSpinResult {
  success: boolean;
  prize?: Prize;
  message: string;
  spins_left: number;
  cooldown_expires?: string;
  is_near_miss?: boolean;
  animation_type?: 'normal' | 'jackpot' | 'near_miss';
}

interface PrizeRouletteProps {
  className?: string;
}

const PRIZES: Prize[] = [
  { id: "coins_100", name: "코인 100개", value: 100, color: "#FFD700", probability: 0.35, icon: "🪙" },
  { id: "coins_500", name: "코인 500개", value: 500, color: "#FFA500", probability: 0.20, icon: "💰" },
  { id: "coins_1000", name: "코인 1000개", value: 1000, color: "#FF6B35", probability: 0.15, icon: "💎" },
  { id: "gems_10", name: "젬 10개", value: 10, color: "#9D4EDD", probability: 0.18, icon: "💜" },
  { id: "gems_50", name: "젬 50개", value: 50, color: "#7209B7", probability: 0.10, icon: "🔮" },
  { id: "jackpot", name: "잭팟! 젬 200개", value: 200, color: "#FF0080", probability: 0.015, icon: "🎰" },
  { id: "bonus", name: "보너스 스핀", value: 1, color: "#00FF88", probability: 0.005, icon: "🎁" }
];

export default function PrizeRoulette({ className = '' }: PrizeRouletteProps) {
  const [isSpinning, setIsSpinning] = useState(false);
  const [spinsLeft, setSpinsLeft] = useState(3);
  const [lastResult, setLastResult] = useState<PrizeRouletteSpinResult | null>(null);
  const [rotation, setRotation] = useState(0);
  const [showResultModal, setShowResultModal] = useState(false);
  const [soundEnabled, setSoundEnabled] = useState(true);
  const [showProbabilities, setShowProbabilities] = useState(false);
  const [spinHistory, setSpinHistory] = useState<Prize[]>([]);

  // 사용자 정보 가져오기
  const fetchRouletteInfo = useCallback(async () => {
    try {
      const response = await fetch('/api/games/roulette/info?user_id=temp_user');
      if (response.ok) {
        const data = await response.json();
        setSpinsLeft(data.spins_left || 3);
      } else {
        throw new Error('API 호출 실패');
      }
    } catch (error) {
      console.error('Failed to fetch roulette info:', error);
      
      // API 실패시 로컬 스토리지 fallback
      const savedSpins = localStorage.getItem('roulette_spins_left');
      const lastSpin = localStorage.getItem('roulette_last_spin');
      const today = new Date().toDateString();
      
      if (!lastSpin || lastSpin !== today) {
        setSpinsLeft(3);
        localStorage.setItem('roulette_spins_left', '3');
        localStorage.setItem('roulette_last_spin', today);
      } else {
        setSpinsLeft(parseInt(savedSpins || '3'));
      }
    }
  }, []);

  // 음향 효과 재생
  const playSound = useCallback((type: 'spin' | 'win' | 'jackpot' | 'lose') => {
    if (!soundEnabled) return;
    
    try {
      const audio = new Audio(`/sounds/roulette_${type}.mp3`);
      audio.volume = 0.5;
      audio.play().catch(e => console.log('Sound play failed:', e));
    } catch (error) {
      console.log('Sound not available:', error);
    }
  }, [soundEnabled]);

  // 룰렛 스핀 실행
  const spinRoulette = useCallback(async () => {
    if (isSpinning || spinsLeft <= 0) return;

    setIsSpinning(true);
    playSound('spin');
    
    try {
      // 스핀 애니메이션 시작
      const newRotation = rotation + 1800 + Math.random() * 360;
      setRotation(newRotation);

      // 백엔드 API 호출
      const response = await fetch('/api/games/roulette/spin', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          user_id: 'temp_user',
        }),
      });

      let result: PrizeRouletteSpinResult;
      
      if (response.ok) {
        // API 성공
        result = await response.json();
      } else {
        // API 실패시 클라이언트 사이드 fallback
        await new Promise(resolve => setTimeout(resolve, 3000));
        
        const random = Math.random();
        let cumulativeProbability = 0;
        let selectedPrize = PRIZES[0];
        
        for (const prize of PRIZES) {
          cumulativeProbability += prize.probability;
          if (random <= cumulativeProbability) {
            selectedPrize = prize;
            break;
          }
        }

        result = {
          success: true,
          prize: selectedPrize,
          message: `축하합니다! ${selectedPrize.name}을(를) 획득했습니다!`,
          spins_left: spinsLeft - 1,
          animation_type: selectedPrize.id === 'jackpot' ? 'jackpot' : 'normal'
        };
      }

      // 애니메이션 대기
      await new Promise(resolve => setTimeout(resolve, 3000));

      // 상태 업데이트
      setLastResult(result);
      setSpinsLeft(result.spins_left);
      setShowResultModal(true);
      
      // 히스토리 업데이트
      if (result.prize) {
        setSpinHistory(prev => [result.prize!, ...prev.slice(0, 4)]);
      }
      
      // 로컬 스토리지 업데이트 (백업용)
      localStorage.setItem('roulette_spins_left', result.spins_left.toString());
      
      // 음향 효과
      if (result.prize?.id === 'jackpot') {
        playSound('jackpot');
      } else if (result.prize && result.prize.value > 500) {
        playSound('win');
      } else {
        playSound('win');
      }
      
    } catch (error) {
      console.error('Spin failed:', error);
      setLastResult({
        success: false,
        message: '스핀 중 오류가 발생했습니다. 다시 시도해주세요.',
        spins_left: spinsLeft
      });
    } finally {
      setIsSpinning(false);
    }
  }, [isSpinning, spinsLeft, rotation, playSound]);

  // 결과 모달 닫기
  const closeResultModal = useCallback(() => {
    setShowResultModal(false);
  }, []);

  useEffect(() => {
    fetchRouletteInfo();
  }, [fetchRouletteInfo]);

  return (
    <div className="w-full bg-gradient-to-br from-[var(--color-primary-dark-navy)] via-[var(--color-primary-charcoal)] 
    to-[var(--color-primary-dark-navy)] min-h-screen flex flex-col items-center">
      
      {/* 헤더 - 다른 게임들과 동일한 패턴 */}
      <motion.header
        className="z-20 py-3 sm:py-4 px-4 sm:px-6 w-full bg-gradient-to-br from-[var(--color-primary-dark-navy)]/80 via-[var(--color-primary-charcoal)]/80 to-[var(--color-primary-dark-navy)]/80 backdrop-blur-md border-b border-[var(--border)]/20"
        initial={{ y: -100, opacity: 0 }}
        animate={{ y: 0, opacity: 1 }}
        transition={{ duration: 0.6, ease: "easeOut" }}
      >
        <div className="max-w-6xl mx-auto flex flex-col items-center justify-center gap-2">
          <motion.h1
            className="text-4xl sm:text-6xl font-bold bg-gradient-to-r from-[var(--color-accent-amber)] 
            via-[var(--color-accent-yellow)] to-[var(--color-accent-amber)] bg-clip-text text-transparent text-center tracking-wide"
            whileHover={{ scale: 1.02 }}
          >
            🎰 프라이즈 룰렛
          </motion.h1>
          <motion.p 
            className="text-[var(--text-secondary)] text-center text-sm sm:text-base"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 0.3 }}
          >
            매일 3번까지 무료로 다양한 보상을 획득하세요!
          </motion.p>
        </div>
      </motion.header>

      {/* 메인 게임 영역 */}
      <div className="flex-1 w-full flex flex-col items-center justify-center p-4">
        <motion.div
          className="glass-card p-6 max-w-md w-full text-center"
          initial={{ opacity: 0, scale: 0.95 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ duration: 0.5 }}
        >
          {/* 스핀 정보 */}
          <div className="mb-6">
            <div className="inline-flex items-center gap-2 bg-gradient-to-r from-[var(--color-primary-charcoal)]/80 to-[var(--color-primary-dark-navy)]/80 
            px-4 py-2 rounded-full border border-[var(--border)]/30">
              <span className="text-[var(--color-accent-amber)]">🎲</span>
              <span className="text-[var(--text-primary)] font-semibold">남은 스핀: {spinsLeft}/3</span>
            </div>
          </div>

        {/* 룰렛 휠 - 더 크고 선명하게 */}
        <div className="flex justify-center items-center mb-8">
        <div className="relative w-[340px] h-[340px] sm:w-[420px] sm:h-[420px]">
          {/* 외부 링과 그림자 */}
          <div className="absolute inset-0 rounded-full bg-gradient-to-br from-[var(--color-accent-amber)] via-yellow-400 to-[var(--color-accent-red)] p-2 shadow-2xl">
            <div className="w-full h-full rounded-full bg-gradient-to-br from-gray-900 via-gray-800 to-black overflow-hidden relative shadow-inner">
              
              {/* SVG 기반 룰렛 휠 */}
              <motion.div
                className="w-full h-full relative"
                animate={{ rotate: rotation }}
                transition={{ 
                  duration: isSpinning ? 3 : 0, 
                  ease: isSpinning ? "easeOut" : "linear"
                }}
              >
                <svg width="100%" height="100%" viewBox="0 0 200 200" className="absolute inset-0">
                  {PRIZES.map((prize, index) => {
                    const startAngle = (360 / PRIZES.length) * index - 90; // -90도로 12시 방향 시작
                    const endAngle = (360 / PRIZES.length) * (index + 1) - 90;
                    const centerX = 100;
                    const centerY = 100;
                    const radius = 90;
                    
                    // 호 경로 계산
                    const startAngleRad = (startAngle * Math.PI) / 180;
                    const endAngleRad = (endAngle * Math.PI) / 180;
                    
                    const x1 = centerX + radius * Math.cos(startAngleRad);
                    const y1 = centerY + radius * Math.sin(startAngleRad);
                    const x2 = centerX + radius * Math.cos(endAngleRad);
                    const y2 = centerY + radius * Math.sin(endAngleRad);
                    
                    const largeArcFlag = endAngle - startAngle <= 180 ? "0" : "1";
                    
                    const pathData = [
                      `M ${centerX} ${centerY}`,
                      `L ${x1} ${y1}`,
                      `A ${radius} ${radius} 0 ${largeArcFlag} 1 ${x2} ${y2}`,
                      `Z`
                    ].join(' ');
                    
                    // 텍스트 위치 계산
                    const textAngle = (startAngle + endAngle) / 2;
                    const textAngleRad = (textAngle * Math.PI) / 180;
                    const textRadius = radius * 0.7;
                    const textX = centerX + textRadius * Math.cos(textAngleRad);
                    const textY = centerY + textRadius * Math.sin(textAngleRad);
                    
                    return (
                      <g key={prize.id}>
                        {/* 세그먼트 배경 */}
                        <path
                          d={pathData}
                          fill={prize.color}
                          stroke="rgba(255,255,255,0.2)"
                          strokeWidth="0.5"
                          className={prize.id === 'jackpot' ? 'animate-pulse' : ''}
                          style={{
                            filter: prize.id === 'jackpot' ? 'drop-shadow(0 0 10px rgba(255, 0, 128, 0.5))' : 'none'
                          }}
                        />
                        
                        {/* 아이콘 - 더 크고 선명하게 */}
                        <text
                          x={textX}
                          y={textY - 8}
                          textAnchor="middle"
                          fontSize="18"
                          fill="white"
                          style={{ textShadow: '2px 2px 4px rgba(0,0,0,0.9)' }}
                        >
                          {prize.icon}
                        </text>
                        
                        {/* 텍스트 - 더 크고 선명하게 */}
                        <text
                          x={textX}
                          y={textY + 10}
                          textAnchor="middle"
                          fontSize="9"
                          fill="white"
                          fontWeight="bold"
                          style={{ textShadow: '2px 2px 4px rgba(0,0,0,0.9)' }}
                        >
                          {prize.name.length > 6 ? prize.name.substring(0, 5) + '...' : prize.name}
                        </text>
                      </g>
                    );
                  })}
                </svg>
              </motion.div>
              
              {/* 중앙 원 - 더 크게 */}
              <div className="absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2 w-20 h-20 bg-gradient-to-br from-[var(--color-accent-amber)] via-yellow-400 to-[var(--color-accent-red)] rounded-full border-4 border-white shadow-2xl flex items-center justify-center z-20">
                <span className="text-3xl font-bold text-black drop-shadow">🎯</span>
              </div>
            </div>
          </div>
          
          {/* 포인터 - 더 크게 */}
          <div className="absolute -top-6 left-1/2 transform -translate-x-1/2 z-30">
            <div className="relative">
              <div className="w-0 h-0 border-l-[22px] border-r-[22px] border-t-[35px] border-l-transparent border-r-transparent border-t-[var(--color-accent-amber)] filter drop-shadow-lg"></div>
              <div className="absolute top-0 left-1/2 transform -translate-x-1/2 w-0 h-0 border-l-[18px] border-r-[18px] border-t-[28px] border-l-transparent border-r-transparent border-t-white"></div>
            </div>
          </div>
          
          {/* 스핀 시 글로우 효과 */}
          {isSpinning && (
            <div className="absolute inset-0 rounded-full animate-pulse pointer-events-none">
              <div className="w-full h-full rounded-full bg-gradient-to-r from-[var(--color-accent-amber)]/30 via-yellow-400/30 to-[var(--color-accent-red)]/30 blur-md"></div>
            </div>
          )}
          
          {/* 외부 스파크 효과 */}
          {isSpinning && (
            <div className="absolute inset-0 pointer-events-none">
              {[...Array(8)].map((_, i) => (
                <motion.div
                  key={i}
                  className="absolute w-2 h-2 bg-[var(--color-accent-amber)] rounded-full"
                  style={{
                    top: '50%',
                    left: '50%',
                    transformOrigin: '0 0',
                  }}
                  animate={{
                    rotate: [0, 360],
                    scale: [0, 1, 0],
                    x: [0, Math.cos(i * 45 * Math.PI / 180) * 180],
                    y: [0, Math.sin(i * 45 * Math.PI / 180) * 180],
                  }}
                  transition={{
                    duration: 2,
                    repeat: Infinity,
                    delay: i * 0.1,
                  }}
                />
              ))}
            </div>
          )}
        </div>
        </div>

        {/* 스핀 버튼 */}
        <div className="text-center mb-6">
        <motion.button
          onClick={spinRoulette}
          disabled={isSpinning || spinsLeft <= 0}
          className={`relative px-8 py-4 rounded-xl font-bold text-white text-lg transition-all duration-300 disabled:opacity-50 disabled:cursor-not-allowed min-w-[180px] ${
            spinsLeft > 0 && !isSpinning
              ? 'bg-gradient-to-r from-purple-600 via-pink-600 to-red-600 hover:from-purple-700 hover:via-pink-700 hover:to-red-700 shadow-lg hover:shadow-xl transform hover:scale-105 active:scale-95'
              : 'bg-gradient-to-r from-gray-600 to-gray-700'
          }`}
          whileHover={spinsLeft > 0 && !isSpinning ? { scale: 1.05 } : {}}
          whileTap={spinsLeft > 0 && !isSpinning ? { scale: 0.95 } : {}}
        >
          {isSpinning ? (
            <div className="flex items-center justify-center gap-3">
              <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white"></div>
              <span>스핀 중...</span>
            </div>
          ) : spinsLeft > 0 ? (
            <div className="flex items-center justify-center gap-2">
              <span>🎲</span>
              <span>스핀하기</span>
            </div>
          ) : (
            <div className="flex items-center justify-center gap-2">
              <span>⏰</span>
              <span>스핀 소진</span>
            </div>
          )}
          
          {/* 버튼 글로우 효과 */}
          {spinsLeft > 0 && !isSpinning && (
            <div className="absolute inset-0 rounded-xl bg-gradient-to-r from-purple-600/50 via-pink-600/50 to-red-600/50 blur-md -z-10"></div>
          )}
        </motion.button>
        
        {spinsLeft === 0 && (
          <motion.p 
            className="text-[var(--text-secondary)] text-sm mt-3 flex items-center justify-center gap-2"
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.3 }}
          >
            <span>🌅</span>
            <span>내일 다시 도전하세요!</span>
          </motion.p>
        )}
        </div>

        {/* 결과 표시 */}
        {lastResult && !showResultModal && (
        <motion.div 
          className="max-w-md mx-auto bg-gradient-to-r from-[var(--color-primary-charcoal)]/90 to-[var(--color-primary-dark-navy)]/90 backdrop-blur-sm p-6 rounded-2xl border border-[var(--border)]/30 shadow-2xl"
          initial={{ opacity: 0, y: 20, scale: 0.9 }}
          animate={{ opacity: 1, y: 0, scale: 1 }}
          transition={{ duration: 0.5, ease: "easeOut" }}
        >
          <div className="text-center">
            <p className={`font-bold text-lg mb-3 ${lastResult.success ? 'text-[var(--color-accent-amber)]' : 'text-red-400'}`}>
              {lastResult.message}
            </p>
            {lastResult.prize && (
              <div className="flex items-center justify-center gap-3 p-4 bg-black/20 rounded-xl">
                <span className="text-3xl">{lastResult.prize.icon}</span>
                <div className="text-left">
                  <p className="text-[var(--color-accent-amber)] font-semibold">획득 보상</p>
                  <p className="text-white text-lg font-bold">{lastResult.prize.name}</p>
                </div>
              </div>
            )}
          </div>
        </motion.div>
        )}

        {/* 스핀 히스토리 */}
        {spinHistory.length > 0 && (
        <motion.div 
          className="max-w-md mx-auto mt-6 bg-gradient-to-r from-[var(--color-primary-charcoal)]/80 to-[var(--color-primary-dark-navy)]/80 backdrop-blur-sm p-4 rounded-xl border border-[var(--border)]/30"
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.5, duration: 0.5 }}
        >
          <h4 className="text-[var(--color-accent-amber)] font-semibold mb-3 text-center flex items-center justify-center gap-2">
            <span>🏆</span>
            <span>최근 당첨 내역</span>
          </h4>
          <div className="space-y-2">
            {spinHistory.map((prize, index) => (
              <motion.div
                key={index}
                className="flex items-center justify-between p-3 bg-black/20 rounded-lg border border-[var(--border)]/20"
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: index * 0.1 }}
              >
                <div className="flex items-center gap-3">
                  <span className="text-xl">{prize.icon}</span>
                  <span className="text-[var(--text-primary)] font-medium">{prize.name}</span>
                </div>
                <div className="flex items-center gap-2">
                  <span className="text-[var(--color-accent-amber)] text-sm font-semibold">
                    {prize.value > 0 ? `${prize.value}💰` : '특별 상품'}
                  </span>
                  {index === 0 && (
                    <span className="bg-[var(--color-accent-amber)] text-black text-xs px-2 py-1 rounded-full font-bold">
                      NEW
                    </span>
                  )}
                </div>
              </motion.div>
            ))}
          </div>
        </motion.div>
        )}
        </motion.div>
      </div>

      {/* 결과 모달 */}
      <AnimatePresence>
        {showResultModal && lastResult && (
          <motion.div
            className="fixed inset-0 bg-black/80 backdrop-blur-sm flex items-center justify-center z-50 p-4"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            onClick={closeResultModal}
          >
            <motion.div
              className="bg-gradient-to-br from-[var(--color-primary-charcoal)] to-[var(--color-primary-dark-navy)] p-8 rounded-2xl border border-[var(--border)]/50 max-w-md w-full mx-4 text-center shadow-2xl"
              initial={{ scale: 0.8, opacity: 0, y: 50 }}
              animate={{ scale: 1, opacity: 1, y: 0 }}
              exit={{ scale: 0.8, opacity: 0, y: 50 }}
              transition={{ type: "spring", damping: 25, stiffness: 300 }}
              onClick={(e) => e.stopPropagation()}
            >
              {lastResult.animation_type === 'jackpot' && (
                <motion.div
                  className="text-6xl mb-6"
                  animate={{ 
                    scale: [1, 1.2, 1],
                    rotate: [0, 5, -5, 0]
                  }}
                  transition={{ 
                    duration: 0.6,
                    repeat: Infinity,
                    repeatType: "reverse"
                  }}
                >
                  🎰✨
                </motion.div>
              )}
              
              {lastResult.prize && (
                <div className="mb-6">
                  <div className="w-20 h-20 mx-auto mb-4 bg-gradient-to-br from-[var(--color-accent-amber)]/20 to-[var(--color-accent-red)]/20 rounded-full flex items-center justify-center border border-[var(--color-accent-amber)]/30">
                    <span className="text-4xl">{lastResult.prize.icon}</span>
                  </div>
                  <h3 className="text-2xl font-bold text-[var(--color-accent-amber)] mb-2">
                    축하합니다! 🎉
                  </h3>
                  <p className="text-xl font-semibold text-white">
                    {lastResult.prize.name}
                  </p>
                </div>
              )}
              
              <p className="text-[var(--text-primary)] mb-8 text-lg leading-relaxed">
                {lastResult.message}
              </p>
              
              <button
                onClick={closeResultModal}
                className="bg-gradient-to-r from-[var(--color-accent-purple)] to-[var(--color-accent-red)] text-white px-8 py-3 rounded-xl font-semibold hover:opacity-90 transition-all duration-300 transform hover:scale-105 active:scale-95 shadow-lg"
              >
                확인
              </button>
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>
        </motion.div>
      </div>
    </div>
  );
}
