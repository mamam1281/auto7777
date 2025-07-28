'use client';

import { useState, useEffect } from 'react';
import Link from 'next/link';
import { useParams } from 'next/navigation';

interface User {
  id: number;
  nickname: string;
  email: string;
  cyber_token_balance: number;
  current_rank: string;
  is_verified: boolean;
  is_active: boolean;
  created_at: string;
  last_login: string;
}

interface UserActivity {
  id: number;
  activity_type: string;
  details: string;
  timestamp: string;
}

const UserDetailPage = () => {
  const params = useParams();
  const userId = params?.id as string;
  
  const [user, setUser] = useState<UserDetail | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [showRewardModal, setShowRewardModal] = useState(false);
  
  // 보상 지급 폼 상태
  const [rewardForm, setRewardForm] = useState({
    reward_type: 'BONUS',
    amount: 0,
    reason: '',
  });

  useEffect(() => {
    if (userId) {
      fetchUserDetail();
    }
  }, [userId]);

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
    } catch (err) {
      console.error('Error fetching user details:', err);
      setError('Failed to load user details');
    } finally {
      setLoading(false);
    }
  };

  const handleGiveReward = async () => {
    try {
      const response = await fetch('http://localhost:8000/api/admin/rewards', {
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
          admin_id: 1, // TODO: 실제 관리자 ID 사용
        }),
      });

      if (!response.ok) {
        throw new Error('Failed to give reward');
      }

      // 성공 후 사용자 정보 새로고침
      await fetchUserDetail();
      setShowRewardModal(false);
      setRewardForm({ reward_type: 'BONUS', amount: 0, reason: '' });
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
      case 'VIP': return 'text-yellow-400 bg-yellow-400/10';
      case 'PREMIUM': return 'text-purple-400 bg-purple-400/10';
      default: return 'text-gray-400 bg-gray-400/10';
    }
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

  if (error || !user) {
    return (
      <div className="min-h-screen bg-gray-900 flex items-center justify-center">
        <div className="text-red-500 text-xl">{error || 'User not found'}</div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-900 text-white">
      {/* Header */}
      <div className="bg-gray-800 border-b border-gray-700 p-6">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-4">
            <Link href="/admin/users" className="text-gray-400 hover:text-white transition-colors">
              <ChevronLeft className="w-6 h-6" />
            </Link>
            <div>
              <h1 className="text-3xl font-bold">사용자 상세 정보</h1>
              <p className="text-gray-400 mt-2">{user.nickname} ({user.site_id})</p>
            </div>
          </div>
          <button
            onClick={() => setShowRewardModal(true)}
            className="bg-blue-600 hover:bg-blue-700 px-4 py-2 rounded-lg font-semibold transition-colors flex items-center"
          >
            <Gift className="w-5 h-5 mr-2" />
            보상 지급
          </button>
        </div>
      </div>

      {/* User Info Cards */}
      <div className="p-6 grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Basic Info */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="bg-gray-800 rounded-lg p-6 border border-gray-700"
        >
          <h2 className="text-xl font-bold mb-4">기본 정보</h2>
          <div className="space-y-3">
            <div className="flex items-center justify-between">
              <span className="text-gray-400">사이트 ID</span>
              <span className="font-mono">{user.site_id}</span>
            </div>
            <div className="flex items-center justify-between">
              <span className="text-gray-400">닉네임</span>
              <span className="flex items-center">
                <User className="w-4 h-4 mr-2 text-gray-400" />
                {user.nickname}
              </span>
            </div>
            <div className="flex items-center justify-between">
              <span className="text-gray-400">전화번호</span>
              <span className="flex items-center">
                <Phone className="w-4 h-4 mr-2 text-gray-400" />
                {user.phone_number}
              </span>
            </div>
            <div className="flex items-center justify-between">
              <span className="text-gray-400">가입일</span>
              <span className="flex items-center">
                <Calendar className="w-4 h-4 mr-2 text-gray-400" />
                {formatDate(user.created_at)}
              </span>
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
          <h2 className="text-xl font-bold mb-4">토큰 & 등급</h2>
          <div className="space-y-4">
            <div>
              <p className="text-gray-400 text-sm mb-2">사이버 토큰 잔액</p>
              <div className="flex items-center">
                <Award className="w-8 h-8 text-yellow-400 mr-3" />
                <span className="text-3xl font-bold">{user.cyber_token_balance.toLocaleString()}</span>
              </div>
            </div>
            <div>
              <p className="text-gray-400 text-sm mb-2">회원 등급</p>
              <span className={`px-4 py-2 rounded-full font-semibold inline-block ${getRankColor(user.rank)}`}>
                {user.rank}
              </span>
            </div>
          </div>
        </motion.div>

        {/* Quick Stats */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.2 }}
          className="bg-gray-800 rounded-lg p-6 border border-gray-700"
        >
          <h2 className="text-xl font-bold mb-4">활동 통계</h2>
          <div className="space-y-3">
            <div className="flex items-center justify-between">
              <span className="text-gray-400">최근 활동</span>
              <span>{user.recent_activities.length}건</span>
            </div>
            <div className="flex items-center justify-between">
              <span className="text-gray-400">받은 보상</span>
              <span>{user.recent_rewards.length}건</span>
            </div>
            <div className="flex items-center justify-between">
              <span className="text-gray-400">총 보상 금액</span>
              <span>
                {user.recent_rewards.reduce((sum, reward) => sum + reward.amount, 0).toLocaleString()}
              </span>
            </div>
          </div>
        </motion.div>
      </div>

      {/* Recent Activities & Rewards */}
      <div className="p-6 grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Recent Activities */}
        <div>
          <h2 className="text-xl font-bold mb-4">최근 활동</h2>
          <div className="bg-gray-800 rounded-lg border border-gray-700 overflow-hidden">
            <div className="max-h-96 overflow-y-auto">
              {user.recent_activities.map((activity) => (
                <div key={activity.id} className="p-4 border-b border-gray-700 hover:bg-gray-700 transition-colors">
                  <div className="flex items-start justify-between">
                    <div className="flex items-start">
                      <span className="text-2xl mr-3">{getActivityIcon(activity.activity_type)}</span>
                      <div>
                        <p className="font-semibold">{activity.activity_type}</p>
                        <p className="text-sm text-gray-400">{activity.details}</p>
                      </div>
                    </div>
                    <span className="text-sm text-gray-400">{formatDate(activity.timestamp)}</span>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* Recent Rewards */}
        <div>
          <h2 className="text-xl font-bold mb-4">최근 보상</h2>
          <div className="bg-gray-800 rounded-lg border border-gray-700 overflow-hidden">
            <div className="max-h-96 overflow-y-auto">
              {user.recent_rewards.map((reward) => (
                <div key={reward.id} className="p-4 border-b border-gray-700 hover:bg-gray-700 transition-colors">
                  <div className="flex items-start justify-between">
                    <div>
                      <p className="font-semibold flex items-center">
                        <CreditCard className="w-4 h-4 mr-2 text-yellow-400" />
                        {reward.reward_type}
                      </p>
                      <p className="text-sm text-gray-400">{reward.reason}</p>
                    </div>
                    <div className="text-right">
                      <p className="font-bold text-green-400">+{reward.amount.toLocaleString()}</p>
                      <p className="text-sm text-gray-400">{formatDate(reward.created_at)}</p>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>

      {/* Reward Modal */}
      {showRewardModal && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
          <motion.div
            initial={{ opacity: 0, scale: 0.9 }}
            animate={{ opacity: 1, scale: 1 }}
            className="bg-gray-800 rounded-lg p-6 max-w-md w-full mx-4 border border-gray-700"
          >
            <h3 className="text-xl font-bold mb-4">보상 지급</h3>
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
                  placeholder="0"
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
                disabled={!rewardForm.amount || !rewardForm.reason}
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

'use client';

import { useState, useEffect } from 'react';
import Link from 'next/link';
import { useParams } from 'next/navigation';

interface User {
  id: number;
  nickname: string;
  email: string;
  cyber_token_balance: number;
  current_rank: string;
  is_verified: boolean;
  is_active: boolean;
  created_at: string;
  last_login: string;
}

interface UserActivity {
  id: number;
  activity_type: string;
  details: string;
  timestamp: string;
}

const UserDetailPage = () => {
  const params = useParams();
  const userId = params?.id as string;
  
  const [user, setUser] = useState<User | null>(null);
  const [activities, setActivities] = useState<UserActivity[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [showRewardModal, setShowRewardModal] = useState(false);
  const [rewardAmount, setRewardAmount] = useState<number>(0);

  useEffect(() => {
    if (userId) {
      fetchUserData();
      fetchUserActivities();
    }
  }, [userId]);

  const fetchUserData = async () => {
    try {
      setLoading(true);
      setError(null);

      const response = await fetch(`http://localhost:8000/api/admin/users/${userId}`, {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`,
        },
      });

      if (!response.ok) {
        throw new Error('Failed to fetch user data');
      }

      const userData = await response.json();
      setUser(userData);
    } catch (err) {
      console.error('Error fetching user data:', err);
      setError('Failed to load user data');
    } finally {
      setLoading(false);
    }
  };

  const fetchUserActivities = async () => {
    try {
      const response = await fetch(`http://localhost:8000/api/admin/users/${userId}/activities`, {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`,
        },
      });

      if (response.ok) {
        const activitiesData = await response.json();
        setActivities(activitiesData);
      }
    } catch (err) {
      console.error('Error fetching user activities:', err);
    }
  };

  const handleGiveReward = async () => {
    if (!rewardAmount || rewardAmount <= 0) {
      alert('올바른 보상 수량을 입력해주세요.');
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
          token_amount: rewardAmount,
          reason: `관리자 지급 - ${rewardAmount} 토큰`,
        }),
      });

      if (response.ok) {
        alert('보상이 성공적으로 지급되었습니다.');
        setShowRewardModal(false);
        setRewardAmount(0);
        fetchUserData();
        fetchUserActivities();
      } else {
        throw new Error('Failed to give reward');
      }
    } catch (err) {
      console.error('Error giving reward:', err);
      alert('보상 지급에 실패했습니다.');
    }
  };

  const formatDateTime = (dateString: string) => {
    const date = new Date(dateString);
    return date.toLocaleDateString() + ' ' + date.toLocaleTimeString();
  };

  const getRankColor = (rank: string) => {
    switch (rank) {
      case 'SUPER_ADMIN': return 'bg-red-600';
      case 'ADMIN': return 'bg-purple-600';
      case 'VIP': return 'bg-yellow-600';
      case 'PREMIUM': return 'bg-blue-600';
      case 'BASIC': return 'bg-green-600';
      default: return 'bg-gray-600';
    }
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
        <div className="text-white text-xl">Loading user...</div>
      </div>
    );
  }

  if (error || !user) {
    return (
      <div className="min-h-screen bg-gray-900 flex items-center justify-center">
        <div className="text-red-500 text-xl">{error || 'User not found'}</div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-900 text-white">
      {/* Header */}
      <div className="bg-gray-800 border-b border-gray-700 p-6">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-4">
            <Link href="/admin/users" className="text-blue-400 hover:text-blue-300">
              ← 뒤로가기
            </Link>
            <div>
              <h1 className="text-3xl font-bold">{user.nickname} 상세정보</h1>
              <p className="text-gray-400 mt-2">사용자 ID: {user.id}</p>
            </div>
          </div>
          <button
            onClick={() => setShowRewardModal(true)}
            className="bg-yellow-600 hover:bg-yellow-700 px-4 py-2 rounded-lg transition-colors"
          >
            🎁 보상 지급
          </button>
        </div>
      </div>

      {/* User Info Cards */}
      <div className="p-6 grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <div className="bg-gray-800 rounded-lg p-6 border border-gray-700">
          <h3 className="text-sm font-medium text-gray-400 mb-2">이메일</h3>
          <p className="text-lg font-semibold">{user.email}</p>
        </div>

        <div className="bg-gray-800 rounded-lg p-6 border border-gray-700">
          <h3 className="text-sm font-medium text-gray-400 mb-2">등급</h3>
          <span className={`inline-flex items-center px-3 py-1 rounded-full text-sm font-medium text-white ${getRankColor(user.current_rank)}`}>
            {user.current_rank}
          </span>
        </div>

        <div className="bg-gray-800 rounded-lg p-6 border border-gray-700">
          <h3 className="text-sm font-medium text-gray-400 mb-2">토큰 잔액</h3>
          <p className="text-2xl font-bold text-yellow-400">{user.cyber_token_balance.toLocaleString()}</p>
        </div>

        <div className="bg-gray-800 rounded-lg p-6 border border-gray-700">
          <h3 className="text-sm font-medium text-gray-400 mb-2">상태</h3>
          <div className="flex flex-col space-y-2">
            <span className={`inline-flex items-center px-2 py-1 rounded-full text-xs font-medium ${
              user.is_active ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'
            }`}>
              {user.is_active ? '활성' : '비활성'}
            </span>
            {user.is_verified && (
              <span className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-blue-100 text-blue-800">
                인증됨
              </span>
            )}
          </div>
        </div>
      </div>

      {/* User Details */}
      <div className="px-6 grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Account Information */}
        <div className="bg-gray-800 rounded-lg border border-gray-700 p-6">
          <h2 className="text-xl font-bold mb-4">계정 정보</h2>
          <div className="space-y-4">
            <div>
              <label className="text-sm text-gray-400">가입일</label>
              <p className="text-white">{formatDateTime(user.created_at)}</p>
            </div>
            <div>
              <label className="text-sm text-gray-400">마지막 로그인</label>
              <p className="text-white">{user.last_login ? formatDateTime(user.last_login) : '로그인 기록 없음'}</p>
            </div>
          </div>
        </div>

        {/* Recent Activities */}
        <div className="bg-gray-800 rounded-lg border border-gray-700 p-6">
          <h2 className="text-xl font-bold mb-4">최근 활동</h2>
          <div className="space-y-3 max-h-80 overflow-y-auto">
            {activities.length > 0 ? (
              activities.map((activity) => (
                <div key={activity.id} className="flex items-center space-x-3 p-3 bg-gray-700 rounded-lg">
                  <span className="text-2xl">{getActivityIcon(activity.activity_type)}</span>
                  <div className="flex-1">
                    <p className="text-sm font-medium">{activity.activity_type}</p>
                    <p className="text-xs text-gray-400">{activity.details}</p>
                    <p className="text-xs text-gray-500">{formatDateTime(activity.timestamp)}</p>
                  </div>
                </div>
              ))
            ) : (
              <p className="text-gray-400">활동 기록이 없습니다.</p>
            )}
          </div>
        </div>
      </div>

      {/* Reward Modal */}
      {showRewardModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-gray-800 rounded-lg p-6 w-96 border border-gray-700">
            <h3 className="text-xl font-bold mb-4">보상 지급</h3>
            <div className="mb-4">
              <label className="block text-sm font-medium text-gray-400 mb-2">
                지급할 토큰 수량
              </label>
              <input
                type="number"
                value={rewardAmount}
                onChange={(e) => setRewardAmount(Number(e.target.value))}
                className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-lg text-white focus:border-blue-500 focus:outline-none"
                placeholder="토큰 수량을 입력하세요"
              />
            </div>
            <div className="flex space-x-3">
              <button
                onClick={handleGiveReward}
                className="flex-1 bg-yellow-600 hover:bg-yellow-700 px-4 py-2 rounded-lg transition-colors"
              >
                지급하기
              </button>
              <button
                onClick={() => {
                  setShowRewardModal(false);
                  setRewardAmount(0);
                }}
                className="flex-1 bg-gray-600 hover:bg-gray-700 px-4 py-2 rounded-lg transition-colors"
              >
                취소
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default UserDetailPage;
