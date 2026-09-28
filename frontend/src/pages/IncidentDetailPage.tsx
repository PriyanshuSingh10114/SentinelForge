import React, { useEffect, useState } from 'react';
import { useParams } from 'react-router-dom';
import { api } from '../api/client';
import { useAuth } from '../context/AuthContext';
import {
  ShieldAlert,
  Clock,
  Sparkles,
  GitCommit,
  CheckCircle,
  XCircle,
  AlertTriangle,
  User,
  Server,
  Key,
  ShieldCheck,
  Check,
  X,
} from 'lucide-react';

export const IncidentDetailPage: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const { user } = useAuth();
  const isAdmin = user?.role === 'Admin';

  const [incident, setIncident] = useState<any | null>(null);
  const [attackGraph, setAttackGraph] = useState<any | null>(null);
  const [investigation, setInvestigation] = useState<any | null>(null);
  const [remediations, setRemediations] = useState<any[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [investigating, setInvestigating] = useState<boolean>(false);
  const [activeTab, setActiveTab] = useState<'overview' | 'timeline' | 'graph' | 'ai' | 'remediation'>('overview');
  const [approvalModalAction, setApprovalModalAction] = useState<any | null>(null);
  const [rejectionModalAction, setRejectionModalAction] = useState<any | null>(null);
  const [approvalNotes, setApprovalNotes] = useState<string>('');
  const [rejectionReason, setRejectionReason] = useState<string>('');
  const [actionError, setActionError] = useState<string | null>(null);

  const loadIncidentData = async () => {
    if (!id) return;
    try {
      const [inc, graph, reports, rems] = await Promise.all([
        api.incidents.get(id),
        api.incidents.attackGraph(id),
        api.investigations.getByIncident(id),
        api.remediations.list(),
      ]);
      setIncident(inc);
      setAttackGraph(graph);
      if (reports.length > 0) {
        setInvestigation(reports[0]);
      }
      // Filter remediations belonging to this incident
      setRemediations(rems.filter((r) => r.incident_id === inc.id));
    } catch (e) {
      console.error('Failed loading incident detail', e);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadIncidentData();
  }, [id]);

  const handleRunInvestigation = async () => {
    if (!incident) return;
    setInvestigating(true);
    setActionError(null);
    try {
      const result = await api.investigations.run(incident.id);
      setInvestigation(result);
      setActiveTab('ai');
      await loadIncidentData();
    } catch (err: any) {
      setActionError(err.message || 'Investigation failed');
    } finally {
      setInvestigating(false);
    }
  };

  const handleStatusChange = async (newStatus: string) => {
    if (!incident) return;
    try {
      const updated = await api.incidents.updateStatus(incident.id, newStatus);
      setIncident({ ...incident, status: updated.status });
    } catch (e: any) {
      setActionError(e.message || 'Failed updating status');
    }
  };

  const handleApproveAction = async () => {
    if (!approvalModalAction) return;
    try {
      await api.remediations.approve(approvalModalAction.id, approvalNotes);
      setApprovalModalAction(null);
      setApprovalNotes('');
      await loadIncidentData();
    } catch (e: any) {
      setActionError(e.message || 'Failed approving action');
    }
  };

  const handleRejectAction = async () => {
    if (!rejectionModalAction) return;
    if (!rejectionReason.trim()) {
      setActionError('Rejection reason is required');
      return;
    }
    try {
      await api.remediations.reject(rejectionModalAction.id, rejectionReason);
      setRejectionModalAction(null);
      setRejectionReason('');
      await loadIncidentData();
    } catch (e: any) {
      setActionError(e.message || 'Failed rejecting action');
    }
  };

  if (loading) {
    return <div className="text-center py-24 text-xs font-mono text-slate-500">Loading incident telemetry...</div>;
  }

  if (!incident) {
    return <div className="text-center py-24 text-xs font-mono text-red-400">Incident not found.</div>;
  }

  return (
    <div className="space-y-6">
      {/* Top Header Card */}
      <div className="bg-sentinel-950 border border-sentinel-800 rounded-xl p-6 shadow-xl">
        <div className="flex flex-col lg:flex-row lg:items-center justify-between gap-4">
          <div>
            <div className="flex items-center space-x-3 mb-1">
              <span className="text-base font-bold font-mono text-cyan-400">{incident.incident_number}</span>
              <span
                className={
                  incident.severity === 'CRITICAL'
                    ? 'badge-critical'
                    : incident.severity === 'HIGH'
                    ? 'badge-high'
                    : 'badge-medium'
                }
              >
                {incident.severity}
              </span>
              <span className="badge-info">CONFIDENCE: {(incident.confidence * 100).toFixed(0)}%</span>
            </div>
            <h1 className="text-lg font-bold text-white">{incident.title}</h1>
            <p className="text-xs text-slate-400 mt-1 max-w-3xl">{incident.description}</p>
          </div>

          {/* Right Action Block */}
          <div className="flex items-center space-x-3">
            <select
              value={incident.status}
              onChange={(e) => handleStatusChange(e.target.value)}
              className="bg-sentinel-900 border border-sentinel-700 rounded-lg px-3 py-1.5 text-xs text-slate-200 font-mono focus:outline-none focus:border-cyan-500"
            >
              <option value="OPEN">STATUS: OPEN</option>
              <option value="INVESTIGATING">STATUS: INVESTIGATING</option>
              <option value="CONTAINED">STATUS: CONTAINED</option>
              <option value="RESOLVED">STATUS: RESOLVED</option>
              <option value="CLOSED">STATUS: CLOSED</option>
            </select>

            <button
              onClick={handleRunInvestigation}
              disabled={investigating}
              className="px-3.5 py-1.5 bg-gradient-to-r from-cyan-600 to-blue-600 hover:from-cyan-500 hover:to-blue-500 text-white font-medium rounded-lg text-xs transition-all flex items-center space-x-1.5 shadow-lg shadow-cyan-950/50 disabled:opacity-50"
            >
              <Sparkles className="w-3.5 h-3.5" />
              <span>{investigating ? 'Investigating...' : 'Run AI Investigation'}</span>
            </button>
          </div>
        </div>

        {actionError && (
          <div className="mt-4 p-2.5 bg-red-950/60 border border-red-800 rounded-lg text-xs text-red-300">
            {actionError}
          </div>
        )}

        {/* Tab Navigation */}
        <div className="flex border-b border-sentinel-800/80 mt-6 space-x-6 text-xs font-mono">
          {[
            { key: 'overview', label: 'Overview & Risk Scoring' },
            { key: 'timeline', label: `Timeline (${incident.timeline?.length || 0})` },
            { key: 'graph', label: 'Attack Graph' },
            { key: 'ai', label: 'AI Investigation & Findings' },
            { key: 'remediation', label: `Remediation (${remediations.length})` },
          ].map((tab) => (
            <button
              key={tab.key}
              onClick={() => setActiveTab(tab.key as any)}
              className={`pb-2.5 transition-colors relative ${
                activeTab === tab.key ? 'text-cyan-400 font-semibold' : 'text-slate-400 hover:text-slate-200'
              }`}
            >
              <span>{tab.label}</span>
              {activeTab === tab.key && (
                <span className="absolute bottom-0 left-0 right-0 h-0.5 bg-cyan-400 rounded-full" />
              )}
            </button>
          ))}
        </div>
      </div>

      {/* TAB 1: OVERVIEW & EXPLAINABLE RISK SCORING */}
      {activeTab === 'overview' && (
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Risk Calculation Breakdown (Explainable Scoring) */}
          <div className="lg:col-span-2 bg-sentinel-950 border border-sentinel-800 rounded-xl p-5 shadow-lg space-y-4">
            <div className="flex items-center justify-between border-b border-sentinel-800/80 pb-3">
              <div>
                <h3 className="text-sm font-semibold text-white">Explainable Risk Score Calculation</h3>
                <p className="text-xs font-mono text-slate-400">
                  Transparent additive factors determining severity level
                </p>
              </div>
              <div className="text-right">
                <span className="text-2xl font-bold font-mono text-red-400">{incident.risk_score}</span>
                <span className="text-xs font-mono text-slate-500"> / 100</span>
              </div>
            </div>

            <div className="space-y-2.5">
              {incident.risk_factors?.map((f: any, idx: number) => (
                <div
                  key={idx}
                  className="p-3 rounded-lg bg-sentinel-900/60 border border-sentinel-800/80 flex items-center justify-between"
                >
                  <div className="flex items-center space-x-3">
                    <span className="text-xs font-mono font-bold text-red-400 bg-red-950/80 border border-red-900 rounded px-2 py-0.5">
                      +{f.points}
                    </span>
                    <div>
                      <div className="text-xs font-medium text-slate-200">{f.name}</div>
                      <div className="text-[11px] font-mono text-slate-400">{f.reason}</div>
                    </div>
                  </div>
                  <span className="text-[10px] font-mono text-slate-500 uppercase">Verified</span>
                </div>
              ))}
            </div>
          </div>

          {/* Affected Assets & Users */}
          <div className="bg-sentinel-950 border border-sentinel-800 rounded-xl p-5 shadow-lg space-y-4">
            <h3 className="text-sm font-semibold text-white border-b border-sentinel-800/80 pb-3">
              Implicated Entities
            </h3>

            <div>
              <div className="text-xs font-mono text-slate-400 flex items-center space-x-1.5 mb-2">
                <User className="w-3.5 h-3.5 text-cyan-400" />
                <span>AFFECTED PRINCIPALS</span>
              </div>
              <div className="space-y-1.5">
                {incident.affected_users?.map((u: string, idx: number) => (
                  <div key={idx} className="p-2 bg-sentinel-900 rounded border border-sentinel-800 text-xs font-mono text-slate-200">
                    {u}
                  </div>
                ))}
              </div>
            </div>

            <div className="pt-2">
              <div className="text-xs font-mono text-slate-400 flex items-center space-x-1.5 mb-2">
                <Server className="w-3.5 h-3.5 text-purple-400" />
                <span>TARGETED ASSETS & RESOURCES</span>
              </div>
              <div className="space-y-1.5">
                {incident.affected_assets?.length > 0 ? (
                  incident.affected_assets.map((a: string, idx: number) => (
                    <div key={idx} className="p-2 bg-sentinel-900 rounded border border-sentinel-800 text-xs font-mono text-slate-200">
                      {a}
                    </div>
                  ))
                ) : (
                  <div className="text-xs font-mono text-slate-500 italic">No specific assets labeled</div>
                )}
              </div>
            </div>
          </div>
        </div>
      )}

      {/* TAB 2: CHRONOLOGICAL TIMELINE */}
      {activeTab === 'timeline' && (
        <div className="bg-sentinel-950 border border-sentinel-800 rounded-xl p-6 shadow-lg">
          <h3 className="text-sm font-semibold text-white mb-4">Event Sequence & Attack Progression</h3>
          <div className="relative border-l border-sentinel-800 ml-4 space-y-6">
            {incident.timeline?.map((item: any, idx: number) => (
              <div key={item.id} className="relative pl-6">
                <div className="absolute -left-2 top-1 w-4 h-4 rounded-full bg-sentinel-900 border-2 border-cyan-400 flex items-center justify-center">
                  <div className="w-1.5 h-1.5 rounded-full bg-cyan-400" />
                </div>
                <div className="p-3 bg-sentinel-900/60 border border-sentinel-800/80 rounded-lg">
                  <div className="flex flex-col sm:flex-row sm:items-center justify-between text-xs font-mono mb-1">
                    <span className="font-bold text-cyan-300">{item.event_type}</span>
                    <span className="text-slate-500 text-[11px]">{new Date(item.timestamp).toLocaleString()}</span>
                  </div>
                  <div className="text-xs text-slate-300 font-sans">{item.description}</div>
                  <div className="mt-2 flex items-center space-x-3 text-[11px] font-mono text-slate-400">
                    <span>Actor: <strong className="text-slate-300">{item.actor}</strong></span>
                    <span>IP: <strong className="text-slate-300">{item.source_ip}</strong></span>
                    <span
                      className={
                        item.severity === 'CRITICAL'
                          ? 'text-red-400 font-bold'
                          : item.severity === 'HIGH'
                          ? 'text-orange-400 font-bold'
                          : 'text-slate-400'
                      }
                    >
                      {item.severity}
                    </span>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* TAB 3: ATTACK GRAPH */}
      {activeTab === 'graph' && (
        <div className="bg-sentinel-950 border border-sentinel-800 rounded-xl p-6 shadow-lg">
          <div className="flex items-center justify-between mb-4 border-b border-sentinel-800/80 pb-3">
            <div>
              <h3 className="text-sm font-semibold text-white">Entity Relationship & Attack Graph</h3>
              <p className="text-xs font-mono text-slate-400">Correlated relationship mapping across users, assets, and credentials</p>
            </div>
            <div className="flex items-center space-x-3 text-[11px] font-mono text-slate-400">
              <span className="flex items-center space-x-1"><span className="w-2.5 h-2.5 rounded-full bg-red-500 inline-block" /><span>Incident</span></span>
              <span className="flex items-center space-x-1"><span className="w-2.5 h-2.5 rounded-full bg-cyan-500 inline-block" /><span>User</span></span>
              <span className="flex items-center space-x-1"><span className="w-2.5 h-2.5 rounded-full bg-purple-500 inline-block" /><span>Asset</span></span>
              <span className="flex items-center space-x-1"><span className="w-2.5 h-2.5 rounded-full bg-amber-500 inline-block" /><span>Credential</span></span>
            </div>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="border border-sentinel-800 rounded-lg p-4 bg-sentinel-900/40">
              <h4 className="text-xs font-mono font-bold text-slate-300 mb-3 uppercase">Nodes ({attackGraph?.nodes?.length || 0})</h4>
              <div className="space-y-2">
                {attackGraph?.nodes?.map((node: any) => (
                  <div key={node.id} className="p-2.5 rounded bg-sentinel-950 border border-sentinel-800 flex items-center justify-between text-xs font-mono">
                    <div className="flex items-center space-x-2">
                      <span className={`w-2 h-2 rounded-full ${node.type === 'INCIDENT' ? 'bg-red-500' : node.type === 'USER' ? 'bg-cyan-500' : node.type === 'ASSET' ? 'bg-purple-500' : 'bg-amber-500'}`} />
                      <span className="font-semibold text-slate-200">{node.label}</span>
                    </div>
                    <span className="text-[10px] text-slate-500">{node.type}</span>
                  </div>
                ))}
              </div>
            </div>

            <div className="border border-sentinel-800 rounded-lg p-4 bg-sentinel-900/40">
              <h4 className="text-xs font-mono font-bold text-slate-300 mb-3 uppercase">Relationships / Edges ({attackGraph?.edges?.length || 0})</h4>
              <div className="space-y-2">
                {attackGraph?.edges?.map((edge: any) => (
                  <div key={edge.id} className="p-2.5 rounded bg-sentinel-950 border border-sentinel-800 flex items-center justify-between text-xs font-mono">
                    <span className="text-cyan-400 truncate max-w-[120px]">{edge.source}</span>
                    <span className="text-[10px] text-slate-400 bg-sentinel-900 px-2 py-0.5 rounded border border-sentinel-800">
                      ── {edge.label} ──►
                    </span>
                    <span className="text-purple-400 truncate max-w-[120px]">{edge.target}</span>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>
      )}

      {/* TAB 4: AI INVESTIGATION & FINDINGS */}
      {activeTab === 'ai' && (
        <div className="space-y-6">
          {!investigation ? (
            <div className="bg-sentinel-950 border border-sentinel-800 rounded-xl p-12 text-center shadow-lg">
              <Sparkles className="w-8 h-8 text-cyan-400 mx-auto mb-3" />
              <h3 className="text-sm font-semibold text-white">No AI Investigation Executed Yet</h3>
              <p className="text-xs font-mono text-slate-400 max-w-md mx-auto mt-1 mb-4">
                Trigger the LangGraph AI Investigator to synthesize the attack chain, verify facts, and suggest human-gated remediations.
              </p>
              <button
                onClick={handleRunInvestigation}
                disabled={investigating}
                className="px-4 py-2 bg-gradient-to-r from-cyan-600 to-blue-600 hover:from-cyan-500 text-white rounded-lg text-xs font-medium"
              >
                {investigating ? 'Running LangGraph Agent...' : 'Start AI Investigation'}
              </button>
            </div>
          ) : (
            <div className="space-y-6">
              {/* Executive Summary */}
              <div className="bg-sentinel-950 border border-sentinel-800 rounded-xl p-5 shadow-lg space-y-2">
                <div className="flex items-center justify-between">
                  <div className="flex items-center space-x-2">
                    <Sparkles className="w-4 h-4 text-cyan-400" />
                    <h3 className="text-sm font-semibold text-white">AI Security Investigation Synthesis</h3>
                  </div>
                  <span className="text-xs font-mono text-slate-400">Model: {investigation.model_used}</span>
                </div>
                <p className="text-xs text-slate-300 leading-relaxed font-sans">{investigation.summary}</p>
              </div>

              {/* Attack Chain */}
              <div className="bg-sentinel-950 border border-sentinel-800 rounded-xl p-5 shadow-lg">
                <h4 className="text-xs font-mono font-bold text-slate-300 uppercase mb-3">Synthesized Attack Chain</h4>
                <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
                  {investigation.attack_chain?.map((step: any) => (
                    <div key={step.step_number} className="p-3 bg-sentinel-900 rounded-lg border border-sentinel-800">
                      <div className="flex items-center justify-between text-[11px] font-mono text-cyan-400 mb-1">
                        <span>STAGE {step.step_number}</span>
                        <span className="text-slate-400">{step.stage_name}</span>
                      </div>
                      <div className="text-xs font-semibold text-slate-200">{step.action}</div>
                      <div className="text-[11px] font-mono text-slate-400 mt-1 truncate">Actor: {step.actor}</div>
                    </div>
                  ))}
                </div>
              </div>

              {/* Facts vs Inferences Grid */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                {/* Verified Evidence (FACT) */}
                <div className="bg-sentinel-950 border border-sentinel-800 rounded-xl p-5 shadow-lg">
                  <h4 className="text-xs font-mono font-bold text-emerald-400 uppercase mb-3 flex items-center space-x-1.5">
                    <CheckCircle className="w-3.5 h-3.5" />
                    <span>VERIFIED EVIDENCE (FACT)</span>
                  </h4>
                  <div className="space-y-2">
                    {investigation.evidence?.map((fact: any, idx: number) => (
                      <div key={idx} className="p-2.5 rounded bg-sentinel-900/60 border border-sentinel-800/80 text-xs font-mono text-slate-300">
                        {fact.fact}
                      </div>
                    ))}
                  </div>
                </div>

                {/* Analytical Inferences (INFERENCE) */}
                <div className="bg-sentinel-950 border border-sentinel-800 rounded-xl p-5 shadow-lg">
                  <h4 className="text-xs font-mono font-bold text-amber-400 uppercase mb-3 flex items-center space-x-1.5">
                    <AlertTriangle className="w-3.5 h-3.5" />
                    <span>SECURITY FINDINGS (INFERENCE)</span>
                  </h4>
                  <div className="space-y-2">
                    {investigation.findings?.map((f: any, idx: number) => (
                      <div key={idx} className="p-2.5 rounded bg-sentinel-900/60 border border-sentinel-800/80">
                        <div className="flex items-center justify-between text-[10px] font-mono text-amber-400 mb-0.5">
                          <span>{f.category}</span>
                          <span className="font-bold">{f.severity}</span>
                        </div>
                        <div className="text-xs text-slate-200 font-sans">{f.inference}</div>
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            </div>
          )}
        </div>
      )}

      {/* TAB 5: HUMAN-IN-THE-LOOP REMEDIATION */}
      {activeTab === 'remediation' && (
        <div className="bg-sentinel-950 border border-sentinel-800 rounded-xl p-6 shadow-lg space-y-4">
          <div className="flex items-center justify-between border-b border-sentinel-800/80 pb-3">
            <div>
              <h3 className="text-sm font-semibold text-white">Human-in-the-Loop Remediation Enforcement</h3>
              <p className="text-xs font-mono text-slate-400">
                High-impact containment actions require mandatory Administrator approval before execution
              </p>
            </div>
            <span className="text-xs font-mono bg-purple-950/80 text-purple-300 border border-purple-800 rounded px-2.5 py-1">
              {isAdmin ? 'ADMIN AUTHORIZED' : 'ANALYST / DEV (READ-ONLY)'}
            </span>
          </div>

          {remediations.length === 0 ? (
            <div className="text-center py-10 text-xs font-mono text-slate-500">
              No remediation actions staged. Run AI investigation to generate recommended mitigations.
            </div>
          ) : (
            <div className="space-y-3">
              {remediations.map((action) => (
                <div
                  key={action.id}
                  className="p-4 rounded-xl bg-sentinel-900/70 border border-sentinel-800 flex flex-col md:flex-row md:items-center justify-between gap-4"
                >
                  <div className="space-y-1">
                    <div className="flex items-center space-x-2">
                      <span className="font-bold font-mono text-xs text-white">{action.action_type}</span>
                      <span
                        className={`text-[10px] font-mono px-2 py-0.5 rounded font-medium border ${
                          action.status === 'PENDING_APPROVAL'
                            ? 'bg-amber-950/80 text-amber-300 border-amber-700/80'
                            : action.status === 'EXECUTED'
                            ? 'bg-emerald-950/80 text-emerald-300 border-emerald-700/80'
                            : 'bg-red-950/80 text-red-300 border-red-700/80'
                        }`}
                      >
                        {action.status}
                      </span>
                    </div>
                    <p className="text-xs text-slate-300 font-sans">{action.description}</p>
                    {action.rejection_reason && (
                      <div className="text-[11px] font-mono text-red-400">Rejection Reason: {action.rejection_reason}</div>
                    )}
                    {action.execution_result && (
                      <div className="text-[11px] font-mono text-emerald-400">
                        Execution: {action.execution_result.mode} ({action.execution_result.status})
                      </div>
                    )}
                  </div>

                  {action.status === 'PENDING_APPROVAL' && (
                    <div className="flex items-center space-x-2 shrink-0">
                      {isAdmin ? (
                        <>
                          <button
                            onClick={() => setApprovalModalAction(action)}
                            className="px-3 py-1.5 bg-emerald-600 hover:bg-emerald-500 text-white rounded text-xs font-medium flex items-center space-x-1"
                          >
                            <Check className="w-3.5 h-3.5" />
                            <span>Approve</span>
                          </button>
                          <button
                            onClick={() => setRejectionModalAction(action)}
                            className="px-3 py-1.5 bg-red-700 hover:bg-red-600 text-white rounded text-xs font-medium flex items-center space-x-1"
                          >
                            <X className="w-3.5 h-3.5" />
                            <span>Reject</span>
                          </button>
                        </>
                      ) : (
                        <span className="text-[11px] font-mono text-slate-500 italic border border-sentinel-800 rounded px-2.5 py-1">
                          Admin Approval Required
                        </span>
                      )}
                    </div>
                  )}
                </div>
              ))}
            </div>
          )}
        </div>
      )}

      {/* APPROVAL MODAL */}
      {approvalModalAction && (
        <div className="fixed inset-0 z-50 bg-black/80 backdrop-blur-sm flex items-center justify-center p-4">
          <div className="bg-sentinel-900 border border-sentinel-700 rounded-xl max-w-md w-full p-6 space-y-4 shadow-2xl">
            <h3 className="text-sm font-bold text-white flex items-center space-x-2">
              <ShieldCheck className="w-4 h-4 text-emerald-400" />
              <span>Confirm Remediation Execution</span>
            </h3>
            <p className="text-xs text-slate-300">
              You are approving the simulated execution of <strong>{approvalModalAction.action_type}</strong> for incident {incident.incident_number}.
            </p>
            <div>
              <label className="block text-[11px] font-mono text-slate-400 mb-1">APPROVAL NOTES (OPTIONAL)</label>
              <textarea
                value={approvalNotes}
                onChange={(e) => setApprovalNotes(e.target.value)}
                placeholder="Approved per incident containment procedure..."
                className="w-full bg-sentinel-950 border border-sentinel-700 rounded p-2 text-xs text-slate-200 focus:outline-none focus:border-cyan-500"
                rows={3}
              />
            </div>
            <div className="flex justify-end space-x-2 pt-2">
              <button
                onClick={() => setApprovalModalAction(null)}
                className="px-3 py-1.5 bg-sentinel-800 hover:bg-sentinel-700 rounded text-xs text-slate-300"
              >
                Cancel
              </button>
              <button
                onClick={handleApproveAction}
                className="px-4 py-1.5 bg-emerald-600 hover:bg-emerald-500 text-white rounded text-xs font-medium"
              >
                Confirm & Execute
              </button>
            </div>
          </div>
        </div>
      )}

      {/* REJECTION MODAL */}
      {rejectionModalAction && (
        <div className="fixed inset-0 z-50 bg-black/80 backdrop-blur-sm flex items-center justify-center p-4">
          <div className="bg-sentinel-900 border border-sentinel-700 rounded-xl max-w-md w-full p-6 space-y-4 shadow-2xl">
            <h3 className="text-sm font-bold text-white flex items-center space-x-2">
              <XCircle className="w-4 h-4 text-red-400" />
              <span>Reject Remediation Action</span>
            </h3>
            <p className="text-xs text-slate-300">
              Provide a justification for rejecting <strong>{rejectionModalAction.action_type}</strong>.
            </p>
            <div>
              <label className="block text-[11px] font-mono text-slate-400 mb-1">REJECTION REASON (REQUIRED)</label>
              <textarea
                value={rejectionReason}
                onChange={(e) => setRejectionReason(e.target.value)}
                placeholder="False positive or alternative operational mitigation selected..."
                className="w-full bg-sentinel-950 border border-sentinel-700 rounded p-2 text-xs text-slate-200 focus:outline-none focus:border-cyan-500"
                rows={3}
                required
              />
            </div>
            <div className="flex justify-end space-x-2 pt-2">
              <button
                onClick={() => setRejectionModalAction(null)}
                className="px-3 py-1.5 bg-sentinel-800 hover:bg-sentinel-700 rounded text-xs text-slate-300"
              >
                Cancel
              </button>
              <button
                onClick={handleRejectAction}
                className="px-4 py-1.5 bg-red-700 hover:bg-red-600 text-white rounded text-xs font-medium"
              >
                Reject Action
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
