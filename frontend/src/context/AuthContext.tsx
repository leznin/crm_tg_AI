import React, { createContext, useContext, useEffect, useState, ReactNode, useCallback } from 'react';

interface AuthContextType {
  isAuthenticated: boolean;
  login: (email: string, password: string) => Promise<boolean>;
  logout: () => void;
  loading: boolean;
  error: string | null;
  loginLocked: boolean;
  lockRemainingSeconds: number;
  user: any | null;
}

const AuthContext = createContext<AuthContextType | null>(null);

const API_BASE_URL = 'http://localhost:8000';
const LS_KEY = 'telegram_crm_logged_in';
const META_KEY = 'telegram_crm_login_meta';
const MAX_ATTEMPTS = 5; // attempts before lock
const LOCK_MINUTES = 5; // lock duration

// Function to clear all app data from localStorage
const clearAppData = () => {
  const keysToRemove = [
    'telegram_crm_config',
    'telegram_crm_accounts', 
    'telegram_crm_chats_v2',
    'telegram_crm_managers',
    'telegram_crm_transfers',
    'telegram_crm_keywords',
    'telegram_crm_schema_version',
    'telegram_crm_chat_members',
    'telegram_crm_two_managers_seeded'
  ];
  
  keysToRemove.forEach(key => {
    localStorage.removeItem(key);
  });
};

export const AuthProvider: React.FC<{ children: ReactNode }> = ({ children }) => {
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [loginLocked, setLoginLocked] = useState(false);
  const [lockRemainingSeconds, setLockRemainingSeconds] = useState(0);
  const [user, setUser] = useState<any | null>(null);

  // helper to read/update meta
  const readMeta = () => {
    try {
      return JSON.parse(localStorage.getItem(META_KEY) || 'null') as { attempts: number; lockedUntil?: number } | null;
    } catch { return null; }
  };

  const writeMeta = (meta: { attempts: number; lockedUntil?: number }) => {
    localStorage.setItem(META_KEY, JSON.stringify(meta));
  };

  // Lock countdown effect
  useEffect(() => {
    const interval = setInterval(() => {
      const meta = readMeta();
      if (meta?.lockedUntil) {
        const now = Date.now();
        if (now < meta.lockedUntil) {
          setLoginLocked(true);
          setLockRemainingSeconds(Math.ceil((meta.lockedUntil - now) / 1000));
        } else {
          setLoginLocked(false);
          setLockRemainingSeconds(0);
          writeMeta({ attempts: 0 });
        }
      } else {
        setLoginLocked(false);
        setLockRemainingSeconds(0);
      }
    }, 1000);
    return () => clearInterval(interval);
  }, []);

  // Check authentication on mount
  useEffect(() => {
    const checkAuth = async () => {
      // Only check with server if we have indication of being logged in
      const wasLoggedIn = localStorage.getItem(LS_KEY) === 'true';
      
      if (!wasLoggedIn) {
        // If no indication of being logged in, skip server check
        setIsAuthenticated(false);
        setUser(null);
        setLoading(false);
        return;
      }

      try {
        const response = await fetch(`${API_BASE_URL}/api/v1/auth/me`, {
          credentials: 'include',
        });
        
        if (response.ok) {
          const userData = await response.json();
          setUser(userData);
          setIsAuthenticated(true);
          localStorage.setItem(LS_KEY, 'true');
        } else {
          setIsAuthenticated(false);
          setUser(null);
          localStorage.removeItem(LS_KEY);
          // Clear all app data for unauthenticated users
          clearAppData();
        }
      } catch (error) {
        console.warn('Auth check failed:', error);
        setIsAuthenticated(false);
        setUser(null);
        localStorage.removeItem(LS_KEY);
        // Clear all app data for unauthenticated users
        clearAppData();
      } finally {
        setLoading(false);
      }
    };

    checkAuth();
  }, []);

  const login = useCallback(async (email: string, password: string) => {
    setError(null);
    const meta = readMeta() || { attempts: 0 };
    
    if (meta.lockedUntil && Date.now() < meta.lockedUntil) {
      setLoginLocked(true);
      setError('Слишком много попыток. Попробуйте позже.');
      return false;
    }

    try {
      // Get CSRF token
      const csrfResponse = await fetch(`${API_BASE_URL}/api/v1/auth/csrf-token`, {
        credentials: 'include',
      });
      
      if (!csrfResponse.ok) {
        throw new Error('Failed to get CSRF token');
      }
      
      const { csrf_token } = await csrfResponse.json();
      
      // Login request
      const response = await fetch(`${API_BASE_URL}/api/v1/auth/login`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        credentials: 'include',
        body: JSON.stringify({
          email,
          password,
          csrf_token
        }),
      });

      if (response.ok) {
        const data = await response.json();
        setUser(data.user);
        setIsAuthenticated(true);
        localStorage.setItem(LS_KEY, 'true');
        writeMeta({ attempts: 0 });
        return true;
      } else {
        let errorData;
        try {
          errorData = await response.json();
        } catch {
          errorData = { detail: 'Ошибка сервера' };
        }
        
        const attempts = meta.attempts + 1;
        
        if (attempts >= MAX_ATTEMPTS) {
          const lockedUntil = Date.now() + LOCK_MINUTES * 60 * 1000;
          writeMeta({ attempts, lockedUntil });
          setLoginLocked(true);
          setError('Слишком много попыток. Попробуйте позже.');
        } else {
          writeMeta({ attempts });
          setError(errorData.detail || 'Неверный логин или пароль');
        }
        
        setIsAuthenticated(false);
        setUser(null);
        localStorage.removeItem(LS_KEY);
        // Clear all app data for unauthenticated users
        clearAppData();
        return false;
      }
    } catch (error) {
      console.error('Login error:', error);
      setError('Ошибка подключения к серверу');
      return false;
    }
  }, []);

  const logout = useCallback(async () => {
    try {
      await fetch(`${API_BASE_URL}/api/v1/auth/logout`, {
        method: 'POST',
        credentials: 'include',
      });
    } catch (error) {
      console.error('Logout error:', error);
    } finally {
      setIsAuthenticated(false);
      setUser(null);
      localStorage.removeItem(LS_KEY);
      // Clear all app data when logging out
      clearAppData();
    }
  }, []);

  return (
    <AuthContext.Provider value={{ isAuthenticated, login, logout, loading, error, loginLocked, lockRemainingSeconds, user }}>
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error('useAuth must be used inside AuthProvider');
  return ctx;
};
