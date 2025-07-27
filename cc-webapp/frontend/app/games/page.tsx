'use client';

import './games.css';
import { motion } from 'framer-motion';
import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { 
  Star, 
  Zap, 
  TrendingUp, 
  Dice1, 
  Target, 
  Sparkles,
  Trophy,
  Coins,
  Play,
  ArrowLeft,
  Crown,
  Flame
} from 'lucide-react';

type GameType = 'home' | 'slots' | 'roulette' | 'rps' | 'gacha';

interface GameCardProps {
  title: string;
  description: string;
  icon: React.ReactNode;
  gameType: GameType;
  accent: string;
  difficulty: 'Easy' | 'Medium' | 'Hard';
  minBet: number;
  maxWin: number;
  isNew?: boolean;
  isHot?: boolean;
}

function GameCard({ 
  title, 
  description, 
  icon, 
  gameType, 
  accent, 
  difficulty, 
  minBet, 
  maxWin, 
  isNew, 
  isHot
}: GameCardProps) {
  const router = useRouter();

  const handleClick = () => {
    // 실제 브라우저 팝업 창으로 게임 열기
    const popupConfig = {
      width: 420,
      height: 850,
      resizable: 'no',
      scrollbars: 'no',
      status: 'no',
      toolbar: 'no',
      menubar: 'no',
      location: 'no'
    };
    
    const configString = Object.entries(popupConfig)
      .map(([key, value]) => `${key}=${value}`)
      .join(',');
    
    switch (gameType) {
      case 'slots':
        window.open('/games/slots/popup', 'slots_game', configString);
        break;
      case 'roulette':
        window.open('/games/roulette/popup', 'roulette_game', configString);
        break;
      case 'rps':
        window.open('/games/rps/popup', 'rps_game', configString);
        break;
      case 'gacha':
        window.open('/games/gacha/popup', 'gacha_game', configString);
        break;
      default:
        break;
    }
  };

  return (
    <motion.div
      className="relative group cursor-pointer"
      whileHover={{ y: -4, scale: 1.02 }}
      whileTap={{ scale: 0.98 }}
      onClick={handleClick}
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.4, ease: "easeOut" }}
    >
      {/* 깔끔하고 선명한 카드 디자인 */}
      <div className="relative rounded-xl overflow-hidden
                      transition-all duration-500"
           style={{
             background: 'linear-gradient(145deg, rgba(255,255,255,0.08) 0%, rgba(255,255,255,0.02) 100%)',
             border: '1px solid rgba(255,255,255,0.15)',
             boxShadow: '0 2px 8px rgba(0,0,0,0.15)'
           }}>

        {/* 전문적으로 재설계된 콘텐츠 */}
        <div className="p-4 space-y-5">
          {/* 상단: 제목 */}
          <div className="text-center">
            <h3 className="text-2xl font-black text-white mb-3"
                style={{ 
                  fontFamily: "'Inter', sans-serif",
                  letterSpacing: '-0.02em',
                  fontSize: '22px'
                }}>
              {title}
            </h3>
            
            {/* 난이도 태그 */}
            <span className={`inline-block px-4 py-2 rounded-full text-sm font-semibold ${
              difficulty === 'Easy' ? 'bg-green-500/20 text-green-400 border border-green-500/30' :
              difficulty === 'Medium' ? 'bg-yellow-500/20 text-yellow-400 border border-yellow-500/30' :
              'bg-red-500/20 text-red-400 border border-red-500/30'
            }`}>
              {difficulty}
            </span>
          </div>

          {/* 중간: 게임 정보 */}
          <div className="flex justify-center gap-8">
            <div className="text-center">
              <Coins className="w-7 h-7 text-yellow-400 mx-auto mb-1.5" />
              <div className="text-white font-bold text-lg">{minBet}💎</div>
              <div className="text-gray-300 text-xs font-medium">MIN BET</div>
            </div>
            <div className="text-center">
              <Trophy className="w-7 h-7 text-orange-400 mx-auto mb-1.5" />
              <div className="text-white font-bold text-lg">{maxWin.toLocaleString()}</div>
              <div className="text-gray-300 text-xs font-medium">MAX WIN</div>
            </div>
          </div>

          {/* 하단: 선명한 버튼 */}
          <div className="pt-2">
            <motion.button
              className="w-full py-4 px-6 rounded-lg 
                         bg-gradient-to-r from-emerald-500 to-cyan-500 hover:from-emerald-400 hover:to-cyan-400
                         border border-emerald-400/40 hover:border-emerald-300/60
                         transition-all duration-300 
                         flex items-center justify-center gap-3 
                         text-white font-bold text-xl
                         transform hover:scale-105 active:scale-95"
              style={{
                background: 'linear-gradient(135deg, #10b981 0%, #06b6d4 100%)',
                boxShadow: '0 2px 6px rgba(0,0,0,0.15)'
              }}
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
            >
              <Play className="w-7 h-7" />
              <span className="tracking-wide">PLAY NOW</span>
            </motion.button>
          </div>
        </div>
      </div>
    </motion.div>
  );
}

