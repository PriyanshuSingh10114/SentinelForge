import React from 'react';
import { NavLink } from 'react-router-dom';
import { useAuth } from '../../context/AuthContext';
import {
  LayoutDashboard,
  AlertTriangle,
  Radio,
  FileKey,
  ShieldCheck,
  Binary,
  Sliders,
  Users,
  ScrollText,
} from 'lucide-react';

export const Sidebar: React.FC = () => {
  const { user } = useAuth();
  const isAdmin = user?.role === 'Admin';
  const isAnalystOrAdmin = user?.role === 'Admin' || user?.role === 'Analyst';

  const navItems = [
    { to: '/', label: 'Posture Dashboard', icon: LayoutDashboard, exact: true },
    { to: '/incidents', label: 'Incidents & Graph', icon: AlertTriangle },
    { to: '/events', label: 'Event Telemetry', icon: Radio },
    { to: '/dlp', label: 'DLP & Classification', icon: FileKey },
    { to: '/threats', label: 'STRIDE Threat Model', icon: ShieldCheck },
    { to: '/scans', label: 'AppSec Scans', icon: Binary },
  ];

  const adminItems = [
    { to: '/policies', label: 'Security Policies', icon: Sliders },
    { to: '/users', label: 'User & IAM Access', icon: Users },
  ];

  return (
    <aside className="w-64 border-r border-sentinel-800 bg-sentinel-950 flex flex-col justify-between py-4">
      <div className="space-y-6 px-3">
        <div>
          <div className="text-[10px] font-mono font-semibold uppercase tracking-wider text-slate-500 px-3 mb-2">
            Security Operations
          </div>
          <nav className="space-y-1">
            {navItems.map((item) => {
              const Icon = item.icon;
              return (
                <NavLink
                  key={item.to}
                  to={item.to}
                  end={item.exact}
                  className={({ isActive }) =>
                    `flex items-center space-x-3 px-3 py-2 rounded-md text-xs font-medium transition-colors ${
                      isActive
                        ? 'bg-cyan-950/60 text-cyan-300 border border-cyan-800/60 shadow-sm'
                        : 'text-slate-400 hover:text-slate-200 hover:bg-sentinel-900'
                    }`
                  }
                >
                  <Icon className="w-4 h-4" />
                  <span>{item.label}</span>
                </NavLink>
              );
            })}
          </nav>
        </div>

        {isAdmin && (
          <div>
            <div className="text-[10px] font-mono font-semibold uppercase tracking-wider text-purple-400/80 px-3 mb-2">
              Administration (Gated)
            </div>
            <nav className="space-y-1">
              {adminItems.map((item) => {
                const Icon = item.icon;
                return (
                  <NavLink
                    key={item.to}
                    to={item.to}
                    className={({ isActive }) =>
                      `flex items-center space-x-3 px-3 py-2 rounded-md text-xs font-medium transition-colors ${
                        isActive
                          ? 'bg-purple-950/60 text-purple-300 border border-purple-800/60 shadow-sm'
                          : 'text-slate-400 hover:text-slate-200 hover:bg-sentinel-900'
                      }`
                    }
                  >
                    <Icon className="w-4 h-4" />
                    <span>{item.label}</span>
                  </NavLink>
                );
              })}
            </nav>
          </div>
        )}

        {isAnalystOrAdmin && (
          <div>
            <div className="text-[10px] font-mono font-semibold uppercase tracking-wider text-slate-500 px-3 mb-2">
              Compliance & Audit
            </div>
            <nav className="space-y-1">
              <NavLink
                to="/audit-logs"
                className={({ isActive }) =>
                  `flex items-center space-x-3 px-3 py-2 rounded-md text-xs font-medium transition-colors ${
                    isActive
                      ? 'bg-cyan-950/60 text-cyan-300 border border-cyan-800/60 shadow-sm'
                      : 'text-slate-400 hover:text-slate-200 hover:bg-sentinel-900'
                  }`
                }
              >
                <ScrollText className="w-4 h-4" />
                <span>Immutable Audit Trail</span>
              </NavLink>
            </nav>
          </div>
        )}
      </div>

      <div className="px-6 text-[11px] font-mono text-slate-500 border-t border-sentinel-800/60 pt-4">
        <div>SentinelForge v1.0.0</div>
        <div className="text-[10px] text-slate-600">Deterministic Control Core</div>
      </div>
    </aside>
  );
};
