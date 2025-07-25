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
  { id: "coins_500", name: "코인 500개", value: 500, color: "#FF8C00", probability: 0.25, icon: "🪙" },
  { id: "gems_10", name: "젬 10개", value: 10, color: "#00CED1", probability: 0.2, icon: "💎" },
  { id: "gems_50", name: "젬 50개", value: 50, color: "#9370DB", probability: 0.1, icon: "💎" },
  { id: "special_item", name: "특별 아이템", value: 0, color: "#FF69B4", probability: 0.085, icon: "🎁" },
  { id: "jackpot", name: "잭팟! 젬 200개", value: 200, color: "#FF0080", probability: 0.015, icon: "🎰" },
  { id: "bonus", name: "보너스 스핀", value: 1, color: "#00FF88", probability: 0.005, icon: "🎁" }
];

export default function PrizeRoulette({ className = '' }: PrizeRouletteProps) {
  const [isSpinning, setIsSpinning] = useState(false);
  const [spinsLeft, setSpinsLeft] = useState(3);
  const [lastResult, setLastResult] = useState<PrizeRouletteSpinResult | null>(null);
  const [rotation, setRotation] = useState(0);
  const [showResultModal, setShowResultModal] = useState(false);
  const [spinHistory, setSpinHistory] = useState<Prize[]>([]);

  // 사용자 정보 가져오기
  const fetchRouletteInfo = useCallback(async () => {
    try {
      const response = await fetch('/api/roulette/info');
      const data = await response.json();
      
      if (data.success) {
        setSpinsLeft(data.spins_left || 3);
        
        // 로컬 스토리지에서 히스토리 불러오기
        const savedHistory = localStorage.getItem('roulette_history');
        if (savedHistory) {
          setSpinHistory(JSON.parse(savedHistory));
        }
      }
    } catch (error) {
      console.error('Failed to fetch roulette info:', error);
      // 백업으로 로컬 스토리지 사용
      const savedSpins = localStorage.getItem('roulette_spins_left');
      if (savedSpins) {
        setSpinsLeft(parseInt(savedSpins));
      } else {
        setSpinsLeft(3);
        localStorage.setItem('roulette_spins_left', '3');
      }
    }
  }, []);

  // 룰렛 스핀 함수
  const spinRoulette = useCallback(async () => {
    if (isSpinning || spinsLeft <= 0) return;

    setIsSpinning(true);
    
    // 랜덤 회전각 계산 (3~5바퀴 + 랜덤 각도)
    const spins = 3 + Math.random() * 2; // 3~5바퀴
    const finalAngle = Math.random() * 360; // 0~360도
    const totalRotation = rotation + (spins * 360) + finalAngle;
    
    setRotation(totalRotation);

    try {
      const response = await fetch('/api/roulette/spin', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
      });
      
      const result = await response.json();
      
      // 3초 후 결과 표시
      setTimeout(() => {
        setIsSpinning(false);
        setLastResult(result);
        setSpinsLeft(result.spins_left);
        setShowResultModal(true);
        
        // 히스토리 업데이트
        if (result.prize) {
          const newHistory = [result.prize, ...spinHistory.slice(0, 4)];
          setSpinHistory(newHistory);
          localStorage.setItem('roulette_history', JSON.stringify(newHistory));
        }
        
        // 로컬 스토리지 업데이트
        localStorage.setItem('roulette_spins_left', result.spins_left.toString());
      }, 3000);
      
    } catch (error) {
      console.error('Spin failed:', error);
      setIsSpinning(false);
      setLastResult({
        success: false,
        message: '스핀에 실패했습니다. 다시 시도해주세요.',
        spins_left: spinsLeft - 1
      });
      setSpinsLeft(prev => Math.max(0, prev - 1));
    }
  }, [isSpinning, spinsLeft, rotation, spinHistory]);

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

          {/* 룰렛 휠 */}
          <div className="flex justify-center items-center mb-8">
            <div className="relative w-[300px] h-[300px] sm:w-[350px] sm:h-[350px]">
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
                        const anglePerSegment = 360 / PRIZES.length;
                        const startAngle = index * anglePerSegment;
                        const endAngle = (index + 1) * anglePerSegment;
                        const centerAngle = startAngle + anglePerSegment / 2;
                        
                        const x1 = 100 + 90 * Math.cos((startAngle - 90) * Math.PI / 180);
                        const y1 = 100 + 90 * Math.sin((startAngle - 90) * Math.PI / 180);
                        const x2 = 100 + 90 * Math.cos((endAngle - 90) * Math.PI / 180);
                        const y2 = 100 + 90 * Math.sin((endAngle - 90) * Math.PI / 180);
                        
                        const largeArcFlag = anglePerSegment > 180 ? 1 : 0;
                        const pathData = `M 100 100 L ${x1} ${y1} A 90 90 0 ${largeArcFlag} 1 ${x2} ${y2} Z`;
                        
                        const textX = 100 + 60 * Math.cos((centerAngle - 90) * Math.PI / 180);
                        const textY = 100 + 60 * Math.sin((centerAngle - 90) * Math.PI / 180);
                        
                        return (
                          <g key={prize.id}>
                            {/* 세그먼트 배경 */}
                            <path
                              d={pathData}
                              fill={prize.color}
                              stroke="#ffffff"
                              strokeWidth="2"
                              className="transition-all duration-300 hover:brightness-110"
                            />
                            
                            {/* 아이콘 */}
                            <text
                              x={textX}
                              y={textY - 6}
                              textAnchor="middle"
                              fontSize="16"
                              fill="white"
                              style={{ textShadow: '2px 2px 4px rgba(0,0,0,0.9)' }}
                            >
                              {prize.icon}
                            </text>
                            
                            {/* 텍스트 */}
                            <text
                              x={textX}
                              y={textY + 8}
                              textAnchor="middle"
                              fontSize="8"
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
                  
                  {/* 중앙 원 */}
                  <div className="absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2 w-16 h-16 bg-gradient-to-br from-[var(--color-accent-amber)] via-yellow-400 to-[var(--color-accent-red)] rounded-full border-4 border-white shadow-2xl flex items-center justify-center z-20">
                    <span className="text-2xl font-bold text-black drop-shadow">🎯</span>
                  </div>
                </div>
              </div>
              
              {/* 포인터 */}
              <div className="absolute -top-4 left-1/2 transform -translate-x-1/2 z-30">
                <div className="relative">
                  <div className="w-0 h-0 border-l-[18px] border-r-[18px] border-t-[28px] border-l-transparent border-r-transparent border-t-[var(--color-accent-amber)] filter drop-shadow-lg"></div>
                  <div className="absolute top-0 left-1/2 transform -translate-x-1/2 w-0 h-0 border-l-[14px] border-r-[14px] border-t-[22px] border-l-transparent border-r-transparent border-t-white"></div>
                </div>
              </div>
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
              className="mb-6 bg-gradient-to-r from-[var(--color-primary-charcoal)]/90 to-[var(--color-primary-dark-navy)]/90 backdrop-blur-sm p-4 rounded-xl border border-[var(--border)]/30 shadow-xl"
              initial={{ opacity: 0, y: 20, scale: 0.9 }}
              animate={{ opacity: 1, y: 0, scale: 1 }}
              transition={{ duration: 0.5, ease: "easeOut" }}
            >
              <div className="text-center">
                <p className={`font-bold text-lg mb-3 ${lastResult.success ? 'text-[var(--color-accent-amber)]' : 'text-red-400'}`}>
                  {lastResult.message}
                </p>
                {lastResult.prize && (
                  <div className="flex items-center justify-center gap-3 p-3 bg-black/20 rounded-lg">
                    <span className="text-2xl">{lastResult.prize.icon}</span>
                    <div className="text-left">
                      <p className="text-[var(--color-accent-amber)] font-semibold text-sm">획득 보상</p>
                      <p className="text-white font-bold">{lastResult.prize.name}</p>
                    </div>
                  </div>
                )}
              </div>
            </motion.div>
          )}

          {/* 스핀 히스토리 */}
          {spinHistory.length > 0 && (
            <motion.div 
              className="bg-gradient-to-r from-[var(--color-primary-charcoal)]/80 to-[var(--color-primary-dark-navy)]/80 backdrop-blur-sm p-4 rounded-xl border border-[var(--border)]/30"
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
                    className="flex items-center justify-between p-3 bg-black/20 rounded-lg"
                    initial={{ opacity: 0, x: -20 }}
                    animate={{ opacity: 1, x: 0 }}
                    transition={{ delay: index * 0.1 }}
                  >
                    <div className="flex items-center gap-2">
                      <span className="text-lg">{prize.icon}</span>
                      <span className="text-[var(--text-primary)] font-medium text-sm">{prize.name}</span>
                    </div>
                    <div className="flex items-center gap-2">
                      <span className="text-[var(--color-accent-amber)] text-xs font-semibold">
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
    </div>
  );
}
