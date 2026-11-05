import React, { useEffect, useState } from 'react';
import { api } from '../api/client';
import { Binary, ShieldCheck, AlertTriangle, Terminal, RefreshCw, Plus } from 'lucide-react';

export const ScansPage: React.FC = () => {
  const [filter, setFilter] = useState('');
  const [findings, setFindings] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [simulating, setSimulating] = useState(false);

  const fetchFindings = async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await api.scans.findings();
      setFindings(data);
    } catch (e: any) {
      setError(e.message || 'Failed fetching scan findings from backend');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchFindings();
  }, []);

  const handleSimulateScan = async () => {
    setSimulating(true);
    try {
      const sampleFindings = [
        {
          scanner: 'bandit',
          rule_id: 'B105:hardcoded_password_string',
          severity: 'HIGH',
          file_path: 'backend/app/core/config.py',
          line_number: 22,
          description: 'Possible hardcoded credential string detected in configuration loader.',
          remediation: 'Load secrets dynamically from environment variables or AWS Secrets Manager.',
        },
        {
          scanner: 'trivy',
          rule_id: 'CONTAINER-ROOT-USER',
          severity: 'MEDIUM',
          file_path: 'docker/Dockerfile.backend',
          line_number: 38,
          description: 'Container image configured to execute process as root user.',
          remediation: 'Add non-root user `appuser` and specify USER directive.',
        },
        {
          scanner: 'pip-audit',
          rule_id: 'PYSEC-2023-CVE-2023-43804',
          severity: 'CRITICAL',
          file_path: 'requirements.txt',
          line_number: 14,
          description: 'Vulnerability in urllib3 cookie handling on cross-domain redirects.',
          remediation: 'Upgrade urllib3 to version 2.0.7 or higher.',
        },
      ];

      for (const item of sampleFindings) {
        await api.scans.ingest(item);
      }
      await fetchFindings();
    } catch (e: any) {
      setError(e.message || 'Failed simulating scan ingestion');
    } finally {
      setSimulating(false);
    }
  };

  const filtered = findings.filter((f) => {
    if (!filter) return true;
    return f.scanner === filter || f.severity === filter || f.status === filter;
  });

  return (
    <div className="space-y-6">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-xl font-bold text-slate-900 flex items-center space-x-2">
            <Binary className="w-5 h-5 text-indigo-600" />
            <span>DevSecOps & Application Security Scans</span>
          </h1>
          <p className="text-xs font-mono text-slate-500 mt-0.5">
            Database-persisted findings from SAST (Bandit), Dependency Audits (pip-audit), and Container Scanners
          </p>
        </div>

        <div className="flex items-center space-x-3 text-xs font-mono">
          <select
            value={filter}
            onChange={(e) => setFilter(e.target.value)}
            className="bg-white border border-slate-300 rounded-lg px-2.5 py-1.5 text-slate-700 focus:outline-none focus:border-indigo-500"
          >
            <option value="">FILTER: ALL</option>
            <option value="bandit">SCANNER: Bandit (SAST)</option>
            <option value="pip-audit">SCANNER: Pip-Audit</option>
            <option value="trivy">SCANNER: Trivy Container</option>
            <option value="CRITICAL">SEVERITY: CRITICAL</option>
            <option value="HIGH">SEVERITY: HIGH</option>
            <option value="OPEN">STATUS: OPEN</option>
            <option value="RESOLVED">STATUS: RESOLVED</option>
          </select>

          <button
            onClick={fetchFindings}
            title="Refresh Scan Findings"
            className="p-1.5 bg-white hover:bg-slate-50 border border-slate-300 rounded text-slate-600 transition-colors"
          >
            <RefreshCw className="w-4 h-4" />
          </button>
        </div>
      </div>

      {error && (
        <div className="p-4 bg-red-50 border border-red-200 rounded-lg text-red-700 text-xs flex items-center gap-2">
          <AlertTriangle className="w-4 h-4 shrink-0" />
          <span>{error}</span>
        </div>
      )}

      {/* Metrics Row */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className="bg-white border border-slate-200 rounded-xl p-4 shadow-sm">
          <div className="text-[11px] font-mono text-slate-500">TOTAL FINDINGS</div>
          <div className="text-2xl font-bold font-mono text-slate-900 mt-1">{findings.length}</div>
        </div>
        <div className="bg-white border border-slate-200 rounded-xl p-4 shadow-sm">
          <div className="text-[11px] font-mono text-slate-500">CRITICAL FINDINGS</div>
          <div className="text-2xl font-bold font-mono text-red-600 mt-1">
            {findings.filter((f) => f.severity === 'CRITICAL').length}
          </div>
        </div>
        <div className="bg-white border border-slate-200 rounded-xl p-4 shadow-sm">
          <div className="text-[11px] font-mono text-slate-500">RESOLVED / MITIGATED</div>
          <div className="text-2xl font-bold font-mono text-emerald-600 mt-1">
            {findings.filter((f) => f.status === 'RESOLVED').length}
          </div>
        </div>
        <div className="bg-white border border-slate-200 rounded-xl p-4 shadow-sm">
          <div className="text-[11px] font-mono text-slate-500">CI/CD PIPELINE STATUS</div>
          <div className="text-sm font-bold font-mono text-emerald-600 mt-2 flex items-center space-x-1">
            <ShieldCheck className="w-4 h-4" />
            <span>{findings.length > 0 ? 'GATES ACTIVE' : 'NO ACTIVE FINDINGS'}</span>
          </div>
        </div>
      </div>

      {/* Findings Table */}
      <div className="bg-white border border-slate-200 rounded-xl p-5 shadow-sm">
        {loading ? (
          <div className="text-center py-12 text-xs font-mono text-slate-500">Loading scan findings from database...</div>
        ) : filtered.length === 0 ? (
          <div className="text-center py-12 text-slate-500">
            <Binary className="w-10 h-10 text-slate-300 mx-auto mb-2" />
            <p className="text-sm font-semibold text-slate-700">No DevSecOps Scan Findings</p>
            <p className="text-xs text-slate-400 mt-1 max-w-sm mx-auto">
              No static analysis (SAST), dependency (SCA), or container scan results are currently recorded in the database.
            </p>
            <button
              onClick={handleSimulateScan}
              disabled={simulating}
              className="mt-4 px-4 py-2 bg-indigo-50 hover:bg-indigo-100 text-indigo-700 border border-indigo-200 rounded-lg text-xs font-medium transition-colors inline-flex items-center space-x-1.5"
            >
              <Terminal className="w-3.5 h-3.5" />
              <span>{simulating ? 'Ingesting Findings...' : 'Simulate DevSecOps Scan Findings'}</span>
            </button>
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs">
              <thead className="border-b border-slate-200 text-[11px] font-mono text-slate-500 uppercase">
                <tr>
                  <th className="pb-2">Scanner</th>
                  <th className="pb-2">Rule Identifier</th>
                  <th className="pb-2">Severity</th>
                  <th className="pb-2">File Location</th>
                  <th className="pb-2">Vulnerability Description & Remediation</th>
                  <th className="pb-2 text-right">Status</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100 font-mono">
                {filtered.map((f) => (
                  <tr key={f.id} className="hover:bg-slate-50 transition-colors">
                    <td className="py-3 font-bold text-indigo-600 uppercase">{f.scanner}</td>
                    <td className="py-3 text-slate-800 font-semibold">{f.rule_id}</td>
                    <td className="py-3">
                      <span
                        className={
                          f.severity === 'CRITICAL'
                            ? 'badge-critical'
                            : f.severity === 'HIGH'
                            ? 'badge-high'
                            : 'badge-medium'
                        }
                      >
                        {f.severity}
                      </span>
                    </td>
                    <td className="py-3 text-slate-600">
                      {f.file_path}
                      {f.line_number && <span className="text-slate-400">:{f.line_number}</span>}
                    </td>
                    <td className="py-3 max-w-md">
                      <div className="text-slate-800 font-sans">{f.description}</div>
                      <div className="text-[11px] text-slate-500 mt-0.5">
                        <strong className="text-slate-600">Remediation:</strong> {f.remediation}
                      </div>
                    </td>
                    <td className="py-3 text-right">
                      <span
                        className={
                          f.status === 'RESOLVED'
                            ? 'badge-success'
                            : 'badge-info'
                        }
                      >
                        {f.status}
                      </span>
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
