import React, { useEffect, useState } from 'react';
import { api } from '../api/client';
import { useAuth } from '../context/AuthContext';
import { Radio, Search, Plus, CheckCircle, RefreshCw } from 'lucide-react';

export const EventsPage: React.FC = () => {
  const { user } = useAuth();
  const isViewer = user?.role === 'Viewer';
  const [events, setEvents] = useState<any[]>([]);
  const [total, setTotal] = useState(0);
  const [actorFilter, setActorFilter] = useState('');
  const [severityFilter, setSeverityFilter] = useState('');
  const [loading, setLoading] = useState(true);

  // Ingestion Modal State
  const [showModal, setShowModal] = useState(false);
  const [ingestPayload, setIngestPayload] = useState(
    JSON.stringify(
      {
        user: 'developer01',
        event_type: 'file_access',
        client_ip: '10.0.0.12',
        severity: 'HIGH',
        resource: 'customer_data.csv',
        classification: 'RESTRICTED',
        action: 'DOWNLOAD',
      },
      null,
      2
    )
  );
  const [ingestStatus, setIngestStatus] = useState<string | null>(null);

  const fetchEvents = async () => {
    setLoading(true);
    try {
      const data = await api.events.list({
        actor: actorFilter || undefined,
        severity: severityFilter || undefined,
        limit: 50,
      });
      setEvents(data.items);
      setTotal(data.total);
    } catch (e) {
      console.error('Failed fetching events', e);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchEvents();
  }, [severityFilter]);

  const handleSearchSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    fetchEvents();
  };

  const handleIngestSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      const parsed = JSON.parse(ingestPayload);
      await api.events.ingest(parsed);
      setIngestStatus('Event ingested and normalized successfully.');
      setTimeout(() => {
        setShowModal(false);
        setIngestStatus(null);
      }, 1000);
      await fetchEvents();
    } catch (err: any) {
      setIngestStatus(`Error: ${err.message}`);
    }
  };

  const [simulating, setSimulating] = useState(false);

  const handleSimulate = async () => {
    setSimulating(true);
    try {
      await api.events.simulate();
      await fetchEvents();
    } catch (err: any) {
      alert(`Simulation error: ${err.message}`);
    } finally {
      setSimulating(false);
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-xl font-bold text-slate-900 flex items-center space-x-2">
            <Radio className="w-5 h-5 text-indigo-600" />
            <span>Normalized Security Event Telemetry</span>
          </h1>
          <p className="text-xs font-mono text-slate-500 mt-0.5">
            Real-time multi-source event stream normalized to canonical entity schema with verified provenance
          </p>
        </div>

        <div className="flex items-center space-x-3">
          <button
            onClick={handleSimulate}
            disabled={simulating || isViewer}
            className="px-3 py-1.5 bg-amber-50 hover:bg-amber-100 text-amber-800 border border-amber-200 rounded-lg text-xs font-medium flex items-center space-x-1.5 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
            title={isViewer ? 'Viewer role is read-only. Cannot generate events.' : 'Generate controlled demonstration events tagged as simulated'}
          >
            <span>{simulating ? 'Generating...' : isViewer ? 'Simulation (Admin/Analyst only)' : 'Generate Demo Events'}</span>
          </button>
          <button
            onClick={() => setShowModal(true)}
            disabled={isViewer}
            title={isViewer ? 'Viewer role is read-only. Cannot ingest events.' : 'Ingest raw event'}
            className="px-3.5 py-1.5 bg-gradient-to-r from-cyan-600 to-blue-600 hover:from-cyan-700 text-white rounded-lg text-xs font-medium flex items-center space-x-1.5 shadow-sm disabled:opacity-50 disabled:cursor-not-allowed"
          >
            <Plus className="w-3.5 h-3.5" />
            <span>Ingest Raw Event</span>
          </button>
          <button
            onClick={fetchEvents}
            className="p-1.5 bg-white hover:bg-slate-50 border border-slate-300 rounded text-slate-600 transition-colors"
          >
            <RefreshCw className="w-4 h-4" />
          </button>
        </div>
      </div>

      {/* Search and Filters */}
      <div className="bg-sentinel-950 border border-sentinel-800 rounded-xl p-4 shadow-lg flex flex-wrap items-center justify-between gap-3">
        <form onSubmit={handleSearchSubmit} className="flex items-center space-x-2 flex-1 max-w-md">
          <div className="relative flex-1">
            <Search className="w-3.5 h-3.5 text-slate-500 absolute left-2.5 top-2.5" />
            <input
              type="text"
              placeholder="Search by actor or principal..."
              value={actorFilter}
              onChange={(e) => setActorFilter(e.target.value)}
              className="w-full bg-sentinel-900 border border-sentinel-800 rounded-lg pl-8 pr-3 py-1.5 text-xs text-slate-200 focus:outline-none focus:border-cyan-500"
            />
          </div>
          <button
            type="submit"
            className="px-3 py-1.5 bg-sentinel-800 hover:bg-sentinel-700 text-xs font-mono rounded text-slate-300"
          >
            Filter
          </button>
        </form>

        <div className="flex items-center space-x-3 text-xs font-mono">
          <select
            value={severityFilter}
            onChange={(e) => setSeverityFilter(e.target.value)}
            className="bg-sentinel-900 border border-sentinel-800 rounded-lg px-2.5 py-1.5 text-slate-300 focus:outline-none focus:border-cyan-500"
          >
            <option value="">SEVERITY: ALL</option>
            <option value="CRITICAL">CRITICAL</option>
            <option value="HIGH">HIGH</option>
            <option value="MEDIUM">MEDIUM</option>
            <option value="LOW">LOW</option>
            <option value="INFO">INFO</option>
          </select>
          <span className="text-slate-500">TOTAL: {total}</span>
        </div>
      </div>

      {/* Events Table */}
      <div className="bg-sentinel-950 border border-sentinel-800 rounded-xl p-5 shadow-lg">
        {loading ? (
          <div className="text-center py-10 text-xs font-mono text-slate-500">Loading events...</div>
        ) : events.length === 0 ? (
          <div className="text-center py-10 text-xs font-mono text-slate-500">No events found matching filters.</div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs">
              <thead className="border-b border-sentinel-800 text-[11px] font-mono text-slate-400 uppercase">
                <tr>
                  <th className="pb-2">Timestamp</th>
                  <th className="pb-2">Provenance</th>
                  <th className="pb-2">Event Type</th>
                  <th className="pb-2">Severity</th>
                  <th className="pb-2">Actor (Normalized)</th>
                  <th className="pb-2">Source IP</th>
                  <th className="pb-2">Source System</th>
                  <th className="pb-2">Resource</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-sentinel-800/60 font-mono">
                {events.map((e) => {
                  const isSimulated =
                    e.source === 'simulated_generator' ||
                    e.raw_payload?.is_simulated === true ||
                    e.normalized_payload?.is_simulated === true;
                  return (
                    <tr key={e.id} className="hover:bg-slate-50 transition-colors">
                      <td className="py-2.5 text-slate-500 text-[11px]">{new Date(e.timestamp).toLocaleTimeString()}</td>
                      <td className="py-2.5">
                        <span
                          className={`px-1.5 py-0.5 rounded text-[10px] font-semibold border ${
                            isSimulated
                              ? 'bg-amber-50 text-amber-800 border-amber-200'
                              : 'bg-emerald-50 text-emerald-700 border-emerald-200'
                          }`}
                        >
                          {isSimulated ? 'SIMULATED' : 'LIVE'}
                        </span>
                      </td>
                      <td className="py-2.5 font-bold text-indigo-600">{e.event_type}</td>
                      <td className="py-2.5">
                        <span
                          className={
                            e.severity === 'CRITICAL'
                              ? 'badge-critical'
                              : e.severity === 'HIGH'
                              ? 'badge-high'
                              : e.severity === 'MEDIUM'
                              ? 'badge-medium'
                              : 'badge-info'
                          }
                        >
                          {e.severity}
                        </span>
                      </td>
                      <td className="py-2.5 text-slate-800 font-medium">{e.actor}</td>
                      <td className="py-2.5 text-slate-600">{e.source_ip}</td>
                      <td className="py-2.5 text-slate-500">{e.source}</td>
                      <td className="py-2.5 text-slate-700 truncate max-w-xs">
                        {e.raw_payload?.resource || e.normalized_payload?.resource || 'N/A'}
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        )}
      </div>

      {/* Ingest Modal */}
      {showModal && (
        <div className="fixed inset-0 z-50 bg-slate-900/40 backdrop-blur-sm flex items-center justify-center p-4">
          <div className="bg-white border border-slate-200 rounded-xl max-w-lg w-full p-6 space-y-4 shadow-2xl">
            <h3 className="text-sm font-bold text-slate-900">Ingest Raw Event (JSON)</h3>
            <p className="text-xs text-slate-500">
              Paste a heterogeneous payload. The normalization layer will automatically map principal, IP, and severity.
            </p>
            <textarea
              value={ingestPayload}
              onChange={(e) => setIngestPayload(e.target.value)}
              rows={9}
              className="w-full bg-slate-50 border border-slate-300 rounded p-3 text-xs font-mono text-slate-800 focus:outline-none focus:border-cyan-600"
            />
            {ingestStatus && (
              <div className="text-xs font-mono text-cyan-700 font-semibold">{ingestStatus}</div>
            )}
            <div className="flex justify-end space-x-2 pt-2">
              <button
                onClick={() => setShowModal(false)}
                className="px-3 py-1.5 bg-slate-100 hover:bg-slate-200 rounded text-xs text-slate-700 transition-colors"
              >
                Cancel
              </button>
              <button
                onClick={handleIngestSubmit}
                className="px-4 py-1.5 bg-cyan-600 hover:bg-cyan-700 text-white rounded text-xs font-medium transition-colors"
              >
                Submit Event
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
