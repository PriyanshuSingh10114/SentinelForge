import React, { useEffect, useState } from 'react';
import { api } from '../api/client';
import { useAuth } from '../context/AuthContext';
import {
  ShieldCheck,
  Plus,
  CheckCircle,
  AlertTriangle,
  Cpu,
  Layers,
  Sparkles,
  RefreshCw,
  XCircle,
} from 'lucide-react';

const PRESET_TEMPLATES = {
  honeywell: {
    name: 'Honeywell OT/ICS Edge-to-Cloud Gateway',
    summary:
      'React Web console communicates with FastAPI gateway via HTTPS/JWT. Core backend communicates with PostgreSQL 16 database, Redis queue, AWS S3 storage buckets, and streams immutable security audit trails to CloudWatch. Edge sensors and PLC controllers push telemetry through an mTLS-authenticated industrial gateway.',
  },
  cloudNative: {
    name: 'Cloud-Native Microservices SIEM Platform',
    summary:
      'Distributed Kubernetes cluster with API Gateway enforcing JWT auth, rate limiting, and RBAC. Microservices communicate with PostgreSQL database, Redis distributed cache, and external threat intel APIs via secure service mesh.',
  },
  zeroTrust: {
    name: 'Zero-Trust Enterprise Network Architecture',
    summary:
      'Identity-aware proxy authenticates users via OAuth2/OIDC. Microsegmentation isolates application tiers, data storage is encrypted at rest using AWS KMS, and all egress traffic passes through a DLP inspection firewall.',
  },
};

