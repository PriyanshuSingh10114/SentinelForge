import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { Shield, Lock, Mail, AlertCircle, ArrowRight, UserCheck } from 'lucide-react';

const DEMO_PRESETS = [
  { role: 'Admin', email: 'admin@sentinelforge.local', pass: 'SentinelAdmin123!', desc: 'Full authority: Policies, users, HITL approvals' },
  { role: 'Analyst', email: 'analyst@sentinelforge.local', pass: 'SentinelAnalyst123!', desc: 'Investigate incidents, run AI agent, inspect evidence' },
  { role: 'Developer', email: 'developer@sentinelforge.local', pass: 'SentinelDev123!', desc: 'Submit scans, review own findings (no policy access)' },
  { role: 'Viewer', email: 'viewer@sentinelforge.local', pass: 'SentinelViewer123!', desc: 'Read-only telemetry observer' },
];

export const LoginPage: React.FC = () => {
  const { login } = useAuth();
  const navigate = useNavigate();
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    try {
      await login(email, password);
      navigate('/');
    } catch (err: any) {
      setError(err.message || 'Authentication failed');
    } finally {
      setLoading(false);
    }
  };

  const handlePresetSelect = (preset: typeof DEMO_PRESETS[0]) => {
    setEmail(preset.email);
    setPassword(preset.pass);
  };

  return (
    <div className="min-h-screen bg-sentinel-950 flex flex-col justify-center items-center px-4 relative overflow-hidden">
      {/* Background Subtle Grid Accent */}
      <div className="absolute inset-0 bg-[linear-gradient(to_right,#0c1017_1px,transparent_1px),linear-gradient(to_bottom,#0c1017_1px,transparent_1px)] bg-[size:4rem_4rem] [mask-image:radial-gradient(ellipse_60%_50%_at_50%_50%,#000_70%,transparent_100%)] pointer-events-none" />

      <div className="w-full max-w-md z-10">
        <div className="text-center mb-8">
          <div className="inline-flex w-12 h-12 rounded-xl bg-gradient-to-tr from-cyan-600 to-blue-600 items-center justify-center shadow-xl shadow-cyan-950/60 mb-3">
            <Shield className="w-7 h-7 text-white" />
          </div>
          <h1 className="text-2xl font-bold tracking-tight text-white">
            SENTINEL<span className="text-cyan-400">FORGE</span>
          </h1>
          <p className="text-xs font-mono text-slate-400 mt-1">Enterprise Security Engineering Platform</p>
        </div>

        <div className="bg-sentinel-900/90 border border-sentinel-800 rounded-xl p-6 shadow-2xl backdrop-blur-md">
          {error && (
            <div className="mb-4 p-3 bg-red-950/60 border border-red-800/80 rounded-lg flex items-start space-x-2 text-xs text-red-300">
              <AlertCircle className="w-4 h-4 text-red-400 shrink-0 mt-0.5" />
              <span>{error}</span>
            </div>
          )}

          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <label className="block text-xs font-mono text-slate-300 mb-1">EMAIL PRINCIPAL</label>
              <div className="relative">
                <Mail className="w-4 h-4 text-slate-500 absolute left-3 top-2.5" />
                <input
                  type="email"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  required
                  placeholder="analyst@sentinelforge.local"
                  className="w-full bg-sentinel-950 border border-sentinel-700/80 rounded-lg pl-9 pr-3 py-2 text-xs text-slate-200 placeholder-slate-600 focus:outline-none focus:border-cyan-500 transition-colors"
                />
              </div>
            </div>

            <div>
              <label className="block text-xs font-mono text-slate-300 mb-1">PASSWORD CREDENTIAL</label>
              <div className="relative">
                <Lock className="w-4 h-4 text-slate-500 absolute left-3 top-2.5" />
                <input
                  type="password"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  required
                  placeholder="••••••••••••"
                  className="w-full bg-sentinel-950 border border-sentinel-700/80 rounded-lg pl-9 pr-3 py-2 text-xs text-slate-200 placeholder-slate-600 focus:outline-none focus:border-cyan-500 transition-colors"
                />
              </div>
            </div>

            <button
              type="submit"
              disabled={loading}
              className="w-full bg-gradient-to-r from-cyan-600 to-blue-600 hover:from-cyan-500 hover:to-blue-500 text-white font-medium py-2 rounded-lg text-xs transition-all flex items-center justify-center space-x-1.5 shadow-lg shadow-cyan-950/40 disabled:opacity-50"
            >
              <span>{loading ? 'Verifying Credentials...' : 'Authenticate'}</span>
              <ArrowRight className="w-3.5 h-3.5" />
            </button>
          </form>

          {/* Preset Demo Accounts for Technical Interview */}
          <div className="mt-6 pt-5 border-t border-sentinel-800">
            <div className="flex items-center space-x-1 text-[11px] font-mono text-slate-400 mb-2.5">
              <UserCheck className="w-3.5 h-3.5 text-cyan-400" />
              <span>PRESET DEMO CREDENTIALS:</span>
            </div>
            <div className="grid grid-cols-2 gap-2">
              {DEMO_PRESETS.map((preset) => (
                <button
                  key={preset.role}
                  type="button"
                  onClick={() => handlePresetSelect(preset)}
                  className="text-left p-2 rounded-lg bg-sentinel-950 hover:bg-sentinel-800 border border-sentinel-800 hover:border-cyan-800/80 transition-all text-[11px]"
                >
                  <div className="font-semibold text-cyan-300 flex items-center justify-between">
                    <span>{preset.role}</span>
                    <span className="text-[9px] font-mono text-slate-500">Select</span>
                  </div>
                  <div className="text-[10px] text-slate-400 truncate">{preset.desc}</div>
                </button>
              ))}
            </div>
          </div>
        </div>

        <div className="text-center text-[11px] font-mono text-slate-500 mt-4">
          Deterministic Control Enforcement • Passwords Never Logged
        </div>
      </div>
    </div>
  );
};
