'use client';

import { useState, useEffect } from 'react';
import Link from 'next/link';
import { useRouter } from 'next/navigation';

interface DashboardStats {
  totalUsers: number;
  activeUsers: number;
  totalRewards: number;
  todayActivities: number;
}

interface RecentActivity {
  id: number;
  user_id: number;
  user_nickname: string;
  activity_type: string;
  details: string;
  timestamp: string;
}

const AdminDashboard = () => {
  const [stats, setStats] = useState<DashboardStats>({
    totalUsers: 0,
    activeUsers: 0,
    totalRewards: 0,
    todayActivities: 0,
  });
  
  const [activities, setActivities] = useState<RecentActivity[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const router = useRouter();

  useEffect(() => {
    // 관리자 권한 체크 (간단한 예시 - 실제로는 더 복잡한 인증 필요)
    const checkAdminAuth = async () => {
      const token = localStorage.getItem('token');
      if (!token) {
        router.push('/auth');
        return;
      }
    };

    checkAdminAuth();
    fetchDashboardData();
  }, [router]);

  const fetchDashboardData = async () => {
    try {
      setLoading(true);
      setError(null);

      // 통계 데이터 가져오기
      const [usersRes, activitiesRes] = await Promise.all([
        fetch('http://localhost:8000/api/admin/users', {
          headers: {
            'Authorization': `Bearer ${localStorage.getItem('token')}`,
          },
        }),
        fetch('http://localhost:8000/api/admin/activities?limit=10', {
          headers: {
            'Authorization': `Bearer ${localStorage.getItem('token')}`,
          },
        }),
      ]);

      if (!usersRes.ok || !activitiesRes.ok) {
        throw new Error('Failed to fetch data');
      }

      const users = await usersRes.json();
      const activitiesData = await activitiesRes.json();

      // 통계 계산
      const now = new Date();
      const today = new Date(now.getFullYear(), now.getMonth(), now.getDate());
      
      const activeUsersCount = users.filter((user: any) => {
        const lastActive = new Date(user.created_at);
        return (now.getTime() - lastActive.getTime()) < 7 * 24 * 60 * 60 * 1000; // 7일 이내 활동
      }).length;

      const todayActivitiesCount = activitiesData.filter((activity: any) => {
        const activityDate = new Date(activity.timestamp);
        return activityDate >= today;
      }).length;

      setStats({
        totalUsers: users.length,
        activeUsers: activeUsersCount,
        totalRewards: users.reduce((sum: number, user: any) => sum + (user.cyber_token_balance || 0), 0),
        todayActivities: todayActivitiesCount,
      });

      setActivities(activitiesData.slice(0, 5));
    } catch (err) {
      console.error('Error fetching dashboard data:', err);
      setError('Failed to load dashboard data');
    } finally {
      setLoading(false);
    }
  };

  const formatTime = (timestamp: string) => {
    const date = new Date(timestamp);
    const now = new Date();
    const diff = now.getTime() - date.getTime();
    
    if (diff < 60000) return '방금 전';
    if (diff < 3600000) return `${Math.floor(diff / 60000)}분 전`;
    if (diff < 86400000) return `${Math.floor(diff / 3600000)}시간 전`;
    return date.toLocaleDateString();
  };

  const getActivityIcon = (type: string) => {
    switch (type) {
      case 'LOGIN': return '🔐';
      case 'GAME_PLAY': return '🎮';
      case 'REWARD_RECEIVED': return '🎁';
      case 'SIGNUP': return '👤';
      case 'PURCHASE': return '💳';
      default: return '📋';
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-900 flex items-center justify-center">
        <div className="text-white text-xl">Loading...</div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen bg-gray-900 flex items-center justify-center">
        <div className="text-red-500 text-xl">{error}</div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-900 text-white">
      {/* Compact Header */}
      <div className="bg-gray-800 border-b border-gray-700 px-6 py-3 flex items-center justify-between">
        <div>
          <h1 className="text-xl font-bold">관리자 대시보드</h1>
          <p className="text-gray-400 text-sm">시스템 현황 및 사용자 관리</p>
        </div>
        <div className="text-right text-sm text-gray-400">
          {new Date().toLocaleDateString('ko-KR')} {new Date().toLocaleTimeString('ko-KR')}
        </div>
      </div>

      {/* Compact Stats Grid */}
      <div className="p-4 grid grid-cols-4 gap-4">
        <div className="bg-gray-800 rounded p-3 border border-gray-700">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-gray-400 text-xs">전체 사용자</p>
              <p className="text-xl font-bold mt-1">{stats.totalUsers.toLocaleString()}</p>
            </div>
            <span className="text-2xl">👥</span>
          </div>
        </div>

        <div className="bg-gray-800 rounded p-3 border border-gray-700">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-gray-400 text-xs">활성 사용자</p>
              <p className="text-xl font-bold mt-1">{stats.activeUsers.toLocaleString()}</p>
            </div>
            <span className="text-2xl">📈</span>
          </div>
        </div>

        <div className="bg-gray-800 rounded p-3 border border-gray-700">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-gray-400 text-xs">총 토큰</p>
              <p className="text-xl font-bold mt-1">{stats.totalRewards.toLocaleString()}</p>
            </div>
            <span className="text-2xl">🏆</span>
          </div>
        </div>

        <div className="bg-gray-800 rounded p-3 border border-gray-700">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-gray-400 text-xs">오늘 활동</p>
              <p className="text-xl font-bold mt-1">{stats.todayActivities.toLocaleString()}</p>
            </div>
            <span className="text-2xl">⚡</span>
          </div>
        </div>
      </div>

      {/* Main Content Grid */}
      <div className="px-4 pb-4 grid grid-cols-3 gap-4 h-[calc(100vh-180px)]">
        {/* Quick Actions - Compact List */}
        <div className="bg-gray-800 rounded border border-gray-700 p-4">
          <h2 className="text-lg font-bold mb-3">빠른 작업</h2>
          <div className="space-y-2">
            <Link href="/admin/users" className="flex items-center p-2 hover:bg-gray-700 rounded transition-colors cursor-pointer">
              <span className="text-lg mr-3">👥</span>
              <div className="flex-1">
                <p className="font-medium text-sm">사용자 관리</p>
                <p className="text-xs text-gray-400">사용자 목록 및 상세 정보</p>
              </div>
            </Link>

            <Link href="/admin/rewards" className="flex items-center p-2 hover:bg-gray-700 rounded transition-colors cursor-pointer">
              <span className="text-lg mr-3">🎁</span>
              <div className="flex-1">
                <p className="font-medium text-sm">보상 지급</p>
                <p className="text-xs text-gray-400">사용자에게 토큰 지급</p>
              </div>
            </Link>

            <Link href="/admin/logs" className="flex items-center p-2 hover:bg-gray-700 rounded transition-colors cursor-pointer">
              <span className="text-lg mr-3">📊</span>
              <div className="flex-1">
                <p className="font-medium text-sm">활동 로그</p>
                <p className="text-xs text-gray-400">전체 활동 기록 조회</p>
              </div>
            </Link>
          </div>
        </div>

        {/* Recent Activities - Compact Table */}
        <div className="col-span-2 bg-gray-800 rounded border border-gray-700 p-4">
          <h2 className="text-lg font-bold mb-3">최근 활동</h2>
          <div className="overflow-y-auto h-[calc(100%-40px)]">
            <table className="w-full text-sm">
              <thead className="sticky top-0 bg-gray-700">
                <tr>
                  <th className="px-3 py-2 text-left text-xs font-medium text-gray-300">사용자</th>
                  <th className="px-3 py-2 text-left text-xs font-medium text-gray-300">활동</th>
                  <th className="px-3 py-2 text-left text-xs font-medium text-gray-300">상세</th>
                  <th className="px-3 py-2 text-left text-xs font-medium text-gray-300">시간</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-700">
                {activities.map((activity) => (
                  <tr key={activity.id} className="hover:bg-gray-700">
                    <td className="px-3 py-2">
                      <Link href={`/admin/users/${activity.user_id}`} className="text-blue-400 hover:text-blue-300 text-sm">
                        {activity.user_nickname}
                      </Link>
                    </td>
                    <td className="px-3 py-2">
                      <span className="inline-flex items-center text-sm">
                        <span className="mr-2">{getActivityIcon(activity.activity_type)}</span>
                        {activity.activity_type}
                      </span>
                    </td>
                    <td className="px-3 py-2 text-sm text-gray-400 max-w-xs truncate">
                      {activity.details}
                    </td>
                    <td className="px-3 py-2 text-sm text-gray-400">
                      {formatTime(activity.timestamp)}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>
  );
};

export default AdminDashboard;
