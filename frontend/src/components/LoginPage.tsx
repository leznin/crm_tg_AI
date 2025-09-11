import React, { useState } from 'react';
import { useAuth } from '../context/AuthContext';

const LoginPage: React.FC = () => {
  const { login, error, loginLocked, lockRemainingSeconds } = useAuth();
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [submitting, setSubmitting] = useState(false);
  const [showPass, setShowPass] = useState(false);

  const onSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (loginLocked) return;
    setSubmitting(true);
    await login(email.trim().toLowerCase(), password);
    setSubmitting(false);
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-slate-900 via-indigo-900 to-slate-950 text-gray-200 p-4">
      <div className="w-full max-w-md relative">
        <div className="absolute -inset-0.5 bg-gradient-to-r from-indigo-500 via-purple-500 to-pink-500 rounded-2xl blur opacity-30" />
        <form onSubmit={onSubmit} className="relative bg-slate-900/70 backdrop-blur-xl rounded-2xl p-8 space-y-6 border border-white/10 shadow-2xl">
          <div className="text-center space-y-1">
            <h1 className="text-2xl font-semibold bg-clip-text text-transparent bg-gradient-to-r from-indigo-300 via-sky-200 to-purple-300">Вход в Telegram CRM</h1>
            <p className="text-xs text-gray-400">Введите выданные учетные данные</p>
          </div>
          <div className="space-y-4">
            <div className="space-y-2">
              <label className="text-sm font-medium text-gray-300">Email</label>
              <input
                type="email"
                required
                value={email}
                onChange={e => setEmail(e.target.value)}
                autoComplete="username"
                inputMode="email"
                spellCheck={false}
                className="w-full px-4 py-2.5 rounded-xl bg-slate-800/70 border border-white/10 focus:outline-none focus:ring-2 focus:ring-indigo-500/60 focus:border-indigo-400/40 text-sm placeholder:text-gray-500"
                placeholder="you@example.com"
              />
            </div>
            <div className="space-y-2">
              <label className="text-sm font-medium text-gray-300">Пароль</label>
              <div className="relative">
                <input
                  type={showPass ? 'text' : 'password'}
                  required
                  value={password}
                  onChange={e => setPassword(e.target.value)}
                  autoComplete="current-password"
                  className="w-full px-4 py-2.5 rounded-xl bg-slate-800/70 border border-white/10 focus:outline-none focus:ring-2 focus:ring-indigo-500/60 focus:border-indigo-400/40 text-sm placeholder:text-gray-500 pr-10"
                  placeholder="••••••••"
                />
                <button type="button" onClick={() => setShowPass(s => !s)} className="absolute inset-y-0 right-0 px-3 text-gray-400 hover:text-gray-200 text-xs">
                  {showPass ? 'Hide' : 'Show'}
                </button>
              </div>
            </div>
            {error && <div className="text-sm text-red-400 bg-red-900/30 border border-red-500/30 rounded-md px-3 py-2 select-text">{error}</div>}
            {loginLocked && (
              <div className="text-xs text-amber-300 bg-amber-900/30 border border-amber-500/30 rounded-md px-3 py-2">
                Вход временно заблокирован. Осталось секунд: {lockRemainingSeconds}
              </div>
            )}
          </div>
          <button
            type="submit"
            disabled={submitting || loginLocked}
            className="w-full py-2.5 rounded-xl bg-gradient-to-r from-indigo-600 to-purple-600 hover:from-indigo-500 hover:to-purple-500 disabled:opacity-40 font-medium text-sm tracking-wide shadow-lg shadow-indigo-950/50 transition"
          >
            {submitting ? 'Входим...' : 'Войти'}
          </button>

        </form>
      </div>
    </div>
  );
};

export default LoginPage;
