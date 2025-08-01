'use client';

import { createContext, useContext, useEffect, useState } from 'react';
import { authAPI } from '../utils/api';

interface User {
  id: string;
  nickname: string;
  rank: 'VIP' | 'PREMIUM' | 'STANDARD';
  cyber_token_balance: number;
  created_at: string;
  site_id: string;
  phone_number: string;
  vip_tier: 'STANDARD' | 'VIP' | 'PREMIUM';
  battlepass_level: number;
  total_spent: number;
  cyber_tokens: number;
  regular_coins: number;
  premium_gems: number;
}

interface UserContextType {
  user: User | null;
  setUser: (user: User | null) => void;
  logout: () => void;
  login: (credentials: { site_id: string; password: string }) => Promise<void>;
  signup: (userData: {
    site_id: string;
    nickname: string;
    phone_number: string;
    password: string;
    invite_code: string;
  }) => Promise<void>;
  checkInviteCode: (code: string) => Promise<boolean>;
  refreshUser: () => Promise<void>;
  isLoading: boolean;
  isVIP: boolean;
  isPremium: boolean;
}

const UserContext = createContext<UserContextType | undefined>(undefined);

export function UserProvider({ children }: { children: React.ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [isLoading, setIsLoading] = useState<boolean>(true); // 초기값을 true로 설정

  // JWT 토큰 만료 확인 함수
  const isTokenExpired = (token: string): boolean => {
    try {
      const payload = JSON.parse(atob(token.split('.')[1]));
      const currentTime = Date.now() / 1000;
      const timeUntilExpiry = payload.exp - currentTime;

      console.log('🕐 토큰 만료 확인:', {
        현재시간: new Date(currentTime * 1000).toLocaleString(),
        만료시간: new Date(payload.exp * 1000).toLocaleString(),
        남은시간: `${Math.floor(timeUntilExpiry / 60)}분`,
        만료여부: payload.exp < currentTime
      });

      return payload.exp < currentTime;
    } catch (error) {
      console.error('❌ 토큰 파싱 오류:', error);
      return true; // 파싱 실패 시 만료된 것으로 간주
    }
  };

  // 자동 로그아웃 함수
  const autoLogout = () => {
    console.log('🔒 토큰 만료로 인한 자동 로그아웃');

    // 사용자에게 알림 (선택사항)
    if (typeof window !== 'undefined') {
      // 토스트나 알럿 대신 콘솔로만 표시 (UX 향상)
      console.log('💡 로그인 세션이 만료되어 다시 로그인해주세요.');
    }

    localStorage.removeItem('token');
    localStorage.removeItem('user');
    setUser(null);
    setIsLoading(false);
    // 로그인 페이지로 리다이렉트는 page.tsx에서 처리
  };

  // 토큰 만료 체크 및 자동 갱신
  useEffect(() => {
    const checkTokenExpiry = () => {
      // 사용자가 이미 로그인되어 있지 않은 경우에만 체크
      if (!user) {
        console.log('📝 사용자가 로그인되어 있지 않음 - 토큰 체크 건너뜀');
        return;
      }

      const token = localStorage.getItem('token');
      console.log('🔍 정기 토큰 만료 체크:', token ? '토큰 존재' : '토큰 없음');

      if (token) {
        const isExpired = isTokenExpired(token);
        console.log('⏰ 정기 토큰 만료 상태:', isExpired ? '만료됨' : '유효함');

        if (isExpired) {
          console.log('🔒 정기 체크에서 토큰 만료 발견 - 자동 로그아웃');
          autoLogout();
        }
      } else {
        console.log('� 토큰이 없어서 자동 로그아웃');
        autoLogout();
      }
    };

    // 로그인된 사용자에 대해서만 정기 체크 시작
    if (user) {
      // 5분마다 토큰 만료 체크
      const interval = setInterval(checkTokenExpiry, 5 * 60 * 1000);

      // 브라우저 포커스 시 토큰 재확인 (다른 탭에서 돌아왔을 때)
      const handleVisibilityChange = () => {
        if (!document.hidden) {
          console.log('🔍 브라우저 포커스 복귀 - 토큰 상태 재확인');
          checkTokenExpiry();
        }
      };

      // 윈도우 포커스 시에도 확인
      const handleFocus = () => {
        console.log('🔍 윈도우 포커스 - 토큰 상태 재확인');
        checkTokenExpiry();
      };

      document.addEventListener('visibilitychange', handleVisibilityChange);
      window.addEventListener('focus', handleFocus);

      return () => {
        clearInterval(interval);
        document.removeEventListener('visibilitychange', handleVisibilityChange);
        window.removeEventListener('focus', handleFocus);
      };
    }
  }, [user]); // user 상태가 변경될 때만 실행

  // 컴포넌트 마운트 시 토큰으로 사용자 정보 복원
  useEffect(() => {
    const initializeUser = async () => {
      console.log('🚀 initializeUser 함수 시작');

      // 클라이언트 환경에서만 실행
      if (typeof window === 'undefined') {
        console.log('🔧 서버 환경 - 초기화 건너뜀');
        setIsLoading(false);
        return;
      }

      try {
        const token = localStorage.getItem('token');
        console.log('🔑 토큰 확인:', token ? '존재함' : '없음');

        if (token) {
          // 토큰 만료 확인
          if (isTokenExpired(token)) {
            console.log('🔒 저장된 토큰이 만료됨 - 자동 로그아웃');
            autoLogout();
            return;
          }

          console.log('🔄 저장된 토큰으로 사용자 정보 복원 시도...');
          const userData = await authAPI.getCurrentUser();

          // API 응답을 User 타입으로 변환
          const formattedUser: User = {
            id: userData.data.id.toString(),
            nickname: userData.data.nickname || 'Unknown',
            rank: 'STANDARD' as 'VIP' | 'PREMIUM' | 'STANDARD',
            cyber_token_balance: userData.data.cyber_token_balance || 0,
            created_at: userData.data.created_at || new Date().toISOString(),
            site_id: userData.data.email || '',
            phone_number: userData.data.email || '',
            vip_tier: 'STANDARD',
            battlepass_level: 1,
            total_spent: 0,
            cyber_tokens: userData.data.cyber_token_balance || 0,
            regular_coins: userData.data.cyber_token_balance || 0,
            premium_gems: 0,
          };

          setUser(formattedUser);
          localStorage.setItem('user', JSON.stringify(formattedUser));
          console.log('✅ 사용자 정보 복원 성공:', formattedUser.nickname);
        } else {
          console.log('📝 저장된 토큰이 없음 - 로그인 필요');
        }
      } catch (error) {
        console.error('❌ 사용자 정보 복원 실패:', error);
        console.log('🗑️ 유효하지 않은 토큰 삭제');
        // 유효하지 않은 토큰 및 사용자 데이터 정리
        try {
          localStorage.removeItem('token');
          localStorage.removeItem('user');
        } catch (storageError) {
          console.error('localStorage 정리 실패:', storageError);
        }
        setUser(null);
      } finally {
        setIsLoading(false);
      }
    };

    initializeUser();
  }, []);

  const login = async (credentials: { site_id: string; password: string }) => {
    try {
      setIsLoading(true);
      // LoginRequest 형식에 맞게 변환
      const loginData = {
        email: credentials.site_id, // site_id를 email로 사용
        password: credentials.password
      };
      const response = await authAPI.login(loginData);

      console.log('🔍 로그인 API 응답:', response);
      console.log('🔍 응답 타입:', typeof response);
      console.log('🔍 응답 키들:', Object.keys(response));

      // 토큰 저장
      localStorage.setItem('token', response.data.access_token);

      // 사용자 정보가 없으면 별도로 조회
      if (!response.user) {
        console.log('📥 사용자 정보가 응답에 없음 - 별도 조회');
        const userData = await apiClient.getMe() as ApiUser;
        console.log('👤 별도 조회한 사용자 정보:', userData);

        const formattedUser: User = {
          id: userData.id.toString(),
          nickname: userData.nickname,
          rank: userData.vip_tier as 'VIP' | 'PREMIUM' | 'STANDARD',
          cyber_token_balance: userData.cyber_tokens,
          created_at: userData.created_at,
          site_id: userData.site_id,
          phone_number: userData.phone_number,
          vip_tier: userData.vip_tier,
          battlepass_level: userData.battlepass_level,
          total_spent: userData.total_spent,
          cyber_tokens: userData.cyber_tokens,
          regular_coins: userData.regular_coins,
          premium_gems: userData.premium_gems,
        };

        setUser(formattedUser);
        localStorage.setItem('user', JSON.stringify(formattedUser));
      } else {
        // 사용자 정보 변환 및 저장
        const formattedUser: User = {
          id: response.user.id,
          nickname: response.user.nickname,
          rank: response.user.vip_tier as 'VIP' | 'PREMIUM' | 'STANDARD',
          cyber_token_balance: response.user.cyber_tokens,
          created_at: response.user.created_at,
          site_id: response.user.site_id,
          phone_number: response.user.phone_number,
          vip_tier: response.user.vip_tier,
          battlepass_level: response.user.battlepass_level,
          total_spent: response.user.total_spent,
          cyber_tokens: response.user.cyber_tokens,
          regular_coins: response.user.regular_coins,
          premium_gems: response.user.premium_gems,
        };

        setUser(formattedUser);
        localStorage.setItem('user', JSON.stringify(formattedUser));
      }
    } catch (error) {
      console.error('로그인 실패:', error);
      throw error;
    } finally {
      setIsLoading(false);
    }
  };

  const signup = async (userData: {
    site_id: string;
    nickname: string;
    phone_number: string;
    password: string;
    invite_code: string;
  }) => {
    try {
      setIsLoading(true);
      console.log('🚀 회원가입 API 호출 시작:', userData);

      const response: any = await authAPI.register(userData);
      console.log('📦 회원가입 API 응답:', response);

      // 회원가입 응답 검증
      if (!response) {
        throw new Error('서버 응답이 없습니다.');
      }

      // 토큰이 있으면 자동 로그인 처리
      if (response.data?.access_token) {
        localStorage.setItem('token', response.data.access_token);
        console.log('✅ 회원가입 성공, 토큰 저장 완료');

        // 사용자 정보를 별도로 가져오기
        try {
          const response = await authAPI.getCurrentUser();
          const userData = response.data || response;
          console.log('👤 사용자 정보 가져오기 성공:', userData);

          const formattedUser: User = {
            id: userData.id,
            nickname: userData.nickname,
            rank: (userData.vip_tier || 'STANDARD') as 'VIP' | 'PREMIUM' | 'STANDARD',
            cyber_token_balance: userData.cyber_tokens || 0,
            created_at: userData.created_at,
            site_id: userData.site_id,
            phone_number: userData.phone_number,
            vip_tier: userData.vip_tier || 'STANDARD',
            battlepass_level: userData.battlepass_level || 1,
            total_spent: userData.total_spent || 0,
            cyber_tokens: userData.cyber_tokens || 0,
            regular_coins: userData.regular_coins || 0,
            premium_gems: userData.premium_gems || 0,
          };

          setUser(formattedUser);
          localStorage.setItem('user', JSON.stringify(formattedUser));
          console.log('✅ 회원가입 후 자동 로그인 성공:', formattedUser.nickname);
        } catch (userError) {
          console.error('⚠️ 사용자 정보 가져오기 실패:', userError);
          // 토큰은 있지만 사용자 정보 가져오기 실패 - 로그아웃
          localStorage.removeItem('token');
          throw new Error('회원가입은 성공했지만 로그인에 실패했습니다. 다시 로그인해주세요.');
        }
      } else {
        throw new Error('회원가입은 성공했지만 토큰을 받지 못했습니다.');
      }
    } catch (error) {
      console.error('회원가입 실패:', error);
      throw error;
    } finally {
      setIsLoading(false);
    }
  };

  const checkInviteCode = async (code: string): Promise<boolean> => {
    try {
      const response = await authAPI.checkInviteCode(code);
      return response.data.valid === true;
    } catch (error) {
      console.error('초대코드 확인 실패:', error);
      return false;
    }
  };

  const refreshUser = async () => {
    const token = localStorage.getItem('token');
    if (!token) return;

    try {
      setIsLoading(true);
      const userData = await apiClient.getMe() as ApiUser;

      const formattedUser: User = {
        id: userData.id,
        nickname: userData.nickname,
        rank: userData.vip_tier as 'VIP' | 'PREMIUM' | 'STANDARD',
        cyber_token_balance: userData.cyber_tokens,
        created_at: userData.created_at,
        site_id: userData.site_id,
        phone_number: userData.phone_number,
        vip_tier: userData.vip_tier,
        battlepass_level: userData.battlepass_level,
        total_spent: userData.total_spent,
        cyber_tokens: userData.cyber_tokens,
        regular_coins: userData.regular_coins,
        premium_gems: userData.premium_gems,
      }; setUser(formattedUser);
      localStorage.setItem('user', JSON.stringify(formattedUser));
    } catch (error) {
      console.error('사용자 정보 새로고침 실패:', error);
      logout(); // 토큰이 유효하지 않으면 로그아웃
    } finally {
      setIsLoading(false);
    }
  };

  const logout = () => {
    console.log('🚪 로그아웃 시작');
    console.log('🗑️ 현재 localStorage 상태:', {
      token: localStorage.getItem('token') ? '존재' : '없음',
      user: localStorage.getItem('user') ? '존재' : '없음'
    });

    setUser(null);
    // 🔒 모든 인증 관련 데이터 완전 삭제
    localStorage.removeItem('user');
    localStorage.removeItem('token');
    localStorage.removeItem('userNickname');
    localStorage.removeItem('splashSeen'); // 스플래시도 다시 보여주기

    console.log('🧹 localStorage 정리 완료:', {
      token: localStorage.getItem('token') ? '존재' : '없음',
      user: localStorage.getItem('user') ? '존재' : '없음'
    });

    // 🔄 페이지 새로고침으로 완전 초기화
    console.log('🔄 페이지 새로고침으로 완전 초기화');
    window.location.href = '/';
  };

  const handleSetUser = (newUser: User | null) => {
    setUser(newUser);
    if (newUser) {
      localStorage.setItem('user', JSON.stringify(newUser));
    } else {
      localStorage.removeItem('user');
    }
  };

  const isVIP = user?.rank === 'VIP';
  const isPremium = user?.rank === 'PREMIUM' || isVIP;

  return (
    <UserContext.Provider
      value={{
        user,
        setUser: handleSetUser,
        logout,
        login,
        signup,
        checkInviteCode,
        refreshUser,
        isLoading,
        isVIP,
        isPremium,
      }}
    >
      {children}
    </UserContext.Provider>
  );
}

export function useUser() {
  const context = useContext(UserContext);
  if (context === undefined) {
    throw new Error('useUser는 UserProvider 내에서 사용해야 합니다');
  }
  return context;
}

// 랭크별 접근 권한 체크 유틸리티
export function hasRankAccess(userRank: string, requiredRank: string): boolean {
  const rankHierarchy = {
    'VIP': 3,
    'PREMIUM': 2,
    'STANDARD': 1
  };

  const userLevel = rankHierarchy[userRank as keyof typeof rankHierarchy] || 1;
  const requiredLevel = rankHierarchy[requiredRank as keyof typeof rankHierarchy] || 1;

  return userLevel >= requiredLevel;
}
