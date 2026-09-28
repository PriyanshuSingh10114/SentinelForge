import React from 'react';
import { useAuth } from '../../context/AuthContext';
import { Shield, ShieldAlert, LogOut, User, Activity } from 'lucide-react';

export const Navbar: React.FC = () => {
  const { user, logout } = useAuth();

  const getRoleBadge = (role?: string) => {
    switch (role) {
      case 'Admin':
        return 'bg-purple-950/80 text-purple-300 border-purple-700/60';
      case 'Analyst':
        return 'bg-cyan-950/80 text-cyan-300 border-cyan-700/60';
      case 'Developer':
        return 'bg-emerald-950/80 text-emerald-300 border-emerald-700/60';
      default:
        return 'bg-slate-800 text-slate-300 border-slate-700';
    }
  };

  return (
    <header className="h-14 border-b border-sentinel-800 bg-sentinel-950/90 backdrop-blur sticky top-0 z-30 flex items-center justify-between px-6">
      <div className="flex items-center space-x-3">
        <div className="w-8 h-8 rounded bg-gradient-to-br from-cyan-500 to-blue-600 flex items-center justify-center shadow-lg shadow-cyan-950/50">
          <Shield className="w-5 h-5 text-white" />
        </div>
        <div>
          <span className="font-bold tracking-wider text-base bg-gradient-to-r from-white via-slate-200 to-slate-400 bg-clip-text text-transparent">
            SENTINEL<span className="text-cyan-400">FORGE</span>
          </span>
          <span className="text-[10px] font-mono tracking-widest text-slate-500 ml-2 border border-sentinel-800 rounded px-1.5 py-0.2">
            SEC-OPS CONSOLE
          </span>
        </div>
      </div>

      <div className="hidden md:flex items-center text-xs font-mono text-amber-400/90 bg-amber-950/30 border border-amber-800/40 rounded px-2.5 py-1">
        <ShieldAlert className="w-3.5 h-3.5 mr-1.5 text-amber-400" />
        DEMO ENVIRONMENT — SYNTHETIC SECURITY DATA ONLY
      </div>

      <div className="flex items-center space-x-4">
        {user && (
          <div className="flex items-center space-x-3">
            <span className={`text-xs px-2.5 py-0.5 rounded font-mono font-medium border ${getRoleBadge(user.role)}`}>
              {user.role}
            </span>
            <div className="text-right hidden sm:block">
              <div className="text-xs font-medium text-slate-200">{user.name}</div>
              <div className="text-[11px] font-mono text-slate-400">{user.email}</div>
            </div>
            <button
              onClick={logout}
              title="Sign Out"
              className="p-1.5 text-slate-400 hover:text-red-400 hover:bg-sentinel-900 rounded transition-colors"
            >
              <LogOut className="w-4 h-4" />
            </button>
          </div>
        )}
      </div>
    </header>
  );
};
