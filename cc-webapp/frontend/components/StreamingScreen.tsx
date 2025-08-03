'use client';

import React, { useState, useEffect, useRef } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import {
  Heart,
  MessageCircle,
  Gift,
  Crown,
  Users,
  TrendingUp,
  X,
  ChevronRight,
  Play,
  Mic,
  Video,
  Settings,
  MoreVertical,
  AlertCircle,
  Eye,
  Clock,
  Award,
  Coins,
  Trophy,
  Flame,
  Star as StarIcon,
  Radio
} from 'lucide-react';
import Image from 'next/image';
import { Card, CardContent, CardHeader, CardTitle } from './ui/card';
import { Button } from './ui/button';
import { Input } from './ui/input';
import { User } from '../types/user';

interface StreamingScreenProps {
  user: User;
  onBack: () => void;
  onUpdateUser: (updates: Partial<User>) => void;
  onAddNotification: (message: string, type: 'success' | 'error' | 'info' | 'warning') => void;
}

interface Stream {
  id: string;
  title: string;
  streamerName: string;
  viewers: number;
  thumbnail: string;
  category: string;
  isLive: boolean;
  hearts: number;
  donations: number;
  tags: string[];
  startedAt: Date;
}

interface Message {
  id: string;
  username: string;
  content: string;
  timestamp: Date;
  isDonation?: boolean;
  donationAmount?: number;
  isStreamer?: boolean;
  userLevel?: number;
}

interface Donation {
  id: string;
  username: string;
  amount: number;
  message?: string;
  timestamp: Date;
}

interface Category {
  id: string;
  name: string;
  icon: string;
  color: string;
  count: number;
}

