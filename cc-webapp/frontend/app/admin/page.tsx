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
      {/* Header */}
      <div className="bg-gray-800 border-b border-gray-700 p-6">
        <h1 className="text-3xl font-bold">관리자 대시보드</h1>
        <p className="text-gray-400 mt-2">시스템 현황 및 사용자 관리</p>
      </div>

      {/* Stats Grid */}
      <div className="p-6 grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <div className="bg-gray-800 rounded-lg p-6 border border-gray-700">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-gray-400 text-sm">전체 사용자</p>
              <p className="text-3xl font-bold mt-2">{stats.totalUsers.toLocaleString()}</p>
            </div>
            <span className="text-4xl">👥</span>
          </div>
        </div>

        <div className="bg-gray-800 rounded-lg p-6 border border-gray-700">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-gray-400 text-sm">활성 사용자</p>
              <p className="text-3xl font-bold mt-2">{stats.activeUsers.toLocaleString()}</p>
            </div>
            <span className="text-4xl">📈</span>
          </div>
        </div>

        <div className="bg-gray-800 rounded-lg p-6 border border-gray-700">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-gray-400 text-sm">총 토큰</p>
              <p className="text-3xl font-bold mt-2">{stats.totalRewards.toLocaleString()}</p>
            </div>
            <span className="text-4xl">🏆</span>
          </div>
        </div>

        <div className="bg-gray-800 rounded-lg p-6 border border-gray-700">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-gray-400 text-sm">오늘 활동</p>
              <p className="text-3xl font-bold mt-2">{stats.todayActivities.toLocaleString()}</p>
            </div>
            <span className="text-4xl">⚡</span>
          </div>
        </div>
      </div>

      {/* Quick Actions */}
      <div className="px-6 mb-6">
        <h2 className="text-xl font-bold mb-4">빠른 작업</h2>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <Link href="/admin/users" className="bg-gray-800 rounded-lg p-4 border border-gray-700 hover:border-blue-500 transition-colors cursor-pointer">
            <div className="flex items-center space-x-3">
              <span className="text-3xl">👥</span>
              <div>
                <p className="font-semibold">사용자 관리</p>
                <p className="text-sm text-gray-400">사용자 목록 및 상세 정보</p>
              </div>
            </div>
          </Link>

          <Link href="/admin/rewards" className="bg-gray-800 rounded-lg p-4 border border-gray-700 hover:border-yellow-500 transition-colors cursor-pointer">
            <div className="flex items-center space-x-3">
              <span className="text-3xl">🎁</span>
              <div>
                <p className="font-semibold">보상 지급</p>
                <p className="text-sm text-gray-400">사용자에게 토큰 지급</p>
              </div>
            </div>
          </Link>

          <Link href="/admin/activities" className="bg-gray-800 rounded-lg p-4 border border-gray-700 hover:border-purple-500 transition-colors cursor-pointer">
            <div className="flex items-center space-x-3">
              <span className="text-3xl">📊</span>
              <div>
                <p className="font-semibold">활동 로그</p>
                <p className="text-sm text-gray-400">전체 활동 기록 조회</p>
              </div>
            </div>
          </Link>
        </div>
      </div>

      {/* Recent Activities */}
      <div className="px-6 pb-6">
        <h2 className="text-xl font-bold mb-4">최근 활동</h2>
        <div className="bg-gray-800 rounded-lg border border-gray-700 overflow-hidden">
          <table className="w-full">
            <thead className="bg-gray-700">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-300 uppercase tracking-wider">
                  사용자
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-300 uppercase tracking-wider">
                  활동 유형
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-300 uppercase tracking-wider">
                  상세 내용
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-300 uppercase tracking-wider">
                  시간
                </th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-700">
              {activities.map((activity) => (
                <tr key={activity.id} className="hover:bg-gray-700 transition-colors">
                  <td className="px-6 py-4 whitespace-nowrap">
                    <Link href={`/admin/users/${activity.user_id}`} className="text-blue-400 hover:text-blue-300">
                      {activity.user_nickname}
                    </Link>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <span className="inline-flex items-center">
                      <span className="mr-2">{getActivityIcon(activity.activity_type)}</span>
                      {activity.activity_type}
                    </span>
                  </td>
                  <td className="px-6 py-4 text-sm text-gray-400">
                    {activity.details}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-400">
                    {formatTime(activity.timestamp)}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};

export default AdminDashboard;
