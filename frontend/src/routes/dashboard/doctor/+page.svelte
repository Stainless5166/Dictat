<script lang="ts">
  import { onMount } from 'svelte';
  import { dictationsStore } from '$stores/dictations';
  import { DictationStatus } from '$lib/api';
  import DictationsList from '$components/dictation/DictationsList.svelte';
  import LoadingSpinner from '$components/shared/LoadingSpinner.svelte';

  let selectedStatus: DictationStatus | 'all' = 'all';

  onMount(async () => {
    await dictationsStore.loadList();
  });

  const handleFilterChange = async () => {
    await dictationsStore.loadList({
      status: selectedStatus === 'all' ? undefined : selectedStatus
    });
  };
</script>

<svelte:head>
  <title>Doctor Dashboard - Dictat</title>
</svelte:head>

<div class="mx-auto max-w-7xl px-4 py-8 sm:px-6 lg:px-8">
  <div class="mb-8">
    <h1 class="text-3xl font-bold text-gray-900">Doctor Dashboard</h1>
    <p class="mt-2 text-gray-600">Manage your dictations and review transcriptions</p>
  </div>

  <div class="mb-6 flex items-center justify-between">
    <div class="flex items-center gap-4">
      <label for="status" class="text-sm font-medium text-gray-700">Filter by status:</label>
      <select
        id="status"
        bind:value={selectedStatus}
        on:change={handleFilterChange}
        class="rounded-md border-gray-300 px-3 py-2 focus:border-primary-500 focus:ring-primary-500"
      >
        <option value="all">All</option>
        <option value={DictationStatus.PENDING}>Pending</option>
        <option value={DictationStatus.IN_PROGRESS}>In Progress</option>
        <option value={DictationStatus.COMPLETED}>Completed</option>
        <option value={DictationStatus.REVIEWED}>Reviewed</option>
        <option value={DictationStatus.REJECTED}>Rejected</option>
      </select>
    </div>

    <a href="/dictations/upload" class="btn-primary">
      + Upload New Dictation
    </a>
  </div>

  {#if $dictationsStore.loading}
    <div class="flex justify-center py-12">
      <LoadingSpinner size="lg" />
    </div>
  {:else if $dictationsStore.items.length === 0}
    <div class="card text-center">
      <p class="text-gray-600">No dictations found. Upload your first dictation to get started.</p>
      <a href="/dictations/upload" class="btn-primary mt-4 inline-block">
        Upload Dictation
      </a>
    </div>
  {:else}
    <DictationsList dictations={$dictationsStore.items} role="doctor" />
  {/if}
</div>
