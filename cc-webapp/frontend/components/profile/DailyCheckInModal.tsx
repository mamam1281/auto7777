'use client';

import React, { useState, useEffect, useRef } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { 
  Gift, 
  Sparkles, 
  X, 
  Star, 
  Calendar, 
  TrendingUp, 
  Award, 
  Clock 
} from 'lucide-react';
import { Button } from '../ui/basic/button';
import { Card } from '../ui/basic/card';
import { SimpleProgressBar } from '../SimpleProgressBar';

// canvas-confetti가 설치되지 않았으므로 간단한 대체 함수 제공
const confetti = (options: any) => {
  console.log('Confetti effect triggered with options:', options);
  // 실제 설치 후 활성화하려면 import confetti from 'canvas-confetti'; 사용
  return null;
};

interface DailyCheckInModalProps {
  isOpen: boolean;
  onClose: () => void;
  onClaim: (day: number) => void;
  currentStreak: number;
  lastCheckIn: string | null;
  todayReward: number;
}

export function DailyCheckInModal({ 
  isOpen, 
  onClose, 
  onClaim, 
  currentStreak, 
  lastCheckIn,
  todayReward 
}: DailyCheckInModalProps) {
  const [timeUntilReset, setTimeUntilReset] = useState('');
  const [canClaim, setCanClaim] = useState(true);
  const confettiRef = useRef<HTMLDivElement>(null);

  const dailyRewards = [50, 75, 100, 150, 200, 300, 500]; // 7일 보상
  
  // confetti 효과를 위한 함수
  const triggerConfetti = () => {
    if (typeof window !== 'undefined' && confettiRef.current) {
      const rect = confettiRef.current.getBoundingClientRect();
      const x = rect.left + rect.width / 2;
      const y = rect.top + rect.height / 2;
      
      try {
        confetti({
          particleCount: 100,
          spread: 70,
          origin: { 
            x: x / window.innerWidth, 
            y: y / window.innerHeight 
          },
          colors: ['#5b30f6', '#8054f2', '#FFD700', '#22c55e']
        });
      } catch (error) {
        console.error('Confetti error:', error);
      }
    }
  };

  useEffect(() => {
    const interval = setInterval(() => {
      const now = new Date();
      const tomorrow = new Date(now);
      tomorrow.setDate(tomorrow.getDate() + 1);
      tomorrow.setHours(0, 0, 0, 0);
      
      const difference = tomorrow.getTime() - now.getTime();
      const hours = Math.floor(difference / (1000 * 60 * 60));
      const minutes = Math.floor((difference % (1000 * 60 * 60)) / (1000 * 60));
      
      setTimeUntilReset(`${hours}시간 ${minutes}분`);
    }, 60000);

    return () => clearInterval(interval);
  }, []);

  // 항상 claim 가능하도록 설정
  useEffect(() => {
    setCanClaim(true);
  }, []);

  if (!isOpen) return null;

  return (
    <AnimatePresence>
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        exit={{ opacity: 0 }}
        className="fixed inset-0 bg-black/80 backdrop-blur-sm z-50 p-4 overflow-y-auto"
        style={{ display: 'flex', alignItems: 'flex-start', justifyContent: 'center', paddingTop: '2rem', paddingBottom: '2rem' }}
      >
        <motion.div
          initial={{ scale: 0.8, opacity: 0 }}
          animate={{ scale: 1, opacity: 1 }}
          exit={{ scale: 0.8, opacity: 0 }}
          className="w-full max-w-lg mx-auto my-8" /* 여백 추가 및 auto로 중앙 정렬 */
        >
          <Card 
            className="profile-modal w-full bg-gray-800/95 border border-gray-600/50 shadow-lg relative"
            style={{ padding: '2rem', maxWidth: '100%' }} /* 패딩과 너비 조정 */
          >
            {/* Background decoration - 스크린샷과 동일한 어두운 배경 */}
            <div className="absolute inset-0 bg-gradient-to-br from-gray-700/30 via-transparent to-gray-900/30 pointer-events-none" />
            <motion.div 
              className="absolute top-0 left-0 w-full h-full opacity-10 pointer-events-none"
              animate={{ 
                background: [
                  'radial-gradient(circle at 10% 10%, rgb(75 85 99) 0%, transparent 50%)',
                  'radial-gradient(circle at 90% 20%, rgb(55 65 81) 0%, transparent 50%)',
                  'radial-gradient(circle at 30% 80%, rgb(107 114 128) 0%, transparent 50%)'
                ]
              }}
              transition={{ duration: 8, repeat: Infinity, repeatType: 'reverse' }}
            />
            
            <div className="relative profile-modal-content" ref={confettiRef}>
              <div className="flex items-center justify-between mb-6">
                <div className="flex items-center gap-3">
                  <div className="w-12 h-12 rounded-xl gradient-primary flex items-center justify-center border border-primary/30 shadow-elegant">
                    <motion.div
                      animate={{ rotate: [0, 10, -10, 0] }}
                      transition={{ duration: 2, repeat: Infinity, ease: "easeInOut" }}
                    >
                      <Gift className="w-6 h-6 text-white" />
                    </motion.div>
                  </div>
                  <div>
                    <h2 className="text-xl text-white game-title flex items-center gap-1">
                      데일리 체크인
                      <motion.div
                        animate={{ y: [0, -2, 0], rotate: [0, -5, 5, 0] }}
                        transition={{ duration: 1.5, repeat: Infinity, ease: "easeInOut" }}
                      >
                        <Sparkles className="w-5 h-5 text-game-gold" />
                      </motion.div>
                    </h2>
                    <p className="text-base text-muted-foreground whitespace-nowrap" style={{ padding: '12px' }}>매일 접속하여 보상을 받으세요!</p>
                  </div>
                </div>
                
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={onClose}
                  className="h-8 w-8 p-0 text-muted-foreground hover:text-white"
                >
                  <X className="h-4 w-4" />
                </Button>
              </div>

              {/* Current streak display - Enhanced 3D Layout */}
              <div className="mb-6 p-4 rounded-2xl bg-gradient-to-br from-primary/25 to-purple-500/20 
                              border-2 border-primary/50 shadow-2xl shadow-primary/30 backdrop-blur-sm
                              relative overflow-hidden">
                
                {/* Header Section - Icon + Title */}
                <div className="flex items-center gap-3 mb-4">
                  <motion.div
                    className="flex items-center justify-center w-10 h-10 min-w-[2.5rem] min-h-[2.5rem] rounded-full bg-yellow-400/20 border-2 border-yellow-400/40
                               shadow-lg shadow-yellow-400/20 flex-shrink-0 aspect-square"
                    animate={{ scale: [1, 1.05, 1] }}
                    transition={{ duration: 2, repeat: Infinity, ease: "easeInOut" }}
                  >
                    <Star className="w-5 h-5 text-yellow-400" />
                  </motion.div>
                  <div className="flex-1 min-w-0">
                    <h3 className="text-lg font-bold text-white leading-tight exo-bold drop-shadow-sm">연속 접속</h3>
                    <p className="text-base text-white/80 leading-tight whitespace-nowrap">매일 접속으로 보상 획득</p>
                  </div>
                </div>
                
                {/* Main Stats Row - Streak Number + Progress */}
                <div className="grid grid-cols-[auto_1fr] gap-6 items-center mb-6">
                  {/* Left: Large Streak Number */}
                  <motion.div
                    className="flex flex-col items-center justify-center px-6 py-4 rounded-xl 
                               bg-gradient-to-br from-primary via-purple-600 to-primary/80 
                               border-2 border-primary/60 shadow-xl shadow-primary/40 min-w-[100px]
                               backdrop-blur-sm"
                    animate={{ scale: [1, 1.02, 1] }}
                    transition={{ duration: 2, repeat: Infinity }}
                  >
                    <span className="text-2xl font-black text-white leading-none exo-bold drop-shadow-md">{currentStreak}</span>
                    <span className="text-sm font-medium text-white/90 leading-none mt-1">일째</span>
                  </motion.div>
                  
                  {/* Right: Progress Section */}
                  <div className="space-y-2">
                    {/* Progress Info */}
                    <div className="flex items-center justify-between">
                      <span className="text-base font-medium text-white/90 drop-shadow-sm">주간 진행률</span>
                      <span className="text-base font-bold text-primary drop-shadow-sm">{currentStreak % 7}/7일</span>
                    </div>
                    
                    {/* Progress Bar */}
                    <div className="space-y-1">
                      <SimpleProgressBar
                        progress={(currentStreak % 7) * (100 / 7)}
                        size="md"
                        showPercentage={false}
                        className="w-full"
                      />
                      <div className="flex items-center justify-between text-sm text-white/70">
                        <span>시작</span>
                        <span>7일 완주</span>
                      </div>
                    </div>
                  </div>
                </div>
                
                {/* Bottom Bonus Section - Simplified Layout */}
                <div className="p-4 rounded-xl bg-gradient-to-r from-yellow-500/25 to-orange-500/20 
                                border-2 border-yellow-400/50 shadow-xl shadow-yellow-400/20 relative
                                backdrop-blur-sm">
                  <div className="flex items-center gap-4">
                    <div className="flex items-center justify-center w-10 h-10 min-w-[2.5rem] min-h-[2.5rem] rounded-full bg-yellow-400/40 
                                    border border-yellow-400/60 shadow-lg shadow-yellow-400/30 flex-shrink-0 aspect-square">
                      <Award className="w-5 h-5 text-yellow-400" />
                    </div>
                    <div className="flex-1 min-w-0">
                      <div className="text-base font-bold text-yellow-300 leading-tight drop-shadow-sm whitespace-nowrap">
                        7일 달성 보너스
                      </div>
                      <div className="text-base font-black text-yellow-400 leading-tight drop-shadow-sm whitespace-nowrap">
                        +200💎 특별 보상
                      </div>
                    </div>
                  </div>
                </div>
              </div>

              {/* Today's reward */}
              <div className="mb-6 text-center">
                <motion.div
                  whileHover={{ scale: 1.05 }}
                  animate={{ 
                    boxShadow: ['0 0 0px rgba(255, 215, 0, 0.3)', '0 0 15px rgba(255, 215, 0, 0.5)', '0 0 0px rgba(255, 215, 0, 0.3)']
                  }}
                  transition={{ duration: 2, repeat: Infinity }}
                  className="inline-flex items-center gap-2 px-4 py-3 rounded-xl bg-game-gold/10 border border-game-gold/20"
                >
                  <motion.div
                    animate={{ rotate: [0, 10, -10, 0] }}
                    transition={{ duration: 3, repeat: Infinity, ease: "easeInOut" }}
                  >
                    <Calendar className="w-5 h-5 text-game-gold" />
                  </motion.div>
                  <span className="text-white exo-medium">오늘의 보상</span>
                  <motion.div
                    animate={{ scale: [1, 1.15, 1] }}
                    transition={{ duration: 1.5, repeat: Infinity }}
                  >
                    <span className="text-xl text-game-gold game-title">{todayReward}💎</span>
                  </motion.div>
                </motion.div>
              </div>

              {/* Weekly reward calendar */}
              <div className="mb-6 mt-8">
                <h3 className="text-base text-white mb-4 exo-medium flex items-center gap-3">
                  <TrendingUp className="w-4 h-4 text-primary" />
                  <span>주간 보상 캘린더</span>
                </h3>
                <div className="grid grid-cols-7 gap-4">
                  {dailyRewards.map((reward, index) => {
                    const day = index + 1;
                    const isCompleted = currentStreak >= day;
                    const isToday = currentStreak === day - 1 && canClaim;
                    const isSpecial = day === 7; // 7일차는 특별 보상
                    
                    return (
                      <motion.div
                        key={day}
                        whileHover={{ scale: 1.05 }}
                        animate={
                          isToday 
                            ? { 
                                scale: [1, 1.05, 1],
                                boxShadow: [
                                  '0 0 0px rgba(91, 48, 246, 0.3)', 
                                  '0 0 10px rgba(91, 48, 246, 0.5)', 
                                  '0 0 0px rgba(91, 48, 246, 0.3)'
                                ] 
                              }
                            : {}
                        }
                        transition={{ duration: 1.5, repeat: isToday ? Infinity : 0 }}
                        className={`
                          aspect-square rounded-xl border-2 flex flex-col items-center justify-center
                          relative overflow-hidden backdrop-blur-sm
                          ${isSpecial ? 'border-width: 3px' : ''}
                          ${isCompleted 
                            ? 'bg-game-success/25 border-game-success/60 text-game-success' 
                            : isToday 
                              ? 'bg-primary/25 border-primary/60 text-primary' 
                              : 'bg-muted/15 border-border/40 text-muted-foreground'
                          }
                          ${isSpecial && !isCompleted ? 'border-game-gold/50 shadow-lg shadow-game-gold/20' : ''}
                        `}
                      >
                        {/* Background gradient for special day */}
                        {isSpecial && (
                          <div className="absolute inset-0 bg-gradient-to-br from-yellow-400/10 via-transparent to-orange-400/10"></div>
                        )}
                        
                        {/* Content */}
                        <div className="relative z-10 flex flex-col items-center justify-center h-full">
                          <div className="text-lg font-bold mb-1">{day}</div>
                          <div className="text-sm font-medium">{reward}💎</div>
                          
                          {/* Status indicators */}
                          {isCompleted && (
                            <div className="absolute top-0 right-0 w-5 h-5 min-w-[1.25rem] min-h-[1.25rem] bg-green-500 rounded-full 
                                            flex items-center justify-center text-white text-sm font-bold
                                            border-2 border-white shadow-lg transform translate-x-1 -translate-y-1 flex-shrink-0 aspect-square">
                              ✓
                            </div>
                          )}
                          {isToday && (
                            <div className="absolute top-0 right-0 w-5 h-5 min-w-[1.25rem] min-h-[1.25rem] bg-blue-500 rounded-full 
                                            flex items-center justify-center animate-pulse
                                            border-2 border-white shadow-lg transform translate-x-1 -translate-y-1 flex-shrink-0 aspect-square">
                              <div className="w-2 h-2 min-w-[0.5rem] min-h-[0.5rem] bg-white rounded-full flex-shrink-0 aspect-square"></div>
                            </div>
                          )}
                        </div>
                      </motion.div>
                    );
                  })}
                </div>
              </div>

              {/* Action buttons */}
              <div className="space-y-3">
                {canClaim ? (
                  <div>
                    <Button
                      onClick={() => {
                        triggerConfetti();
                        onClaim(currentStreak + 1);
                      }}
                      className="w-full h-14 bg-primary hover:bg-primary/90 
                                 text-white font-semibold text-lg rounded-lg
                                 transition-colors duration-200
                                 shadow-md hover:shadow-lg
                                 flex items-center justify-center gap-3"
                    >
                      <Gift className="w-5 h-5" />
                      {todayReward}💎 받기
                      <Sparkles className="w-4 h-4" />
                    </Button>
                  </div>
                ) : (
                  <div className="text-center p-6 rounded-xl bg-gradient-to-br from-slate-800/40 to-slate-900/60 
                                  border-2 border-slate-700/50 shadow-xl shadow-slate-900/30 
                                  backdrop-blur-sm relative overflow-hidden">
                    
                    {/* 시계 아이콘 - motion 애니메이션 완전 제거 */}
                    <div className="mx-auto mb-4 w-12 h-12 min-w-[3rem] min-h-[3rem] rounded-full bg-gray-700/60 border-2 border-gray-600/50 
                                    flex items-center justify-center shadow-lg shadow-gray-900/40 flex-shrink-0 aspect-square">
                      <Clock className="w-6 h-6 text-gray-400" />
                    </div>
                    
                    {/* 안내 텍스트 크기 1단계 업 */}
                    <p className="text-base font-semibold text-gray-300 mb-3">오늘은 이미 받았어요!</p>
                    <p className="text-sm text-gray-400 bg-gray-700/40 py-2 px-3 rounded-lg inline-block 
                                  border border-gray-600/30 shadow-sm">
                      다음 보상까지: <span className="text-white font-medium">{timeUntilReset}</span>
                    </p>
                  </div>
                )}

                <motion.div
                  whileHover={{ scale: 1.02 }}
                  whileTap={{ scale: 0.98 }}
                >
                  <Button
                    onClick={onClose}
                    variant="outline"
                    className="w-full h-10 text-white border-border hover:bg-muted/20 exo-medium"
                  >
                    나중에 받기
                  </Button>
                </motion.div>
              </div>

              {/* FOMO text */}
              <motion.div
                animate={{ 
                  opacity: [0.7, 1, 0.7],
                  y: [0, -2, 0]
                }}
                transition={{ duration: 2, repeat: Infinity }}
                className="text-center mt-4 p-3 rounded-lg bg-gradient-to-r from-amber-900/30 to-red-900/20 
                           border border-amber-700/40 shadow-lg shadow-amber-900/20 backdrop-blur-sm"
              >
                <div className="text-base text-amber-300 font-medium flex items-center justify-center gap-2">
                  <span>⚠️</span>
                  <span>하루라도 놓치면 연속 기록이 초기화돼요!</span>
                </div>
              </motion.div>
            </div>
          </Card>
        </motion.div>
      </motion.div>
    </AnimatePresence>
  );
}

// Default export for convenience
export default DailyCheckInModal;
