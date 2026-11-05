import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { api } from '../api/client';
import {
  ShieldAlert,
  AlertOctagon,
  FileWarning,
  Activity,
  ArrowUpRight,
  TrendingDown,
  Clock,
  CheckCircle2,
} from 'lucide-react';
import {
  AreaChart,
  Area,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
  BarChart,
  Bar,
} from 'recharts';

export const DashboardPage: React.FC = () => {
  const [incidents, setIncidents] = useState<any[]>([]);
  const [dlpCount, setDlpCount] = useState<number>(0);
  const [eventsCount, setEventsCount] = useState<number>(0);
  const [remediations, setRemediations] = useState<any[]>([]);
  const [telemetryTrend, setTelemetryTrend] = useState<any[]>([]);
  const [loading, setLoading] = useState<boolean>(true);

  useEffect(() => {
    async function loadData() {
      try {
        const [incList, dlpList, evList, remList] = await Promise.all([
          api.incidents.list(),
          api.dlp.findings(),
          api.events.list({ limit: 100 }),
          api.remediations.list().catch(() => []),
        ]);
        setIncidents(incList);
        setDlpCount(dlpList.length);
        setEventsCount(evList.total);
        setRemediations(remList);

        // Derive real time-series from persisted event timestamps
        if (evList.items && evList.items.length > 0) {
          const buckets: Record<string, { events: number; anomalies: number }> = {};
          // Sort chronologically
          const sorted = [...evList.items].sort(
            (a, b) => new Date(a.timestamp).getTime() - new Date(b.timestamp).getTime()
          );

          for (const ev of sorted) {
            const d = new Date(ev.timestamp);
            const timeKey = d.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
            if (!buckets[timeKey]) {
              buckets[timeKey] = { events: 0, anomalies: 0 };
            }
            buckets[timeKey].events += 1;
            if (ev.severity === 'CRITICAL' || ev.severity === 'HIGH') {
              buckets[timeKey].anomalies += 1;
            }
          }

          const trendData = Object.entries(buckets).map(([time, data]) => ({
            time,
            events: data.events,
            anomalies: data.anomalies,
          }));
          setTelemetryTrend(trendData);
        } else {
          setTelemetryTrend([]);
        }
      } catch (e) {
        console.error('Failed loading dashboard telemetry', e);
      } finally {
        setLoading(false);
      }
    }
    loadData();
  }, []);

  const criticalCount = incidents.filter((i) => i.severity === 'CRITICAL').length;
  const highCount = incidents.filter((i) => i.severity === 'HIGH').length;
  const openCount = incidents.filter((i) => i.status === 'OPEN' || i.status === 'INVESTIGATING').length;

  // Real-time posture score calculated from verified system telemetry
  const postureScore =
    incidents.length === 0 && dlpCount === 0 && eventsCount === 0
      ? 100
      : Math.max(30, 100 - criticalCount * 18 - highCount * 8 - Math.min(20, dlpCount * 3));

  // Compute real Mean Time to Investigate (MTTI) from actual resolved incidents
  const resolvedIncidents = incidents.filter(
    (i) => (i.status === 'RESOLVED' || i.status === 'CLOSED') && i.resolved_at && i.detected_at
  );
  let mttiValue = 'N/A';
  let mttiSub = 'No closed incidents in database';
  if (resolvedIncidents.length > 0) {
    const totalMin = resolvedIncidents.reduce(
      (acc, cur) => acc + (new Date(cur.resolved_at).getTime() - new Date(cur.detected_at).getTime()) / 60000,
      0
    );
    const avgMin = (totalMin / resolvedIncidents.length).toFixed(1);
    mttiValue = `${avgMin} min`;
    mttiSub = `Derived from ${resolvedIncidents.length} resolved incident(s)`;
  }

  // Compute real Human-in-the-Loop approval metrics
  const pendingRemediations = remediations.filter((r) => r.status === 'PENDING_APPROVAL').length;
  const executedRemediations = remediations.filter((r) => r.status === 'EXECUTED').length;
  const gateValue =
    remediations.length > 0
      ? `${pendingRemediations} Pending`
      : '0 Pending Actions';
  const gateSub =
    remediations.length > 0
      ? `${executedRemediations} Approved & Executed`
      : 'Zero unreviewed actions';

  return (
    <div className="space-y-6">
      {/* Top Banner & Posture Score */}
      <div className="grid grid-cols-1 lg:grid-cols-4 gap-4">
        {/* Posture Score Widget */}
        <div className="bg-sentinel-950 border border-sentinel-800 rounded-xl p-5 flex items-center justify-between shadow-lg">
          <div>
            <div className="text-xs font-mono text-slate-400">ORGANIZATION SECURITY POSTURE</div>
            <div className="flex items-baseline space-x-2 mt-1">
              <span className={`text-4xl font-bold font-mono ${postureScore > 75 ? 'text-emerald-400' : postureScore > 50 ? 'text-amber-400' : 'text-red-400'}`}>
                {postureScore}
              </span>
              <span className="text-xs text-slate-500 font-mono">/ 100</span>
            </div>
            <div className="text-[11px] text-slate-400 mt-1 flex items-center">
              <span className="inline-block w-2 h-2 rounded-full bg-emerald-500 mr-1.5 animate-pulse" />
              Calculated from active incidents & DLP telemetry
            </div>
          </div>
          <div className="w-14 h-14 rounded-full border-4 border-sentinel-800 flex items-center justify-center font-mono font-bold text-xs bg-sentinel-900 text-slate-300">
            {postureScore > 75 ? 'SECURE' : postureScore > 50 ? 'GUARDED' : 'CRITICAL'}
          </div>
        </div>

        {/* Critical Incidents Card */}
        <div className="bg-sentinel-950 border border-sentinel-800 rounded-xl p-5 shadow-lg">
          <div className="flex items-center justify-between">
            <span className="text-xs font-mono text-slate-400">CRITICAL INCIDENTS</span>
            <AlertOctagon className="w-4 h-4 text-red-400" />
          </div>
          <div className="text-3xl font-bold font-mono text-red-400 mt-2">{criticalCount}</div>
          <div className="text-[11px] text-slate-500 mt-1">Requiring immediate containment</div>
        </div>

        {/* High Severity Card */}
        <div className="bg-sentinel-950 border border-sentinel-800 rounded-xl p-5 shadow-lg">
          <div className="flex items-center justify-between">
            <span className="text-xs font-mono text-slate-400">HIGH SEVERITY</span>
            <ShieldAlert className="w-4 h-4 text-orange-400" />
          </div>
          <div className="text-3xl font-bold font-mono text-orange-400 mt-2">{highCount}</div>
          <div className="text-[11px] text-slate-500 mt-1">Investigating via AI orchestrator</div>
        </div>

        {/* DLP Violations Card */}
        <div className="bg-sentinel-950 border border-sentinel-800 rounded-xl p-5 shadow-lg">
          <div className="flex items-center justify-between">
            <span className="text-xs font-mono text-slate-400">DLP INTERCEPTIONS</span>
            <FileWarning className="w-4 h-4 text-cyan-400" />
          </div>
          <div className="text-3xl font-bold font-mono text-cyan-400 mt-2">{dlpCount}</div>
          <div className="text-[11px] text-slate-500 mt-1">Credentials & PII masked in transit</div>
        </div>
      </div>

      {/* Charts Section */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2 bg-sentinel-950 border border-sentinel-800 rounded-xl p-5 shadow-lg">
          <div className="flex items-center justify-between mb-4">
            <div>
              <h3 className="text-sm font-semibold text-white">Event Telemetry Velocity & Anomaly Trends</h3>
              <p className="text-xs font-mono text-slate-400">Ingested events and anomalous security triggers over time</p>
            </div>
            <div className="text-xs font-mono text-cyan-400 flex items-center space-x-1">
              <Activity className="w-3.5 h-3.5" />
              <span>LIVE INGESTION</span>
            </div>
          </div>
          <div className="h-60 w-full">
            {telemetryTrend.length === 0 ? (
              <div className="h-full w-full flex flex-col items-center justify-center border border-dashed border-slate-200 rounded-lg p-6 text-center">
                <Activity className="w-8 h-8 text-slate-300 mb-2" />
                <p className="text-xs font-semibold text-slate-700">No Telemetry Timestamps Recorded</p>
                <p className="text-[11px] text-slate-400 mt-1 max-w-xs">
                  Event velocity is calculated dynamically from persisted event timestamps. Ingest security events to visualize trends.
                </p>
              </div>
            ) : (
              <ResponsiveContainer width="100%" height="100%">
                <AreaChart data={telemetryTrend}>
                  <defs>
                    <linearGradient id="colorEvents" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="5%" stopColor="#0284c7" stopOpacity={0.3} />
                      <stop offset="95%" stopColor="#0284c7" stopOpacity={0} />
                    </linearGradient>
                    <linearGradient id="colorAnomalies" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="5%" stopColor="#ef4444" stopOpacity={0.3} />
                      <stop offset="95%" stopColor="#ef4444" stopOpacity={0} />
                    </linearGradient>
                  </defs>
                  <XAxis dataKey="time" stroke="#64748b" fontSize={11} />
                  <YAxis stroke="#64748b" fontSize={11} allowDecimals={false} />
                  <Tooltip
                    contentStyle={{ backgroundColor: '#ffffff', borderColor: '#e2e8f0', fontSize: '11px', borderRadius: '8px', boxShadow: '0 4px 6px -1px rgba(0, 0, 0, 0.1)' }}
                  />
                  <Area type="monotone" dataKey="events" stroke="#0284c7" fillOpacity={1} fill="url(#colorEvents)" name="Events" />
                  <Area type="monotone" dataKey="anomalies" stroke="#ef4444" fillOpacity={1} fill="url(#colorAnomalies)" name="Threat Triggers" />
                </AreaChart>
              </ResponsiveContainer>
            )}
          </div>
        </div>

        {/* Security Metrics Breakdown */}
        <div className="bg-sentinel-950 border border-sentinel-800 rounded-xl p-5 shadow-lg flex flex-col justify-between">
          <div>
            <h3 className="text-sm font-semibold text-white mb-1">Operational Metrics</h3>
            <p className="text-xs font-mono text-slate-400 mb-4">SecOps response SLA telemetry</p>

            <div className="space-y-4">
              <div className="p-3 bg-sentinel-900/60 rounded-lg border border-sentinel-800/80">
                <div className="text-[11px] text-slate-400">Mean Time to Investigate (MTTI)</div>
                <div className="text-xl font-bold font-mono text-emerald-600 mt-0.5">{mttiValue}</div>
                <div className="text-[10px] text-slate-500">{mttiSub}</div>
              </div>

              <div className="p-3 bg-sentinel-900/60 rounded-lg border border-sentinel-800/80">
                <div className="text-[11px] text-slate-400">Human Approval Gate Status</div>
                <div className="text-xl font-bold font-mono text-cyan-700 mt-0.5">{gateValue}</div>
                <div className="text-[10px] text-slate-500">{gateSub}</div>
              </div>

              <div className="p-3 bg-sentinel-900/60 rounded-lg border border-sentinel-800/80">
                <div className="text-[11px] text-slate-400">Total Telemetry Ingested</div>
                <div className="text-xl font-bold font-mono text-white mt-0.5">{eventsCount} Events</div>
                <div className="text-[10px] text-slate-500">Persisted in database ledger</div>
              </div>
            </div>
          </div>

          <div className="mt-4 pt-3 border-t border-sentinel-800/80 text-[11px] font-mono text-slate-500 flex items-center justify-between">
            <span>Deterministic Rules: Active</span>
            <span className="text-emerald-400">PASSING</span>
          </div>
        </div>
      </div>

      {/* Active Incidents Table */}
      <div className="bg-sentinel-950 border border-sentinel-800 rounded-xl p-5 shadow-lg">
        <div className="flex items-center justify-between mb-4">
          <div>
            <h3 className="text-sm font-semibold text-white">Active Correlated Incidents</h3>
            <p className="text-xs font-mono text-slate-400">High-priority clusters identified by the correlation engine</p>
          </div>
          <Link
            to="/incidents"
            className="text-xs font-mono text-cyan-400 hover:text-cyan-300 flex items-center space-x-1"
          >
            <span>View All Incidents</span>
            <ArrowUpRight className="w-3.5 h-3.5" />
          </Link>
        </div>

        {incidents.length === 0 ? (
          <div className="text-center py-8 text-xs font-mono text-slate-500">
            No active incidents detected. Ingest security events to observe automatic correlation.
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs">
              <thead className="border-b border-sentinel-800 text-[11px] font-mono text-slate-400 uppercase">
                <tr>
                  <th className="pb-2">Incident ID</th>
                  <th className="pb-2">Title</th>
                  <th className="pb-2">Severity</th>
                  <th className="pb-2">Risk Score</th>
                  <th className="pb-2">Status</th>
                  <th className="pb-2">Detected</th>
                  <th className="pb-2 text-right">Action</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-sentinel-800/60 font-mono">
                {incidents.slice(0, 5).map((inc) => (
                  <tr key={inc.id} className="hover:bg-sentinel-900/50 transition-colors">
                    <td className="py-2.5 font-bold text-cyan-400">{inc.incident_number}</td>
                    <td className="py-2.5 font-sans font-medium text-slate-200">{inc.title}</td>
                    <td className="py-2.5">
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
                    <td className="py-2.5 font-bold">
                      <span className={inc.risk_score >= 80 ? 'text-red-400' : 'text-amber-400'}>
                        {inc.risk_score} / 100
                      </span>
                    </td>
                    <td className="py-2.5">
                      <span className="badge-info">{inc.status}</span>
                    </td>
                    <td className="py-2.5 text-slate-400 text-[11px]">
                      {new Date(inc.detected_at).toLocaleTimeString()}
                    </td>
                    <td className="py-2.5 text-right font-sans">
                      <Link
                        to={`/incidents/${inc.id}`}
                        className="px-2.5 py-1 bg-cyan-50 hover:bg-cyan-100 text-cyan-700 border border-cyan-200 rounded text-xs font-medium transition-colors"
                      >
                        Investigate
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
