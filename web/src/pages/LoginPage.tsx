import { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { api } from '../lib/api';

export default function LoginPage({ mode = 'login' }: { mode?: 'login' | 'register' }) {
  const navigate = useNavigate();
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [phone, setPhone] = useState('');
  const [err, setErr] = useState('');

  const submit = async () => {
    setErr('');
    try {
      if (mode === 'register') {
        await api.register({ username, password, phone, language: 'uz' });
      } else {
        await api.login(username, password);
      }
      navigate('/app');
    } catch (e) {
      setErr(mode === 'register' ? 'Ro\'yxatdan o\'tishda xatolik' : 'Login yoki parol noto\'g\'ri');
    }
  };

  return (
    <div className="max-w-md mx-auto px-4 py-16">
      <h1 className="font-heading text-2xl font-bold">
        {mode === 'login' ? 'Kirish' : 'Ro\'yxatdan o\'tish'}
      </h1>
      <p className="text-muted text-sm mt-1">
        {mode === 'login'
          ? 'Xisobingizga kiring va xarita bilan ishlang'
          : 'Yangi hisob yarating — bir daqiqa'}
      </p>

      <div className="card mt-6 space-y-4">
        <div>
          <label className="text-sm text-muted">Login</label>
          <input className="input mt-1" value={username} onChange={(e) => setUsername(e.target.value)} />
        </div>
        {mode === 'register' && (
          <div>
            <label className="text-sm text-muted">Telefon (ixtiyoriy)</label>
            <input className="input mt-1" value={phone} onChange={(e) => setPhone(e.target.value)} placeholder="+9989XXXXXXXX" />
          </div>
        )}
        <div>
          <label className="text-sm text-muted">Parol</label>
          <input type="password" className="input mt-1" value={password} onChange={(e) => setPassword(e.target.value)} onKeyDown={(e) => e.key === 'Enter' && submit()} />
        </div>
        {err && <p className="text-danger text-sm">{err}</p>}
        <button onClick={submit} className="btn-primary w-full !py-3">
          {mode === 'login' ? 'Kirish' : 'Ro\'yxatdan o\'tish'}
        </button>
        <p className="text-muted text-sm text-center">
          {mode === 'login' ? (
            <>Hisobingiz yo'qmi? <Link to="/register" className="text-cyan">Ro'yxatdan o'ting</Link></>
          ) : (
            <>Hisobingiz bormi? <Link to="/login" className="text-cyan">Kiring</Link></>
          )}
        </p>
      </div>
    </div>
  );
}
