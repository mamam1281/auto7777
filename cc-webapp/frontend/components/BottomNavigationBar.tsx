import React from 'react';
import { Home, Gamepad, Store, Wallet, User } from 'lucide-react';
import { motion } from 'framer-motion';

export interface NavItemData {
  id: string;
  label: string;
  icon: React.ElementType;
  path: string;
}

export const navItems: NavItemData[] = [
  { id: 'home', label: '홈', icon: Home, path: '/' },
  { id: 'game', label: '게임', icon: Gamepad, path: '/games' },
  { id: 'shop', label: '상점', icon: Store, path: '/shop' },
  { id: 'wallet', label: '월렛', icon: Wallet, path: '/wallet' },
  { id: 'profile', label: '프로필', icon: User, path: '/profile' },
];

export interface BottomNavigationBarProps {
  activeTab: string;
  onTabClick: (tabId: string, path: string) => void;
}

const BottomNavigationBar: React.FC<BottomNavigationBarProps> = ({
  activeTab,
  onTabClick,
}) => {
  const iconSize = 24; // Corresponds to --icon-lg
  // Design Tokens:
  // Spacing: --spacing-0-5 (4px), --spacing-1 (8px), --spacing-1-5 (12px), --spacing-2 (16px)
  // Colors: text-purple-primary, bg-purple-primary/10, text-text-secondary, hover:text-foreground, hover:bg-white/5
  // Font size: text-xs (12px)
  return (
    <nav
      className="fixed bottom-0 left-0 right-0 z-50 h-20 w-full border-t flex justify-center"
      style={{
        position: 'fixed !important' as any,
        bottom: '0 !important' as any,
        left: '0 !important' as any,
        right: '0 !important' as any,
        width: '100vw !important' as any,
        height: '80px !important' as any,
        background: 'linear-gradient(135deg, rgba(26, 26, 46, 0.95) 0%, rgba(22, 33, 62, 0.95) 25%, rgba(26, 26, 46, 0.95) 50%, rgba(22, 33, 62, 0.95) 75%, rgba(26, 26, 46, 0.95) 100%) !important' as any,
        backdropFilter: 'blur(10px) !important' as any,
        WebkitBackdropFilter: 'blur(10px) !important' as any,
        borderTop: '1px solid rgba(139, 92, 246, 0.2) !important' as any,
        zIndex: '999 !important' as any,
        display: 'flex !important' as any,
        justifyContent: 'center !important' as any,
        alignItems: 'center !important' as any,
        margin: '0 !important' as any,
        padding: '0 !important' as any,
        boxSizing: 'border-box !important' as any,
        maxWidth: 'none !important' as any,
        transform: 'none !important' as any,
        inset: 'auto 0 0 0 !important' as any,
      }}
    >
      <div 
        className="w-full flex items-center justify-around" 
        style={{ 
          height: '100%', 
          padding: 0, 
          margin: 0,
          maxWidth: '420px',
          width: '100%',
          boxSizing: 'border-box'
        }}
      >
      {navItems.map((item) => {
        const isActive = activeTab === item.id;
        const IconComponent = item.icon;        return (
          <motion.button
            key={item.id}
            onClick={() => {
              console.log('BottomNav onClick triggered:', item.id, item.path);
              onTabClick(item.id, item.path);
            }}            className={`
              flex flex-col items-center justify-center gap-0.5 rounded-xl min-w-14 transition-all duration-300 relative
              ${isActive
                ? 'bg-gradient-to-br from-purple-500/20 to-indigo-600/20 shadow-md shadow-purple-500/10 border border-purple-400/25' 
                : 'hover:bg-gradient-to-br hover:from-white/5 hover:to-purple-500/5 hover:border hover:border-purple-500/15'
              }
            `}
            style={{
              color: isActive ? '#ffffff' : '#e5e7eb',
              padding: '8px 16px',
              margin: 0,
              boxSizing: 'border-box',
            }}
            aria-current={isActive ? 'page' : undefined}
            aria-label={`${item.label} 탭`}
            whileTap={{ scale: 0.95 }}
            whileHover={{ scale: 1.02, y: -1 }}
            transition={{ 
              type: "spring", 
              stiffness: 300, 
              damping: 25,
              duration: 0.2
            }}
          >
            {/* 활성 상태일 때 글로우 효과 */}
            {isActive && (
              <motion.div
                className="absolute inset-0 bg-gradient-to-br from-purple-400/20 to-indigo-500/20 rounded-xl"
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                transition={{ duration: 0.3 }}
              />
            )}
            <IconComponent 
              size={iconSize} 
              className={`mb-0.5 transition-all duration-300 relative z-10 ${
                isActive ? 'text-purple-300 drop-shadow-sm' : 'text-gray-300 group-hover:text-purple-200'
              }`} 
            />            <span className={`font-medium transition-all duration-300 relative z-10 ${
              isActive ? 'text-purple-200' : 'text-gray-300 group-hover:text-white'
            }`}
            style={{ fontSize: '10px' }}
            >
              {item.label}
            </span>
          </motion.button>
        );
      })}
      </div>
    </nav>
  );
};

export default BottomNavigationBar;
