'use client';

import React, { useState, useEffect, useCallback } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { 
  ArrowLeft, 
  Coins, 
  Zap, 
  Crown, 
  Star, 
  Diamond,
  Heart,
  RefreshCw,
  Volume2,
  VolumeX,
  Sparkles,
  Flame
} from 'lucide-react';
import { User } from '../../types';
import { Button } from '../ui/button';
import { Slider } from '../ui/slider';

interface NeonSlotGameProps {
  user: User;
  onBack: () => void;
  onUpdateUser: (user: User) => void;
  onAddNotification: (message: string) => void;
}

type SlotSymbol = {
  id: string;
  icon: React.ComponentType<any>;
  name: string;
  value: number;
  rarity: 'common' | 'rare' | 'epic' | 'legendary';
  color: string;
  isWild?: boolean;
};

const SLOT_SYMBOLS: SlotSymbol[] = [
  { id: 'cherry', icon: Heart, name: '체리', value: 2, rarity: 'common', color: 'text-pink-400' },
  { id: 'lemon', icon: Star, name: '별', value: 3, rarity: 'common', color: 'text-yellow-400' },
  { id: 'diamond', icon: Diamond, name: '다이아', value: 5, rarity: 'rare', color: 'text-blue-400' },
  { id: 'crown', icon: Crown, name: '크라운', value: 10, rarity: 'epic', color: 'text-gold' },
  { id: 'seven', icon: Sparkles, name: '세븐', value: 25, rarity: 'legendary', color: 'text-primary' },
  { id: 'wild', icon: Flame, name: '와일드', value: 0, rarity: 'legendary', color: 'text-gradient-primary', isWild: true }
];

interface SpinResult {
  reels: SlotSymbol[][];
  finalReels: SlotSymbol[];
  winAmount: number;
  isJackpot: boolean;
  isBigWin: boolean;
  hasWilds: boolean;
  multiplier: number;
  winningPositions: boolean[];
}

