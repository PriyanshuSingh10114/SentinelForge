import React, { useState, useEffect } from 'react';
import { api } from '../api/client';
import { Users, UserPlus, ShieldCheck, Mail, Calendar, CheckCircle, XCircle } from 'lucide-react';

interface User {
  id: string;
  email: string;
  name: string;
  role: string | { id?: string; name: string };
  is_active: boolean;
  failed_login_attempts: number;
  last_login_at: string | null;
  created_at: string;
}

export const UsersPage: React.FC = () => {
  const [users, setUsers] = useState<User[]>([]);
  const [loading, setLoading] = useState(true);
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [email, setEmail] = useState('');
  const [name, setName] = useState('');
  const [password, setPassword] = useState('');
  const [roleName, setRoleName] = useState('DEVELOPER');
  const [error, setError] = useState<string | null>(null);

  const fetchUsers = async () => {
    try {
      setLoading(true);
      const res = await api.getUsers();
      setUsers(Array.isArray(res) ? res : (res as any).data || []);
    } catch (err: any) {
      setError(err.message || 'Failed to fetch users');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchUsers();
  }, []);

  const handleCreate = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      await api.createUser({
        email,
        name,
        password,
        role_name: roleName,
      });
      setShowCreateModal(false);
      setEmail('');
      setName('');
      setPassword('');
      fetchUsers();
    } catch (err: any) {
      alert('Failed to provision user: ' + err.message);
    }
  };

  const getRoleBadge = (role: string) => {
    const r = (role || '').toUpperCase();
    switch (r) {
      case 'ADMIN':
        return 'bg-purple-50 text-purple-700 border-purple-200';
      case 'ANALYST':
      case 'SECURITY_ANALYST':
        return 'bg-cyan-50 text-cyan-700 border-cyan-200';
      case 'DEVELOPER':
        return 'bg-indigo-50 text-indigo-700 border-indigo-200';
      default:
        return 'bg-slate-100 text-slate-700 border-slate-200';
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-slate-900 tracking-tight flex items-center gap-2">
            <Users className="w-7 h-7 text-indigo-600" />
            Users & IAM Roles
          </h1>
          <p className="text-sm text-slate-500 mt-1">
            Enterprise identity management, least-privilege RBAC role enforcement, and lockout status.
          </p>
        </div>
        <button
          onClick={() => setShowCreateModal(true)}
          className="flex items-center gap-2 px-4 py-2 bg-indigo-600 hover:bg-indigo-700 text-white text-sm font-medium rounded-lg transition-colors shadow-sm"
        >
          <UserPlus className="w-4 h-4" />
          Provision Identity
        </button>
      </div>

      {error && (
        <div className="p-4 bg-red-50 border border-red-200 rounded-lg text-red-700 text-sm">
          {error}
        </div>
      )}

      <div className="bg-white border border-slate-200 rounded-xl overflow-hidden shadow-sm">
        <div className="overflow-x-auto">
          <table className="w-full text-left text-sm text-slate-700">
            <thead className="bg-slate-50 text-slate-600 text-xs uppercase tracking-wider border-b border-slate-200">
              <tr>
                <th className="px-6 py-4 font-semibold">User</th>
                <th className="px-6 py-4 font-semibold">Role</th>
                <th className="px-6 py-4 font-semibold">Account Status</th>
                <th className="px-6 py-4 font-semibold">Failed Logins</th>
                <th className="px-6 py-4 font-semibold">Last Authentication</th>
                <th className="px-6 py-4 font-semibold">Created</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-200">
              {loading ? (
                <tr>
                  <td colSpan={6} className="px-6 py-8 text-center text-slate-500">
                    Loading directory users...
                  </td>
                </tr>
              ) : users.length === 0 ? (
                <tr>
                  <td colSpan={6} className="px-6 py-8 text-center text-slate-500">
                    No active user records found.
                  </td>
                </tr>
              ) : (
                users.map((u) => (
                  <tr key={u.id} className="hover:bg-slate-50 transition-colors">
                    <td className="px-6 py-4">
                      <div className="flex items-center gap-3">
                        <div className="w-8 h-8 rounded-full bg-slate-100 border border-slate-200 flex items-center justify-center text-xs font-semibold text-slate-700">
                          {u.name.substring(0, 2).toUpperCase()}
                        </div>
                        <div>
                          <div className="font-semibold text-slate-900">{u.name}</div>
                          <div className="text-xs text-slate-500 flex items-center gap-1">
                            <Mail className="w-3 h-3 text-slate-400" />
                            {u.email}
                          </div>
                        </div>
                      </div>
                    </td>
                    <td className="px-6 py-4">
                      {(() => {
                        const roleName = typeof u.role === 'string' ? u.role : (u.role?.name || 'Viewer');
                        return (
                          <span className={`px-2 py-0.5 rounded text-xs font-semibold border ${getRoleBadge(roleName)}`}>
                            {roleName.toUpperCase()}
                          </span>
                        );
                      })()}
                    </td>
                    <td className="px-6 py-4">
                      {u.is_active ? (
                        <span className="flex items-center gap-1.5 text-xs font-medium text-emerald-400">
                          <CheckCircle className="w-3.5 h-3.5" />
                          Active
                        </span>
                      ) : (
                        <span className="flex items-center gap-1.5 text-xs font-medium text-red-400">
                          <XCircle className="w-3.5 h-3.5" />
                          Locked / Suspended
                        </span>
                      )}
                    </td>
                    <td className="px-6 py-4">
                      <span className={`text-xs font-semibold ${u.failed_login_attempts >= 5 ? 'text-red-400' : 'text-slate-400'}`}>
                        {u.failed_login_attempts} strikes
                      </span>
                    </td>
                    <td className="px-6 py-4 text-xs text-slate-400">
                      {u.last_login_at ? new Date(u.last_login_at).toLocaleString() : 'Never'}
                    </td>
                    <td className="px-6 py-4 text-xs text-slate-400">
                      <div className="flex items-center gap-1">
                        <Calendar className="w-3.5 h-3.5 text-slate-500" />
                        {new Date(u.created_at).toLocaleDateString()}
                      </div>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>

      {showCreateModal && (
        <div className="fixed inset-0 bg-slate-900/40 backdrop-blur-sm flex items-center justify-center p-4 z-50">
          <div className="bg-white border border-slate-200 rounded-xl max-w-md w-full p-6 space-y-4 shadow-2xl">
            <h2 className="text-lg font-bold text-slate-900 flex items-center gap-2">
              <ShieldCheck className="w-5 h-5 text-indigo-600" />
              Provision Enterprise User
            </h2>
            <form onSubmit={handleCreate} className="space-y-4">
              <div>
                <label className="block text-xs font-semibold text-slate-700 mb-1">Full Name</label>
                <input
                  type="text"
                  required
                  value={name}
                  onChange={(e) => setName(e.target.value)}
                  placeholder="e.g., Alex Vance"
                  className="w-full bg-white border border-slate-300 rounded-lg px-3 py-2 text-sm text-slate-900 placeholder-slate-400 focus:outline-none focus:border-indigo-500"
                />
              </div>
              <div>
                <label className="block text-xs font-semibold text-slate-700 mb-1">Email Address</label>
                <input
                  type="email"
                  required
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  placeholder="e.g., avance@sentinelforge.local"
                  className="w-full bg-white border border-slate-300 rounded-lg px-3 py-2 text-sm text-slate-900 placeholder-slate-400 focus:outline-none focus:border-indigo-500"
                />
              </div>
              <div>
                <label className="block text-xs font-semibold text-slate-700 mb-1">Initial Password</label>
                <input
                  type="password"
                  required
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  placeholder="Min 8 characters, numbers & symbols"
                  className="w-full bg-white border border-slate-300 rounded-lg px-3 py-2 text-sm text-slate-900 placeholder-slate-400 focus:outline-none focus:border-indigo-500"
                />
              </div>
              <div>
                <label className="block text-xs font-semibold text-slate-700 mb-1">Assigned RBAC Role</label>
                <select
                  value={roleName}
                  onChange={(e) => setRoleName(e.target.value)}
                  className="w-full bg-white border border-slate-300 rounded-lg px-3 py-2 text-sm text-slate-900 focus:outline-none focus:border-indigo-500"
                >
                  <option value="VIEWER">VIEWER (Read-Only Audit)</option>
                  <option value="DEVELOPER">DEVELOPER (Scan & DLPs)</option>
                  <option value="SECURITY_ANALYST">SECURITY_ANALYST (Triage & Investigate)</option>
                  <option value="ADMIN">ADMIN (Full Authority & Approvals)</option>
                </select>
              </div>
              <div className="flex justify-end gap-3 pt-2">
                <button
                  type="button"
                  onClick={() => setShowCreateModal(false)}
                  className="px-4 py-2 bg-slate-100 hover:bg-slate-200 text-slate-700 text-sm font-medium rounded-lg transition-colors"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="px-4 py-2 bg-indigo-600 hover:bg-indigo-700 text-white text-sm font-medium rounded-lg transition-colors"
                >
                  Provision User
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};
export default UsersPage;
