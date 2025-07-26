'use client';

import React, { useState, useEffect } from 'react';
import AdminLayout from '../../layouts/AdminLayout';
import { motion } from 'framer-motion';
import { Users, Award, Activity, TrendingUp } from 'lucide-react';

// 임시 차트 데이터 - 실제로는 API에서 가져올 것입니다
const activityData = [
  { date: '7/20', count: 120 },
  { date: '7/21', count: 180 },
  { date: '7/22', count: 150 },
  { date: '7/23', count: 220 },
  { date: '7/24', count: 250 },
  { date: '7/25', count: 190 },
  { date: '7/26', count: 280 },
];

// 임시 최근 활동 데이터
const recentActivities = [
  { id: 1, user: '사용자1', type: '로그인', time: '방금 전' },
  { id: 2, user: '사용자2', type: '게임 플레이', time: '5분 전' },
  { id: 3, user: '사용자3', type: '보상 획득', time: '10분 전' },
  { id: 4, user: '사용자4', type: '회원가입', time: '30분 전' },
  { id: 5, user: '사용자5', type: '결제', time: '1시간 전' },
];

const AdminDashboard: React.FC = () => {
  // 실제 구현에서는 API에서 데이터를 가져옵니다
  const [stats, setStats] = useState({
    totalUsers: 0,
    activeUsers: 0,
    totalRewards: 0,
    todayActivities: 0,
  });
  
  const [loading, setLoading] = useState(true);

  // 데이터 로딩 시뮬레이션
  useEffect(() => {
    const timer = setTimeout(() => {
      setStats({
        totalUsers: 1250,
        activeUsers: 483,
        totalRewards: 12500,
        todayActivities: 876,
      });
      setLoading(false);
    }, 1000);

    return () => clearTimeout(timer);
  }, []);

  const fadeIn = {
    initial: { opacity: 0, y: 20 },
    animate: { opacity: 1, y: 0 },
    transition: { duration: 0.4 }
  };
  
  // 최대 활동 수를 기준으로 차트의 높이를 계산합니다
  const maxCount = Math.max(...activityData.map(d => d.count));

  return (
    <AdminLayout title="관리자 대시보드">
      {/* 통계 카드 */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
        <StatCard 
          icon={<Users className="w-8 h-8" />}
          title="총 사용자"
          value={stats.totalUsers.toLocaleString()}
          trend="+5.2%"
          trendUp={true}
          loading={loading}
          color="cyan"
        />
        <StatCard 
          icon={<Activity className="w-8 h-8" />}
          title="활성 사용자"
          value={stats.activeUsers.toLocaleString()}
          trend="+2.1%"
          trendUp={true}
          loading={loading}
          color="green"
        />
        <StatCard 
          icon={<Award className="w-8 h-8" />}
          title="총 보상 지급량"
          value={stats.totalRewards.toLocaleString()}
          trend="+12.5%"
          trendUp={true}
          loading={loading}
          color="purple"
        />
        <StatCard 
          icon={<TrendingUp className="w-8 h-8" />}
          title="오늘의 활동"
          value={stats.todayActivities.toLocaleString()}
          trend="-3.8%"
          trendUp={false}
          loading={loading}
          color="pink"
        />
      </div>

      {/* 차트와 활동 로그 영역 */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-8">
        {/* 차트 섹션 */}
        <motion.div 
          className="lg:col-span-2 bg-gray-900 rounded-xl p-6 border border-gray-800 shadow-xl"
          {...fadeIn}
          transition={{ delay: 0.2 }}
        >
          <h2 className="text-xl font-semibold mb-6 text-white">일간 활동 추이</h2>
          <div className="h-64 flex items-end justify-between space-x-2">
            {activityData.map((day, index) => (
              <div key={index} className="flex flex-col items-center flex-1">
                <div className="relative w-full flex justify-center">
                  <motion.div 
                    className="w-12 bg-gradient-to-t from-cyan-600 to-cyan-400 rounded-t-md"
                    initial={{ height: 0 }}
                    animate={{ height: `${(day.count / maxCount) * 100}%` }}
                    transition={{ duration: 1, delay: 0.1 * index }}
                  >
                    <div className="absolute -top-7 left-1/2 transform -translate-x-1/2 text-xs text-gray-400">
                      {day.count}
                    </div>
                  </motion.div>
                </div>
                <div className="mt-2 text-xs text-gray-400">{day.date}</div>
              </div>
            ))}
          </div>
        </motion.div>

        {/* 최근 활동 로그 */}
        <motion.div 
          className="bg-gray-900 rounded-xl p-6 border border-gray-800 shadow-xl"
          {...fadeIn}
          transition={{ delay: 0.3 }}
        >
          <h2 className="text-xl font-semibold mb-6 text-white">실시간 활동</h2>
          <div className="space-y-4">
            {recentActivities.map((activity, index) => (
              <motion.div 
                key={activity.id}
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ duration: 0.3, delay: 0.1 * index }}
                className="flex items-center p-3 rounded-lg bg-gray-800 border border-gray-700"
              >
                <div className="w-2 h-2 rounded-full bg-cyan-400 mr-3"></div>
                <div className="flex-1">
                  <div className="text-sm font-medium text-white">{activity.user}</div>
                  <div className="text-xs text-gray-400">{activity.type}</div>
                </div>
                <div className="text-xs text-gray-500">{activity.time}</div>
              </motion.div>
            ))}
          </div>
          <div className="mt-4 text-center">
            <button className="text-sm text-cyan-400 hover:text-cyan-300 transition-colors">
              모든 활동 보기 &rarr;
            </button>
          </div>
        </motion.div>
      </div>

      {/* 하단 섹션 - 추가 통계 또는 정보 */}
      <motion.div 
        className="bg-gray-900 rounded-xl p-6 border border-gray-800 shadow-xl"
        {...fadeIn}
        transition={{ delay: 0.4 }}
      >
        <h2 className="text-xl font-semibold mb-6 text-white">사용자 등급 분포</h2>
        <div className="flex justify-between items-center">
          <RankDistribution 
            title="일반" 
            percentage={65} 
            color="bg-blue-500" 
          />
          <RankDistribution 
            title="VIP" 
            percentage={25} 
            color="bg-purple-500" 
          />
          <RankDistribution 
            title="프리미엄" 
            percentage={10} 
            color="bg-pink-500" 
          />
        </div>
      </motion.div>
    </AdminLayout>
  );
};

