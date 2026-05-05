// ═════════════════════════════════════════════
// PIXELMIND API CLIENT
// Connects frontend to backend API
// ═════════════════════════════════════════════

// Detect environment and set API URL
const getAPIUrl = () => {
  // Production
  if (window.location.hostname === 'pixelmind.app' || window.location.hostname.includes('vercel.app')) {
    return 'https://your-backend.onrender.com/api'; // Update this
  }
  
  // Localhost development
  if (window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1') {
    return 'http://localhost:8000/api';
  }
  
  // Default fallback
  return 'http://localhost:8000/api';
};

const API_URL = getAPIUrl();
const TIMEOUT = 30000; // 30 seconds

// ─────────────────────────────────────────────
// API REQUEST HELPER
// ─────────────────────────────────────────────
async function apiCall(endpoint, options = {}) {
  const {
    method = 'GET',
    body = null,
    headers = {},
    withAuth = true,
  } = options;

  // Get token from localStorage
  const token = localStorage.getItem('access_token');
  
  const defaultHeaders = {
    'Content-Type': 'application/json',
    ...headers,
  };

  if (withAuth && token) {
    defaultHeaders['Authorization'] = `Bearer ${token}`;
  }

  const config = {
    method,
    headers: defaultHeaders,
    timeout: TIMEOUT,
  };

  if (body) {
    config.body = JSON.stringify(body);
  }

  try {
    const response = await fetch(`${API_URL}${endpoint}`, config);
    
    // Handle 401 - Token expired
    if (response.status === 401) {
      localStorage.removeItem('access_token');
      localStorage.removeItem('refresh_token');
      window.location.href = '/login';
      throw new Error('Session expired. Please login again.');
    }

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || `API Error: ${response.status}`);
    }

    return await response.json();
  } catch (error) {
    console.error(`API Call Error [${method} ${endpoint}]:`, error);
    throw error;
  }
}

// ─────────────────────────────────────────────
// FILE UPLOAD HELPER
// ─────────────────────────────────────────────
async function uploadFile(endpoint, file, additionalFields = {}) {
  const formData = new FormData();
  formData.append('file', file);
  
  Object.keys(additionalFields).forEach(key => {
    formData.append(key, additionalFields[key]);
  });

  const token = localStorage.getItem('access_token');
  const headers = {};
  if (token) {
    headers['Authorization'] = `Bearer ${token}`;
  }

  try {
    const response = await fetch(`${API_URL}${endpoint}`, {
      method: 'POST',
      body: formData,
      headers,
      timeout: 120000, // 2 minutes for uploads
    });

    if (response.status === 401) {
      localStorage.removeItem('access_token');
      window.location.href = '/login';
      throw new Error('Session expired.');
    }

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || `Upload Error: ${response.status}`);
    }

    return await response.json();
  } catch (error) {
    console.error(`File Upload Error [${endpoint}]:`, error);
    throw error;
  }
}

// ─────────────────────────────────────────────
// AUTH ENDPOINTS
// ─────────────────────────────────────────────
const auth = {
  login: (email, password) =>
    apiCall('/auth/login', {
      method: 'POST',
      body: { email, password },
      withAuth: false,
    }),
  
  register: (email, password, name) =>
    apiCall('/auth/register', {
      method: 'POST',
      body: { email, password, name },
      withAuth: false,
    }),
  
  logout: () => {
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
    return Promise.resolve();
  },
  
  getCurrentUser: () =>
    apiCall('/auth/me', { method: 'GET' }),
};

// ─────────────────────────────────────────────
// PROJECT ENDPOINTS
// ─────────────────────────────────────────────
const projects = {
  list: () =>
    apiCall('/projects', { method: 'GET' }),
  
  create: (name, description) =>
    apiCall('/projects', {
      method: 'POST',
      body: { name, description },
    }),
  
  get: (projectId) =>
    apiCall(`/projects/${projectId}`, { method: 'GET' }),
  
  update: (projectId, data) =>
    apiCall(`/projects/${projectId}`, {
      method: 'PUT',
      body: data,
    }),
  
  delete: (projectId) =>
    apiCall(`/projects/${projectId}`, { method: 'DELETE' }),
};

// ─────────────────────────────────────────────
// EDITOR ENDPOINTS
// ─────────────────────────────────────────────
const editor = {
  uploadFile: (file, projectId) =>
    uploadFile('/editor/upload', file, { project_id: projectId }),
  
  processImage: (fileId, effects) =>
    apiCall('/editor/process/image', {
      method: 'POST',
      body: { file_id: fileId, effects },
    }),
  
  processVideo: (fileId, effects) =>
    apiCall('/editor/process/video', {
      method: 'POST',
      body: { file_id: fileId, effects },
    }),
  
  processAudio: (fileId, effects) =>
    apiCall('/editor/process/audio', {
      method: 'POST',
      body: { file_id: fileId, effects },
    }),
  
  export: (fileId, format) =>
    apiCall('/editor/export', {
      method: 'POST',
      body: { file_id: fileId, format },
    }),
};

// ─────────────────────────────────────────────
// EXPORT API
// ─────────────────────────────────────────────
const API = {
  URL: API_URL,
  call: apiCall,
  uploadFile,
  auth,
  projects,
  editor,
};

// Export for use in scripts
window.API = API;
