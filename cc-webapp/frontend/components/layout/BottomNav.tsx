'use client';

import React from 'react';
import { motion } from 'framer-motion';
import { Home, User, Gift, ShoppingBag, MessageCircle } from 'lucide-react';
import { useRouter, usePathname } from 'next/navigation';
import { openGamePopup } from '../../utils/gamePopup';

export default function BottomNav() {
  const router = useRouter();
  const pathname = usePathname();
  
  const navItems = [
    { icon: Home, label: '홈', path: '/home' },
    { icon: Gift, label: '보상', path: '/rewards' },
    { icon: ShoppingBag, label: '상점', path: '/shop' },
    { icon: MessageCircle, label: '채팅', path: '/chat' },
    { icon: User, label: '프로필', path: '/profile' },
  ];
  
  const isActive = (path: string) => {
    if (path === '/home' && pathname === '/') return true;
    return pathname?.startsWith(path);
  };

  return (
    <motion.nav 
      initial={{ y: 20, opacity: 0 }}
      animate={{ y: 0, opacity: 1 }}
      className="fixed bottom-0 left-0 right-0 h-16 bg-card border-t border-border flex justify-around items-center px-2"
    >
      {navItems.map(item => {
        const active = isActive(item.path);
        const Icon = item.icon;
        
        return (
          <button
            key={item.path}
            onClick={() => {
              // 프로필 메뉴는 팝업으로 열기
              if (item.path === '/profile') {
                openGamePopup('profile');
              } else {
                router.push(item.path);
              }
            }}
            className={`flex flex-col items-center justify-center w-16 h-full relative ${
              active ? 'text-primary' : 'text-muted-foreground'
            }`}
          >
            {active && (
              <motion.div
                layoutId="bottomNavIndicator"
                className="absolute top-0 left-0 right-0 mx-auto w-12 h-1 bg-primary rounded-b-md"
              />
            )}
            <Icon className={`w-5 h-5 ${active ? 'text-primary' : 'text-muted-foreground'}`} />
            <span className="text-xs mt-1">{item.label}</span>
          </button>
        );
      })}
    </motion.nav>
  );
}