export const ThreatModelingPage: React.FC = () => {
  const { user } = useAuth();
  const isViewer = user?.role === 'Viewer';
  const isAnalystOrAdmin = user?.role === 'Admin' || user?.role === 'Analyst';
  const [models, setModels] = useState<any[]>([]);
  const [selectedModel, setSelectedModel] = useState<any | null>(null);
  const [modelName, setModelName] = useState(PRESET_TEMPLATES.honeywell.name);
  const [architectureSummary, setArchitectureSummary] = useState(PRESET_TEMPLATES.honeywell.summary);
  const [creating, setCreating] = useState(false);
  const [loading, setLoading] = useState(true);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);
  const [successMessage, setSuccessMessage] = useState<string | null>(null);

  const fetchModels = async (selectId?: string) => {
    try {
      setErrorMessage(null);
      const data = await api.threats.list();
      setModels(data);
      if (data.length > 0) {
        if (selectId) {
          const matched = data.find((m: any) => m.id === selectId);
          setSelectedModel(matched || data[0]);
        } else if (!selectedModel) {
          setSelectedModel(data[0]);
        }
      }
    } catch (e: any) {
      console.error('Failed fetching threat models', e);
      setErrorMessage(e.message || 'Failed loading threat models from server');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchModels();
  }, []);

  const handleCreateModel = async (e?: React.FormEvent) => {
    if (e) e.preventDefault();
    if (!modelName.trim() || !architectureSummary.trim()) {
      setErrorMessage('Please provide both an Architecture Name and an Architecture Summary.');
      return;
    }
    setCreating(true);
    setErrorMessage(null);
    setSuccessMessage(null);

    try {
      const created = await api.threats.create(modelName, architectureSummary);
      setSelectedModel(created);
      setSuccessMessage(`Successfully generated STRIDE threat model with ${created.items?.length || 0} threat vectors & mitigations!`);
      await fetchModels(created.id);
    } catch (e: any) {
      console.error('Failed creating threat model', e);
      setErrorMessage(e.message || 'Failed to generate threat model. Please verify your authentication.');
    } finally {
      setCreating(false);
    }
  };

  const handleUpdateItemStatus = async (itemId: string, newStatus: string) => {
    try {
      setErrorMessage(null);
      await api.threats.updateStatus(itemId, newStatus);
      if (selectedModel) {
        const updated = await api.threats.get(selectedModel.id);
        setSelectedModel(updated);
        await fetchModels(selectedModel.id);
      }
    } catch (e: any) {
      console.error('Failed updating threat item', e);
      setErrorMessage(e.message || 'Failed updating status (Admin or Analyst role required)');
    }
  };

  const getStrideBadge = (cat: string) => {
    switch (cat) {
      case 'SPOOFING':
        return 'bg-blue-50 text-blue-700 border-blue-200';
      case 'TAMPERING':
        return 'bg-amber-50 text-amber-800 border-amber-200';
      case 'REPUDIATION':
        return 'bg-slate-100 text-slate-700 border-slate-300';
      case 'INFO_DISCLOSURE':
        return 'bg-purple-50 text-purple-700 border-purple-200';
      case 'DOS':
        return 'bg-red-50 text-red-700 border-red-200';
      case 'ELEVATION':
        return 'bg-orange-50 text-orange-700 border-orange-200';
      default:
        return 'bg-slate-100 text-slate-700 border-slate-300';
    }
  };

  return (
    <div className="space-y-6">
      {/* Page Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
        <div>
          <h1 className="text-xl font-bold text-slate-900 flex items-center space-x-2">
            <ShieldCheck className="w-5 h-5 text-cyan-600" />
            <span>STRIDE Threat Modeling Engine</span>
          </h1>
          <p className="text-xs font-mono text-slate-500 mt-0.5">
            Automated architectural threat generation, STRIDE categorization, and mitigation tracking
          </p>
        </div>
        <div className="flex items-center space-x-2">
          <span className="inline-flex items-center px-2.5 py-1 rounded-full text-xs font-mono bg-cyan-50 text-cyan-700 border border-cyan-200">
            <Sparkles className="w-3.5 h-3.5 mr-1" />
            NIST SP 800-53 & STRIDE Aligned
          </span>
        </div>
      </div>

      {/* Notifications */}
      {errorMessage && (
        <div className="p-3.5 bg-red-50 border border-red-200 rounded-xl text-xs text-red-700 flex items-center justify-between shadow-sm">
          <div className="flex items-center space-x-2">
            <XCircle className="w-4 h-4 shrink-0 text-red-500" />
            <span>{errorMessage}</span>
          </div>
          <button onClick={() => setErrorMessage(null)} className="text-red-400 hover:text-red-600 font-bold ml-2">
            ✕
          </button>
        </div>
      )}

      {successMessage && (
        <div className="p-3.5 bg-emerald-50 border border-emerald-200 rounded-xl text-xs text-emerald-800 flex items-center justify-between shadow-sm">
          <div className="flex items-center space-x-2">
            <CheckCircle className="w-4 h-4 shrink-0 text-emerald-600" />
            <span>{successMessage}</span>
          </div>
          <button onClick={() => setSuccessMessage(null)} className="text-emerald-500 hover:text-emerald-700 font-bold ml-2">
            ✕
          </button>
        </div>
      )}

      {/* Model Creation & Selector */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Creator Form */}
        <div className="lg:col-span-2 bg-white border border-slate-200 rounded-xl p-5 shadow-sm">
          <div className="flex items-center justify-between mb-3">
            <h3 className="text-sm font-semibold text-slate-900 flex items-center space-x-2">
              <Layers className="w-4 h-4 text-cyan-600" />
              <span>Model New Architecture</span>
            </h3>
            <span className="text-[11px] font-mono text-slate-400">Rule-driven STRIDE mapper</span>
          </div>

          {/* Quick Preset Buttons */}
          <div className="mb-4">
            <label className="block text-[11px] font-mono text-slate-500 mb-1.5 uppercase tracking-wider">
              Quick Architecture Presets:
            </label>
            <div className="flex flex-wrap gap-2">
              <button
                type="button"
                onClick={() => {
                  setModelName(PRESET_TEMPLATES.honeywell.name);
                  setArchitectureSummary(PRESET_TEMPLATES.honeywell.summary);
                }}
                className="px-2.5 py-1 text-[11px] font-medium bg-slate-50 hover:bg-cyan-50 hover:text-cyan-700 text-slate-700 border border-slate-200 rounded-md transition-colors"
              >
                Honeywell OT/ICS Gateway
              </button>
              <button
                type="button"
                onClick={() => {
                  setModelName(PRESET_TEMPLATES.cloudNative.name);
                  setArchitectureSummary(PRESET_TEMPLATES.cloudNative.summary);
                }}
                className="px-2.5 py-1 text-[11px] font-medium bg-slate-50 hover:bg-cyan-50 hover:text-cyan-700 text-slate-700 border border-slate-200 rounded-md transition-colors"
              >
                Cloud-Native SIEM
              </button>
              <button
                type="button"
                onClick={() => {
                  setModelName(PRESET_TEMPLATES.zeroTrust.name);
                  setArchitectureSummary(PRESET_TEMPLATES.zeroTrust.summary);
                }}
                className="px-2.5 py-1 text-[11px] font-medium bg-slate-50 hover:bg-cyan-50 hover:text-cyan-700 text-slate-700 border border-slate-200 rounded-md transition-colors"
              >
                Zero-Trust Network
              </button>
            </div>
          </div>

          <form onSubmit={handleCreateModel} className="space-y-4">
            <div>
              <label className="block text-[11px] font-mono font-medium text-slate-600 mb-1">
                ARCHITECTURE / SYSTEM NAME
              </label>
              <input
                type="text"
                value={modelName}
                onChange={(e) => setModelName(e.target.value)}
                placeholder="e.g. Honeywell OT/ICS Edge-to-Cloud Gateway"
                required
                className="w-full bg-slate-50 border border-slate-200 rounded-lg px-3 py-2 text-xs text-slate-900 focus:outline-none focus:ring-1 focus:ring-cyan-500 focus:border-cyan-500 font-sans"
              />
            </div>

            <div>
              <label className="block text-[11px] font-mono font-medium text-slate-600 mb-1">
                ARCHITECTURE SUMMARY, DATA STORES & TRUST BOUNDARIES
              </label>
              <textarea
                value={architectureSummary}
                onChange={(e) => setArchitectureSummary(e.target.value)}
                rows={4}
                placeholder="Describe system components (API gateways, auth, databases, S3 storage, Redis, edge sensors)..."
                required
                className="w-full bg-slate-50 border border-slate-200 rounded-lg p-3 text-xs text-slate-900 focus:outline-none focus:ring-1 focus:ring-cyan-500 focus:border-cyan-500 font-sans leading-relaxed"
              />
            </div>

            <div className="flex justify-end items-center pt-1">
              <button
                type="submit"
                disabled={creating || isViewer}
                title={isViewer ? 'Viewer role is read-only. Cannot generate threat models.' : 'Generate STRIDE Model'}
                className="px-4 py-2 bg-cyan-600 hover:bg-cyan-700 text-white rounded-lg text-xs font-semibold flex items-center space-x-1.5 shadow-sm transition-all disabled:opacity-50 disabled:cursor-not-allowed cursor-pointer"
              >
                {creating ? (
                  <>
                    <RefreshCw className="w-3.5 h-3.5 animate-spin" />
                    <span>Analyzing Architecture...</span>
                  </>
                ) : (
                  <>
                    <Sparkles className="w-3.5 h-3.5" />
                    <span>{isViewer ? 'Threat Modeling (Admin/Analyst only)' : 'Generate STRIDE Model'}</span>
                  </>
                )}
              </button>
            </div>
          </form>
        </div>

        {/* Existing Models Selector */}
        <div className="bg-white border border-slate-200 rounded-xl p-5 shadow-sm flex flex-col justify-between">
          <div>
            <div className="flex items-center justify-between mb-3">
              <h3 className="text-sm font-semibold text-slate-900">
                Threat Models ({models.length})
              </h3>
              <button
                onClick={() => fetchModels(selectedModel?.id)}
                className="text-slate-400 hover:text-slate-600 p-1"
                title="Refresh models"
              >
                <RefreshCw className="w-3.5 h-3.5" />
              </button>
            </div>

            {loading ? (
              <div className="py-8 text-center text-xs text-slate-400 font-mono">
                Loading models...
              </div>
            ) : models.length === 0 ? (
              <div className="py-8 text-center text-xs text-slate-500">
                No threat models created yet. Fill out the form to generate your first architecture analysis.
              </div>
            ) : (
              <div className="space-y-2 max-h-72 overflow-y-auto pr-1">
                {models.map((m) => (
                  <button
                    key={m.id}
                    type="button"
                    onClick={() => setSelectedModel(m)}
                    className={`w-full text-left p-3 rounded-lg border text-xs transition-colors cursor-pointer ${
                      selectedModel?.id === m.id
                        ? 'bg-cyan-50 border-cyan-300 text-cyan-900 font-semibold shadow-sm'
                        : 'bg-slate-50 border-slate-200 text-slate-700 hover:bg-slate-100 hover:text-slate-900'
                    }`}
                  >
                    <div className="font-semibold text-slate-900">{m.name}</div>
                    <div className="text-[10px] font-mono text-slate-500 mt-1 flex items-center justify-between">
                      <span>Threats: {m.items?.length || 0} items</span>
                      <span>{new Date(m.created_at).toLocaleDateString()}</span>
                    </div>
                  </button>
                ))}
              </div>
            )}
          </div>

          <div className="mt-4 pt-3 border-t border-slate-100 text-[11px] font-mono text-slate-400">
            STRIDE: Spoofing, Tampering, Repudiation, Info Disclosure, DoS, Elevation
          </div>
        </div>
      </div>

      {/* Selected Model Threats Breakdown */}
      {selectedModel && (
        <div className="bg-white border border-slate-200 rounded-xl p-6 shadow-sm space-y-4">
          <div className="flex flex-col sm:flex-row sm:items-center justify-between border-b border-slate-100 pb-3 gap-2">
            <div>
              <h3 className="text-sm font-bold text-slate-900">{selectedModel.name}</h3>
              <p className="text-xs text-slate-600 font-sans mt-0.5">{selectedModel.architecture_summary}</p>
            </div>
            <div className="text-xs font-mono font-semibold px-2.5 py-1 bg-cyan-50 text-cyan-800 rounded-md border border-cyan-200 shrink-0">
              STRIDE THREATS: {selectedModel.items?.length || 0}
            </div>
          </div>

          <div className="space-y-3">
            {(!selectedModel.items || selectedModel.items.length === 0) ? (
              <div className="py-6 text-center text-xs text-slate-500">
                No threat items linked to this model.
              </div>
            ) : (
              selectedModel.items.map((item: any) => (
                <div
                  key={item.id}
                  className="p-4 rounded-xl bg-slate-50 border border-slate-200 flex flex-col md:flex-row md:items-center justify-between gap-4"
                >
                  <div className="space-y-1.5 flex-1">
                    <div className="flex items-center space-x-2">
                      <span className={`text-[10px] font-mono px-2 py-0.5 rounded border font-bold ${getStrideBadge(item.stride_category)}`}>
                        {item.stride_category}
                      </span>
                      <span className="text-xs font-bold font-mono text-slate-800">{item.target_component}</span>
                    </div>
                    <div className="text-xs text-slate-700 font-sans">{item.description}</div>
                    <div className="text-[11px] font-mono text-emerald-800 bg-emerald-50 border border-emerald-200 rounded p-2 mt-1">
                      <span className="font-bold">Mitigation:</span> {item.mitigation}
                    </div>
                  </div>

                  <div className="shrink-0 flex items-center space-x-2">
                    <span className="text-[10px] font-mono text-slate-400">STATUS:</span>
                    <select
                      value={item.status}
                      onChange={(e) => handleUpdateItemStatus(item.id, e.target.value)}
                      disabled={!isAnalystOrAdmin}
                      title={!isAnalystOrAdmin ? 'Analyst or Admin role required to update threat item status' : 'Update status'}
                      className="bg-white border border-slate-300 rounded-lg px-2.5 py-1 text-xs font-mono font-semibold text-slate-800 focus:outline-none focus:ring-1 focus:ring-cyan-500 focus:border-cyan-500 shadow-sm cursor-pointer disabled:opacity-60 disabled:cursor-not-allowed"
                    >
                      <option value="OPEN">OPEN</option>
                      <option value="MITIGATED">MITIGATED</option>
                      <option value="ACCEPTED">ACCEPTED</option>
                      <option value="FALSE_POSITIVE">FALSE_POSITIVE</option>
                    </select>
                  </div>
                </div>
              ))
            )}
          </div>
        </div>
      )}
    </div>
  );
};
