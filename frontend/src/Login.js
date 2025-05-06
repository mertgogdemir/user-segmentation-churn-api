import React, { useState } from 'react';
import { supabase } from './supabaseClient';
import './App.css';

export default function Login({ onLogin }) {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [isRegister, setIsRegister] = useState(false);

  async function handleSubmit(e) {
    e.preventDefault();
    setLoading(true);
    setError('');
    try {
      let result;
      if (isRegister) {
        result = await supabase.auth.signUp({ email, password });
        if (result.error) throw result.error;
        alert('Kayıt başarılı! Lütfen e-posta adresinizi doğrulayın.');
      } else {
        result = await supabase.auth.signInWithPassword({ email, password });
        if (result.error) throw result.error;
        onLogin();
      }
    } catch (err) {
      setError(err.message);
    }
    setLoading(false);
  }

  return (
    <div className="login-container">
      <form className="login-form" onSubmit={handleSubmit}>
        <h2>{isRegister ? 'Kayıt Ol' : 'Giriş Yap'}</h2>
        <input
          type="email"
          placeholder="E-posta"
          value={email}
          onChange={e => setEmail(e.target.value)}
          required
        />
        <input
          type="password"
          placeholder="Şifre"
          value={password}
          onChange={e => setPassword(e.target.value)}
          required
        />
        <button type="submit" disabled={loading}>
          {loading ? '...' : isRegister ? 'Kayıt Ol' : 'Giriş Yap'}
        </button>
        <div className="login-switch">
          <span>
            {isRegister ? 'Zaten hesabın var mı?' : 'Hesabın yok mu?'}
            <button type="button" onClick={() => setIsRegister(v => !v)}>
              {isRegister ? 'Giriş Yap' : 'Kayıt Ol'}
            </button>
          </span>
        </div>
        {error && <div className="login-error">{error}</div>}
      </form>
    </div>
  );
}
