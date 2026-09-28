import React, { useState, useEffect } from 'react';
import { api } from '../api/client';
import { Shield, Plus, ToggleLeft, ToggleRight, AlertTriangle, FileCode } from 'lucide-react';

interface SecurityPolicy {
  id: string;
  name: string;
  description: string;
  policy_type: string;
  configuration: any;
  enabled: boolean;
  created_at: string;
}

export const PoliciesPage: React.FC = () => {
  const [policies, setPolicies] = useState<SecurityPolicy[]>([]);
  const [loading, setLoading] = useState(true);
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [name, setName] = useState('');
  const [description, setDescription] = useState('');
  const [policyType, setPolicyType] = useState('DLP');
  const [configJson, setConfigJson] = useState('{\n  "action": "BLOCK",\n  "severity": "RESTRICTED",\n  "patterns": ["AWS_ACCESS_KEY", "PRIVATE_KEY"]\n}');
  const [error, setError] = useState<string | null>(null);

  const fetchPolicies = async () => {
    try {
      setLoading(true);
      const res = await api.getPolicies();
      setPolicies(Array.isArray(res) ? res : (res as any).data || []);
    } catch (err: any) {
      setError(err.message || 'Failed to fetch policies');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchPolicies();
  }, []);

  const handleToggle = async (policy: SecurityPolicy) => {
    try {
      await api.updatePolicy(policy.id, { enabled: !policy.enabled });
      fetchPolicies();
    } catch (err: any) {
      alert('Failed to update policy: ' + err.message);
    }
  };

  const handleCreate = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      let parsedConfig = {};
      try {
        parsedConfig = JSON.parse(configJson);
      } catch {
        alert('Invalid JSON configuration');
        return;
      }
      await api.createPolicy({
        name,
        description,
        policy_type: policyType,
        configuration: parsedConfig,
        enabled: true,
      });
      setShowCreateModal(false);
      setName('');
      setDescription('');
      fetchPolicies();
    } catch (err: any) {
      alert('Failed to create policy: ' + err.message);
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-white tracking-tight flex items-center gap-2">
            <Shield className="w-7 h-7 text-indigo-400" />
            Security & DLP Policies
          </h1>
          <p className="text-sm text-slate-400 mt-1">
            Deterministic rule configuration and data boundary governance enforced server-side.
          </p>
        </div>
        <button
          onClick={() => setShowCreateModal(true)}
          className="flex items-center gap-2 px-4 py-2 bg-indigo-600 hover:bg-indigo-500 text-white text-sm font-medium rounded-lg transition-colors shadow-sm"
        >
          <Plus className="w-4 h-4" />
          Create Policy
        </button>
      </div>

      {error && (
        <div className="p-4 bg-red-950/40 border border-red-800 rounded-lg text-red-300 text-sm flex items-center gap-2">
          <AlertTriangle className="w-5 h-5 flex-shrink-0" />
          {error}
        </div>
      )}

      {loading ? (
        <div className="text-center py-12 text-slate-400">Loading security policies...</div>
      ) : policies.length === 0 ? (
        <div className="bg-slate-900 border border-slate-800 rounded-xl p-12 text-center text-slate-400">
          <Shield className="w-12 h-12 text-slate-600 mx-auto mb-3" />
          <p className="text-lg font-medium text-slate-300">No active policies configured</p>
          <p className="text-sm text-slate-500 mt-1">Click above to initialize your first automated security rule.</p>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {policies.map((p) => (
            <div key={p.id} className="bg-slate-900 border border-slate-800 rounded-xl p-5 flex flex-col justify-between hover:border-slate-700 transition-colors">
              <div>
                <div className="flex items-center justify-between mb-2">
                  <div className="flex items-center gap-2">
                    <span className="px-2 py-0.5 rounded text-xs font-semibold bg-indigo-950 text-indigo-300 border border-indigo-800">
                      {p.policy_type}
                    </span>
                    <h3 className="font-semibold text-white text-base">{p.name}</h3>
                  </div>
                  <button
                    onClick={() => handleToggle(p)}
                    className="text-slate-400 hover:text-white transition-colors"
                    title={p.enabled ? "Disable Policy" : "Enable Policy"}
                  >
                    {p.enabled ? (
                      <ToggleRight className="w-7 h-7 text-emerald-400" />
                    ) : (
                      <ToggleLeft className="w-7 h-7 text-slate-600" />
                    )}
                  </button>
                </div>
                <p className="text-sm text-slate-400 mb-4">{p.description}</p>
                <div className="bg-slate-950 border border-slate-800 rounded-lg p-3 text-xs font-mono text-slate-300 overflow-x-auto">
                  <pre>{JSON.stringify(p.configuration, null, 2)}</pre>
                </div>
              </div>
              <div className="mt-4 pt-3 border-t border-slate-800 flex items-center justify-between text-xs text-slate-500">
                <span>Status: <strong className={p.enabled ? "text-emerald-400" : "text-amber-500"}>{p.enabled ? 'ACTIVE' : 'DISABLED'}</strong></span>
                <span>Configured: {new Date(p.created_at).toLocaleDateString()}</span>
              </div>
            </div>
          ))}
        </div>
      )}

      {showCreateModal && (
        <div className="fixed inset-0 bg-black/70 backdrop-blur-sm flex items-center justify-center p-4 z-50">
          <div className="bg-slate-900 border border-slate-800 rounded-xl max-w-lg w-full p-6 space-y-4 shadow-2xl">
            <h2 className="text-lg font-bold text-white flex items-center gap-2">
              <FileCode className="w-5 h-5 text-indigo-400" />
              Configure Security Policy
            </h2>
            <form onSubmit={handleCreate} className="space-y-4">
              <div>
                <label className="block text-xs font-medium text-slate-300 mb-1">Policy Name</label>
                <input
                  type="text"
                  required
                  value={name}
                  onChange={(e) => setName(e.target.value)}
                  placeholder="e.g., Block Production AWS Secrets Ingress"
                  className="w-full bg-slate-950 border border-slate-800 rounded-lg px-3 py-2 text-sm text-slate-200 focus:outline-none focus:border-indigo-500"
                />
              </div>
              <div>
                <label className="block text-xs font-medium text-slate-300 mb-1">Type</label>
                <select
                  value={policyType}
                  onChange={(e) => setPolicyType(e.target.value)}
                  className="w-full bg-slate-950 border border-slate-800 rounded-lg px-3 py-2 text-sm text-slate-200 focus:outline-none focus:border-indigo-500"
                >
                  <option value="DLP">Data Loss Prevention (DLP)</option>
                  <option value="RULE">Correlation Rule</option>
                  <option value="RATE_LIMIT">Rate Limiting Threshold</option>
                  <option value="AUTH">Authentication Security</option>
                </select>
              </div>
              <div>
                <label className="block text-xs font-medium text-slate-300 mb-1">Description</label>
                <textarea
                  rows={2}
                  value={description}
                  onChange={(e) => setDescription(e.target.value)}
                  placeholder="Describe enforcement logic and incident trigger boundaries..."
                  className="w-full bg-slate-950 border border-slate-800 rounded-lg px-3 py-2 text-sm text-slate-200 focus:outline-none focus:border-indigo-500"
                />
              </div>
              <div>
                <label className="block text-xs font-medium text-slate-300 mb-1">Configuration (JSON)</label>
                <textarea
                  rows={4}
                  value={configJson}
                  onChange={(e) => setConfigJson(e.target.value)}
                  className="w-full bg-slate-950 border border-slate-800 rounded-lg px-3 py-2 text-xs font-mono text-slate-200 focus:outline-none focus:border-indigo-500"
                />
              </div>
              <div className="flex justify-end gap-3 pt-2">
                <button
                  type="button"
                  onClick={() => setShowCreateModal(false)}
                  className="px-4 py-2 bg-slate-800 hover:bg-slate-700 text-slate-300 text-sm font-medium rounded-lg transition-colors"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="px-4 py-2 bg-indigo-600 hover:bg-indigo-500 text-white text-sm font-medium rounded-lg transition-colors"
                >
                  Save Policy
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};
export default PoliciesPage;
