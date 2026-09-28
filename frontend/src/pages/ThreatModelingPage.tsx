import React, { useEffect, useState } from 'react';
import { api } from '../api/client';
import { ShieldCheck, Plus, CheckCircle, ShieldAlert, Cpu } from 'lucide-react';

export const ThreatModelingPage: React.FC = () => {
  const [models, setModels] = useState<any[]>([]);
  const [selectedModel, setSelectedModel] = useState<any | null>(null);
  const [modelName, setModelName] = useState('');
  const [architectureSummary, setArchitectureSummary] = useState('');
  const [creating, setCreating] = useState(false);
  const [loading, setLoading] = useState(true);

  const fetchModels = async () => {
    try {
      const data = await api.threats.list();
      setModels(data);
      if (data.length > 0 && !selectedModel) {
        setSelectedModel(data[0]);
      }
    } catch (e) {
      console.error('Failed fetching threat models', e);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchModels();
  }, []);

  const handleCreateModel = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!modelName || !architectureSummary) return;
    setCreating(true);
    try {
      const created = await api.threats.create(modelName, architectureSummary);
      setModelName('');
      setArchitectureSummary('');
      setSelectedModel(created);
      await fetchModels();
    } catch (e) {
      console.error('Failed creating threat model', e);
    } finally {
      setCreating(false);
    }
  };

  const handleUpdateItemStatus = async (itemId: string, newStatus: string) => {
    try {
      await api.threats.updateStatus(itemId, newStatus);
      if (selectedModel) {
        const updated = await api.threats.get(selectedModel.id);
        setSelectedModel(updated);
        await fetchModels();
      }
    } catch (e) {
      console.error('Failed updating threat item', e);
    }
  };

  const getStrideBadge = (cat: string) => {
    switch (cat) {
      case 'SPOOFING':
        return 'bg-blue-950/80 text-blue-300 border-blue-700/60';
      case 'TAMPERING':
        return 'bg-amber-950/80 text-amber-300 border-amber-700/60';
      case 'REPUDIATION':
        return 'bg-slate-900/80 text-slate-300 border-slate-700/60';
      case 'INFO_DISCLOSURE':
        return 'bg-purple-950/80 text-purple-300 border-purple-700/60';
      case 'DOS':
        return 'bg-red-950/80 text-red-300 border-red-700/60';
      case 'ELEVATION':
        return 'bg-orange-950/80 text-orange-300 border-orange-700/60';
      default:
        return 'bg-slate-800 text-slate-300 border-slate-700';
    }
  };

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-xl font-bold text-white flex items-center space-x-2">
          <ShieldCheck className="w-5 h-5 text-cyan-400" />
          <span>STRIDE Threat Modeling Engine</span>
        </h1>
        <p className="text-xs font-mono text-slate-400 mt-0.5">
          Automated architectural threat generation, STRIDE categorization, and mitigation tracking
        </p>
      </div>

      {/* Model Creation & Selector */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Creator Form */}
        <div className="lg:col-span-2 bg-sentinel-950 border border-sentinel-800 rounded-xl p-5 shadow-lg">
          <h3 className="text-sm font-semibold text-white mb-3">Model New Architecture</h3>
          <form onSubmit={handleCreateModel} className="space-y-4">
            <div>
              <label className="block text-[11px] font-mono text-slate-400 mb-1">ARCHITECTURE NAME</label>
              <input
                type="text"
                value={modelName}
                onChange={(e) => setModelName(e.target.value)}
                placeholder="e.g. SentinelForge Microservices Infrastructure"
                required
                className="w-full bg-sentinel-900 border border-sentinel-700 rounded-lg px-3 py-1.5 text-xs text-slate-200 focus:outline-none focus:border-cyan-500 font-sans"
              />
            </div>

            <div>
              <label className="block text-[11px] font-mono text-slate-400 mb-1">
                ARCHITECTURE SUMMARY & TRUST BOUNDARIES
              </label>
              <textarea
                value={architectureSummary}
                onChange={(e) => setArchitectureSummary(e.target.value)}
                rows={4}
                placeholder="Describe components (e.g. React client, FastAPI gateway, PostgreSQL, S3 buckets, Redis queues, and JWT auth service)..."
                required
                className="w-full bg-sentinel-900 border border-sentinel-700 rounded-lg p-3 text-xs text-slate-200 focus:outline-none focus:border-cyan-500 font-sans"
              />
            </div>

            <div className="flex justify-between items-center pt-1">
              <button
                type="button"
                onClick={() => {
                  setModelName('Cloud Native SIEM/DLP Platform');
                  setArchitectureSummary(
                    'React Web console accesses FastAPI gateway via HTTPS/JWT. Core backend communicates with PostgreSQL 16 database, Redis queue, AWS S3 storage buckets, and streams immutable security audit trails to CloudWatch.'
                  );
                }}
                className="text-[11px] font-mono text-cyan-400 hover:underline"
              >
                Insert Architecture Template
              </button>
              <button
                type="submit"
                disabled={creating}
                className="px-4 py-1.5 bg-gradient-to-r from-cyan-600 to-blue-600 hover:from-cyan-500 text-white rounded-lg text-xs font-medium flex items-center space-x-1.5 disabled:opacity-50"
              >
                <Plus className="w-3.5 h-3.5" />
                <span>{creating ? 'Analyzing Architecture...' : 'Generate STRIDE Model'}</span>
              </button>
            </div>
          </form>
        </div>

        {/* Existing Models Selector */}
        <div className="bg-sentinel-950 border border-sentinel-800 rounded-xl p-5 shadow-lg">
          <h3 className="text-sm font-semibold text-white mb-3">Threat Models ({models.length})</h3>
          <div className="space-y-2 max-h-64 overflow-y-auto pr-1">
            {models.map((m) => (
              <button
                key={m.id}
                onClick={() => setSelectedModel(m)}
                className={`w-full text-left p-3 rounded-lg border text-xs transition-colors ${
                  selectedModel?.id === m.id
                    ? 'bg-cyan-950/60 border-cyan-800 text-cyan-200'
                    : 'bg-sentinel-900/60 border-sentinel-800 text-slate-400 hover:bg-sentinel-900 hover:text-slate-200'
                }`}
              >
                <div className="font-semibold text-slate-200">{m.name}</div>
                <div className="text-[10px] font-mono text-slate-500 mt-1">
                  Threats: {m.items?.length || 0} items • {new Date(m.created_at).toLocaleDateString()}
                </div>
              </button>
            ))}
          </div>
        </div>
      </div>

      {/* Selected Model Threats Breakdown */}
      {selectedModel && (
        <div className="bg-sentinel-950 border border-sentinel-800 rounded-xl p-6 shadow-lg space-y-4">
          <div className="flex flex-col sm:flex-row sm:items-center justify-between border-b border-sentinel-800/80 pb-3 gap-2">
            <div>
              <h3 className="text-sm font-bold text-white">{selectedModel.name}</h3>
              <p className="text-xs text-slate-400 font-sans mt-0.5">{selectedModel.architecture_summary}</p>
            </div>
            <div className="text-xs font-mono text-cyan-400">
              STRIDE THREATS: {selectedModel.items?.length || 0}
            </div>
          </div>

          <div className="space-y-3">
            {selectedModel.items?.map((item: any) => (
              <div
                key={item.id}
                className="p-4 rounded-xl bg-sentinel-900/60 border border-sentinel-800 flex flex-col md:flex-row md:items-center justify-between gap-4"
              >
                <div className="space-y-1.5 flex-1">
                  <div className="flex items-center space-x-2">
                    <span className={`text-[10px] font-mono px-2 py-0.5 rounded border font-bold ${getStrideBadge(item.stride_category)}`}>
                      {item.stride_category}
                    </span>
                    <span className="text-xs font-bold font-mono text-slate-300">{item.target_component}</span>
                  </div>
                  <div className="text-xs text-slate-200 font-sans">{item.description}</div>
                  <div className="text-[11px] font-mono text-emerald-400/90 bg-emerald-950/20 border border-emerald-900/40 rounded p-2 mt-1">
                    Mitigation: {item.mitigation}
                  </div>
                </div>

                <div className="shrink-0">
                  <select
                    value={item.status}
                    onChange={(e) => handleUpdateItemStatus(item.id, e.target.value)}
                    className="bg-sentinel-950 border border-sentinel-700 rounded-lg px-2.5 py-1 text-xs font-mono text-slate-300 focus:outline-none focus:border-cyan-500"
                  >
                    <option value="OPEN">OPEN</option>
                    <option value="MITIGATED">MITIGATED</option>
                    <option value="ACCEPTED">ACCEPTED</option>
                    <option value="FALSE_POSITIVE">FALSE_POSITIVE</option>
                  </select>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};
