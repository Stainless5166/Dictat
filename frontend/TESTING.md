# Testing Guide

Comprehensive testing guide for the Dictat frontend application.

## Testing Stack

- **Unit/Component Tests**: Vitest + Testing Library
- **E2E Tests**: Playwright
- **Coverage**: Vitest Coverage (v8)
- **CI/CD**: GitHub Actions

## Running Tests

### Unit Tests

```bash
# Run tests in watch mode
npm run test

# Run tests once
npm run test:run

# Run tests with UI
npm run test:ui

# Run tests with coverage
npm run test:coverage
```

### E2E Tests

```bash
# Run E2E tests
npm run test:e2e

# Run E2E tests in UI mode
npm run test:e2e:ui

# Debug E2E tests
npm run test:e2e:debug

# Show last test report
npm run test:e2e:report
```

### All Tests

```bash
# Run all tests (unit + e2e)
npm run test:run && npm run test:e2e
```

## Test Structure

```
frontend/
├── src/
│   └── tests/
│       ├── setup.ts              # Test setup and global mocks
│       ├── helpers/              # Test utilities
│       │   ├── mockApi.ts        # Mock API responses
│       │   └── testUtils.ts      # Helper functions
│       └── unit/                 # Unit tests
│           ├── components/       # Component tests
│           └── stores/           # Store tests
├── e2e/                          # E2E tests
│   ├── auth.spec.ts
│   ├── navigation.spec.ts
│   └── dictations.spec.ts
└── playwright-report/            # E2E test reports (gitignored)
```

## Writing Tests

### Unit Tests (Vitest)

Test files use `.test.ts` or `.spec.ts` extension.

#### Store Tests

```typescript
import { describe, it, expect, beforeEach, vi } from 'vitest';
import { get } from 'svelte/store';
import { authStore } from '$stores/auth';

describe('Auth Store', () => {
  beforeEach(() => {
    authStore.logout();
    vi.clearAllMocks();
  });

  it('should login successfully', async () => {
    await authStore.login({
      username: 'user@example.com',
      password: 'password'
    });

    const state = get(authStore);
    expect(state.user).toBeTruthy();
    expect(state.error).toBeNull();
  });
});
```

#### Component Tests

```typescript
import { describe, it, expect } from 'vitest';
import { render, screen } from '@testing-library/svelte';
import Toast from '$components/shared/Toast.svelte';

describe('Toast Component', () => {
  it('should render toast message', () => {
    render(Toast, {
      props: {
        message: 'Test message',
        type: 'success'
      }
    });

    expect(screen.getByText('Test message')).toBeInTheDocument();
  });
});
```

### E2E Tests (Playwright)

Test files use `.spec.ts` extension in `e2e/` directory.

```typescript
import { test, expect } from '@playwright/test';

test.describe('Authentication', () => {
  test('should login successfully', async ({ page }) => {
    await page.goto('/auth/login');

    await page.getByLabel('Email address').fill('doctor@example.com');
    await page.getByLabel('Password').fill('password123');
    await page.getByRole('button', { name: 'Sign in' }).click();

    await expect(page).toHaveURL(/.*dashboard/);
  });
});
```

## Test Helpers

### Mock API

Use `createMockApi()` to mock API calls:

```typescript
import { createMockApi } from '../helpers/mockApi';

vi.mock('$lib/api', () => ({
  api: createMockApi()
}));
```

### Test Utilities

```typescript
import { createMockFile, waitFor } from '../helpers/testUtils';

// Create a mock audio file
const file = createMockFile('recording.mp3', 1024000, 'audio/mpeg');

// Wait for condition
await waitFor(() => get(store).loading === false);
```

## Coverage Requirements

### Current Targets

- **Overall**: 70% minimum
- **Stores**: 80% minimum (critical business logic)
- **Components**: 70% minimum
- **Utils**: 80% minimum

### Checking Coverage

```bash
npm run test:coverage
```

Coverage reports are generated in:
- `coverage/index.html` - HTML report
- `coverage/lcov.info` - LCOV format (for CI)

### Coverage Thresholds

Configured in `vitest.config.ts`:

```typescript
coverage: {
  lines: 70,
  functions: 70,
  branches: 70,
  statements: 70
}
```

