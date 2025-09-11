import React from 'react';
import { AppProvider } from './context/AppContext';
import { AuthProvider, useAuth } from './context/AuthContext';
import Layout from './components/Layout';
import LoginPage from './components/LoginPage';

const AppContent: React.FC = () => {
  const { isAuthenticated, loading } = useAuth();
  
  if (loading) {
    return (
      <div className="h-screen flex items-center justify-center bg-slate-900 text-gray-300">Загрузка...</div>
    );
  }
  
  // Only load AppProvider for authenticated users
  if (isAuthenticated) {
    return (
      <AppProvider>
        <Layout />
      </AppProvider>
    );
  }
  
  return <LoginPage />;
};

function App() {
  return (
    <AuthProvider>
      <AppContent />
    </AuthProvider>
  );
}

export default App;