// 통계 카드 컴포넌트
interface StatCardProps {
  icon: React.ReactNode;
  title: string;
  value: string;
  trend: string;
  trendUp: boolean;
  loading: boolean;
  color: 'cyan' | 'green' | 'purple' | 'pink';
}

const StatCard: React.FC<StatCardProps> = ({ 
  icon, title, value, trend, trendUp, loading, color 
}) => {
  // 색상 매핑
  const colorMap = {
    cyan: 'from-cyan-600 to-cyan-400 shadow-cyan-900/20',
    green: 'from-green-600 to-green-400 shadow-green-900/20',
    purple: 'from-purple-600 to-purple-400 shadow-purple-900/20',
    pink: 'from-pink-600 to-pink-400 shadow-pink-900/20',
  };

  const gradientClass = colorMap[color];

  return (
    <motion.div 
      className="bg-gray-900 rounded-xl p-6 border border-gray-800 shadow-xl relative overflow-hidden"
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.4 }}
    >
      {/* 백그라운드 그라데이션 효과 */}
      <div className={`absolute top-0 right-0 w-24 h-24 rounded-full blur-3xl bg-gradient-to-br ${gradientClass} opacity-20`}></div>
      
      <div className="flex justify-between items-start">
        <div className={`w-12 h-12 rounded-lg bg-gradient-to-br ${gradientClass} flex items-center justify-center shadow-lg`}>
          {icon}
        </div>
        <div className="flex flex-col items-end">
          <div className={`text-sm ${trendUp ? 'text-green-400' : 'text-red-400'}`}>
            {trend}
          </div>
        </div>
      </div>
      
      <div className="mt-4">
        <div className="text-gray-400 text-sm">{title}</div>
        {loading ? (
          <div className="h-8 w-24 bg-gray-800 rounded animate-pulse mt-1"></div>
        ) : (
          <div className="text-2xl font-bold mt-1 text-white">{value}</div>
        )}
      </div>
    </motion.div>
  );
};

// 등급 분포 컴포넌트
interface RankDistributionProps {
  title: string;
  percentage: number;
  color: string;
}

const RankDistribution: React.FC<RankDistributionProps> = ({ 
  title, percentage, color 
}) => {
  return (
    <div className="flex-1 mx-2">
      <div className="flex justify-between mb-2">
        <span className="text-sm text-gray-400">{title}</span>
        <span className="text-sm text-white">{percentage}%</span>
      </div>
      <div className="w-full bg-gray-800 rounded-full h-2">
        <motion.div 
          className={`h-2 rounded-full ${color}`} 
          initial={{ width: 0 }}
          animate={{ width: `${percentage}%` }}
          transition={{ duration: 1 }}
        />
      </div>
    </div>
  );
};

export default AdminDashboard;