function HomePage() {
  const games: GameCardProps[] = [
    {
      title: "코스믹 포츈",
      description: "우주 슬롯머신의 짜릿한 재미",
      icon: <Sparkles className="w-5 h-5 text-purple-400" />,
      gameType: "slots",
      accent: "purple-400",
      difficulty: "Easy",
      minBet: 10,
      maxWin: 100000,
      isNew: true,
      isHot: true
    },
    {
      title: "갤럭시 룰렛",
      description: "운명의 숫자를 맞춰보세요",
      icon: <Target className="w-5 h-5 text-blue-400" />,
      gameType: "roulette",
      accent: "blue-400",
      difficulty: "Medium",
      minBet: 50,
      maxWin: 350000,
      isHot: true
    },
    {
      title: "코스믹 배틀",
      description: "가위바위보 우주 대결",
      icon: <Dice1 className="w-5 h-5 text-emerald-400" />,
      gameType: "rps",
      accent: "emerald-400",
      difficulty: "Easy",
      minBet: 20,
      maxWin: 80000
    },
    {
      title: "스텔라 랜덤뽑기",
      description: "행운의 랜덤뽑기로 특별한 보상을 획득하세요!",
      icon: <Star className="w-5 h-5 text-orange-400" />,
      gameType: "gacha",
      accent: "orange-400",
      difficulty: "Hard",
      minBet: 100,
      maxWin: 1000000,
      isNew: true
    }
  ];

  return (
    <div className="game-dashboard w-full max-w-[420px] mx-auto min-h-screen bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900 
                    relative overflow-hidden">
      
      {/* 깔끔한 별빛 효과만 유지 */}
      <div className="absolute inset-0 opacity-20">
        {[
          { left: 15, top: 20, delay: 0.5, duration: 3.2 },
          { left: 85, top: 35, delay: 1.2, duration: 4.1 },
          { left: 45, top: 15, delay: 2.0, duration: 3.8 },
          { left: 25, top: 70, delay: 0.8, duration: 3.5 },
          { left: 75, top: 60, delay: 1.8, duration: 4.2 },
          { left: 35, top: 85, delay: 1.0, duration: 3.7 },
          { left: 90, top: 25, delay: 2.5, duration: 3.3 },
          { left: 10, top: 50, delay: 0.3, duration: 4.0 },
          { left: 60, top: 40, delay: 1.5, duration: 3.6 },
          { left: 80, top: 80, delay: 2.2, duration: 3.9 }
        ].map((star, i) => (
          <div
            key={i}
            className="absolute w-0.5 h-0.5 bg-yellow-300 rounded-full animate-pulse"
            style={{
              left: `${star.left}%`,
              top: `${star.top}%`,
              animationDelay: `${star.delay}s`,
              animationDuration: `${star.duration}s`
            }}
          />
        ))}
      </div>

      {/* 메인 컨텐츠 */}
      <div className="relative z-10 min-h-screen flex flex-col px-2 max-w-lg mx-auto w-full">
        
        {/* 개선된 헤더 */}
        <motion.header
          className="py-5 text-center relative z-20"
          initial={{ opacity: 0, y: -40 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 1, ease: "easeOut" }}
        >
          <motion.h1
            className="text-6xl font-black tracking-tight mb-4 leading-tight"
            style={{
              fontFamily: "'Inter', 'SF Pro Display', -apple-system, BlinkMacSystemFont, sans-serif",
              textShadow: '0 12px 40px rgba(0,0,0,0.6), 0 6px 20px rgba(168,85,247,0.4), 0 4px 12px rgba(255,255,255,0.1)'
            }}
            whileHover={{ scale: 1.02, y: -2 }}
            transition={{ duration: 0.4, ease: "easeOut" }}
          >
            <span className="cosmic-gradient-text font-black tracking-tight"
                  style={{
                    background: 'linear-gradient(135deg, #ffffff 0%, #f8fafc 20%, #e2e8f0 40%, #cbd5e1 60%, #94a3b8 80%, #64748b 100%)',
                    backgroundClip: 'text',
                    WebkitBackgroundClip: 'text',
                    WebkitTextFillColor: 'transparent',
                    color: 'transparent',
                    textShadow: 'none'
                  }}>
              COSMIC CASINO
            </span>
          </motion.h1>
          <motion.p
            className="text-lg font-semibold mb-8 tracking-wide"
            style={{
              fontFamily: "'Inter', sans-serif",
              color: 'rgba(255, 255, 255, 0.85)',
              textShadow: '0 4px 16px rgba(0,0,0,0.5), 0 2px 8px rgba(0,0,0,0.3)',
              letterSpacing: '0.03em',
              fontWeight: '600'
            }}
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 0.6 }}
          >
            Premium Cosmic Gaming Experience
          </motion.p>
          
          {/* 프리미엄 통계 */}
          <motion.div
            className="flex items-center justify-center gap-4 text-sm"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.8 }}
          >
            <div className="flex items-center gap-2 px-4 py-3 rounded-xl 
                            bg-white/5 backdrop-blur-md
                            border border-white/10 hover:border-white/20
                            transition-all duration-300">
              <TrendingUp className="w-4 h-4 text-emerald-300" />
              <span style={{ 
                fontFamily: "'Inter', sans-serif",
                color: 'rgba(255, 255, 255, 0.9)',
                fontWeight: '500',
                letterSpacing: '0.02em'
              }}>99.2% RTP</span>
            </div>
            <div className="flex items-center gap-2 px-4 py-3 rounded-xl 
                            bg-white/5 backdrop-blur-md
                            border border-white/10 hover:border-white/20
                            transition-all duration-300">
              <Zap className="w-4 h-4 text-amber-300" />
              <span style={{ 
                fontFamily: "'Inter', sans-serif",
                color: 'rgba(255, 255, 255, 0.9)',
                fontWeight: '500',
                letterSpacing: '0.02em'
              }}>Instant Payout</span>
            </div>
          </motion.div>
        </motion.header>

        {/* 게임 그리드 */}
        <main className="flex-1 pb-8">
          <motion.div
            className="flex flex-col gap-4"
            initial="hidden"
            animate="visible"
            variants={{
              visible: {
                transition: {
                  staggerChildren: 0.1
                }
              }
            }}
          >
            {games.map((game, index) => (
              <motion.div
                key={index}
                variants={{
                  hidden: { opacity: 0, y: 20 },
                  visible: { opacity: 1, y: 0 }
                }}
              >
                <GameCard {...game} />
              </motion.div>
            ))}
          </motion.div>
        </main>

        {/* 프리미엄 푸터 */}
        <motion.footer
          className="py-6 text-center border-t border-white/10 backdrop-blur-md"
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 1.2 }}
        >
          <p style={{
               fontFamily: "'Inter', sans-serif",
               color: 'rgba(255, 255, 255, 0.6)',
               fontSize: '0.875rem',
               fontWeight: '400',
               letterSpacing: '0.025em',
               textShadow: '0 2px 8px rgba(0,0,0,0.3)'
             }}>
            Responsible Gaming • Licensed & Secure ⭐
          </p>
        </motion.footer>
      </div>
    </div>
  );
}

