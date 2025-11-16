<script lang="ts">
  import { authStore } from '$stores/auth';
  import LoadingSpinner from '$components/shared/LoadingSpinner.svelte';

  let email = '';
  let password = '';
  let loading = false;

  const handleSubmit = async (e: Event) => {
    e.preventDefault();
    loading = true;

    try {
      await authStore.login({ username: email, password });
    } catch (error) {
      // Error is handled in the store and displayed via error message
    } finally {
      loading = false;
    }
  };
</script>

<svelte:head>
  <title>Login - Dictat</title>
</svelte:head>

<div class="flex min-h-screen items-center justify-center bg-gray-50 px-4 py-12 sm:px-6 lg:px-8">
  <div class="w-full max-w-md space-y-8">
    <div>
      <h2 class="mt-6 text-center text-3xl font-bold tracking-tight text-gray-900">
        Sign in to Dictat
      </h2>
      <p class="mt-2 text-center text-sm text-gray-600">
        Medical dictation transcription service
      </p>
    </div>

    <form class="mt-8 space-y-6" on:submit={handleSubmit}>
      {#if $authStore.error}
        <div class="rounded-md bg-red-50 p-4">
          <p class="text-sm text-red-800">{$authStore.error}</p>
        </div>
      {/if}

      <div class="space-y-4 rounded-md shadow-sm">
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
          <label for="password" class="label">Password</label>
          <input
            id="password"
            name="password"
            type="password"
            autocomplete="current-password"
            required
            bind:value={password}
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
              <span>Signing in...</span>
            </div>
          {:else}
            Sign in
          {/if}
        </button>
      </div>

      <div class="text-center text-sm">
        <span class="text-gray-600">Don't have an account?</span>
        <a href="/auth/register" class="font-medium text-primary-600 hover:text-primary-500">
          Register here
        </a>
      </div>
    </form>
  </div>
</div>
