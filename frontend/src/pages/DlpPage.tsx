import React, { useEffect, useState } from 'react';
import { api } from '../api/client';
import { FileKey, ShieldAlert, CheckCircle, Search, Play, FileText, Lock } from 'lucide-react';

const DEMO_PAYLOADS = [
  {
    name: 'AWS Credentials (.env leak)',
    content: 'AWS_ACCESS_KEY_ID=AKIAIOSFODNN7EXAMPLE\nAWS_SECRET_ACCESS_KEY=wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY\nAWS_REGION=us-east-1',
  },
  {
    name: 'Database Connection String',
    content: 'DATABASE_URL=postgresql://core_admin:P@ssw0rdSuperSecret2026@10.0.4.15:5432/customer_db',
  },
  {
    name: 'Customer PII Records',
    content: 'Support Ticket #4910:\nClient: Alice Smith\nEmail: alice.smith@secure-bank.org\nPhone: (555) 782-9912\nAccount ID: ACCT-89214',
  },
  {
    name: 'Clean Public Config',
    content: 'ENVIRONMENT=production\nAPP_NAME=SentinelForge\nPORT=8000\nLOG_LEVEL=INFO',
  },
];

export const DlpPage: React.FC = () => {
  const [content, setContent] = useState('');
  const [scanResult, setScanResult] = useState<any | null>(null);
  const [scanning, setScanning] = useState(false);
  const [history, setHistory] = useState<any[]>([]);
  const [loadingHistory, setLoadingHistory] = useState(true);

  const fetchHistory = async () => {
    try {
      const data = await api.dlp.findings();
      setHistory(data);
    } catch (e) {
      console.error('Failed fetching DLP history', e);
    } finally {
      setLoadingHistory(false);
    }
  };

  useEffect(() => {
    fetchHistory();
  }, []);

  const handleScan = async () => {
    if (!content.trim()) return;
    setScanning(true);
    try {
      const res = await api.dlp.scan(content);
      setScanResult(res);
      await fetchHistory();
    } catch (e) {
      console.error('DLP scan error', e);
    } finally {
      setScanning(false);
    }
  };

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-xl font-bold text-white flex items-center space-x-2">
          <FileKey className="w-5 h-5 text-cyan-400" />
          <span>Data Loss Prevention (DLP) & Secret Masking</span>
        </h1>
        <p className="text-xs font-mono text-slate-400 mt-0.5">
          Deterministic classification, Shannon entropy analysis, and automated secret masking
        </p>
      </div>

      {/* Interactive Scanner Box */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2 bg-sentinel-950 border border-sentinel-800 rounded-xl p-5 shadow-lg space-y-4">
          <div className="flex items-center justify-between">
            <h3 className="text-sm font-semibold text-white">Interactive Payload & Secret Inspector</h3>
            <div className="flex items-center space-x-2">
              <span className="text-[11px] font-mono text-slate-400">Load Preset:</span>
              {DEMO_PAYLOADS.map((preset) => (
                <button
                  key={preset.name}
                  onClick={() => setContent(preset.content)}
                  className="px-2 py-0.5 rounded bg-sentinel-900 hover:bg-sentinel-800 text-[10px] font-mono text-cyan-300 border border-sentinel-700/80 transition-colors"
                >
                  {preset.name.split(' ')[0]}
                </button>
              ))}
            </div>
          </div>

          <textarea
            value={content}
            onChange={(e) => setContent(e.target.value)}
            placeholder="Paste code, configuration files, environment variables, or log text to test DLP policies..."
            rows={7}
            className="w-full bg-sentinel-900/60 border border-sentinel-700 rounded-lg p-3 text-xs font-mono text-slate-200 placeholder-slate-600 focus:outline-none focus:border-cyan-500"
          />

          <div className="flex items-center justify-between pt-1">
            <div className="text-[11px] font-mono text-slate-500 flex items-center space-x-1.5">
              <Lock className="w-3.5 h-3.5 text-cyan-400" />
              <span>Secrets are masked immediately upon detection (Zero Plaintext Guarantee)</span>
            </div>
            <button
              onClick={handleScan}
              disabled={scanning || !content.trim()}
              className="px-4 py-2 bg-gradient-to-r from-cyan-600 to-blue-600 hover:from-cyan-500 text-white rounded-lg text-xs font-medium flex items-center space-x-1.5 shadow-md shadow-cyan-950/40 disabled:opacity-50"
            >
              <Play className="w-3.5 h-3.5 fill-current" />
              <span>{scanning ? 'Scanning...' : 'Inspect Content'}</span>
            </button>
          </div>
        </div>

        {/* Real-time Scan Result Card */}
        <div className="bg-sentinel-950 border border-sentinel-800 rounded-xl p-5 shadow-lg flex flex-col justify-between">
          <div>
            <h3 className="text-sm font-semibold text-white mb-4 border-b border-sentinel-800 pb-2">
              DLP Policy Verdict
            </h3>
            {scanResult ? (
              <div className="space-y-4">
                <div>
                  <div className="text-[11px] font-mono text-slate-400">DATA CLASSIFICATION</div>
                  <div className="mt-1">
                    <span
                      className={`text-sm font-mono font-bold px-2.5 py-1 rounded border ${
                        scanResult.classification === 'RESTRICTED'
                          ? 'bg-red-950/90 text-red-300 border-red-700'
                          : scanResult.classification === 'CONFIDENTIAL'
                          ? 'bg-orange-950/90 text-orange-300 border-orange-700'
                          : 'bg-emerald-950/90 text-emerald-300 border-emerald-700'
                      }`}
                    >
                      {scanResult.classification}
                    </span>
                  </div>
                </div>

                <div>
                  <div className="text-[11px] font-mono text-slate-400">ENFORCED POLICY ACTION</div>
                  <div className="mt-1">
                    <span
                      className={`text-sm font-mono font-bold px-2.5 py-1 rounded border ${
                        scanResult.action === 'BLOCK'
                          ? 'bg-red-950/90 text-red-300 border-red-700'
                          : scanResult.action === 'WARN'
                          ? 'bg-yellow-950/90 text-yellow-300 border-yellow-700'
                          : 'bg-emerald-950/90 text-emerald-300 border-emerald-700'
                      }`}
                    >
                      {scanResult.action}
                    </span>
                  </div>
                </div>

                <div>
                  <div className="text-[11px] font-mono text-slate-400 mb-1.5">
                    FINDINGS ({scanResult.findings_count})
                  </div>
                  <div className="space-y-1.5 max-h-40 overflow-y-auto pr-1">
                    {scanResult.findings.map((f: any, idx: number) => (
                      <div key={idx} className="p-2 bg-sentinel-900 rounded border border-sentinel-800 text-[11px] font-mono">
                        <div className="text-cyan-400 font-semibold">{f.data_type}</div>
                        <div className="text-slate-300 truncate">{f.matched_masked}</div>
                        <div className="text-[10px] text-slate-500 mt-0.5">{f.reason}</div>
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            ) : (
              <div className="text-center py-12 text-xs font-mono text-slate-500">
                Run a scan to view classification verdict and masked findings.
              </div>
            )}
          </div>

          <div className="text-[10px] font-mono text-slate-500 border-t border-sentinel-800 pt-3 mt-4">
            Deterministic Regex + Shannon Entropy Core
          </div>
        </div>
      </div>

      {/* Historical DLP Interceptions Table */}
      <div className="bg-sentinel-950 border border-sentinel-800 rounded-xl p-5 shadow-lg">
        <h3 className="text-sm font-semibold text-white mb-1">DLP Detection Audit History</h3>
        <p className="text-xs font-mono text-slate-400 mb-4">
          All persisted security findings stored strictly with masked values
        </p>

        {loadingHistory ? (
          <div className="text-center py-8 text-xs font-mono text-slate-500">Loading historical findings...</div>
        ) : history.length === 0 ? (
          <div className="text-center py-8 text-xs font-mono text-slate-500">No DLP findings recorded yet.</div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs">
              <thead className="border-b border-sentinel-800 text-[11px] font-mono text-slate-400 uppercase">
                <tr>
                  <th className="pb-2">Token Type</th>
                  <th className="pb-2">Masked Pattern (Zero Plaintext)</th>
                  <th className="pb-2">Classification</th>
                  <th className="pb-2">Action</th>
                  <th className="pb-2">Source</th>
                  <th className="pb-2">Detected At</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-sentinel-800/60 font-mono">
                {history.map((h) => (
                  <tr key={h.id} className="hover:bg-sentinel-900/50 transition-colors">
                    <td className="py-2.5 font-bold text-cyan-400">{h.data_type}</td>
                    <td className="py-2.5 text-slate-300 font-mono">{h.matched_pattern}</td>
                    <td className="py-2.5">
                      <span
                        className={
                          h.classification === 'RESTRICTED'
                            ? 'badge-critical'
                            : h.classification === 'CONFIDENTIAL'
                            ? 'badge-high'
                            : 'badge-info'
                        }
                      >
                        {h.classification}
                      </span>
                    </td>
                    <td className="py-2.5">
                      <span
                        className={
                          h.action === 'BLOCK'
                            ? 'text-red-400 font-bold'
                            : h.action === 'WARN'
                            ? 'text-amber-400 font-bold'
                            : 'text-emerald-400'
                        }
                      >
                        {h.action}
                      </span>
                    </td>
                    <td className="py-2.5 text-slate-400 truncate max-w-xs">{h.source_id}</td>
                    <td className="py-2.5 text-slate-500 text-[11px]">
                      {new Date(h.created_at).toLocaleTimeString()}
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