## Mocking Patterns

### Mock Browser APIs

#### LocalStorage

```typescript
beforeEach(() => {
  const mockStorage = {
    getItem: vi.fn(),
    setItem: vi.fn(),
    removeItem: vi.fn()
  };
  global.localStorage = mockStorage as any;
});
```

#### Fetch

```typescript
global.fetch = vi.fn().mockResolvedValue({
  ok: true,
  status: 200,
  json: async () => ({ data: 'test' })
});
```

#### MediaRecorder

```typescript
global.MediaRecorder = vi.fn().mockImplementation(() => ({
  start: vi.fn(),
  stop: vi.fn(),
  ondataavailable: null,
  onstop: null
}));
```

### Mock SvelteKit

#### Navigation

```typescript
vi.mock('$app/navigation', () => ({
  goto: vi.fn(),
  invalidate: vi.fn()
}));
```

#### Stores

```typescript
vi.mock('$app/stores', () => ({
  page: {
    subscribe: vi.fn()
  }
}));
```

## CI/CD Integration

Tests run automatically on:
- Push to `main`, `develop`, or `claude/**` branches
- Pull requests to `main` or `develop`

### GitHub Actions Workflow

`.github/workflows/test.yml` runs:

1. **Type Checking**: `npm run check`
2. **Linting**: `npm run lint`
3. **Unit Tests**: `npm run test:run`
4. **Coverage**: `npm run test:coverage`
5. **E2E Tests**: `npm run test:e2e`
6. **Build**: `npm run build`

### Artifacts

- Coverage reports uploaded to Codecov
- Playwright reports saved for 30 days
- Build artifacts saved for 7 days

## Best Practices

### 1. Test Isolation

Each test should be independent:

```typescript
beforeEach(() => {
  // Reset state
  authStore.logout();
  vi.clearAllMocks();
});
```

### 2. Descriptive Test Names

```typescript
// Good
it('should show error when password is too short', ...)

// Bad
it('validates password', ...)
```

### 3. Test User Behavior

Focus on what users see and do:

```typescript
// Good - testing user interaction
await page.getByRole('button', { name: 'Submit' }).click();

// Bad - testing implementation details
await page.click('.submit-btn-class');
```

### 4. Avoid Testing Implementation Details

```typescript
// Good - testing outcome
expect(get(authStore).user).toBeTruthy();

// Bad - testing internal state
expect(authStore._internalState).toBe('logged-in');
```

### 5. Use Test Data Builders

```typescript
// Create reusable test data
export const createMockUser = (overrides = {}) => ({
  id: 1,
  email: 'test@example.com',
  role: 'doctor',
  ...overrides
});
```

## Debugging Tests

### Vitest

```bash
# Run specific test file
npm run test src/tests/unit/stores/auth.test.ts

# Run tests matching pattern
npm run test -- --grep "login"

# Run with UI for debugging
npm run test:ui
```

### Playwright

```bash
# Run in debug mode
npm run test:e2e:debug

# Run specific test
npx playwright test e2e/auth.spec.ts

# Show trace viewer
npx playwright show-trace trace.zip
```

### VS Code Integration

Recommended extensions:
- **Vitest**: Run tests from sidebar
- **Playwright Test for VSCode**: Run E2E tests in VS Code

## Common Issues

### Test Timeout

Increase timeout for slow tests:

```typescript
it('slow test', async () => {
  // ...
}, 10000); // 10 second timeout
```

### Flaky E2E Tests

Use `waitFor` for async conditions:

```typescript
await expect(page.locator('.loading')).toHaveCount(0);
await page.waitForLoadState('networkidle');
```

### Mock Not Working

Ensure mocks are set up before imports:

```typescript
// Mock BEFORE importing component
vi.mock('$lib/api', () => ({ ... }));

// THEN import
import { authStore } from '$stores/auth';
```

## Resources

- [Vitest Documentation](https://vitest.dev/)
- [Testing Library](https://testing-library.com/docs/svelte-testing-library/intro/)
- [Playwright Documentation](https://playwright.dev/)
- [Svelte Testing Handbook](https://timdeschryver.dev/blog/how-to-test-svelte-components)
