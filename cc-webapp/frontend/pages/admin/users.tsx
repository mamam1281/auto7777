'use client';

import React, { useState } from 'react';
import AdminLayout from '../../layouts/AdminLayout';
import { motion } from 'framer-motion';
import { Search, Filter, ChevronDown, Edit, Award } from 'lucide-react';
import { useUsers, useGiveReward } from '../../hooks/useAdminApi';
import { User } from '../../types/admin';

const UsersPage: React.FC = () => {
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedRank, setSelectedRank] = useState('모든 등급');
  const [showFilters, setShowFilters] = useState(false);
  const [isRewardModalOpen, setIsRewardModalOpen] = useState(false);
  const [selectedUser, setSelectedUser] = useState<User | null>(null);
  const [rewardAmount, setRewardAmount] = useState(100);
  const [rewardReason, setRewardReason] = useState('');
  const [currentPage, setCurrentPage] = useState(0);
  const [pageSize] = useState(10);
  
  // API 훅 사용
  const { 
    data: usersData, 
    loading: usersLoading, 
    error: usersError, 
    refetch: refetchUsers 
  } = useUsers({
    skip: currentPage * pageSize,
    limit: pageSize,
    search: searchTerm || undefined,
  });

  const { 
    giveReward, 
    loading: rewardLoading, 
    error: rewardError 
  } = useGiveReward();

  // 로딩 중이거나 데이터가 없을 때의 사용자 목록
  const users = usersData?.data || [];
  const totalUsers = usersData?.total || 0;

  // 클라이언트 사이드 랭크 필터링 (API에서 필터링하지 않는 경우)
  const filteredUsers = users.filter(user => {
    const matchesRank = selectedRank === '모든 등급' || user.rank === selectedRank;
    return matchesRank;
  });

  // 보상 모달 열기
  const openRewardModal = (user: User) => {
    setSelectedUser(user);
    setIsRewardModalOpen(true);
    setRewardReason('');
    setRewardAmount(100);
  };

  // 보상 지급 처리
  const handleGiveReward = async () => {
    if (!selectedUser) return;
    
    try {
      await giveReward({
        user_id: selectedUser.id,
        reward_type: 'BONUS',
        amount: rewardAmount,
        reason: rewardReason,
        admin_id: 1, // 임시 관리자 ID - 실제로는 로그인한 관리자 ID 사용
      });
      
      // 성공 시 모달 닫기 및 데이터 새로고침
      setIsRewardModalOpen(false);
      refetchUsers();
      
      // 성공 알림 (실제로는 토스트 등 사용)
      alert(`${selectedUser.nickname}님에게 ${rewardAmount} 토큰이 지급되었습니다.`);
    } catch (error) {
      // 에러 처리는 useGiveReward 훅에서 처리됨
      console.error('보상 지급 실패:', error);
    }
  };

  // 날짜 포맷 헬퍼 함수
  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    return date.toLocaleDateString('ko-KR', { 
      year: 'numeric',
      month: 'short',
      day: 'numeric'
    });
  };

  return (
    <AdminLayout title="사용자 관리">
      {/* 에러 표시 */}
      {usersError && (
        <div className="mb-4 p-4 bg-red-900 border border-red-700 rounded-lg text-red-200">
          오류: {usersError}
          <button 
            onClick={refetchUsers}
            className="ml-2 text-red-400 hover:text-red-300 underline"
          >
            다시 시도
          </button>
        </div>
      )}

      <div className="mb-6 flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
        {/* 검색창 */}
        <div className="relative w-full sm:w-96">
          <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-500 h-4 w-4" />
          <input
            type="text"
            placeholder="사용자 ID 또는 닉네임으로 검색"
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="w-full pl-10 pr-4 py-2 bg-gray-800 text-white border border-gray-700 rounded-lg focus:outline-none focus:border-cyan-500"
          />
        </div>

        {/* 필터 버튼 */}
        <div className="relative">
          <button 
            onClick={() => setShowFilters(!showFilters)}
            className="flex items-center gap-2 px-4 py-2 bg-gray-800 hover:bg-gray-700 text-white rounded-lg border border-gray-700"
          >
            <Filter className="h-4 w-4" />
            필터
            <ChevronDown className={`h-4 w-4 transition-transform ${showFilters ? 'rotate-180' : ''}`} />
          </button>
          
          {/* 필터 드롭다운 */}
          {showFilters && (
            <div className="absolute right-0 mt-2 w-48 bg-gray-800 border border-gray-700 rounded-lg shadow-xl z-10">
              <div className="p-2">
                <div className="text-xs text-gray-400 mb-1">등급</div>
                {['모든 등급', 'STANDARD', 'PREMIUM', 'VIP'].map((rank) => (
                  <div 
                    key={rank}
                    onClick={() => { setSelectedRank(rank); setShowFilters(false); }}
                    className={`px-3 py-2 rounded cursor-pointer ${selectedRank === rank ? 'bg-cyan-900 text-white' : 'text-gray-300 hover:bg-gray-700'}`}
                  >
                    {rank}
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      </div>

      {/* 사용자 테이블 */}
      <div className="bg-gray-900 rounded-xl border border-gray-800 shadow-xl overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead>
              <tr className="border-b border-gray-800">
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-400 uppercase tracking-wider">ID</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-400 uppercase tracking-wider">닉네임</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-400 uppercase tracking-wider">등급</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-400 uppercase tracking-wider">토큰</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-400 uppercase tracking-wider">가입일</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-400 uppercase tracking-wider">작업</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-800">
              {usersLoading ? (
                // 로딩 스켈레톤
                Array(pageSize).fill(0).map((_, i) => (
                  <tr key={i}>
                    {Array(6).fill(0).map((_, j) => (
                      <td key={j} className="px-6 py-4 whitespace-nowrap">
                        <div className="h-4 bg-gray-800 rounded animate-pulse"></div>
                      </td>
                    ))}
                  </tr>
                ))
              ) : filteredUsers.length === 0 ? (
                <tr>
                  <td colSpan={6} className="px-6 py-4 text-center text-gray-500">
                    {searchTerm ? '검색 결과가 없습니다' : '사용자가 없습니다'}
                  </td>
                </tr>
              ) : (
                filteredUsers.map((user, index) => (
                  <motion.tr 
                    key={user.id}
                    initial={{ opacity: 0 }}
                    animate={{ opacity: 1 }}
                    transition={{ duration: 0.3, delay: index * 0.05 }}
                    className="hover:bg-gray-800"
                  >
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-300">{user.site_id}</td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="text-sm font-medium text-white">{user.nickname}</div>
                      <div className="text-xs text-gray-500">{user.phone_number}</div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <span className={`px-2 py-1 text-xs rounded-full ${
                        user.rank === 'VIP' ? 'bg-purple-900 text-purple-200' :
                        user.rank === 'PREMIUM' ? 'bg-pink-900 text-pink-200' :
                        'bg-blue-900 text-blue-200'
                      }`}>
                        {user.rank}
                      </span>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-cyan-400 font-medium">
                      {user.cyber_token_balance.toLocaleString()}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-400">
                      {formatDate(user.created_at)}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm">
                      <div className="flex space-x-2">
                        <button 
                          className="p-1 rounded-md hover:bg-gray-700"
                          onClick={() => console.log('상세보기', user.id)}
                        >
                          <Edit className="h-4 w-4 text-gray-400" />
                        </button>
                        <button 
                          className="p-1 rounded-md hover:bg-gray-700"
                          onClick={() => openRewardModal(user)}
                        >
                          <Award className="h-4 w-4 text-gray-400" />
                        </button>
                      </div>
                    </td>
                  </motion.tr>
                ))
              )}
            </tbody>
          </table>
        </div>

        {/* 페이지네이션 */}
        {totalUsers > pageSize && (
          <div className="px-6 py-3 border-t border-gray-800 flex justify-between items-center">
            <div className="text-sm text-gray-400">
              총 {totalUsers}명 중 {currentPage * pageSize + 1}-{Math.min((currentPage + 1) * pageSize, totalUsers)}명 표시
            </div>
            <div className="flex gap-2">
              <button
                onClick={() => setCurrentPage(Math.max(0, currentPage - 1))}
                disabled={currentPage === 0}
                className="px-3 py-1 bg-gray-800 text-white rounded disabled:opacity-50"
              >
                이전
              </button>
              <button
                onClick={() => setCurrentPage(currentPage + 1)}
                disabled={(currentPage + 1) * pageSize >= totalUsers}
                className="px-3 py-1 bg-gray-800 text-white rounded disabled:opacity-50"
              >
                다음
              </button>
            </div>
          </div>
        )}
      </div>

      {/* 보상 지급 모달 */}
      {isRewardModalOpen && selectedUser && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <motion.div 
            initial={{ opacity: 0, scale: 0.9 }}
            animate={{ opacity: 1, scale: 1 }}
            className="bg-gray-900 rounded-xl border border-gray-800 shadow-2xl p-6 w-full max-w-md"
          >
            <h3 className="text-xl font-semibold text-white mb-6">보상 지급</h3>
            
            {/* 보상 에러 표시 */}
            {rewardError && (
              <div className="mb-4 p-3 bg-red-900 border border-red-700 rounded-lg text-red-200 text-sm">
                {rewardError}
              </div>
            )}
            
            <div className="mb-6">
              <div className="text-sm text-gray-400">사용자</div>
              <div className="text-lg font-medium text-white">{selectedUser.nickname}</div>
              <div className="text-sm text-gray-500">현재 토큰: {selectedUser.cyber_token_balance.toLocaleString()}</div>
            </div>
            
            <div className="mb-4">
              <label className="block text-sm text-gray-400 mb-2">보상 금액</label>
              <input
                type="number"
                min="1"
                value={rewardAmount}
                onChange={(e) => setRewardAmount(parseInt(e.target.value) || 0)}
                className="w-full px-4 py-2 bg-gray-800 text-white border border-gray-700 rounded-lg focus:outline-none focus:border-cyan-500"
              />
            </div>
            
            <div className="mb-6">
              <label className="block text-sm text-gray-400 mb-2">지급 사유</label>
              <textarea
                value={rewardReason}
                onChange={(e) => setRewardReason(e.target.value)}
                className="w-full px-4 py-2 bg-gray-800 text-white border border-gray-700 rounded-lg focus:outline-none focus:border-cyan-500 h-24 resize-none"
                placeholder="보상 지급 사유를 입력하세요"
                required
              />
            </div>
            
            <div className="flex justify-end gap-3">
              <button 
                onClick={() => setIsRewardModalOpen(false)}
                disabled={rewardLoading}
                className="px-4 py-2 border border-gray-600 text-gray-300 hover:bg-gray-800 rounded-lg disabled:opacity-50"
              >
                취소
              </button>
              <button 
                onClick={handleGiveReward}
                disabled={rewardLoading || !rewardReason.trim() || rewardAmount <= 0}
                className="px-4 py-2 bg-gradient-to-r from-cyan-600 to-cyan-500 text-white rounded-lg hover:from-cyan-500 hover:to-cyan-400 disabled:opacity-50"
              >
                {rewardLoading ? '처리중...' : '지급'}
              </button>
            </div>
          </motion.div>
        </div>
      )}
    </AdminLayout>
  );
};

export default UsersPage;
