import { Metadata } from 'next';
import AdminLoginForm from '../../../components/auth/AdminLoginForm';
import { Suspense } from 'react';

export const metadata: Metadata = {
    title: '관리자 로그인 - 모델카지노',
    description: '관리자 전용 로그인 페이지',
};

export default function AdminLoginPage() {
    return (
        <div className="auth-container">
            <div className="auth-card">
                <Suspense fallback={null}>
                    <AdminLoginForm
                        onSwitchToLogin={() => {
                            window.location.href = '/auth';
                        }}
                    />
                </Suspense>
            </div>
        </div>
    );
}
