# Dictat Frontend Testing Guide

Comprehensive testing setup for the Dictat medical dictation frontend using Vitest and Playwright.

## Table of Contents

- [Overview](#overview)
- [Test Stack](#test-stack)
- [Running Tests](#running-tests)
- [Test Structure](#test-structure)
- [Writing Tests](#writing-tests)
- [Coverage Goals](#coverage-goals)
- [CI/CD Integration](#cicd-integration)

## Overview

The Dictat frontend uses a modern testing stack with:
- **Vitest** for unit and integration tests
- **React Testing Library** for component testing
- **Playwright** for E2E tests
- **MSW** (Mock Service Worker) for API mocking
- **Happy DOM** for fast DOM implementation

## Test Stack

### Unit & Integration Tests (Vitest)
- Framework: **Vitest 1.0+**
- Testing utilities: **@testing-library/react**
- DOM matchers: **@testing-library/jest-dom**
- User interactions: **@testing-library/user-event**
- DOM environment: **happy-dom**
- API mocking: **MSW (Mock Service Worker)**

### E2E Tests (Playwright)
- Framework: **Playwright 1.40+**
- Browsers: Chromium, Firefox, WebKit, Mobile Chrome
- Features: Screenshots, videos, traces, parallel execution

## Running Tests

### Unit & Integration Tests

```bash
# Run all tests once
npm test

# Watch mode (re-run on changes)
npm run test:watch

# With UI (interactive mode)
npm run test:ui

# Generate coverage report
npm run test:coverage
```

### E2E Tests

```bash
# Run all E2E tests (headless)
npm run test:e2e

# Run with UI (interactive mode)
npm run test:e2e:ui

# Run headed (see browser)
npm run test:e2e:headed

# Debug mode
npm run test:e2e:debug
```

### All Tests (CI mode)

```bash
# Run all tests for CI
npm run test:ci
```

## Test Structure

```
frontend/
├── src/
│   ├── components/
│   │   ├── __tests__/           # Component tests
│   │   │   ├── Toast.test.tsx
│   │   │   ├── AudioPlayer.test.tsx
│   │   │   └── ProtectedRoute.test.tsx
│   │   ├── Toast.tsx
│   │   └── ...
│   ├── hooks/
│   │   ├── __tests__/           # Hook tests
│   │   │   └── useToast.test.tsx
│   │   └── useToast.tsx
│   ├── pages/
│   │   ├── __tests__/           # Page integration tests
│   │   │   ├── Login.test.tsx
│   │   │   └── DoctorDashboard.test.tsx
│   │   └── ...
│   └── test/                    # Test utilities
│       ├── setup.ts             # Global test setup
│       ├── utils.tsx            # Render helpers
│       ├── mockData.ts          # Mock data
│       └── mocks/
│           ├── handlers.ts      # MSW handlers
│           └── server.ts        # MSW server
├── tests/
│   ├── e2e/                     # E2E tests
│   │   ├── authentication.spec.ts
│   │   ├── doctor-workflow.spec.ts
│   │   └── secretary-workflow.spec.ts
│   └── fixtures/                # Test fixtures
│       └── auth.ts
├── vitest.config.ts
└── playwright.config.ts
```

## Writing Tests

### Unit Test Example (Component)

```typescript
// src/components/__tests__/Toast.test.tsx
import { describe, it, expect, vi } from 'vitest';
import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import Toast from '../Toast';

describe('Toast', () => {
  it('should render success toast', () => {
    const mockOnClose = vi.fn();
    render(<Toast message="Success!" type="success" onClose={mockOnClose} />);

    expect(screen.getByText('Success!')).toBeInTheDocument();
  });

  it('should call onClose when clicked', async () => {
    const user = userEvent.setup();
    const mockOnClose = vi.fn();
    render(<Toast message="Test" type="info" onClose={mockOnClose} />);

    const closeButton = screen.getByRole('button', { hidden: true });
    await user.click(closeButton);

    expect(mockOnClose).toHaveBeenCalledTimes(1);
  });
});
```

### Integration Test Example (Page)

```typescript
// src/pages/__tests__/Login.test.tsx
import { describe, it, expect, vi } from 'vitest';
import { screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { renderWithProviders } from '@/test/utils';
import Login from '../Login';

vi.mock('@/lib/api', () => ({
  default: {
    auth: {
      login: vi.fn(),
      me: vi.fn(),
    },
  },
}));

describe('Login Page', () => {
  it('should handle successful login', async () => {
    const user = userEvent.setup();
    const api = await import('@/lib/api');

    vi.mocked(api.default.auth.login).mockResolvedValue({
      access_token: 'token',
      refresh_token: 'refresh',
      token_type: 'bearer',
      expires_in: 1800,
    });

    renderWithProviders(<Login />);

    await user.type(screen.getByPlaceholderText('Email address'), 'test@example.com');
    await user.type(screen.getByPlaceholderText('Password'), 'password123');
    await user.click(screen.getByRole('button', { name: /sign in/i }));

    await waitFor(() => {
      expect(api.default.auth.login).toHaveBeenCalled();
    });
  });
});
```

### E2E Test Example

```typescript
// tests/e2e/authentication.spec.ts
import { test, expect } from '@playwright/test';

test('should login successfully', async ({ page }) => {
  // Mock API
  await page.route('**/api/v1/auth/login', async (route) => {
    await route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify({
        access_token: 'mock-token',
        refresh_token: 'mock-refresh',
        token_type: 'bearer',
        expires_in: 1800,
      }),
    });
  });

  await page.goto('/login');

  await page.getByPlaceholder('Email address').fill('doctor@example.com');
  await page.getByPlaceholder('Password').fill('password123');
  await page.getByRole('button', { name: /sign in/i }).click();

  await expect(page).toHaveURL(/.*dashboard/);
});
```

## Coverage Goals

**Minimum Coverage Thresholds** (enforced in `vitest.config.ts`):
- **Lines**: 70%
- **Functions**: 70%
- **Branches**: 70%
- **Statements**: 70%

**Target Coverage by Module**:
- **Components**: 80%+ (higher for critical components)
- **Pages**: 75%+
- **Hooks**: 85%+
- **Utilities**: 90%+
- **API Client**: 80%+

### View Coverage Report

```bash
npm run test:coverage

# Open HTML report
open coverage/index.html
```

## Test Utilities

### Render Helpers

```typescript
// src/test/utils.tsx
import { renderWithProviders } from '@/test/utils';

// Renders with Router + Auth providers
renderWithProviders(<MyComponent />);

// Renders with Auth provider only
renderWithAuth(<MyComponent />);
```

### Mock Data

```typescript
// src/test/mockData.ts
import { mockDoctor, mockSecretary, mockDictation } from '@/test/mockData';

const user = mockDoctor;
const dictation = mockDictation;
```

### API Mocking (MSW)

```typescript
// src/test/mocks/handlers.ts
import { http, HttpResponse } from 'msw';

export const handlers = [
  http.get('/api/v1/dictations', () => {
    return HttpResponse.json({ items: [] });
  }),
];
```

## Best Practices

### 1. Test Behavior, Not Implementation
```typescript
// ❌ Bad - testing implementation
expect(wrapper.find('.toast-container').length).toBe(1);

// ✅ Good - testing behavior
expect(screen.getByText('Success!')).toBeInTheDocument();
```

### 2. Use User Events
```typescript
// ❌ Bad - fireEvent
fireEvent.click(button);

// ✅ Good - userEvent (more realistic)
const user = userEvent.setup();
await user.click(button);
```

### 3. Wait for Async Updates
```typescript
// ✅ Always use waitFor for async
await waitFor(() => {
  expect(screen.getByText('Loaded')).toBeInTheDocument();
});
```

### 4. Clean Tests
```typescript
// ✅ Clear mocks between tests
beforeEach(() => {
  vi.clearAllMocks();
});
```

### 5. Descriptive Test Names
```typescript
// ✅ Clear and descriptive
it('should show error message when login fails', () => {
  // ...
});
```

## Debugging Tests

### Vitest

```bash
# Run specific test file
npm test -- Toast.test.tsx

# Run specific test
npm test -- -t "should render success toast"

# Debug in VS Code
# Add breakpoint, press F5
```

### Playwright

```bash
# Debug mode (opens inspector)
npm run test:e2e:debug

# Headed mode (see browser)
npm run test:e2e:headed

# Generate test code
npx playwright codegen http://localhost:5173
```

### View Test Output

```bash
# Playwright HTML report
npx playwright show-report

# Vitest UI
npm run test:ui
```

## CI/CD Integration

### GitHub Actions Example

```yaml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest

    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-node@v3
        with:
          node-version: '18'

      - name: Install dependencies
        run: npm ci

      - name: Run unit tests
        run: npm run test:coverage

      - name: Install Playwright
        run: npx playwright install --with-deps

      - name: Run E2E tests
        run: npm run test:e2e

      - name: Upload coverage
        uses: codecov/codecov-action@v3
        with:
          files: ./coverage/lcov.info
```

## Troubleshooting

### Common Issues

**Issue**: Tests timeout
```bash
# Increase timeout in vitest.config.ts
test: {
  testTimeout: 10000,
}
```

**Issue**: Playwright browser not found
```bash
# Reinstall browsers
npx playwright install
```

**Issue**: Mock not working
```typescript
// Ensure mock is before import
vi.mock('@/lib/api', () => ({
  default: { /* ... */ }
}));
```

## Resources

- [Vitest Documentation](https://vitest.dev/)
- [React Testing Library](https://testing-library.com/react)
- [Playwright Documentation](https://playwright.dev/)
- [MSW Documentation](https://mswjs.io/)

## Support

For testing questions or issues, see:
- Project documentation in `/docs`
- CLAUDE.md for development guidelines
- Create an issue on GitHub
