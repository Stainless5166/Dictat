<script lang="ts">
  import { onMount } from 'svelte';
  import { goto } from '$app/navigation';
  import { authStore } from '$stores/auth';

  onMount(() => {
    // Redirect based on auth status
    if ($authStore.isAuthenticated) {
      goto('/dashboard');
    } else {
      goto('/auth/login');
    }
  });
</script>

<div class="flex items-center justify-center">
  <div class="text-center">
    <h1 class="text-2xl font-bold">Loading...</h1>
  </div>
</div>
