<script lang="ts">
  import { authStore } from '$stores/auth';
  import { UserRole } from '$lib/api';
  import LoadingSpinner from '$components/shared/LoadingSpinner.svelte';

  let email = '';
  let password = '';
  let confirmPassword = '';
  let fullName = '';
  let role: UserRole = UserRole.DOCTOR;
  let loading = false;
  let validationError = '';

  const validateForm = (): boolean => {
    if (password.length < 8) {
      validationError = 'Password must be at least 8 characters';
      return false;
    }

    if (!/[A-Z]/.test(password)) {
      validationError = 'Password must contain at least one uppercase letter';
      return false;
    }

    if (!/[a-z]/.test(password)) {
      validationError = 'Password must contain at least one lowercase letter';
      return false;
    }

    if (!/[0-9]/.test(password)) {
      validationError = 'Password must contain at least one digit';
      return false;
    }

    if (password !== confirmPassword) {
      validationError = 'Passwords do not match';
      return false;
    }

    validationError = '';
    return true;
  };

  const handleSubmit = async (e: Event) => {
    e.preventDefault();

    if (!validateForm()) {
      return;
    }

    loading = true;

    try {
      await authStore.register({
        email,
        password,
        full_name: fullName,
        role
      });
    } catch (error) {
      // Error is handled in the store
    } finally {
      loading = false;
    }
  };
</script>

<svelte:head>
  <title>Register - Dictat</title>
</svelte:head>

<div class="flex min-h-screen items-center justify-center bg-gray-50 px-4 py-12 sm:px-6 lg:px-8">
  <div class="w-full max-w-md space-y-8">
    <div>
      <h2 class="mt-6 text-center text-3xl font-bold tracking-tight text-gray-900">
        Create your account
      </h2>
      <p class="mt-2 text-center text-sm text-gray-600">Join the Dictat platform</p>
    </div>

    <form class="mt-8 space-y-6" on:submit={handleSubmit}>
      {#if $authStore.error || validationError}
        <div class="rounded-md bg-red-50 p-4">
          <p class="text-sm text-red-800">{validationError || $authStore.error}</p>
        </div>
      {/if}

      <div class="space-y-4">
        <div>
          <label for="fullName" class="label">Full Name</label>
          <input
            id="fullName"
            name="fullName"
            type="text"
            required
            bind:value={fullName}
            class="input"
            placeholder="Dr. Jane Smith"
          />
        </div>

        <div>
          <label for="email" class="label">Email address</label>
          <input
            id="email"
            name="email"
            type="email"
            autocomplete="email"
            required
            bind:value={email}
            class="input"
            placeholder="doctor@example.com"
          />
        </div>

        <div>
          <label for="role" class="label">Role</label>
          <select id="role" name="role" bind:value={role} class="input">
            <option value={UserRole.DOCTOR}>Doctor</option>
            <option value={UserRole.SECRETARY}>Secretary</option>
            <option value={UserRole.ADMIN}>Admin</option>
          </select>
        </div>

        <div>
          <label for="password" class="label">Password</label>
          <input
            id="password"
            name="password"
            type="password"
            autocomplete="new-password"
            required
            bind:value={password}
            class="input"
            placeholder="••••••••"
          />
          <p class="mt-1 text-xs text-gray-500">
            Min 8 characters with uppercase, lowercase, and digit
          </p>
        </div>

        <div>
          <label for="confirmPassword" class="label">Confirm Password</label>
          <input
            id="confirmPassword"
            name="confirmPassword"
            type="password"
            autocomplete="new-password"
            required
            bind:value={confirmPassword}
            class="input"
            placeholder="••••••••"
          />
        </div>
      </div>

      <div>
        <button type="submit" disabled={loading} class="btn-primary w-full">
          {#if loading}
            <div class="flex items-center justify-center gap-2">
              <LoadingSpinner size="sm" />
              <span>Creating account...</span>
            </div>
          {:else}
            Register
          {/if}
        </button>
      </div>

      <div class="text-center text-sm">
        <span class="text-gray-600">Already have an account?</span>
        <a href="/auth/login" class="font-medium text-primary-600 hover:text-primary-500">
          Sign in here
        </a>
      </div>
    </form>
  </div>
</div>
