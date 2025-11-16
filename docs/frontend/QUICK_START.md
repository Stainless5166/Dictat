# Frontend Quick Start Guide

Get started with building the Dictat frontend in 10 minutes.

## Prerequisites

- Node.js 18+ and npm/yarn/pnpm
- TypeScript knowledge
- React, Vue, or Svelte experience

## Step 1: Choose Your Frontend Framework

Dictat API works with any frontend framework. We recommend:

- **React** with Vite (modern, popular)
- **Svelte** with SvelteKit (lightweight, fast)
- **Vue** with Nuxt (progressive, flexible)

### Create React App with Vite

```bash
npm create vite@latest dictat-frontend -- --template react-ts
cd dictat-frontend
npm install
```

### Create Svelte App

```bash
npm create svelte@latest dictat-frontend
cd dictat-frontend
npm install
```

## Step 2: Copy API Client Files

Copy the TypeScript API client and types to your project:

```bash
# From the Dictat backend repo
mkdir -p src/lib src/types

cp docs/frontend/api-types.ts src/types/
cp docs/frontend/api-client.ts src/lib/
```

## Step 3: Configure API Client

Create `src/lib/api.ts`:

```typescript
import { createAPIClient } from './api-client';

export const api = createAPIClient({
  baseURL: import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1',
  onAuthError: () => {
    // Redirect to login page
    window.location.href = '/login';
  },
  onNetworkError: (error) => {
    console.error('Network error:', error);
    // Show toast notification
  },
});

export default api;
```

Create `.env`:

```bash
VITE_API_URL=http://localhost:8000/api/v1
```

## Step 4: Create Authentication Context (React)

Create `src/contexts/AuthContext.tsx`:

```tsx
import { createContext, useContext, useState, useEffect, ReactNode } from 'react';
import api from '../lib/api';
import type { CurrentUser } from '../types/api-types';

interface AuthContextType {
  user: CurrentUser | null;
  loading: boolean;
  login: (email: string, password: string) => Promise<void>;
  logout: () => Promise<void>;
  isAuthenticated: boolean;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<CurrentUser | null>(null);
  const [loading, setLoading] = useState(true);

  // Load user on mount
  useEffect(() => {
    loadUser();
  }, []);

  const loadUser = async () => {
    try {
      const token = api.getAccessToken();
      if (token) {
        const user = await api.auth.me();
        setUser(user);
      }
    } catch (error) {
      console.error('Failed to load user:', error);
      api.clearTokens();
    } finally {
      setLoading(false);
    }
  };

  const login = async (email: string, password: string) => {
    const response = await api.auth.login({
      username: email,
      password,
    });

    // Load user profile
    const user = await api.auth.me();
    setUser(user);
  };

  const logout = async () => {
    await api.auth.logout();
    setUser(null);
  };

  return (
    <AuthContext.Provider
      value={{
        user,
        loading,
        login,
        logout,
        isAuthenticated: !!user,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within AuthProvider');
  }
  return context;
}
```

## Step 5: Create Login Page

Create `src/pages/Login.tsx`:

```tsx
import { useState } from 'react';
import { useAuth } from '../contexts/AuthContext';
import { useNavigate } from 'react-router-dom';

export default function Login() {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const { login } = useAuth();
  const navigate = useNavigate();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    try {
      await login(email, password);
      navigate('/dashboard');
    } catch (err: any) {
      setError(err?.error?.detail || 'Login failed');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="login-page">
      <form onSubmit={handleSubmit}>
        <h1>Dictat Login</h1>

        {error && <div className="error">{error}</div>}

        <div>
          <label>Email</label>
          <input
            type="email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            required
          />
        </div>

        <div>
          <label>Password</label>
          <input
            type="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            required
          />
        </div>

        <button type="submit" disabled={loading}>
          {loading ? 'Logging in...' : 'Login'}
        </button>
      </form>
    </div>
  );
}
```

## Step 6: Create Protected Route Component

Create `src/components/ProtectedRoute.tsx`:

