<script lang="ts">
  import '../app.css';
  import { onMount } from 'svelte';
  import { authStore } from '$stores/auth';
  import { page } from '$app/stores';
  import Navigation from '$components/shared/Navigation.svelte';
  import Toast from '$components/shared/Toast.svelte';

  onMount(async () => {
    // Load user on app start
    await authStore.loadUser();
  });

  $: isAuthPage = $page.url.pathname.startsWith('/auth');
</script>

{#if !isAuthPage && $authStore.user}
  <Navigation />
{/if}

<main class="min-h-screen {isAuthPage ? 'flex items-center justify-center' : 'pt-16'}">
  <slot />
</main>

<Toast />
