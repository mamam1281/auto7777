'use client';

interface AdminLayoutProps {
    children: React.ReactNode;
}

const AdminLayout: React.FC<AdminLayoutProps> = ({ children }) => {
    return (
        <div className="min-h-screen bg-gray-900 text-white">
            {children}
        </div>
    );
};

export default AdminLayout;
