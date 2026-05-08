import { AuthProvider, useAuth } from './hooks/useAuth';
import LoginPage from './pages/LoginPage';
import { ChatPage } from './pages/ChatPage';
import './App.css';

function AppInner() {
  const { user, isLoading } = useAuth();
  if (isLoading) {
    return <div className="min-h-screen flex items-center justify-center text-gray-400">Loading...</div>;
  }
  return user ? <ChatPage /> : <LoginPage />;
}

function App() {
  return (
    <AuthProvider>
      <AppInner />
    </AuthProvider>
  );
}

export default App