export function NeonSlotGame({ user, onBack, onUpdateUser, onAddNotification }: NeonSlotGameProps) {
  const [reels, setReels] = useState<SlotSymbol[]>([SLOT_SYMBOLS[0], SLOT_SYMBOLS[1], SLOT_SYMBOLS[2]]);
  const [spinningReels, setSpinningReels] = useState<SlotSymbol[][]>([[], [], []]);
  const [isSpinning, setIsSpinning] = useState(false);
  const [reelStopOrder, setReelStopOrder] = useState<number[]>([]);
  const [betAmount, setBetAmount] = useState(100);
  const [soundEnabled, setSoundEnabled] = useState(true);
  const [winAmount, setWinAmount] = useState(0);
  const [isWin, setIsWin] = useState(false);
  const [winningPositions, setWinningPositions] = useState<boolean[]>([false, false, false]);
  const [currentJackpot, setCurrentJackpot] = useState(50000);
  const [consecutiveWins, setConsecutiveWins] = useState(0);
  const [showWinModal, setShowWinModal] = useState(false);
  const [multiplier, setMultiplier] = useState(1);
  const [particles, setParticles] = useState<Array<{id: number, x: number, y: number, type: string}>>([]);
  const [isAutoSpinning, setIsAutoSpinning] = useState(false);
  const [autoSpinCount, setAutoSpinCount] = useState(0);
  const [coinDrops, setCoinDrops] = useState<Array<{id: number, x: number, delay: number}>>([]);
  
  // Jackpot calculation
  useEffect(() => {
    setCurrentJackpot(50000 + (user.gameStats.slot.totalSpins * 50));
  }, [user.gameStats.slot.totalSpins]);

  // Auto spin logic
  useEffect(() => {
    if (isAutoSpinning && autoSpinCount > 0 && !isSpinning) {
      const timer = setTimeout(() => {
        handleSpin();
        setAutoSpinCount(prev => prev - 1);
      }, 1500);
      return () => clearTimeout(timer);
    } else if (autoSpinCount === 0) {
      setIsAutoSpinning(false);
    }
  }, [autoSpinCount, isSpinning, isAutoSpinning]);

  // Generate enhanced particles
  const generateParticles = useCallback((type: string = 'win') => {
    const particleCount = type === 'jackpot' ? 30 : 15;
    const newParticles = Array.from({ length: particleCount }, (_, i) => ({
      id: Date.now() + i,
      x: Math.random() * 100,
      y: Math.random() * 100,
      type
    }));
    setParticles(newParticles);
    setTimeout(() => setParticles([]), 3000);
  }, []);

  // Generate coin drop effect
  const generateCoinDrops = useCallback(() => {
    const newCoins = Array.from({ length: 8 }, (_, i) => ({
      id: Date.now() + i,
      x: 20 + (i * 10) + Math.random() * 5,
      delay: i * 100
    }));
    setCoinDrops(newCoins);
    setTimeout(() => setCoinDrops([]), 2000);
  }, []);

  // Generate spinning reel symbols (for animation)
  const generateSpinningReels = (): SlotSymbol[][] => {
    return Array.from({ length: 3 }, () => 
      Array.from({ length: 20 }, () => 
        SLOT_SYMBOLS[Math.floor(Math.random() * SLOT_SYMBOLS.length)]
      )
    );
  };

  // Generate random symbol weighted by rarity
  const getRandomSymbol = (): SlotSymbol => {
    const weights = {
      common: 50,
      rare: 30,
      epic: 15,
      legendary: 5
    };
    
    const totalWeight = Object.values(weights).reduce((sum, weight) => sum + weight, 0);
    let random = Math.random() * totalWeight;
    
    for (const symbol of SLOT_SYMBOLS) {
      random -= weights[symbol.rarity];
      if (random <= 0) return symbol;
    }
    
    return SLOT_SYMBOLS[0];
  };

  // Generate spin result
  const generateSpinResult = (): SpinResult => {
    const finalReels: SlotSymbol[] = [getRandomSymbol(), getRandomSymbol(), getRandomSymbol()];
    const spinningReelsData = generateSpinningReels();
    
    // Ensure final symbols are at the end of each reel
    spinningReelsData.forEach((reel, index) => {
      reel[reel.length - 1] = finalReels[index];
    });
    
    let totalWinAmount = 0;
    let hasWilds = false;
    let currentMultiplier = multiplier;
    const winPositions = [false, false, false];

    // Check for wilds
    const wildCount = finalReels.filter(symbol => symbol.isWild).length;
    hasWilds = wildCount > 0;

    // Check for matching symbols
    let matchCount = 1;
    const matchingSymbol = finalReels[0];
    winPositions[0] = true;
    
    // Count consecutive matches from left
    for (let i = 1; i < finalReels.length; i++) {
      if (finalReels[i].id === matchingSymbol.id || finalReels[i].isWild || matchingSymbol.isWild) {
        matchCount++;
        winPositions[i] = true;
      } else {
        break;
      }
    }

    // Calculate win only if 2 or more matches
    if (matchCount >= 2) {
      const baseSymbol = finalReels.find(s => !s.isWild) || finalReels[0];
      totalWinAmount = betAmount * baseSymbol.value * matchCount;
      
      // Wild multiplier
      if (hasWilds) {
        currentMultiplier *= (1 + wildCount);
        totalWinAmount *= (1 + wildCount);
      }
    } else {
      // Reset win positions if no win
      winPositions.fill(false);
    }

    // Jackpot check (3 sevens or wilds)
    const isJackpot = finalReels.every(symbol => symbol.id === 'seven' || symbol.isWild);
    if (isJackpot) {
      totalWinAmount = currentJackpot;
      winPositions.fill(true);
    }

    const isBigWin = totalWinAmount >= betAmount * 10;

    return {
      reels: spinningReelsData,
      finalReels,
      winAmount: totalWinAmount,
      isJackpot,
      isBigWin,
      hasWilds,
      multiplier: currentMultiplier,
      winningPositions: winPositions
    };
  };

  // Handle spin with enhanced animation
  const handleSpin = async () => {
    if (user.goldBalance < betAmount) {
      onAddNotification('❌ 골드가 부족합니다!');
      return;
    }

    setIsSpinning(true);
    setIsWin(false);
    setWinAmount(0);
    setWinningPositions([false, false, false]);
    setCoinDrops([]);

    // Deduct bet amount
    const costAmount = betAmount;

    // Generate spin result
    const result = generateSpinResult();
    setSpinningReels(result.reels);

    // Create staggered reel stop timing (more realistic)
    const stopOrder = [0, 1, 2];
    setReelStopOrder([]);

    // 🎯 개별 릴 회전 시뮬레이션 - 각 릴을 개별적으로 제어
    const reelStopTimes = [1200, 1800, 2400]; // Different timing for each reel

    // Stop reels one by one
    for (let i = 0; i < stopOrder.length; i++) {
      setTimeout(() => {
        setReels(prev => {
          const newReels = [...prev];
          newReels[stopOrder[i]] = result.finalReels[stopOrder[i]];
          return newReels;
        });
        setReelStopOrder(prev => [...prev, stopOrder[i]]);
      }, reelStopTimes[i]);
    }

    // Process final result after all reels stop
    setTimeout(() => {
      if (result.winAmount > 0) {
        setIsWin(true);
        setWinAmount(result.winAmount);
        setWinningPositions(result.winningPositions);
        setConsecutiveWins(prev => prev + 1);
        
        // Enhanced particle effects based on win type
        if (result.isJackpot) {
          generateParticles('jackpot');
        } else if (result.isBigWin) {
          generateParticles('bigwin');
        } else {
          generateParticles('win');
        }
        
        generateCoinDrops();
        
        // Update user stats
        const updatedUser = {
          ...user,
          goldBalance: user.goldBalance - costAmount + result.winAmount,
          gameStats: {
            ...user.gameStats,
            slot: {
              ...user.gameStats.slot,
              totalSpins: user.gameStats.slot.totalSpins + 1,
              totalWinnings: user.gameStats.slot.totalWinnings + result.winAmount,
              biggestWin: Math.max(user.gameStats.slot.biggestWin, result.winAmount),
              jackpotHits: result.isJackpot ? user.gameStats.slot.jackpotHits + 1 : user.gameStats.slot.jackpotHits
            }
          },
          stats: {
            ...user.stats,
            gamesPlayed: user.stats.gamesPlayed + 1,
            gamesWon: user.stats.gamesWon + 1,
            totalEarnings: user.stats.totalEarnings + (result.winAmount - costAmount),
            winStreak: user.stats.winStreak + 1
          }
        };

        onUpdateUser(updatedUser);

        // Only important notifications
        if (result.isJackpot) {
          setShowWinModal(true);
          onAddNotification(`🎰 JACKPOT! ${result.winAmount.toLocaleString()}G 획득!`);
        } else if (result.isBigWin) {
          onAddNotification(`🔥 BIG WIN! ${result.winAmount.toLocaleString()}G 획득!`);
        }
      } else {
        setConsecutiveWins(0);
        
        const updatedUser = {
          ...user,
          goldBalance: user.goldBalance - costAmount,
          gameStats: {
            ...user.gameStats,
            slot: {
              ...user.gameStats.slot,
              totalSpins: user.gameStats.slot.totalSpins + 1
            }
          },
          stats: {
            ...user.stats,
            gamesPlayed: user.stats.gamesPlayed + 1,
            winStreak: 0
          }
        };

        onUpdateUser(updatedUser);
      }

      setIsSpinning(false);
      setReelStopOrder([]); // Reset for next spin
    }, 3000);
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-background via-black to-primary-soft relative overflow-hidden">
      {/* Enhanced Particle Effects */}
      <AnimatePresence>
        {particles.map((particle) => (
          <motion.div
            key={particle.id}
            initial={{ 
              opacity: 0,
              scale: 0,
              x: `${particle.x}vw`,
              y: `${particle.y}vh`
            }}
            animate={{ 
              opacity: [0, 1, 0],
              scale: particle.type === 'jackpot' ? [0, 2, 0] : [0, 1.5, 0],
              y: `${particle.y - 20}vh`,
              rotate: 360
            }}
            exit={{ opacity: 0 }}
            transition={{ duration: particle.type === 'jackpot' ? 3 : 2, ease: "easeOut" }}
            className={`fixed w-4 h-4 rounded-full pointer-events-none z-30 ${
              particle.type === 'jackpot' ? 'bg-gradient-gold' : 
              particle.type === 'bigwin' ? 'bg-gradient-to-r from-primary to-gold' :
              'bg-gradient-to-r from-primary to-primary-light'
            }`}
          />
        ))}
      </AnimatePresence>

      {/* Coin Drop Effects */}
      <AnimatePresence>
        {coinDrops.map((coin) => (
          <motion.div
            key={coin.id}
            initial={{ 
              opacity: 0,
              y: -50,
              x: `${coin.x}vw`,
              rotate: 0
            }}
            animate={{ 
              opacity: [0, 1, 1, 0],
              y: 50,
              rotate: 180
            }}
            exit={{ opacity: 0 }}
            transition={{ 
              duration: 1.5, 
              delay: coin.delay / 1000,
              ease: "easeOut" 
            }}
            className="fixed w-6 h-6 bg-gradient-gold rounded-full pointer-events-none z-30 flex items-center justify-center text-black text-xs font-bold"
          >
            G
          </motion.div>
        ))}
      </AnimatePresence>

      {/* Simple Header */}
      <motion.header
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        className="relative z-10 p-4 lg:p-6 border-b border-border-secondary/50 backdrop-blur-xl bg-card/80"
      >
        <div className="flex items-center justify-between max-w-4xl mx-auto">
          <div className="flex items-center gap-4">
            <Button
              variant="outline"
              onClick={onBack}
              className="glass-effect hover:bg-primary/10 transition-all duration-300"
            >
              <ArrowLeft className="w-4 h-4 mr-2" />
              뒤로가기
            </Button>
            
            <h1 className="text-xl lg:text-2xl font-bold text-gradient-primary">
              네온 슬롯
            </h1>
          </div>

          <div className="flex items-center gap-4">
            <Button
              variant="outline"
              size="icon"
              onClick={() => setSoundEnabled(!soundEnabled)}
              className="glass-effect hover:bg-primary/10 transition-all duration-300"
            >
              {soundEnabled ? <Volume2 className="w-4 h-4" /> : <VolumeX className="w-4 h-4" />}
            </Button>
            
            <div className="glass-effect rounded-xl p-3 border border-gold/20">
              <div className="text-right">
                <div className="text-sm text-muted-foreground">보유 골드</div>
                <div className="text-xl font-black text-gradient-gold">
                  {user.goldBalance.toLocaleString()}G
                </div>
              </div>
            </div>
          </div>
        </div>
      </motion.header>

      {/* Main Content */}
      <div className="relative z-10 p-4 lg:p-6 max-w-4xl mx-auto">
        {/* Jackpot Display */}
        <motion.div
          initial={{ opacity: 0, scale: 0.8 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ delay: 0.2 }}
          className="text-center mb-6"
        >
          <div className="glass-effect rounded-2xl p-6 border-2 border-gold/20 gold-soft-glow">
            <motion.div
              animate={{ scale: [1, 1.05, 1] }}
              transition={{ duration: 3, repeat: Infinity }}
              className="text-3xl lg:text-4xl font-black text-gradient-gold mb-2"
            >
              💰 JACKPOT 💰
            </motion.div>
            <div className="text-2xl lg:text-3xl font-bold text-gold">
              {currentJackpot.toLocaleString()}G
            </div>
          </div>
        </motion.div>

        {/* 🎰 슬롯 머신 - 개별 릴만 회전 */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.4 }}
          className="glass-effect rounded-3xl p-8 mb-6 relative overflow-hidden"
        >
          {/* Win Effect Overlay */}
          <AnimatePresence>
            {isWin && (
              <motion.div
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                exit={{ opacity: 0 }}
                className="absolute inset-0 pointer-events-none z-10 rounded-3xl"
              >
                <motion.div
                  animate={{ 
                    opacity: [0.3, 0.7, 0.3]
                  }}
                  transition={{ duration: 1, repeat: Infinity }}
                  className="absolute inset-0 bg-gradient-to-r from-gold/10 via-transparent to-gold/10 rounded-3xl"
                />
              </motion.div>
            )}
          </AnimatePresence>

          {/* 🎯 3개 개별 릴 - 각각 독립적으로 회전 */}
          <div className="grid grid-cols-3 gap-6 mb-6">
            {reels.map((symbol, index) => (
              <div
                key={index}
                className={`aspect-square glass-effect rounded-2xl relative overflow-hidden ${
                  winningPositions[index] ? 'border-2 border-gold soft-glow' : 'border border-border-secondary'
                }`}
              >
                {/* 🎰 개별 릴 회전 컨테이너 */}
                <div className="absolute inset-0 flex items-center justify-center">
                  {/* 회전 중인 심볼들 */}
                  <AnimatePresence>
                    {isSpinning && !reelStopOrder.includes(index) && (
                      <motion.div
                        key={`spinning-${index}`}
                        initial={{ y: '100%' }}
                        animate={{ y: '-100%' }}
                        transition={{ 
                          duration: 0.1, 
                          repeat: Infinity, 
                          ease: "linear" 
                        }}
                        className="absolute inset-0 flex flex-col justify-center"
                      >
                        {spinningReels[index]?.slice(0, 3).map((spinSymbol, spinIndex) => (
                          <div 
                            key={`spin-${index}-${spinIndex}`}
                            className="h-full flex items-center justify-center reel-blur"
                          >
                            <spinSymbol.icon className={`text-4xl lg:text-5xl ${spinSymbol.color}`} />
                          </div>
                        )) || []}
                      </motion.div>
                    )}
                  </AnimatePresence>

                  {/* 🎯 최종 심볼 - 착지 애니메이션 */}
                  <motion.div
                    key={`final-${index}-${symbol.id}`}
                    animate={
                      reelStopOrder.includes(index) ? {
                        scale: [0.8, 1.2, 1],
                        y: [30, -10, 0]
                      } : 
                      winningPositions[index] ? { 
                        scale: [1, 1.2, 1],
                        rotate: [0, 5, -5, 0]
                      } : {}
                    }
                    transition={{ 
                      duration: winningPositions[index] ? 0.6 : 0.5, 
                      repeat: winningPositions[index] ? 3 : 0,
                      type: "spring",
                      stiffness: 300
                    }}
                    className={`text-5xl lg:text-6xl ${symbol.color} z-20 relative ${
                      winningPositions[index] ? 'pulse-win' : ''
                    }`}
                  >
                    <symbol.icon />
                  </motion.div>
                </div>
                
                {/* Symbol name */}
                <div className="absolute bottom-2 left-1/2 transform -translate-x-1/2 text-xs text-muted-foreground">
                  {symbol.name}
                </div>

                {/* Wild effect */}
                {symbol.isWild && (
                  <motion.div
                    animate={{ opacity: [0.3, 0.7, 0.3] }}
                    transition={{ duration: 1, repeat: Infinity }}
                    className="absolute inset-0 bg-gradient-to-r from-primary/10 to-primary-light/10 rounded-2xl pointer-events-none"
                  />
                )}

                {/* Reel Number */}
                <div className="absolute top-2 left-2 text-xs text-muted-foreground font-bold">
                  {index + 1}
                </div>
              </div>
            ))}
          </div>

          {/* 🎉 당첨 표시 */}
          <AnimatePresence>
            {winAmount > 0 && (
              <motion.div
                initial={{ opacity: 0, scale: 0.5, y: 20 }}
                animate={{ opacity: 1, scale: 1, y: 0 }}
                exit={{ opacity: 0, scale: 0.5, y: -20 }}
                className="text-center mb-6"
              >
                <motion.div
                  animate={{ 
                    scale: [1, 1.1, 1],
                    textShadow: [
                      '0 0 10px rgba(255,215,0,0.3)', 
                      '0 0 20px rgba(255,215,0,0.6)', 
                      '0 0 10px rgba(255,215,0,0.3)'
                    ]
                  }}
                  transition={{ duration: 0.8, repeat: 3 }}
                  className="text-4xl lg:text-5xl font-black text-gradient-gold mb-2"
                >
                  {winAmount >= betAmount * 10 ? '🔥 BIG WIN! 🔥' : '🎉 WIN! 🎉'}
                </motion.div>
                <div className="text-3xl lg:text-4xl font-bold text-gold coin-drop">
                  +{winAmount.toLocaleString()}G
                </div>
                {multiplier > 1 && (
                  <div className="text-lg text-primary font-bold">
                    {multiplier}x 멀티플라이어!
                  </div>
                )}
              </motion.div>
            )}
          </AnimatePresence>

          {/* Bet Controls */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-6">
            <div>
              <div className="text-sm font-medium text-foreground mb-2">베팅 금액</div>
              <div className="flex items-center gap-4 mb-3">
                <Slider
                  value={[betAmount]}
                  onValueChange={(value) => setBetAmount(value[0])}
                  max={Math.min(user.goldBalance, 10000)}
                  min={50}
                  step={50}
                  className="flex-1"
                  disabled={isSpinning || isAutoSpinning}
                />
                <div className="text-lg font-bold text-gold min-w-[120px]">
                  {betAmount.toLocaleString()}G
                </div>
              </div>
              
              <div className="grid grid-cols-4 gap-2">
                {[100, 500, 1000, 5000].map((amount) => (
                  <Button
                    key={amount}
                    size="sm"
                    variant="outline"
                    onClick={() => setBetAmount(Math.min(amount, user.goldBalance))}
                    disabled={isSpinning || isAutoSpinning || user.goldBalance < amount}
                    className="border-border-secondary hover:border-primary text-xs btn-hover-lift"
                  >
                    {amount}G
                  </Button>
                ))}
              </div>
            </div>

            <div>
              <div className="text-sm font-medium text-foreground mb-2">연속 승리</div>
              <div className="text-3xl font-bold text-primary mb-4">{consecutiveWins}</div>
            </div>
          </div>

          {/* Enhanced Spin Buttons */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
            <Button
              onClick={handleSpin}
              disabled={isSpinning || isAutoSpinning || user.goldBalance < betAmount}
              className="bg-gradient-game hover:opacity-90 text-white font-bold py-4 text-lg relative overflow-hidden btn-hover-glow"
            >
              {isSpinning ? (
                <>
                  <motion.div
                    animate={{ rotate: 360 }}
                    transition={{ duration: 1, repeat: Infinity, ease: "linear" }}
                  >
                    <RefreshCw className="w-6 h-6 mr-2" />
                  </motion.div>
                  스핀 중...
                </>
              ) : (
                <>
                  <Zap className="w-6 h-6 mr-2" />
                  스핀
                </>
              )}
            </Button>

            <div className="grid grid-cols-2 gap-2">
              <Button
                onClick={() => {
                  setAutoSpinCount(10);
                  setIsAutoSpinning(true);
                }}
                disabled={isSpinning || isAutoSpinning || user.goldBalance < betAmount * 5}
                variant="outline"
                className="border-border-secondary hover:border-primary text-sm btn-hover-lift"
              >
                {isAutoSpinning ? autoSpinCount : '자동 10x'}
              </Button>
              <Button
                onClick={() => {
                  setAutoSpinCount(0);
                  setIsAutoSpinning(false);
                }}
                disabled={!isAutoSpinning}
                variant="outline"
                className="border-error hover:border-error text-error text-sm btn-hover-lift"
              >
                정지
              </Button>
            </div>
          </div>
        </motion.div>

        {/* Game Stats */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.6 }}
          className="grid grid-cols-2 lg:grid-cols-4 gap-4 mb-6"
        >
          <div className="glass-effect rounded-xl p-4 text-center card-hover-float">
            <div className="text-xl font-bold text-primary">
              {user.gameStats.slot.totalSpins}
            </div>
            <div className="text-sm text-muted-foreground">총 스핀</div>
          </div>
          <div className="glass-effect rounded-xl p-4 text-center card-hover-float">
            <div className="text-xl font-bold text-gold">
              {user.gameStats.slot.jackpotHits}
            </div>
            <div className="text-sm text-muted-foreground">잭팟 횟수</div>
          </div>
          <div className="glass-effect rounded-xl p-4 text-center card-hover-float">
            <div className="text-xl font-bold text-success">
              {user.gameStats.slot.biggestWin.toLocaleString()}G
            </div>
            <div className="text-sm text-muted-foreground">최대 승리</div>
          </div>
          <div className="glass-effect rounded-xl p-4 text-center card-hover-float">
            <div className="text-xl font-bold text-warning">
              {user.gameStats.slot.totalWinnings.toLocaleString()}G
            </div>
            <div className="text-sm text-muted-foreground">총 획득</div>
          </div>
        </motion.div>

        {/* Paytable */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.8 }}
          className="glass-effect rounded-xl p-6"
        >
          <h3 className="text-lg font-bold text-foreground mb-4">상금표</h3>
          <div className="grid grid-cols-2 lg:grid-cols-3 gap-3">
            {SLOT_SYMBOLS.map((symbol) => (
              <div key={symbol.id} className="flex items-center gap-3 p-3 rounded-lg bg-secondary/30 card-hover-float">
                <symbol.icon className={`w-8 h-8 ${symbol.color}`} />
                <div className="flex-1">
                  <div className="text-sm font-medium text-foreground">{symbol.name}</div>
                  <div className="text-xs text-muted-foreground">
                    {symbol.isWild ? '모든 심볼 대체' : `x${symbol.value} (2연속)`}
                  </div>
                </div>
              </div>
            ))}
          </div>
        </motion.div>
      </div>
    </div>
  );
}