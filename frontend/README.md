# Dictat Frontend

Web application for medical dictation transcription service.

## TODO Phase 3: Frontend Implementation

### Setup
- Initialize Svelte/React project with Vite
- Configure TypeScript
- Set up Tailwind CSS or UI component library
- Configure ESLint and Prettier

### Features to Implement

#### Authentication
- Login page
- Registration page
- Password reset flow
- Protected route guards

#### Doctor Interface
- Dashboard with dictation list
- Audio recording component (MediaRecorder API)
- Upload dictation with metadata
- View transcription status
- Review and approve transcriptions

#### Secretary Interface
- Dashboard with work queue
- Claim dictation functionality
- Audio playback with controls (play, pause, seek, speed)
- Markdown editor with preview
- Autosave functionality
- Submit transcription for review

#### Shared Components
- Navigation bar
- User profile menu
- Notification system (toasts)
- Search and filter components
- Real-time updates (WebSocket)

### Project Structure

```
frontend/
├── src/
│   ├── components/         # Reusable components
│   │   ├── auth/
│   │   ├── dictation/
│   │   ├── transcription/
│   │   └── shared/
│   ├── pages/             # Page components
│   │   ├── Login.tsx
│   │   ├── Dashboard.tsx
│   │   ├── DoctorDashboard.tsx
│   │   └── SecretaryDashboard.tsx
│   ├── services/          # API client
│   │   └── api.ts
│   ├── stores/            # State management
│   │   ├── auth.ts
│   │   ├── dictations.ts
│   │   └── transcriptions.ts
│   ├── utils/             # Utilities
│   ├── types/             # TypeScript types
│   ├── App.tsx
│   └── main.tsx
├── public/
├── package.json
├── tsconfig.json
├── vite.config.ts
└── tailwind.config.js
```

### Dependencies

```bash
# Core
npm install react react-dom react-router-dom
npm install -D @types/react @types/react-dom

# State Management
npm install zustand  # or redux-toolkit

# HTTP Client
npm install axios

# UI Components
npm install @headlessui/react @heroicons/react

# Forms
npm install react-hook-form zod @hookform/resolvers

# Markdown
npm install react-markdown

# Audio
# Use native MediaRecorder API

# Styling
npm install tailwindcss postcss autoprefixer
npm install -D prettier prettier-plugin-tailwindcss

# Dev Tools
npm install -D vite @vitejs/plugin-react
npm install -D typescript
npm install -D eslint @typescript-eslint/parser @typescript-eslint/eslint-plugin
```

### Development

```bash
# Install dependencies
npm install

# Run development server
npm run dev

# Build for production
npm run build

# Preview production build
npm run preview
```

### Testing

```bash
# Unit tests
npm run test

# E2E tests with Playwright
npm run test:e2e
```

## Environment Variables

Create `.env` file:

```
VITE_API_URL=http://localhost:8000/api/v1
VITE_WS_URL=ws://localhost:8000/ws
```
