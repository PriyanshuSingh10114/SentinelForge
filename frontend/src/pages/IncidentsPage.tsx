import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { api } from '../api/client';
import { AlertTriangle, Filter, Search, Shield, ArrowUpRight } from 'lucide-react';

export const IncidentsPage: React.FC = () => {
  const [incidents, setIncidents] = useState<any[]>([]);
  const [statusFilter, setStatusFilter] = useState<string>('');
  const [severityFilter, setSeverityFilter] = useState<string>('');
  const [searchQuery, setSearchQuery] = useState<string>('');
  const [loading, setLoading] = useState<boolean>(true);

  const fetchIncidents = async () => {
    setLoading(true);
    try {
      const data = await api.incidents.list({
        status: statusFilter || undefined,
        severity: severityFilter || undefined,
      });
      setIncidents(data);
    } catch (e) {
      console.error('Failed fetching incidents', e);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchIncidents();
  }, [statusFilter, severityFilter]);

  const filteredIncidents = incidents.filter((i) => {
    if (!searchQuery) return true;
    const q = searchQuery.toLowerCase();
    return (
      i.incident_number.toLowerCase().includes(q) ||
      i.title.toLowerCase().includes(q) ||
      i.description.toLowerCase().includes(q)
    );
  });

  return (
    <div className="space-y-6">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-xl font-bold text-white flex items-center space-x-2">
            <AlertTriangle className="w-5 h-5 text-cyan-400" />
            <span>Correlated Security Incidents</span>
          </h1>
          <p className="text-xs font-mono text-slate-400 mt-0.5">
            Clusters of correlated events requiring analytical investigation and containment
          </p>
        </div>

        {/* Filters */}
        <div className="flex flex-wrap items-center gap-3">
          <div className="relative">
            <Search className="w-3.5 h-3.5 text-slate-500 absolute left-2.5 top-2.5" />
            <input
              type="text"
              placeholder="Search incidents..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="bg-sentinel-950 border border-sentinel-800 rounded-lg pl-8 pr-3 py-1.5 text-xs text-slate-200 placeholder-slate-500 focus:outline-none focus:border-cyan-500"
            />
          </div>

          <select
            value={statusFilter}
            onChange={(e) => setStatusFilter(e.target.value)}
            className="bg-sentinel-950 border border-sentinel-800 rounded-lg px-2.5 py-1.5 text-xs text-slate-300 focus:outline-none focus:border-cyan-500 font-mono"
          >
            <option value="">STATUS: ALL</option>
            <option value="OPEN">OPEN</option>
            <option value="INVESTIGATING">INVESTIGATING</option>
            <option value="CONTAINED">CONTAINED</option>
            <option value="RESOLVED">RESOLVED</option>
            <option value="CLOSED">CLOSED</option>
          </select>

          <select
            value={severityFilter}
            onChange={(e) => setSeverityFilter(e.target.value)}
            className="bg-sentinel-950 border border-sentinel-800 rounded-lg px-2.5 py-1.5 text-xs text-slate-300 focus:outline-none focus:border-cyan-500 font-mono"
          >
            <option value="">SEVERITY: ALL</option>
            <option value="CRITICAL">CRITICAL</option>
            <option value="HIGH">HIGH</option>
            <option value="MEDIUM">MEDIUM</option>
            <option value="LOW">LOW</option>
          </select>
        </div>
      </div>

      {/* Incidents Table */}
      <div className="bg-sentinel-950 border border-sentinel-800 rounded-xl p-5 shadow-lg">
        {loading ? (
          <div className="text-center py-12 text-xs font-mono text-slate-500">Loading incidents...</div>
        ) : filteredIncidents.length === 0 ? (
          <div className="text-center py-12 text-xs font-mono text-slate-500">
            No incidents found matching current filters.
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs">
              <thead className="border-b border-sentinel-800 text-[11px] font-mono text-slate-400 uppercase">
                <tr>
                  <th className="pb-3">Incident Number</th>
                  <th className="pb-3">Title & Summary</th>
                  <th className="pb-3">Severity</th>
                  <th className="pb-3">Risk Score</th>
                  <th className="pb-3">Confidence</th>
                  <th className="pb-3">Status</th>
                  <th className="pb-3">Detected At</th>
                  <th className="pb-3 text-right">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-sentinel-800/60 font-mono">
                {filteredIncidents.map((inc) => (
                  <tr key={inc.id} className="hover:bg-sentinel-900/50 transition-colors">
                    <td className="py-3 font-bold text-cyan-400">
                      <Link to={`/incidents/${inc.id}`} className="hover:underline">
                        {inc.incident_number}
                      </Link>
                    </td>
                    <td className="py-3 font-sans max-w-md">
                      <div className="font-semibold text-slate-200">{inc.title}</div>
                      <div className="text-slate-400 text-[11px] truncate mt-0.5">{inc.description}</div>
                    </td>
                    <td className="py-3">
                      <span
                        className={
                          inc.severity === 'CRITICAL'
                            ? 'badge-critical'
                            : inc.severity === 'HIGH'
                            ? 'badge-high'
                            : 'badge-medium'
                        }
                      >
                        {inc.severity}
                      </span>
                    </td>
                    <td className="py-3 font-bold">
                      <span className={inc.risk_score >= 80 ? 'text-red-400' : 'text-amber-400'}>
                        {inc.risk_score} / 100
                      </span>
                    </td>
                    <td className="py-3 text-slate-300">{(inc.confidence * 100).toFixed(0)}%</td>
                    <td className="py-3">
                      <span className="badge-info">{inc.status}</span>
                    </td>
                    <td className="py-3 text-slate-400 text-[11px]">
                      {new Date(inc.detected_at).toLocaleString()}
                    </td>
                    <td className="py-3 text-right font-sans">
                      <Link
                        to={`/incidents/${inc.id}`}
                        className="px-3 py-1 bg-sentinel-800 hover:bg-cyan-950 text-cyan-300 border border-cyan-800/50 rounded text-xs transition-colors inline-flex items-center space-x-1"
                      >
                        <span>Inspect</span>
                        <ArrowUpRight className="w-3 h-3" />
                      </Link>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
};
