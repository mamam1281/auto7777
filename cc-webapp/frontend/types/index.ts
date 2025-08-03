// 🎮 게임 사용자 타입
export interface User {
  id: string;
  nickname: string;
  goldBalance: number;
  level: number;
  experience: number;
  maxExperience: number;
  dailyStreak: number;
  achievements: string[];
  inventory: GameItem[];
  stats: GameStats;
  gameStats: GameStatsDetail;
  lastLogin: Date;
  totalPlayTime: number;
  isAdmin: boolean;
  registrationDate: Date;
  lastActivity: Date;
  deviceInfo: string;
  ipAddress: string;
}

// 🎯 게임 아이템 타입
export interface GameItem {
  id: string;
  name: string;
  type: 'powerup' | 'skin' | 'currency' | 'collectible';
  rarity: 'common' | 'rare' | 'epic' | 'legendary';
  quantity: number;
  description: string;
  icon: string;
  value?: number;
}

// 📊 게임 통계 타입
export interface GameStats {
  gamesPlayed: number;
  gamesWon: number;
  highestScore: number;
  totalEarnings: number;
  winStreak: number;
  favoriteGame: string;
}

// 📈 세부 게임 통계 타입
export interface GameStatsDetail {
  slot: {
    totalSpins: number;
    totalWinnings: number;
    biggestWin: number;
    jackpotHits: number;
  };
  rps: {
    totalGames: number;
    wins: number;
    currentStreak: number;
    bestStreak: number;
  };
  gacha: {
    totalPulls: number;
    legendaryPulls: number;
    totalValue: number;
  };
  crash: {
    totalGames: number;
    highestMultiplier: number;
    totalCashedOut: number;
    averageMultiplier: number;
  };
}

// 🔧 알림 인터페이스
export interface Notification {
  id: string;
  message: string;
  timestamp: number;
}

// 📱 앱 화면 타입
export type AppScreen = 
  | 'loading'
  | 'login'
  | 'signup'
  | 'admin-login'
  | 'home-dashboard'
  | 'game-dashboard'
  | 'shop'
  | 'inventory'
  | 'profile'
  | 'settings'
  | 'admin-panel'
  | 'event-mission-panel'
  | 'neon-slot'
  | 'rock-paper-scissors'
  | 'gacha-system'
  | 'neon-crash'
  | 'streaming';

// 🎯 이벤트 타입
export interface Event {
  id: string;
  title: string;
  description: string;
  type: string;
  status: string;
  startDate: Date;
  endDate: Date;
  rewards: Array<{ type: string; amount: number; name?: string }>;
  participants: number;
  maxParticipants?: number;
  requirements?: string[];
  icon: string;
}

// 🎯 미션 타입
export interface Mission {
  id: string;
  title: string;
  description: string;
  type: string;
  status: string;
  progress: number;
  maxProgress: number;
  rewards: Array<{ type: string; amount: number; name?: string }>;
  difficulty: string;
  icon: string;
  expiresAt?: Date;
  requirements?: string[];
}