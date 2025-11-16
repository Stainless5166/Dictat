<script lang="ts">
  import { onMount } from 'svelte';
  import { dictationsStore } from '$stores/dictations';
  import DictationsList from '$components/dictation/DictationsList.svelte';
  import LoadingSpinner from '$components/shared/LoadingSpinner.svelte';

  onMount(async () => {
    // Load both my dictations and the queue
    await dictationsStore.loadList();
  });

  let activeTab: 'my-work' | 'queue' = 'my-work';

  const switchTab = async (tab: 'my-work' | 'queue') => {
    activeTab = tab;
    if (tab === 'queue') {
      await dictationsStore.loadQueue();
    } else {
      await dictationsStore.loadList();
    }
  };
</script>

<svelte:head>
  <title>Secretary Dashboard - Dictat</title>
</svelte:head>

<div class="mx-auto max-w-7xl px-4 py-8 sm:px-6 lg:px-8">
  <div class="mb-8">
    <h1 class="text-3xl font-bold text-gray-900">Secretary Dashboard</h1>
    <p class="mt-2 text-gray-600">Transcribe dictations and manage your work queue</p>
  </div>

  <!-- Tabs -->
  <div class="mb-6 border-b border-gray-200">
    <nav class="-mb-px flex space-x-8">
      <button
        on:click={() => switchTab('my-work')}
        class="border-b-2 px-1 py-4 text-sm font-medium {activeTab === 'my-work'
          ? 'border-primary-500 text-primary-600'
          : 'border-transparent text-gray-500 hover:border-gray-300 hover:text-gray-700'}"
      >
        My Work
      </button>
      <button
        on:click={() => switchTab('queue')}
        class="border-b-2 px-1 py-4 text-sm font-medium {activeTab === 'queue'
          ? 'border-primary-500 text-primary-600'
          : 'border-transparent text-gray-500 hover:border-gray-300 hover:text-gray-700'}"
      >
        Work Queue
      </button>
    </nav>
  </div>

  {#if $dictationsStore.loading}
    <div class="flex justify-center py-12">
      <LoadingSpinner size="lg" />
    </div>
  {:else if $dictationsStore.items.length === 0}
    <div class="card text-center">
      <p class="text-gray-600">
        {activeTab === 'queue'
          ? 'No dictations available in the queue.'
          : 'You have no active dictations.'}
      </p>
      {#if activeTab === 'my-work'}
        <button on:click={() => switchTab('queue')} class="btn-primary mt-4">
          Browse Work Queue
        </button>
      {/if}
    </div>
  {:else}
    <DictationsList dictations={$dictationsStore.items} role="secretary" showQueue={activeTab === 'queue'} />
  {/if}
</div>