export default function App() {
  useEffect(() => {
    document.title = '🎰 COSMIC CASINO - 프리미엄 우주 카지노';
    
    // 프리미엄 그라디언트 텍스트 스타일을 동적으로 추가
    const style = document.createElement('style');
    style.textContent = `
      .cosmic-gradient-text {
        background: linear-gradient(135deg, #ffffff 0%, #f8fafc 20%, #e2e8f0 40%, #cbd5e1 60%, #94a3b8 80%, #64748b 100%) !important;
        -webkit-background-clip: text !important;
        -webkit-text-fill-color: transparent !important;
        background-clip: text !important;
        color: transparent !important;
        display: inline-block !important;
        background-size: 200% 200% !important;
        animation: premium-gradient 3s ease-in-out infinite !important;
        font-weight: 900 !important;
        letter-spacing: -0.02em !important;
      }
      
      @keyframes premium-gradient {
        0%, 100% { 
          background-position: 0% 50%; 
          filter: drop-shadow(0 4px 12px rgba(255,255,255,0.2));
        }
        50% { 
          background-position: 100% 50%; 
          filter: drop-shadow(0 6px 16px rgba(255,255,255,0.3));
        }
      }
    `;
    document.head.appendChild(style);
    
    return () => {
      document.head.removeChild(style);
    };
  }, []);

  return <HomePage />;
}