export function StreamingScreen({
  user,
  onBack,
  onUpdateUser,
  onAddNotification
}: StreamingScreenProps) {
  const [selectedStream, setSelectedStream] = useState<Stream | null>(null);
  const [messages, setMessages] = useState<Message[]>([]);
  const [newMessage, setNewMessage] = useState('');
  const [showDonation, setShowDonation] = useState(false);
  const [donationAmount, setDonationAmount] = useState('');
  const [donationMessage, setDonationMessage] = useState('');
  const [isFollowing, setIsFollowing] = useState(false);
  const [selectedCategory, setSelectedCategory] = useState<string>('all');
  const messagesEndRef = useRef<HTMLDivElement>(null);

  // 인기 스트림 목록
  const popularStreams: Stream[] = [
    {
      id: '1',
      title: '🎰 슬롯머신 대박 도전! 오늘은 꼭 터뜨린다!',
      streamerName: 'LuckyGambler777',
      viewers: 15234,
      thumbnail: '/api/placeholder/320/180',
      category: '슬롯게임',
      isLive: true,
      hearts: 89234,
      donations: 125000,
      tags: ['슬롯', '잭팟', '실시간'],
      startedAt: new Date(Date.now() - 2 * 60 * 60 * 1000)
    },
    {
      id: '2',
      title: '가위바위보 1000연승 도전중! 함께해요~',
      streamerName: 'RPSMaster',
      viewers: 8956,
      thumbnail: '/api/placeholder/320/180',
      category: '가위바위보',
      isLive: true,
      hearts: 45678,
      donations: 89000,
      tags: ['RPS', '연승', '도전'],
      startedAt: new Date(Date.now() - 1 * 60 * 60 * 1000)
    },
    {
      id: '3',
      title: '🎁 가챠 100연차 돌려봅니다! SSR 나올까?',
      streamerName: 'GachaKing',
      viewers: 12456,
      thumbnail: '/api/placeholder/320/180',
      category: '가챠',
      isLive: true,
      hearts: 67890,
      donations: 156000,
      tags: ['가챠', 'SSR', '100연차'],
      startedAt: new Date(Date.now() - 3 * 60 * 60 * 1000)
    },
    {
      id: '4',
      title: '크래시 게임 전략 공개! 함께 수익내자',
      streamerName: 'CrashExpert',
      viewers: 6789,
      thumbnail: '/api/placeholder/320/180',
      category: '크래시',
      isLive: true,
      hearts: 34567,
      donations: 67000,
      tags: ['크래시', '전략', '수익'],
      startedAt: new Date(Date.now() - 30 * 60 * 1000)
    }
  ];

  // 카테고리 목록
  const categories: Category[] = [
    { id: 'all', name: '전체', icon: '🎮', color: 'bg-purple-500', count: 156 },
    { id: 'slot', name: '슬롯게임', icon: '🎰', color: 'bg-yellow-500', count: 45 },
    { id: 'rps', name: '가위바위보', icon: '✂️', color: 'bg-blue-500', count: 23 },
    { id: 'gacha', name: '가챠', icon: '🎁', color: 'bg-pink-500', count: 34 },
    { id: 'crash', name: '크래시', icon: '📈', color: 'bg-red-500', count: 28 },
    { id: 'talk', name: '토크', icon: '💬', color: 'bg-green-500', count: 26 }
  ];

  // 채팅 메시지 자동 스크롤
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  // 가상의 채팅 메시지 시뮬레이션
  useEffect(() => {
    if (!selectedStream) return;

    const interval = setInterval(() => {
      const randomMessages = [
        { username: 'User123', content: '대박! 잭팟 터뜨려주세요!' },
        { username: 'Gambler456', content: 'ㅋㅋㅋㅋ 이거 실화냐' },
        { username: 'ProPlayer', content: '와 진짜 잘하시네요' },
        { username: 'Viewer789', content: '하트 보냈어요 ❤️' },
        { username: 'RichGuy', content: '100 코인 후원합니다!', isDonation: true, donationAmount: 100 }
      ];

      const randomMessage = randomMessages[Math.floor(Math.random() * randomMessages.length)];
      const newMsg: Message = {
        id: Date.now().toString(),
        ...randomMessage,
        timestamp: new Date(),
        userLevel: Math.floor(Math.random() * 50) + 1
      };

      setMessages(prev => [...prev.slice(-50), newMsg]);
    }, 3000);

    return () => clearInterval(interval);
  }, [selectedStream]);

  const handleSendMessage = () => {
    if (!newMessage.trim() || !selectedStream) return;

    const message: Message = {
      id: Date.now().toString(),
      username: user.username,
      content: newMessage,
      timestamp: new Date(),
      userLevel: user.level || 1
    };

    setMessages(prev => [...prev, message]);
    setNewMessage('');
  };

  const handleDonation = () => {
    const amount = parseInt(donationAmount);
    if (isNaN(amount) || amount <= 0) {
      onAddNotification('올바른 후원 금액을 입력해주세요.', 'error');
      return;
    }

    if (user.gold < amount) {
      onAddNotification('골드가 부족합니다.', 'error');
      return;
    }

    const donation: Message = {
      id: Date.now().toString(),
      username: user.username,
      content: donationMessage || `${amount} 코인 후원!`,
      timestamp: new Date(),
      isDonation: true,
      donationAmount: amount,
      userLevel: user.level || 1
    };

    setMessages(prev => [...prev, donation]);
    onUpdateUser({ gold: user.gold - amount });
    onAddNotification(`${amount} 코인을 후원했습니다!`, 'success');
    
    setShowDonation(false);
    setDonationAmount('');
    setDonationMessage('');
  };

  const handleSendHeart = () => {
    if (selectedStream) {
      onAddNotification('하트를 보냈습니다! ❤️', 'success');
    }
  };

  const formatViewers = (num: number) => {
    if (num >= 10000) return `${(num / 1000).toFixed(1)}K`;
    if (num >= 1000) return `${(num / 1000).toFixed(1)}K`;
    return num.toString();
  };

  const formatDuration = (startedAt: Date) => {
    const now = new Date();
    const diff = now.getTime() - startedAt.getTime();
    const hours = Math.floor(diff / (1000 * 60 * 60));
    const minutes = Math.floor((diff % (1000 * 60 * 60)) / (1000 * 60));
    
    if (hours > 0) {
      return `${hours}시간 ${minutes}분`;
    }
    return `${minutes}분`;
  };

  if (selectedStream) {
    return (
      <div className="min-h-screen bg-gray-900 text-white">
        {/* 헤더 */}
        <div className="bg-gray-800 border-b border-gray-700 p-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-4">
              <button
                onClick={() => setSelectedStream(null)}
                className="p-2 hover:bg-gray-700 rounded-lg transition-colors"
              >
                <X className="w-5 h-5" />
              </button>
              <div>
                <h2 className="font-semibold text-lg">{selectedStream.title}</h2>
                <div className="flex items-center gap-2 text-sm text-gray-400">
                  <span>{selectedStream.streamerName}</span>
                  <span>•</span>
                  <span className="text-red-500 flex items-center gap-1">
                    <Radio className="w-3 h-3" />
                    LIVE
                  </span>
                  <span>•</span>
                  <span>{formatDuration(selectedStream.startedAt)}</span>
                </div>
              </div>
            </div>
            <div className="flex items-center gap-3">
              <Button
                onClick={() => setIsFollowing(!isFollowing)}
                variant={isFollowing ? "secondary" : "default"}
                size="sm"
                className={isFollowing ? "bg-gray-600" : "bg-purple-600 hover:bg-purple-700"}
              >
                {isFollowing ? '팔로잉' : '팔로우'}
              </Button>
              <Button
                variant="ghost"
                size="icon"
                className="hover:bg-gray-700"
              >
                <Settings className="w-5 h-5" />
              </Button>
              <Button
                variant="ghost"
                size="icon"
                className="hover:bg-gray-700"
              >
                <MoreVertical className="w-5 h-5" />
              </Button>
            </div>
          </div>
        </div>

        <div className="flex h-[calc(100vh-80px)]">
          {/* 스트림 영역 */}
          <div className="flex-1 bg-black relative">
            <div className="absolute inset-0 flex items-center justify-center">
              <Image
                src={selectedStream.thumbnail}
                alt={selectedStream.title}
                width={1280}
                height={720}
                className="w-full h-full object-contain"
                unoptimized
              />
              <div className="absolute inset-0 bg-black/30 flex items-center justify-center">
                <Play className="w-20 h-20 text-white/80" />
              </div>
            </div>
            
            {/* 스트림 정보 오버레이 */}
            <div className="absolute top-4 left-4 right-4 flex justify-between">
              <div className="bg-black/60 backdrop-blur px-3 py-2 rounded-lg flex items-center gap-2">
                <Eye className="w-4 h-4 text-red-500" />
                <span className="text-sm font-medium">{formatViewers(selectedStream.viewers)} 시청중</span>
              </div>
              <div className="flex gap-2">
                <div className="bg-black/60 backdrop-blur px-3 py-2 rounded-lg flex items-center gap-2">
                  <Heart className="w-4 h-4 text-pink-500" />
                  <span className="text-sm font-medium">{formatViewers(selectedStream.hearts)}</span>
                </div>
                <div className="bg-black/60 backdrop-blur px-3 py-2 rounded-lg flex items-center gap-2">
                  <Coins className="w-4 h-4 text-yellow-500" />
                  <span className="text-sm font-medium">{formatViewers(selectedStream.donations)}</span>
                </div>
              </div>
            </div>
          </div>

          {/* 채팅 영역 */}
          <div className="w-96 bg-gray-800 flex flex-col">
            {/* 채팅 헤더 */}
            <div className="p-4 border-b border-gray-700">
              <h3 className="font-semibold">실시간 채팅</h3>
            </div>

            {/* 채팅 메시지 */}
            <div className="flex-1 overflow-y-auto p-4 space-y-2">
              {messages.map((message) => (
                <motion.div
                  key={message.id}
                  initial={{ opacity: 0, y: 10 }}
                  animate={{ opacity: 1, y: 0 }}
                  className={`${
                    message.isDonation 
                      ? 'bg-yellow-500/20 border border-yellow-500/30 p-2 rounded' 
                      : ''
                  }`}
                >
                  <div className="flex items-start gap-2">
                    <div className="flex-shrink-0">
                      <div className="w-6 h-6 bg-purple-600 rounded-full flex items-center justify-center text-xs">
                        {message.userLevel}
                      </div>
                    </div>
                    <div className="flex-1 min-w-0">
                      <div className="flex items-baseline gap-1">
                        <span className={`font-medium text-sm ${
                          message.isDonation ? 'text-yellow-400' : 'text-purple-400'
                        }`}>
                          {message.username}
                        </span>
                        {message.isDonation && (
                          <span className="text-yellow-400 text-xs">
                            💰 {message.donationAmount} 코인
                          </span>
                        )}
                      </div>
                      <p className="text-sm text-gray-200 break-words">
                        {message.content}
                      </p>
                    </div>
                  </div>
                </motion.div>
              ))}
              <div ref={messagesEndRef} />
            </div>

            {/* 채팅 입력 */}
            <div className="p-4 border-t border-gray-700 space-y-3">
              <div className="flex gap-2">
                <Button
                  onClick={handleSendHeart}
                  size="icon"
                  variant="ghost"
                  className="hover:bg-gray-700 text-pink-500"
                >
                  <Heart className="w-5 h-5" />
                </Button>
                <Button
                  onClick={() => setShowDonation(!showDonation)}
                  size="icon"
                  variant="ghost"
                  className="hover:bg-gray-700 text-yellow-500"
                >
                  <Gift className="w-5 h-5" />
                </Button>
              </div>

              {showDonation && (
                <motion.div
                  initial={{ opacity: 0, height: 0 }}
                  animate={{ opacity: 1, height: 'auto' }}
                  exit={{ opacity: 0, height: 0 }}
                  className="space-y-2"
                >
                  <Input
                    type="number"
                    placeholder="후원 금액"
                    value={donationAmount}
                    onChange={(e) => setDonationAmount(e.target.value)}
                    className="bg-gray-700 border-gray-600"
                  />
                  <Input
                    placeholder="메시지 (선택사항)"
                    value={donationMessage}
                    onChange={(e) => setDonationMessage(e.target.value)}
                    className="bg-gray-700 border-gray-600"
                  />
                  <Button
                    onClick={handleDonation}
                    className="w-full bg-yellow-600 hover:bg-yellow-700"
                  >
                    후원하기
                  </Button>
                </motion.div>
              )}

              <div className="flex gap-2">
                <Input
                  placeholder="메시지를 입력하세요..."
                  value={newMessage}
                  onChange={(e) => setNewMessage(e.target.value)}
                  onKeyPress={(e) => e.key === 'Enter' && handleSendMessage()}
                  className="bg-gray-700 border-gray-600"
                />
                <Button
                  onClick={handleSendMessage}
                  size="icon"
                  className="bg-purple-600 hover:bg-purple-700"
                >
                  <ChevronRight className="w-5 h-5" />
                </Button>
              </div>
            </div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-900">
      {/* 헤더 */}
      <div className="bg-gray-800 border-b border-gray-700 p-4 sticky top-0 z-10">
        <div className="max-w-7xl mx-auto flex items-center justify-between">
          <div className="flex items-center gap-4">
            <button
              onClick={onBack}
              className="p-2 hover:bg-gray-700 rounded-lg transition-colors"
            >
              <X className="w-5 h-5 text-gray-400" />
            </button>
            <h1 className="text-2xl font-bold text-white">라이브 스트리밍</h1>
          </div>
          <div className="flex items-center gap-2">
            <div className="bg-gray-700 px-3 py-1.5 rounded-lg flex items-center gap-2">
              <Eye className="w-4 h-4 text-red-500" />
              <span className="text-sm text-gray-300">
                {popularStreams.reduce((sum, s) => sum + s.viewers, 0).toLocaleString()} 시청중
              </span>
            </div>
          </div>
        </div>
      </div>

      {/* 카테고리 필터 */}
      <div className="bg-gray-800/50 border-b border-gray-700 px-4 py-3 sticky top-16 z-10 backdrop-blur">
        <div className="max-w-7xl mx-auto">
          <div className="flex items-center gap-2 overflow-x-auto scrollbar-hide">
            {categories.map((category) => (
              <button
                key={category.id}
                onClick={() => setSelectedCategory(category.id)}
                className={`flex items-center gap-2 px-4 py-2 rounded-lg transition-all whitespace-nowrap ${
                  selectedCategory === category.id
                    ? 'bg-purple-600 text-white'
                    : 'bg-gray-700 text-gray-300 hover:bg-gray-600'
                }`}
              >
                <span className="text-lg">{category.icon}</span>
                <span className="font-medium">{category.name}</span>
                <span className="text-xs bg-black/20 px-1.5 py-0.5 rounded">
                  {category.count}
                </span>
              </button>
            ))}
          </div>
        </div>
      </div>

      {/* 스트림 목록 */}
      <div className="max-w-7xl mx-auto p-4">
        <div className="mb-6">
          <h2 className="text-xl font-bold text-white mb-4 flex items-center gap-2">
            <Flame className="w-5 h-5 text-orange-500" />
            인기 라이브
          </h2>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
            {popularStreams.map((stream) => (
              <motion.div
                key={stream.id}
                whileHover={{ scale: 1.02 }}
                whileTap={{ scale: 0.98 }}
              >
                <Card 
                  className="bg-gray-800 border-gray-700 cursor-pointer hover:bg-gray-750 transition-colors overflow-hidden"
                  onClick={() => setSelectedStream(stream)}
                >
                  <div className="relative">
                    <Image
                      src={stream.thumbnail}
                      alt={stream.title}
                      width={320}
                      height={180}
                      className="w-full h-40 object-cover"
                      unoptimized
                    />
                    <div className="absolute top-2 left-2 bg-red-600 px-2 py-1 rounded text-xs font-semibold flex items-center gap-1">
                      <Radio className="w-3 h-3" />
                      LIVE
                    </div>
                    <div className="absolute bottom-2 left-2 bg-black/60 backdrop-blur px-2 py-1 rounded text-xs flex items-center gap-1">
                      <Eye className="w-3 h-3" />
                      {formatViewers(stream.viewers)}
                    </div>
                  </div>
                  <CardContent className="p-4">
                    <h3 className="font-semibold text-white mb-1 line-clamp-2">
                      {stream.title}
                    </h3>
                    <p className="text-sm text-gray-400 mb-2">{stream.streamerName}</p>
                    <div className="flex items-center justify-between text-sm">
                      <span className="text-purple-400">{stream.category}</span>
                      <div className="flex items-center gap-3 text-gray-400">
                        <span className="flex items-center gap-1">
                          <Heart className="w-3 h-3 text-pink-500" />
                          {formatViewers(stream.hearts)}
                        </span>
                        <span className="flex items-center gap-1">
                          <Coins className="w-3 h-3 text-yellow-500" />
                          {formatViewers(stream.donations)}
                        </span>
                      </div>
                    </div>
                    <div className="mt-2 flex flex-wrap gap-1">
                      {stream.tags.map((tag) => (
                        <span
                          key={tag}
                          className="text-xs bg-gray-700 px-2 py-0.5 rounded text-gray-300"
                        >
                          #{tag}
                        </span>
                      ))}
                    </div>
                  </CardContent>
                </Card>
              </motion.div>
            ))}
          </div>
        </div>

        {/* 추천 스트리머 */}
        <div className="mb-6">
          <h2 className="text-xl font-bold text-white mb-4 flex items-center gap-2">
            <Crown className="w-5 h-5 text-yellow-500" />
            추천 스트리머
          </h2>
          <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-6 gap-4">
            {[1, 2, 3, 4, 5, 6].map((i) => (
              <Card key={i} className="bg-gray-800 border-gray-700 p-4 text-center hover:bg-gray-750 transition-colors cursor-pointer">
                <div className="w-16 h-16 bg-gradient-to-br from-purple-500 to-pink-500 rounded-full mx-auto mb-2 flex items-center justify-center">
                  <StarIcon className="w-8 h-8 text-white" />
                </div>
                <h4 className="font-medium text-white text-sm mb-1">Streamer{i}</h4>
                <p className="text-xs text-gray-400">12.5K 팔로워</p>
                <Button 
                  size="sm" 
                  className="mt-2 w-full bg-purple-600 hover:bg-purple-700 text-xs"
                >
                  팔로우
                </Button>
              </Card>
            ))}
          </div>
        </div>

        {/* 스트리밍 시작 안내 */}
        <Card className="bg-gradient-to-r from-purple-900/50 to-pink-900/50 border-purple-700/50">
          <CardContent className="p-6 text-center">
            <div className="w-16 h-16 bg-purple-600 rounded-full mx-auto mb-4 flex items-center justify-center">
              <Video className="w-8 h-8 text-white" />
            </div>
            <h3 className="text-xl font-bold text-white mb-2">스트리밍을 시작해보세요!</h3>
            <p className="text-gray-300 mb-4">
              당신의 게임 플레이를 공유하고 팬들과 소통하세요
            </p>
            <Button className="bg-purple-600 hover:bg-purple-700">
              스트리밍 시작하기
            </Button>
          </CardContent>
        </Card>

        {/* 주간 랭킹 */}
        <div className="mt-8">
          <h2 className="text-xl font-bold text-white mb-4 flex items-center gap-2">
            <Trophy className="w-5 h-5 text-yellow-500" />
            주간 스트리머 랭킹
          </h2>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            {['후원 랭킹', '시청자 랭킹', '하트 랭킹'].map((rankType, index) => (
              <Card key={rankType} className="bg-gray-800 border-gray-700">
                <CardHeader className="pb-3">
                  <CardTitle className="text-lg flex items-center gap-2">
                    {index === 0 && <Coins className="w-5 h-5 text-yellow-500" />}
                    {index === 1 && <Users className="w-5 h-5 text-blue-500" />}
                    {index === 2 && <Heart className="w-5 h-5 text-pink-500" />}
                    {rankType}
                  </CardTitle>
                </CardHeader>
                <CardContent className="space-y-2">
                  {[1, 2, 3, 4, 5].map((rank) => (
                    <div key={rank} className="flex items-center justify-between p-2 hover:bg-gray-700 rounded-lg transition-colors">
                      <div className="flex items-center gap-3">
                        <span className={`font-bold ${
                          rank === 1 ? 'text-yellow-500' :
                          rank === 2 ? 'text-gray-400' :
                          rank === 3 ? 'text-orange-600' :
                          'text-gray-500'
                        }`}>
                          {rank}
                        </span>
                        <Image
                          src={`/api/placeholder/32/32`}
                          alt={`Rank ${rank}`}
                          width={32}
                          height={32}
                          className="rounded-full"
                          unoptimized
                        />
                        <span className="text-sm text-white">Streamer{rank}</span>
                      </div>
                      <span className="text-sm text-gray-400">
                        {index === 0 && `${1000 - rank * 100}K`}
                        {index === 1 && `${500 - rank * 50}K`}
                        {index === 2 && `${800 - rank * 80}K`}
                      </span>
                    </div>
                  ))}
                </CardContent>
              </Card>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}