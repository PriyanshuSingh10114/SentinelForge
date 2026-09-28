import React, { useEffect, useState } from 'react';
import { api } from '../api/client';
import { Radio, Search, Plus, CheckCircle, RefreshCw } from 'lucide-react';

export const EventsPage: React.FC = () => {
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

  return (
    <div className="space-y-6">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-xl font-bold text-white flex items-center space-x-2">
            <Radio className="w-5 h-5 text-cyan-400" />
            <span>Normalized Security Event Telemetry</span>
          </h1>
          <p className="text-xs font-mono text-slate-400 mt-0.5">
            Real-time multi-source event stream normalized to canonical entity schema
          </p>
        </div>

        <div className="flex items-center space-x-3">
          <button
            onClick={() => setShowModal(true)}
            className="px-3.5 py-1.5 bg-gradient-to-r from-cyan-600 to-blue-600 hover:from-cyan-500 text-white rounded-lg text-xs font-medium flex items-center space-x-1.5 shadow-md shadow-cyan-950/40"
          >
            <Plus className="w-3.5 h-3.5" />
            <span>Ingest Test Event</span>
          </button>
          <button
            onClick={fetchEvents}
            className="p-1.5 bg-sentinel-900 hover:bg-sentinel-800 border border-sentinel-800 rounded text-slate-400 hover:text-slate-200"
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
                  <th className="pb-2">Event Type</th>
                  <th className="pb-2">Severity</th>
                  <th className="pb-2">Actor (Normalized)</th>
                  <th className="pb-2">Source IP</th>
                  <th className="pb-2">Source System</th>
                  <th className="pb-2">Resource</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-sentinel-800/60 font-mono">
                {events.map((e) => (
                  <tr key={e.id} className="hover:bg-sentinel-900/50 transition-colors">
                    <td className="py-2.5 text-slate-500 text-[11px]">{new Date(e.timestamp).toLocaleTimeString()}</td>
                    <td className="py-2.5 font-bold text-cyan-400">{e.event_type}</td>
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
                    <td className="py-2.5 text-slate-200">{e.actor}</td>
                    <td className="py-2.5 text-slate-400">{e.source_ip}</td>
                    <td className="py-2.5 text-slate-500">{e.source}</td>
                    <td className="py-2.5 text-slate-300 truncate max-w-xs">
                      {(e.raw_payload || {}).get?.('resource') || (e.normalized_payload || {}).resource || 'N/A'}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>

      {/* Ingest Modal */}
      {showModal && (
        <div className="fixed inset-0 z-50 bg-black/80 backdrop-blur-sm flex items-center justify-center p-4">
          <div className="bg-sentinel-900 border border-sentinel-700 rounded-xl max-w-lg w-full p-6 space-y-4 shadow-2xl">
            <h3 className="text-sm font-bold text-white">Ingest Raw Event (JSON)</h3>
            <p className="text-xs text-slate-400">
              Paste a heterogeneous payload. The normalization layer will automatically map principal, IP, and severity.
            </p>
            <textarea
              value={ingestPayload}
              onChange={(e) => setIngestPayload(e.target.value)}
              rows={9}
              className="w-full bg-sentinel-950 border border-sentinel-700 rounded p-3 text-xs font-mono text-slate-200 focus:outline-none focus:border-cyan-500"
            />
            {ingestStatus && (
              <div className="text-xs font-mono text-cyan-400">{ingestStatus}</div>
            )}
            <div className="flex justify-end space-x-2 pt-2">
              <button
                onClick={() => setShowModal(false)}
                className="px-3 py-1.5 bg-sentinel-800 rounded text-xs text-slate-300"
              >
                Cancel
              </button>
              <button
                onClick={handleIngestSubmit}
                className="px-4 py-1.5 bg-cyan-600 hover:bg-cyan-500 text-white rounded text-xs font-medium"
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
