import React, { useState, useEffect } from 'react';
import { api } from '../api/client';
import { History, Shield, CheckCircle2, XCircle, Search, Filter } from 'lucide-react';

interface AuditLog {
  id: string;
  actor_id: string;
  action: string;
  resource_type: string;
  resource_id: string | null;
  result: string;
  metadata_payload: any;
  timestamp: string;
}

export const AuditLogsPage: React.FC = () => {
  const [logs, setLogs] = useState<AuditLog[]>([]);
  const [loading, setLoading] = useState(true);
  const [actionFilter, setActionFilter] = useState('');
  const [searchTerm, setSearchTerm] = useState('');

  const fetchLogs = async () => {
    try {
      setLoading(true);
      const res = await api.getAuditLogs({ limit: 100 });
      setLogs(Array.isArray(res) ? res : (res as any).data || []);
    } catch (err: any) {
      console.error('Failed to fetch audit logs', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchLogs();
  }, []);

  const filteredLogs = logs.filter((log) => {
    const matchesAction = actionFilter ? log.action.includes(actionFilter) : true;
    const matchesSearch = searchTerm
      ? (log.actor_id && log.actor_id.toLowerCase().includes(searchTerm.toLowerCase())) ||
        (log.resource_type && log.resource_type.toLowerCase().includes(searchTerm.toLowerCase())) ||
        (log.action && log.action.toLowerCase().includes(searchTerm.toLowerCase()))
      : true;
    return matchesAction && matchesSearch;
  });

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-white tracking-tight flex items-center gap-2">
            <History className="w-7 h-7 text-indigo-400" />
            Immutable Audit Trail
          </h1>
          <p className="text-sm text-slate-400 mt-1">
            Tamper-evident system audit log of security events, administrative policies, and human approvals.
          </p>
        </div>
      </div>

      <div className="flex flex-col sm:flex-row gap-3">
        <div className="relative flex-1">
          <Search className="w-4 h-4 text-slate-500 absolute left-3 top-3" />
          <input
            type="text"
            placeholder="Search by Actor ID, Action, or Resource..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="w-full pl-9 pr-4 py-2 bg-slate-900 border border-slate-800 rounded-lg text-sm text-slate-200 focus:outline-none focus:border-indigo-500"
          />
        </div>
        <div className="relative sm:w-64">
          <Filter className="w-4 h-4 text-slate-500 absolute left-3 top-3" />
          <select
            value={actionFilter}
            onChange={(e) => setActionFilter(e.target.value)}
            className="w-full pl-9 pr-4 py-2 bg-slate-900 border border-slate-800 rounded-lg text-sm text-slate-200 focus:outline-none focus:border-indigo-500"
          >
            <option value="">All Actions</option>
            <option value="USER_LOGIN">USER_LOGIN</option>
            <option value="FAILED_LOGIN">FAILED_LOGIN</option>
            <option value="POLICY_">POLICY Operations</option>
            <option value="REMEDIATION_">REMEDIATION Actions</option>
            <option value="INVESTIGATION_">INVESTIGATION Events</option>
            <option value="DLP_">DLP Detections</option>
          </select>
        </div>
      </div>

      <div className="bg-slate-900 border border-slate-800 rounded-xl overflow-hidden shadow-sm">
        <div className="overflow-x-auto">
          <table className="w-full text-left text-sm text-slate-300">
            <thead className="bg-slate-950 text-slate-400 text-xs uppercase tracking-wider border-b border-slate-800">
              <tr>
                <th className="px-6 py-4">Timestamp (UTC)</th>
                <th className="px-6 py-4">Action</th>
                <th className="px-6 py-4">Actor</th>
                <th className="px-6 py-4">Resource</th>
                <th className="px-6 py-4">Result</th>
                <th className="px-6 py-4">Details / Metadata</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800">
              {loading ? (
                <tr>
                  <td colSpan={6} className="px-6 py-8 text-center text-slate-500">
                    Loading cryptographic audit events...
                  </td>
                </tr>
              ) : filteredLogs.length === 0 ? (
                <tr>
                  <td colSpan={6} className="px-6 py-8 text-center text-slate-500">
                    No matching audit records found.
                  </td>
                </tr>
              ) : (
                filteredLogs.map((log) => (
                  <tr key={log.id} className="hover:bg-slate-800/40 transition-colors">
                    <td className="px-6 py-4 text-xs font-mono text-slate-400">
                      {new Date(log.timestamp).toISOString()}
                    </td>
                    <td className="px-6 py-4">
                      <span className="font-mono text-xs font-semibold px-2 py-0.5 rounded bg-slate-800 text-indigo-300 border border-slate-700">
                        {log.action}
                      </span>
                    </td>
                    <td className="px-6 py-4 text-xs text-slate-300 font-mono">
                      {log.actor_id || 'SYSTEM_DAEMON'}
                    </td>
                    <td className="px-6 py-4 text-xs text-slate-400">
                      {log.resource_type} {log.resource_id ? `(${log.resource_id.substring(0, 8)}...)` : ''}
                    </td>
                    <td className="px-6 py-4">
                      {log.result === 'SUCCESS' || log.result === 'ALLOWED' ? (
                        <span className="flex items-center gap-1.5 text-xs font-medium text-emerald-400">
                          <CheckCircle2 className="w-3.5 h-3.5" />
                          {log.result}
                        </span>
                      ) : (
                        <span className="flex items-center gap-1.5 text-xs font-medium text-rose-400">
                          <XCircle className="w-3.5 h-3.5" />
                          {log.result}
                        </span>
                      )}
                    </td>
                    <td className="px-6 py-4 text-xs text-slate-400 font-mono max-w-xs truncate">
                      {log.metadata_payload ? JSON.stringify(log.metadata_payload) : '-'}
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};
export default AuditLogsPage;
