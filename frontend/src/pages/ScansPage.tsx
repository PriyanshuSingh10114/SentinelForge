import React, { useState } from 'react';
import { Binary, ShieldCheck, AlertTriangle, Bug, Terminal } from 'lucide-react';

const DEMO_SCAN_FINDINGS = [
  {
    id: 'SCAN-001',
    scanner: 'bandit',
    rule_id: 'B105:hardcoded_password_string',
    severity: 'HIGH',
    file_path: 'backend/app/core/config.py',
    line_number: 22,
    description: 'Possible hardcoded password or credential assigned in code.',
    remediation: 'Load secrets dynamically from environment variables or AWS Secrets Manager.',
    status: 'RESOLVED',
  },
  {
    id: 'SCAN-002',
    scanner: 'pip-audit',
    rule_id: 'PYSEC-2023-CVE-2023-43804',
    severity: 'MEDIUM',
    file_path: 'requirements.txt',
    line_number: 14,
    description: 'Vulnerability in urllib3 cookie handling on cross-domain redirects.',
    remediation: 'Upgrade urllib3 to version 2.0.7 or higher.',
    status: 'OPEN',
  },
  {
    id: 'SCAN-003',
    scanner: 'trivy',
    rule_id: 'CONTAINER-ROOT-USER',
    severity: 'MEDIUM',
    file_path: 'docker/Dockerfile.backend',
    line_number: 38,
    description: 'Container image configured to execute process as root user.',
    remediation: 'Add non-root user `sentinel` and specify USER sentinel directive.',
    status: 'RESOLVED',
  },
  {
    id: 'SCAN-004',
    scanner: 'gitleaks',
    rule_id: 'AWS-ACCESS-KEY-LEAK',
    severity: 'CRITICAL',
    file_path: 'samples/.env.backup',
    line_number: 4,
    description: 'AWS IAM access key detected in tracked sample file.',
    remediation: 'Immediately rotate credentials in AWS IAM and scrub git history.',
    status: 'OPEN',
  },
];

export const ScansPage: React.FC = () => {
  const [filter, setFilter] = useState('');
  const [findings, setFindings] = useState(DEMO_SCAN_FINDINGS);

  const filtered = findings.filter((f) => {
    if (!filter) return true;
    return f.scanner === filter || f.severity === filter || f.status === filter;
  });

  return (
    <div className="space-y-6">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-xl font-bold text-white flex items-center space-x-2">
            <Binary className="w-5 h-5 text-cyan-400" />
            <span>DevSecOps & Application Security Scans</span>
          </h1>
          <p className="text-xs font-mono text-slate-400 mt-0.5">
            Ingested findings from SAST (Bandit), Dependency Audits, Container Scanners, and Secret Detection
          </p>
        </div>

        <div className="flex items-center space-x-3 text-xs font-mono">
          <select
            value={filter}
            onChange={(e) => setFilter(e.target.value)}
            className="bg-sentinel-950 border border-sentinel-800 rounded-lg px-2.5 py-1.5 text-slate-300 focus:outline-none focus:border-cyan-500"
          >
            <option value="">FILTER: ALL</option>
            <option value="bandit">SCANNER: Bandit (SAST)</option>
            <option value="pip-audit">SCANNER: Pip-Audit</option>
            <option value="trivy">SCANNER: Trivy Container</option>
            <option value="gitleaks">SCANNER: GitLeaks</option>
            <option value="CRITICAL">SEVERITY: CRITICAL</option>
            <option value="HIGH">SEVERITY: HIGH</option>
            <option value="OPEN">STATUS: OPEN</option>
            <option value="RESOLVED">STATUS: RESOLVED</option>
          </select>
        </div>
      </div>

      {/* Metrics Row */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className="bg-sentinel-950 border border-sentinel-800 rounded-xl p-4 shadow">
          <div className="text-[11px] font-mono text-slate-400">TOTAL FINDINGS</div>
          <div className="text-2xl font-bold font-mono text-white mt-1">{findings.length}</div>
        </div>
        <div className="bg-sentinel-950 border border-sentinel-800 rounded-xl p-4 shadow">
          <div className="text-[11px] font-mono text-slate-400">CRITICAL FINDINGS</div>
          <div className="text-2xl font-bold font-mono text-red-400 mt-1">
            {findings.filter((f) => f.severity === 'CRITICAL').length}
          </div>
        </div>
        <div className="bg-sentinel-950 border border-sentinel-800 rounded-xl p-4 shadow">
          <div className="text-[11px] font-mono text-slate-400">RESOLVED / MITIGATED</div>
          <div className="text-2xl font-bold font-mono text-emerald-400 mt-1">
            {findings.filter((f) => f.status === 'RESOLVED').length}
          </div>
        </div>
        <div className="bg-sentinel-950 border border-sentinel-800 rounded-xl p-4 shadow">
          <div className="text-[11px] font-mono text-slate-400">CI/CD PIPELINE STATUS</div>
          <div className="text-sm font-bold font-mono text-emerald-400 mt-2 flex items-center space-x-1">
            <ShieldCheck className="w-4 h-4" />
            <span>GATES ENFORCED</span>
          </div>
        </div>
      </div>

      {/* Findings Table */}
      <div className="bg-sentinel-950 border border-sentinel-800 rounded-xl p-5 shadow-lg">
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead className="border-b border-sentinel-800 text-[11px] font-mono text-slate-400 uppercase">
              <tr>
                <th className="pb-2">Scanner</th>
                <th className="pb-2">Rule Identifier</th>
                <th className="pb-2">Severity</th>
                <th className="pb-2">File Location</th>
                <th className="pb-2">Vulnerability Description & Remediation</th>
                <th className="pb-2 text-right">Status</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-sentinel-800/60 font-mono">
              {filtered.map((f) => (
                <tr key={f.id} className="hover:bg-sentinel-900/50 transition-colors">
                  <td className="py-3 font-bold text-cyan-400 uppercase">{f.scanner}</td>
                  <td className="py-3 text-slate-300 font-semibold">{f.rule_id}</td>
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
                  <td className="py-3 text-slate-400">
                    {f.file_path}:{f.line_number}
                  </td>
                  <td className="py-3 font-sans max-w-md">
                    <div className="text-slate-200">{f.description}</div>
                    <div className="text-[11px] font-mono text-emerald-400/90 mt-0.5">
                      Fix: {f.remediation}
                    </div>
                  </td>
                  <td className="py-3 text-right">
                    <span
                      className={`text-[10px] px-2 py-0.5 rounded font-mono font-medium border ${
                        f.status === 'RESOLVED'
                          ? 'bg-emerald-950/80 text-emerald-300 border-emerald-700/80'
                          : 'bg-amber-950/80 text-amber-300 border-amber-700/80'
                      }`}
                    >
                      {f.status}
                    </span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};
