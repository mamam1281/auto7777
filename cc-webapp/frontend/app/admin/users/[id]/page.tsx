'use client';

import { useState, useEffect } from 'react';
import Link from 'next/link';
import { useParams } from 'next/navigation';
import { motion } from 'framer-motion';
import { 
  ChevronLeft, 
  Gift, 
  User, 
  Calendar, 
  Award,
  Mail,
  Shield,
  Activity,
  Coins,
  Clock,
  RefreshCw,
  X
} from 'lucide-react';

interface User {
  id: number;
  nickname: string;
  email: string;
  cyber_token_balance?: number;
  current_rank?: string;
  vip_tier?: string;
  battlepass_level?: number;
  total_spent?: number;
  is_verified?: boolean;
  is_active?: boolean;
  created_at: string;
  last_login?: string;
  tokens?: {
    coins: number;
    gems: number;
    cyber_tokens: number;
    streak: number;
  };
  total_games?: number;
  win_rate?: number;
}

interface ActivityLog {
  id: number;
  user_id: number;
  activity_type: string;
  details: string;
  ip_address: string;
  timestamp: string;
}

interface RewardForm {
  reward_type: string;
  amount: number;
  reason: string;
}

const UserDetailPage = () => {
  const params = useParams();
  const userId = params?.id as string;
  
  const [user, setUser] = useState<User | null>(null);
  const [activities, setActivities] = useState<ActivityLog[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [showRewardModal, setShowRewardModal] = useState(false);
  const [rewardForm, setRewardForm] = useState<RewardForm>({
    reward_type: 'BONUS',
    amount: 0,
    reason: ''
  });

  const fetchUserDetail = async () => {
    try {
      setLoading(true);
      setError(null);

      const response = await fetch(`http://localhost:8000/api/admin/users/${userId}`, {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`,
        },
      });

      if (!response.ok) {
        throw new Error('Failed to fetch user details');
      }

      const data = await response.json();
      setUser(data);

      // Mock activities for demonstration
      setActivities([
        {
          id: 1,
          user_id: parseInt(userId),
          activity_type: 'LOGIN',
          details: '정상 로그인',
          ip_address: '192.168.1.100',
          timestamp: new Date().toISOString()
        },
        {
          id: 2,
          user_id: parseInt(userId),
          activity_type: 'GAME_PLAY',
          details: '슬롯머신 게임 플레이',
          ip_address: '192.168.1.100',
          timestamp: new Date(Date.now() - 3600000).toISOString()
        },
        {
          id: 3,
          user_id: parseInt(userId),
          activity_type: 'REWARD_RECEIVED',
          details: '데일리 보너스 수령',
          ip_address: '192.168.1.100',
          timestamp: new Date(Date.now() - 7200000).toISOString()
        }
      ]);

    } catch (err) {
      console.error('Error fetching user details:', err);
      setError('Failed to load user details');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (userId) {
      fetchUserDetail();
    }
  }, [userId]);

  const refreshUserData = () => {
    setLoading(true);
    fetchUserDetail();
  };

  const handleGiveReward = async () => {
    if (!rewardForm.amount || rewardForm.amount <= 0) {
      alert('올바른 보상 수량을 입력해주세요.');
      return;
    }

    if (!rewardForm.reason.trim()) {
      alert('보상 지급 사유를 입력해주세요.');
      return;
    }

    try {
      const response = await fetch(`http://localhost:8000/api/admin/users/${userId}/give-reward`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('token')}`,
        },
        body: JSON.stringify({
          user_id: parseInt(userId),
          reward_type: rewardForm.reward_type,
          amount: rewardForm.amount,
          reason: rewardForm.reason,
          admin_id: 1,
        }),
      });

      if (!response.ok) {
        throw new Error('Failed to give reward');
      }

      await fetchUserDetail();
      setShowRewardModal(false);
      setRewardForm({ reward_type: 'BONUS', amount: 0, reason: '' });
      alert('보상이 성공적으로 지급되었습니다.');
    } catch (err) {
      console.error('Error giving reward:', err);
      alert('보상 지급에 실패했습니다.');
    }
  };

  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    return date.toLocaleDateString('ko-KR', {
      year: 'numeric',
      month: 'long',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    });
  };

  const getRankColor = (rank: string) => {
    switch (rank) {
      case 'VIP': return 'text-yellow-400 bg-yellow-400/10 border-yellow-400/20';
      case 'PREMIUM': return 'text-purple-400 bg-purple-400/10 border-purple-400/20';
      case 'SUPER_ADMIN': return 'text-red-400 bg-red-400/10 border-red-400/20';
      case 'ADMIN': return 'text-blue-400 bg-blue-400/10 border-blue-400/20';
      case 'BASIC': return 'text-green-400 bg-green-400/10 border-green-400/20';
      default: return 'text-gray-400 bg-gray-400/10 border-gray-400/20';
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-900 flex items-center justify-center">
        <div className="text-white text-xl flex items-center">
          <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-white mr-3"></div>
          사용자 정보를 불러오는 중...
        </div>
      </div>
    );
  }

  if (error || !user) {
    return (
      <div className="min-h-screen bg-gray-900 flex items-center justify-center">
        <div className="text-center">
          <div className="text-red-500 text-xl mb-4">{error || '사용자를 찾을 수 없습니다'}</div>
          <Link href="/admin/users" className="text-blue-400 hover:text-blue-300">
            ← 사용자 목록으로 돌아가기
          </Link>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-900 text-white">
      {/* Compact Header */}
      <div className="bg-gray-800 border-b border-gray-700 px-4 py-2">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-3">
            <Link href="/admin/users" className="text-gray-400 hover:text-white transition-colors">
              <ChevronLeft className="w-5 h-5" />
            </Link>
            <div>
              <h1 className="text-lg font-bold">{user.nickname} 상세</h1>
              <p className="text-gray-400 text-xs">사용자 ID: {user.id} | 가입일: {new Date(user.created_at).toLocaleDateString('ko-KR')}</p>
            </div>
          </div>
          <div className="flex items-center space-x-2">
            <button
              onClick={() => setShowRewardModal(true)}
              className="bg-blue-600 hover:bg-blue-700 px-3 py-1 rounded text-sm transition-colors flex items-center"
            >
              <Gift className="w-4 h-4 mr-1" />
              보상 지급
            </button>
            <button
              onClick={refreshUserData}
              className="bg-gray-600 hover:bg-gray-500 px-3 py-1 rounded text-sm transition-colors"
            >
              <RefreshCw className="w-4 h-4" />
            </button>
          </div>
        </div>
      </div>

      {/* Compact User Info Grid */}
      <div className="p-4 space-y-4">
        {/* 3-Column Layout */}
        <div className="grid grid-cols-3 gap-4">
          {/* Left: Basic Info */}
          <div className="bg-gray-800 rounded border border-gray-700">
            <div className="bg-gray-700 px-3 py-2 border-b border-gray-600">
              <h3 className="text-sm font-medium text-white flex items-center">
                <User className="w-4 h-4 mr-2" />
                기본 정보
              </h3>
            </div>
            <div className="p-3 space-y-3">
              <div className="flex justify-between text-sm">
                <span className="text-gray-400">닉네임</span>
                <span className="text-white font-medium">{user.nickname}</span>
              </div>
              <div className="flex justify-between text-sm">
                <span className="text-gray-400">이메일</span>
                <span className="text-white">{user.email}</span>
              </div>
              <div className="flex justify-between text-sm">
                <span className="text-gray-400">VIP 등급</span>
                <span className={`font-medium ${
                  user.vip_tier === 'PREMIUM' ? 'text-purple-400' :
                  user.vip_tier === 'VIP' ? 'text-yellow-400' : 'text-gray-300'
                }`}>
                  {user.vip_tier}
                </span>
              </div>
              <div className="flex justify-between text-sm">
                <span className="text-gray-400">배틀패스 레벨</span>
                <span className="text-white">{user.battlepass_level}</span>
              </div>
              <div className="flex justify-between text-sm">
                <span className="text-gray-400">총 지출</span>
                <span className="text-green-400 font-medium">{user.total_spent?.toLocaleString()}원</span>
              </div>
            </div>
          </div>

          {/* Center: Token Balance */}
          <div className="bg-gray-800 rounded border border-gray-700">
            <div className="bg-gray-700 px-3 py-2 border-b border-gray-600">
              <h3 className="text-sm font-medium text-white flex items-center">
                <Coins className="w-4 h-4 mr-2" />
                토큰 보유량
              </h3>
            </div>
            <div className="p-3 space-y-3">
              <div className="flex justify-between text-sm">
                <span className="text-gray-400">일반 코인</span>
                <span className="text-yellow-400 font-bold">{user.tokens?.coins?.toLocaleString() || 0}</span>
              </div>
              <div className="flex justify-between text-sm">
                <span className="text-gray-400">프리미엄 젬</span>
                <span className="text-purple-400 font-bold">{user.tokens?.gems?.toLocaleString() || 0}</span>
              </div>
              <div className="flex justify-between text-sm">
                <span className="text-gray-400">사이버 토큰</span>
                <span className="text-blue-400 font-bold">{user.tokens?.cyber_tokens?.toLocaleString() || 0}</span>
              </div>
              <div className="flex justify-between text-sm">
                <span className="text-gray-400">현재 스트릭</span>
                <span className="text-orange-400 font-bold">{user.tokens?.streak || 0}일</span>
              </div>
            </div>
          </div>

          {/* Right: Activity Summary */}
          <div className="bg-gray-800 rounded border border-gray-700">
            <div className="bg-gray-700 px-3 py-2 border-b border-gray-600">
              <h3 className="text-sm font-medium text-white flex items-center">
                <Activity className="w-4 h-4 mr-2" />
                활동 요약
              </h3>
            </div>
            <div className="p-3 space-y-3">
              <div className="flex justify-between text-sm">
                <span className="text-gray-400">최근 접속</span>
                <span className="text-white">{formatDate(user.last_login)}</span>
              </div>
              <div className="flex justify-between text-sm">
                <span className="text-gray-400">총 게임</span>
                <span className="text-blue-400">{user.total_games || 0}회</span>
              </div>
              <div className="flex justify-between text-sm">
                <span className="text-gray-400">승률</span>
                <span className="text-green-400">{user.win_rate || 0}%</span>
              </div>
              <div className="flex justify-between text-sm">
                <span className="text-gray-400">가입일</span>
                <span className="text-gray-300">{formatDate(user.created_at)}</span>
              </div>
            </div>
          </div>
        </div>

        {/* Activity Logs Table */}
        <div className="bg-gray-800 rounded border border-gray-700">
          <div className="bg-gray-700 px-3 py-2 border-b border-gray-600 flex items-center justify-between">
            <h3 className="text-sm font-medium text-white flex items-center">
              <Clock className="w-4 h-4 mr-2" />
              최근 활동 ({activities.length})
            </h3>
            <Link 
              href={`/admin/logs?user=${user.id}`}
              className="text-blue-400 hover:text-blue-300 text-xs"
            >
              전체 보기 →
            </Link>
          </div>
          
          <div className="max-h-80 overflow-auto">
            <table className="w-full text-sm">
              <thead className="bg-gray-700 sticky top-0">
                <tr>
                  <th className="px-3 py-2 text-left text-xs font-medium text-gray-300">시간</th>
                  <th className="px-3 py-2 text-left text-xs font-medium text-gray-300">활동</th>
                  <th className="px-3 py-2 text-left text-xs font-medium text-gray-300">상세</th>
                  <th className="px-3 py-2 text-left text-xs font-medium text-gray-300">IP</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-700">
                {activities.slice(0, 10).map((activity) => (
                  <tr key={activity.id} className="hover:bg-gray-700 transition-colors">
                    <td className="px-3 py-2 text-gray-400 text-xs whitespace-nowrap">
                      {new Date(activity.timestamp).toLocaleString('ko-KR', { 
                        month: '2-digit', 
                        day: '2-digit', 
                        hour: '2-digit', 
                        minute: '2-digit' 
                      })}
                    </td>
                    <td className="px-3 py-2 whitespace-nowrap">
                      <span className={`px-2 py-1 rounded text-xs font-medium ${
                        activity.activity_type === 'LOGIN' ? 'bg-green-900 text-green-300' :
                        activity.activity_type.startsWith('GAME_') ? 'bg-blue-900 text-blue-300' :
                        activity.activity_type === 'PURCHASE' ? 'bg-purple-900 text-purple-300' :
                        'bg-gray-700 text-gray-300'
                      }`}>
                        {activity.activity_type}
                      </span>
                    </td>
                    <td className="px-3 py-2 text-gray-300 max-w-xs">
                      <div className="truncate">{activity.details}</div>
                    </td>
                    <td className="px-3 py-2 text-gray-400 font-mono text-xs">
                      {activity.ip_address}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
            <User className="w-5 h-5 mr-2" />
            기본 정보
          </h2>
          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <span className="text-gray-400">사용자 ID</span>
              <span className="font-mono text-blue-400">{user.id}</span>
            </div>
            <div className="flex items-center justify-between">
              <span className="text-gray-400">닉네임</span>
              <span className="font-semibold">{user.nickname}</span>
            </div>
            <div className="flex items-center justify-between">
              <span className="text-gray-400 flex items-center">
                <Mail className="w-4 h-4 mr-1" />
                이메일
              </span>
              <span className="text-sm">{user.email}</span>
            </div>
            <div className="flex items-center justify-between">
              <span className="text-gray-400 flex items-center">
                <Calendar className="w-4 h-4 mr-1" />
                가입일
              </span>
              <span className="text-sm">{formatDate(user.created_at)}</span>
            </div>
          </div>
        </motion.div>

        {/* Token & Rank Info */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.1 }}
          className="bg-gray-800 rounded-lg p-6 border border-gray-700"
        >
          <h2 className="text-xl font-bold mb-4 flex items-center">
            <Award className="w-5 h-5 mr-2 text-yellow-400" />
            토큰 & 등급
          </h2>
          <div className="space-y-4">
            <div>
              <p className="text-gray-400 text-sm mb-2">사이버 토큰 잔액</p>
              <div className="flex items-center">
                <span className="text-3xl font-bold text-yellow-400">
                  {user.cyber_token_balance.toLocaleString()}
                </span>
                <span className="text-gray-400 ml-2">토큰</span>
              </div>
            </div>
            <div>
              <p className="text-gray-400 text-sm mb-2">회원 등급</p>
              <span className={`px-4 py-2 rounded-lg font-semibold inline-block border ${getRankColor(user.current_rank)}`}>
                {user.current_rank}
              </span>
            </div>
          </div>
        </motion.div>

        {/* Status Info */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.2 }}
          className="bg-gray-800 rounded-lg p-6 border border-gray-700"
        >
          <h2 className="text-xl font-bold mb-4 flex items-center">
            <Activity className="w-5 h-5 mr-2 text-green-400" />
            상태 정보
          </h2>
          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <span className="text-gray-400">계정 상태</span>
              <span className={`px-3 py-1 rounded-full text-sm font-medium ${
                user.is_active ? 'bg-green-600 text-white' : 'bg-red-600 text-white'
              }`}>
                {user.is_active ? '활성' : '비활성'}
              </span>
            </div>
            <div className="flex items-center justify-between">
              <span className="text-gray-400 flex items-center">
                <Shield className="w-4 h-4 mr-1" />
                인증 상태
              </span>
              <span className={`px-3 py-1 rounded-full text-sm font-medium ${
                user.is_verified ? 'bg-blue-600 text-white' : 'bg-gray-600 text-white'
              }`}>
                {user.is_verified ? '인증됨' : '미인증'}
              </span>
            </div>
            <div className="flex items-center justify-between">
              <span className="text-gray-400">마지막 로그인</span>
              <span className="text-sm">
                {user.last_login ? formatDate(user.last_login) : '기록 없음'}
              </span>
            </div>
          </div>
        </motion.div>
      </div>

      {/* Reward Modal */}
      {showRewardModal && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
          <motion.div
            initial={{ opacity: 0, scale: 0.9 }}
            animate={{ opacity: 1, scale: 1 }}
            className="bg-gray-800 rounded-lg p-6 max-w-md w-full mx-4 border border-gray-700"
          >
            <h3 className="text-xl font-bold mb-4 flex items-center">
              <Gift className="w-5 h-5 mr-2 text-yellow-400" />
              보상 지급
            </h3>
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-400 mb-2">
                  보상 유형
                </label>
                <select
                  value={rewardForm.reward_type}
                  onChange={(e) => setRewardForm({ ...rewardForm, reward_type: e.target.value })}
                  className="w-full bg-gray-700 border border-gray-600 rounded-lg px-4 py-2 text-white focus:outline-none focus:border-blue-500"
                >
                  <option value="BONUS">보너스</option>
                  <option value="EVENT">이벤트</option>
                  <option value="COMPENSATION">보상</option>
                  <option value="ADMIN">관리자 지급</option>
                </select>
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-400 mb-2">
                  지급 금액
                </label>
                <input
                  type="number"
                  value={rewardForm.amount}
                  onChange={(e) => setRewardForm({ ...rewardForm, amount: parseInt(e.target.value) || 0 })}
                  className="w-full bg-gray-700 border border-gray-600 rounded-lg px-4 py-2 text-white focus:outline-none focus:border-blue-500"
                  placeholder="지급할 토큰 수량"
                />
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-400 mb-2">
                  지급 사유
                </label>
                <textarea
                  value={rewardForm.reason}
                  onChange={(e) => setRewardForm({ ...rewardForm, reason: e.target.value })}
                  className="w-full bg-gray-700 border border-gray-600 rounded-lg px-4 py-2 text-white focus:outline-none focus:border-blue-500"
                  rows={3}
                  placeholder="보상 지급 사유를 입력하세요..."
                />
              </div>
            </div>
            
            <div className="flex justify-end space-x-3 mt-6">
              <button
                onClick={() => setShowRewardModal(false)}
                className="px-4 py-2 bg-gray-700 hover:bg-gray-600 rounded-lg transition-colors"
              >
                취소
              </button>
              <button
                onClick={handleGiveReward}
                disabled={!rewardForm.amount || !rewardForm.reason.trim()}
                className="px-4 py-2 bg-blue-600 hover:bg-blue-700 rounded-lg transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
              >
                지급하기
              </button>
            </div>
          </motion.div>
        </div>
      )}
    </div>
  );
};

export default UserDetailPage;
