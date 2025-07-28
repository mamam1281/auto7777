'use client';

import React from 'react';
import { useRouter, usePathname } from 'next/navigation';
import { Provider } from 'react-redux';
import { store } from '../store/store';
import AppHeader from '../components/AppHeader';
import BottomNavigationBar from '../components/BottomNavigationBar';
import { AuthProvider } from '../lib/auth';

export interface LayoutWrapperProps {
  children: React.ReactNode;
}

// 사이드바 없는 깔끔한 레이아웃 (AppHeader + BottomNav만 유지)
export default function LayoutWrapper({ children }: LayoutWrapperProps) {
  const router = useRouter();
  const pathname = usePathname();

  // 관리자 페이지 여부 체크
  const isAdminPage = pathname?.startsWith('/admin') || false;

  // 현재 경로에 따라 activeTab 설정
  const getActiveTab = () => {
    if (pathname === '/') return 'home';
    if (pathname === '/games') return 'game';
    if (pathname === '/shop') return 'shop';
    if (pathname === '/wallet') return 'wallet';
    if (pathname === '/profile') return 'profile';
    if (pathname === '/dashboard-new') return 'home';
    return 'home';
  };

  const [activeTab, setActiveTab] = React.useState(getActiveTab());

  // pathname이 변경될 때마다 activeTab 업데이트
  React.useEffect(() => {
    setActiveTab(getActiveTab());
    
    // 관리자 페이지일 때 body에 특별한 클래스 추가
    if (isAdminPage) {
      document.body.classList.add('admin-page');
      document.body.classList.remove('miniapp-page');
    } else {
      document.body.classList.add('miniapp-page');
      document.body.classList.remove('admin-page');
    }
  }, [pathname, isAdminPage]);

  const handleTabClick = (tabId: string, path: string) => {
    console.log(`🚀 바텀네비 클릭: ${tabId} -> ${path}`);
    setActiveTab(tabId);
    router.push(path);
  };

  const handleNotificationsClick = () => {
    console.log('Notifications clicked');
  };

  const handleSettingsClick = () => {
    console.log('Settings clicked');
  };

  return (
    <Provider store={store}>
      <AuthProvider>
        <div 
          className={isAdminPage ? "admin-container" : "miniapp-container"}
          style={isAdminPage ? { width: '100vw', maxWidth: 'none', margin: 0 } : {}}
        >
          {/* AppHeader - 관리자 페이지에서는 숨김 */}
          {!isAdminPage && (
            <AppHeader
              appName="CasinoClub"
              onNotificationsClick={handleNotificationsClick}
              onSettingsClick={handleSettingsClick}
              hasNotifications={false}
            />
          )}

          {/* 메인 콘텐츠 영역 */}
          <div 
            className={isAdminPage ? "admin-content" : "miniapp-content"}
            style={isAdminPage ? { width: '100%', maxWidth: 'none' } : {}}
          >
            {children}
          </div>
        </div>

        {/* BottomNavigationBar - 관리자 페이지에서는 숨김 */}
        {!isAdminPage && (
          <BottomNavigationBar
            activeTab={activeTab}
            onTabClick={handleTabClick}
          />
        )}
      </AuthProvider>
    </Provider>
  );
}
