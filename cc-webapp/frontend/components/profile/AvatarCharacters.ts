export const AVATAR_CHARACTERS = {
  DIAMOND: {
    icon: '💎',
    name: '다이아몬드',
    gradient: 'linear-gradient(135deg, #E3F2FD 0%, #BBDEFB 50%, #90CAF9 100%)',
    shadow: 'rgba(144, 202, 249, 0.4)'
  },
  GOLD: {
    icon: '👑',
    name: '골드',
    gradient: 'linear-gradient(135deg, #FFF8E1 0%, #FFECB3 50%, #FFD54F 100%)',
    shadow: 'rgba(255, 213, 79, 0.4)'
  },
  SILVER: {
    icon: '⭐',
    name: '실버',
    gradient: 'linear-gradient(135deg, #F5F5F5 0%, #E0E0E0 50%, #BDBDBD 100%)',
    shadow: 'rgba(189, 189, 189, 0.4)'
  },
  RUBY: {
    icon: '💖',
    name: '루비',
    gradient: 'linear-gradient(135deg, #FCE4EC 0%, #F8BBD9 50%, #E91E63 100%)',
    shadow: 'rgba(233, 30, 99, 0.4)'
  },
  EMERALD: {
    icon: '💚',
    name: '에메랄드',
    gradient: 'linear-gradient(135deg, #E8F5E8 0%, #C8E6C9 50%, #4CAF50 100%)',
    shadow: 'rgba(76, 175, 80, 0.4)'
  }
} as const;

export type AvatarCharacterType = keyof typeof AVATAR_CHARACTERS;