```tsx
import { Navigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import { UserRole } from '../types/api-types';

interface ProtectedRouteProps {
  children: React.ReactNode;
  allowedRoles?: UserRole[];
}

export default function ProtectedRoute({
  children,
  allowedRoles,
}: ProtectedRouteProps) {
  const { user, loading, isAuthenticated } = useAuth();

  if (loading) {
    return <div>Loading...</div>;
  }

  if (!isAuthenticated) {
    return <Navigate to="/login" replace />;
  }

  if (allowedRoles && user && !allowedRoles.includes(user.role)) {
    return <div>Access denied</div>;
  }

  return <>{children}</>;
}
```

## Step 7: Create Main App with Routing

Update `src/App.tsx`:

```tsx
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import { AuthProvider } from './contexts/AuthContext';
import ProtectedRoute from './components/ProtectedRoute';
import Login from './pages/Login';
import Dashboard from './pages/Dashboard';
import DictationList from './pages/DictationList';
import DictationUpload from './pages/DictationUpload';
import { UserRole } from './types/api-types';

function App() {
  return (
    <AuthProvider>
      <BrowserRouter>
        <Routes>
          <Route path="/login" element={<Login />} />

          <Route
            path="/dashboard"
            element={
              <ProtectedRoute>
                <Dashboard />
              </ProtectedRoute>
            }
          />

          <Route
            path="/dictations"
            element={
              <ProtectedRoute>
                <DictationList />
              </ProtectedRoute>
            }
          />

          <Route
            path="/upload"
            element={
              <ProtectedRoute allowedRoles={[UserRole.DOCTOR, UserRole.ADMIN]}>
                <DictationUpload />
              </ProtectedRoute>
            }
          />

          <Route path="/" element={<Navigate to="/dashboard" />} />
        </Routes>
      </BrowserRouter>
    </AuthProvider>
  );
}

export default App;
```

## Step 8: Create Dictation Upload Page (Doctors)

Create `src/pages/DictationUpload.tsx`:

```tsx
import { useState } from 'react';
import api from '../lib/api';
import { DictationPriority } from '../types/api-types';

export default function DictationUpload() {
  const [file, setFile] = useState<File | null>(null);
  const [title, setTitle] = useState('');
  const [priority, setPriority] = useState(DictationPriority.NORMAL);
  const [notes, setNotes] = useState('');
  const [uploading, setUploading] = useState(false);
  const [progress, setProgress] = useState(0);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!file) return;

    setUploading(true);
    try {
      const dictation = await api.dictations.create(
        {
          file,
          title,
          priority,
          notes,
        },
        (progress) => setProgress(progress)
      );

      alert('Dictation uploaded successfully!');
      // Reset form
      setFile(null);
      setTitle('');
      setNotes('');
    } catch (error) {
      alert('Upload failed');
      console.error(error);
    } finally {
      setUploading(false);
      setProgress(0);
    }
  };

  return (
    <div>
      <h1>Upload Dictation</h1>

      <form onSubmit={handleSubmit}>
        <div>
          <label>Audio File *</label>
          <input
            type="file"
            accept="audio/*"
            onChange={(e) => setFile(e.target.files?.[0] || null)}
            required
          />
        </div>

        <div>
          <label>Title</label>
          <input
            type="text"
            value={title}
            onChange={(e) => setTitle(e.target.value)}
            placeholder="Patient Visit Notes"
          />
        </div>

        <div>
          <label>Priority</label>
          <select
            value={priority}
            onChange={(e) => setPriority(e.target.value as DictationPriority)}
          >
            <option value={DictationPriority.LOW}>Low</option>
            <option value={DictationPriority.NORMAL}>Normal</option>
            <option value={DictationPriority.HIGH}>High</option>
            <option value={DictationPriority.URGENT}>Urgent</option>
          </select>
        </div>

        <div>
          <label>Notes</label>
          <textarea
            value={notes}
            onChange={(e) => setNotes(e.target.value)}
            placeholder="Additional notes..."
          />
        </div>

        {uploading && (
          <div className="progress">
            <div className="progress-bar" style={{ width: `${progress}%` }} />
            <span>{progress.toFixed(1)}%</span>
          </div>
        )}

        <button type="submit" disabled={uploading || !file}>
          {uploading ? 'Uploading...' : 'Upload Dictation'}
        </button>
      </form>
    </div>
  );
}
```

