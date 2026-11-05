import React from 'react';
import { useAuth } from '../../context/AuthContext';
import { ShieldAlert, LogOut, User, Activity } from 'lucide-react';
import { SentinelLogo } from '../ui/SentinelLogo';

export const Navbar: React.FC = () => {
  const { user, logout } = useAuth();

  const getRoleBadge = (role?: string) => {
    switch (role) {
      case 'Admin':
        return 'bg-purple-50 text-purple-700 border-purple-200';
      case 'Analyst':
        return 'bg-cyan-50 text-cyan-700 border-cyan-200';
      case 'Developer':
        return 'bg-emerald-50 text-emerald-700 border-emerald-200';
      default:
        return 'bg-slate-100 text-slate-700 border-slate-200';
    }
  };

  return (
    <header className="h-14 border-b border-slate-200 bg-white sticky top-0 z-30 flex items-center justify-between px-6 shadow-sm">
      <div className="flex items-center space-x-3">
        <SentinelLogo size={34} />
        <div>
          <span className="font-extrabold tracking-wider text-base bg-gradient-to-r from-cyan-600 via-indigo-600 to-slate-900 bg-clip-text text-transparent">
            SENTINEL<span className="text-cyan-600">FORGE</span>
          </span>
          <span className="text-[10px] font-mono tracking-widest text-cyan-700 ml-2 border border-cyan-200 rounded px-1.5 py-0.5 bg-cyan-50 font-medium">
            SEC-OPS CONSOLE
          </span>
        </div>
      </div>

      <div className="hidden md:flex items-center text-xs font-mono text-amber-800 bg-amber-50 border border-amber-200 rounded px-2.5 py-1">
        <ShieldAlert className="w-3.5 h-3.5 mr-1.5 text-amber-600" />
        DEMO ENVIRONMENT — SYNTHETIC SECURITY DATA ONLY
      </div>

      <div className="flex items-center space-x-4">
        {user && (
          <div className="flex items-center space-x-3">
            <span className={`text-xs px-2.5 py-0.5 rounded font-mono font-medium border ${getRoleBadge(user.role)}`}>
              {user.role}
            </span>
            <div className="text-right hidden sm:block">
              <div className="text-xs font-medium text-slate-800">{user.name}</div>
              <div className="text-[11px] font-mono text-slate-500">{user.email}</div>
            </div>
            <button
              onClick={logout}
              title="Sign Out"
              className="p-1.5 text-slate-500 hover:text-red-600 hover:bg-slate-100 rounded transition-colors"
            >
              <LogOut className="w-4 h-4" />
            </button>
          </div>
        )}
      </div>
    </header>
  );
};
