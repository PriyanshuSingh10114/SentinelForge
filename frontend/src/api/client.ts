const API_BASE = '/api/v1';

let authToken: string | null = sessionStorage.getItem('sentinel_token');

export const setAuthToken = (token: string | null) => {
  authToken = token;
  if (token) {
    sessionStorage.setItem('sentinel_token', token);
  } else {
    sessionStorage.removeItem('sentinel_token');
  }
};

export const getAuthToken = () => authToken;

async function request<T>(endpoint: string, options: RequestInit = {}): Promise<T> {
  const headers: Record<string, string> = {
    'Content-Type': 'application/json',
    ...(options.headers as Record<string, string> || {}),
  };

  if (authToken) {
    headers['Authorization'] = `Bearer ${authToken}`;
  }

  const response = await fetch(`${API_BASE}${endpoint}`, {
    ...options,
    headers,
  });

  if (!response.ok) {
    let errorDetail = 'An error occurred';
    try {
      const errJson = await response.json();
      errorDetail = errJson.error?.message || errJson.detail || JSON.stringify(errJson);
    } catch {
      errorDetail = `${response.status} ${response.statusText}`;
    }
    throw new Error(errorDetail);
  }

  return response.json();
}

export const api = {
  auth: {
    login: (email: string, password: string) =>
      request<{ access_token: string; refresh_token: string; token_type: string }>('/auth/login', {
        method: 'POST',
        body: JSON.stringify({ email, password }),
      }),
    me: () => request<any>('/auth/me'),
    logout: () =>
      request<{ message: string }>('/auth/logout', {
        method: 'POST',
      }),
  },
  incidents: {
    list: (params: { status?: string; severity?: string } = {}) => {
      const q = new URLSearchParams();
      if (params.status) q.append('status', params.status);
      if (params.severity) q.append('severity', params.severity);
      return request<any[]>(`/incidents?${q.toString()}`);
    },
    get: (id: string) => request<any>(`/incidents/${id}`),
    attackGraph: (id: string) => request<any>(`/incidents/${id}/attack-graph`),
    updateStatus: (id: string, status: string) =>
      request<any>(`/incidents/${id}/status`, {
        method: 'PATCH',
        body: JSON.stringify({ status }),
      }),
  },
  events: {
    list: (params: Record<string, any> = {}) => {
      const q = new URLSearchParams();
      for (const [k, v] of Object.entries(params)) {
        if (v !== undefined && v !== null && v !== '') q.append(k, String(v));
      }
      return request<{ total: number; items: any[] }>(`/events?${q.toString()}`);
    },
    ingest: (eventData: Record<string, any>) =>
      request<any>('/events', {
        method: 'POST',
        body: JSON.stringify(eventData),
      }),
  },
  dlp: {
    scan: (content: string, sourceType: string = 'PAYLOAD', sourceId?: string) =>
      request<{ classification: string; action: string; findings_count: number; findings: any[] }>(
        '/dlp/scan',
        {
          method: 'POST',
          body: JSON.stringify({ content, source_type: sourceType, source_id: sourceId }),
        }
      ),
    findings: (params: { data_type?: string; classification?: string } = {}) => {
      const q = new URLSearchParams();
      if (params.data_type) q.append('data_type', params.data_type);
      if (params.classification) q.append('classification', params.classification);
      return request<any[]>(`/dlp/findings?${q.toString()}`);
    },
  },
  threats: {
    list: () => request<any[]>('/threat-models'),
    get: (id: string) => request<any>(`/threat-models/${id}`),
    create: (name: string, architecture_summary: string) =>
      request<any>('/threat-models', {
        method: 'POST',
        body: JSON.stringify({ name, architecture_summary }),
      }),
    updateStatus: (itemId: string, status: string) =>
      request<any>(`/threat-models/items/${itemId}/status`, {
        method: 'PATCH',
        body: JSON.stringify({ status }),
      }),
  },
  investigations: {
    run: (incidentId: string) =>
      request<any>(`/investigations/${incidentId}`, {
        method: 'POST',
      }),
    getByIncident: (incidentId: string) => request<any[]>(`/investigations/incident/${incidentId}`),
  },
  remediations: {
    list: (statusFilter?: string) => {
      const q = statusFilter ? `?status=${statusFilter}` : '';
      return request<any[]>(`/remediations${q}`);
    },
    approve: (id: string, notes?: string) =>
      request<any>(`/remediations/${id}/approve`, {
        method: 'POST',
        body: JSON.stringify({ notes }),
      }),
    reject: (id: string, reason: string) =>
      request<any>(`/remediations/${id}/reject`, {
        method: 'POST',
        body: JSON.stringify({ reason }),
      }),
  },
  admin: {
    users: () => request<any[]>('/admin/users'),
    createUser: (data: { email: string; name: string; password: string; role_name: string }) =>
      request<any>('/admin/users', {
        method: 'POST',
        body: JSON.stringify(data),
      }),
    policies: (type?: string) => request<any[]>(`/admin/policies${type ? `?policy_type=${type}` : ''}`),
    createPolicy: (policy: { name: string; description: string; policy_type: string; configuration: any; enabled?: boolean }) =>
      request<any>('/admin/policies', {
        method: 'POST',
        body: JSON.stringify(policy),
      }),
    updatePolicy: (id: string, data: any) =>
      request<any>(`/admin/policies/${id}`, {
        method: 'PUT',
        body: JSON.stringify(data),
      }),
    auditLogs: (limit: number = 50) => request<any[]>(`/admin/audit-logs?limit=${limit}`),
  },
  // Shortcuts
  getUsers: () => request<any[]>('/admin/users'),
  createUser: (data: any) => request<any>('/admin/users', { method: 'POST', body: JSON.stringify(data) }),
  getPolicies: (type?: string) => request<any[]>(`/admin/policies${type ? `?policy_type=${type}` : ''}`),
  createPolicy: (policy: any) => request<any>('/admin/policies', { method: 'POST', body: JSON.stringify(policy) }),
  updatePolicy: (id: string, data: any) => request<any>(`/admin/policies/${id}`, { method: 'PUT', body: JSON.stringify(data) }),
  getAuditLogs: (params: { limit?: number } = {}) => request<any[]>(`/admin/audit-logs?limit=${params.limit || 50}`),
};