## Step 9: Create Work Queue Page (Secretaries)

Create `src/pages/WorkQueue.tsx`:

```tsx
import { useState, useEffect } from 'react';
import api from '../lib/api';
import type { DictationListItem } from '../types/api-types';

export default function WorkQueue() {
  const [queue, setQueue] = useState<DictationListItem[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadQueue();
  }, []);

  const loadQueue = async () => {
    try {
      const response = await api.dictations.queue({ limit: 50 });
      setQueue(response.items);
    } catch (error) {
      console.error('Failed to load queue:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleClaim = async (id: number) => {
    try {
      await api.dictations.claim(id);
      await loadQueue(); // Reload
      // Navigate to transcription page
    } catch (error) {
      alert('Failed to claim dictation');
    }
  };

  if (loading) return <div>Loading...</div>;

  return (
    <div>
      <h1>Work Queue</h1>

      {queue.length === 0 ? (
        <p>No dictations available</p>
      ) : (
        <table>
          <thead>
            <tr>
              <th>Priority</th>
              <th>Title</th>
              <th>Duration</th>
              <th>Created</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            {queue.map((item) => (
              <tr key={item.id}>
                <td>
                  <span className={`priority-${item.priority}`}>
                    {item.priority}
                  </span>
                </td>
                <td>{item.title || 'Untitled'}</td>
                <td>{item.duration}s</td>
                <td>{new Date(item.created_at).toLocaleString()}</td>
                <td>
                  <button onClick={() => handleClaim(item.id)}>
                    Claim & Transcribe
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </div>
  );
}
```

## Step 10: Install Dependencies

```bash
npm install react-router-dom
npm install -D @types/react-router-dom
```

## Run the App

```bash
# Start the backend (if not already running)
cd /path/to/Dictat
uv run uvicorn main:app --reload

# Start the frontend (in a new terminal)
cd dictat-frontend
npm run dev
```

Open http://localhost:5173 (or the port Vite assigns).

## Next Steps

1. **Implement Transcription Editor**
   - Use CodeMirror or Monaco for markdown editing
   - Add autosave every 2-3 seconds
   - Preview markdown in split view

2. **Add Real-Time Updates**
   - Poll every 30 seconds for updates
   - Or implement WebSocket connection (future)

3. **Improve UX**
   - Add toast notifications
   - Loading skeletons
   - Error boundaries
   - Responsive design

4. **Add More Features**
   - Audio waveform visualization
   - Keyboard shortcuts for transcription
   - Search and filtering
   - Export transcriptions as PDF

5. **Testing**
   - Unit tests with Vitest
   - Integration tests with Playwright
   - E2E tests

## Useful Resources

- **API Reference**: `docs/frontend/API_REFERENCE.md`
- **Type Definitions**: `docs/frontend/api-types.ts`
- **API Client**: `docs/frontend/api-client.ts`
- **OpenAPI Spec**: `http://localhost:8000/openapi.json`
- **Swagger UI**: `http://localhost:8000/docs`

## Common Issues

### CORS Errors

If you see CORS errors, make sure the backend `.env` includes your frontend URL:

```bash
CORS_ORIGINS=http://localhost:3000,http://localhost:5173
```

### 401 Unauthorized

Make sure you're logged in and the token is valid:

```typescript
const token = api.getAccessToken();
console.log('Token:', token);
```

### TypeScript Errors

Make sure TypeScript is configured correctly:

```json
// tsconfig.json
{
  "compilerOptions": {
    "target": "ES2020",
    "lib": ["ES2020", "DOM"],
    "module": "ESNext",
    "moduleResolution": "bundler",
    "strict": true,
    "jsx": "react-jsx"
  }
}
```

## Support

For questions, see the full API reference or open a GitHub issue.
