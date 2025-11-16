<script lang="ts">
  import { onMount } from 'svelte';
  import { goto } from '$app/navigation';
  import { authStore, userRole } from '$stores/auth';
  import { UserRole } from '$lib/api';
  import LoadingSpinner from '$components/shared/LoadingSpinner.svelte';

  onMount(async () => {
    // Redirect based on role
    if ($userRole === UserRole.DOCTOR) {
      goto('/dashboard/doctor');
    } else if ($userRole === UserRole.SECRETARY) {
      goto('/dashboard/secretary');
    } else if ($userRole === UserRole.ADMIN) {
      goto('/dashboard/admin');
    }
  });
</script>

<svelte:head>
  <title>Dashboard - Dictat</title>
</svelte:head>

<div class="flex min-h-screen items-center justify-center">
  <LoadingSpinner size="lg" />
</div>
