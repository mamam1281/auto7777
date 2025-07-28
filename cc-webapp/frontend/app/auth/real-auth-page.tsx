'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import { useAuth } from '../../lib/auth';
import Link from 'next/link';

const RealAuthPage = () => {
    const [isLogin, setIsLogin] = useState(true);
    const [isLoading, setIsLoading] = useState(false);
    const [formData, setFormData] = useState({
        site_id: '',
        password: '',
        nickname: '',
        phone_number: '',
        invite_code: ''
    });
    const [error, setError] = useState('');

    const { login } = useAuth();
    const router = useRouter();

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        setIsLoading(true);
        setError('');

        try {
            // 단순화된 로그인 처리
            // 백엔드 요청을 생략하고 더미 데이터로 직접 로그인 처리
            // 실제 구현에서는 백엔드 API 연동이 필요

            const userData = {
                id: 1,
                site_id: formData.site_id,
                nickname: "사용자",
                phone_number: "010-1234-5678",
                cyber_token_balance: 1000,
                rank: "STANDARD"
            };

            // 더미 토큰 생성
            const token = "dummy_token_" + Math.random().toString(36).substring(2);

            // 로그인 처리
            login(token, userData);

            // 메인 페이지로 리디렉션
            router.push('/');

        } catch (err: any) {
            setError(err.message || '로그인 처리 중 오류가 발생했습니다.');
        } finally {
            setIsLoading(false);
        }
    };

    return (
        <div className="min-h-screen bg-gray-900 flex items-center justify-center">
            <div className="bg-gray-800 p-8 rounded-lg border border-gray-700 w-96">
                <h1 className="text-2xl font-bold text-white mb-6 text-center">
                    {isLogin ? '로그인' : '회원가입'}
                </h1>

                {error && (
                    <div className="bg-red-600 text-white p-3 rounded mb-4 text-sm">
                        {error}
                    </div>
                )}

                <form onSubmit={handleSubmit} className="space-y-4">
                    <div>
                        <label htmlFor="site-id" className="block text-gray-300 text-sm mb-2">사이트 ID</label>
                        <input
                            id="site-id"
                            type="text"
                            value={formData.site_id}
                            onChange={(e) => setFormData({ ...formData, site_id: e.target.value })}
                            className="w-full bg-gray-700 text-white px-3 py-2 rounded border border-gray-600 focus:border-blue-500"
                            required
                        />
                    </div>

                    <div>
                        <label htmlFor="password" className="block text-gray-300 text-sm mb-2">비밀번호</label>
                        <input
                            id="password"
                            type="password"
                            value={formData.password}
                            onChange={(e) => setFormData({ ...formData, password: e.target.value })}
                            className="w-full bg-gray-700 text-white px-3 py-2 rounded border border-gray-600 focus:border-blue-500"
                            required
                        />
                    </div>

                    {!isLogin && (
                        <>
                            <div>
                                <label className="block text-gray-300 text-sm mb-2">닉네임</label>
                                <input
                                    type="text"
                                    value={formData.nickname}
                                    onChange={(e) => setFormData({ ...formData, nickname: e.target.value })}
                                    className="w-full bg-gray-700 text-white px-3 py-2 rounded border border-gray-600 focus:border-blue-500"
                                    required
                                />
                            </div>

                            <div>
                                <label className="block text-gray-300 text-sm mb-2">전화번호</label>
                                <input
                                    type="tel"
                                    value={formData.phone_number}
                                    onChange={(e) => setFormData({ ...formData, phone_number: e.target.value })}
                                    className="w-full bg-gray-700 text-white px-3 py-2 rounded border border-gray-600 focus:border-blue-500"
                                    required
                                />
                            </div>

                            <div>
                                <label className="block text-gray-300 text-sm mb-2">초대코드</label>
                                <input
                                    type="text"
                                    value={formData.invite_code}
                                    onChange={(e) => setFormData({ ...formData, invite_code: e.target.value })}
                                    className="w-full bg-gray-700 text-white px-3 py-2 rounded border border-gray-600 focus:border-blue-500"
                                    required
                                />
                            </div>
                        </>
                    )}

                    <button
                        type="submit"
                        disabled={isLoading}
                        className="w-full bg-blue-600 hover:bg-blue-700 disabled:bg-gray-600 text-white py-3 px-4 rounded transition-colors"
                    >
                        {isLoading ? '처리 중...' : (isLogin ? '로그인' : '회원가입')}
                    </button>
                </form>

                <div className="mt-4 text-center">
                    <button
                        onClick={() => setIsLogin(!isLogin)}
                        className="text-blue-400 hover:text-blue-300 text-sm"
                    >
                        {isLogin ? '회원가입하기' : '로그인하기'}
                    </button>

                    <div className="mt-3 pt-3 border-t border-gray-700">
                        <a href="/admin-login" className="text-red-400 hover:text-red-300 text-sm">
                            관리자 로그인
                        </a>
                    </div>
                </div>
            </div>
        </div>
    );
};

export default RealAuthPage;
