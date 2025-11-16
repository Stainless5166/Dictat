<script lang="ts">
  import { onMount } from 'svelte';
  import { page } from '$app/stores';
  import { goto } from '$app/navigation';
  import { dictationsStore } from '$stores/dictations';
  import { transcriptionsStore } from '$stores/transcriptions';
  import { userRole } from '$stores/auth';
  import { UserRole } from '$lib/api';
  import AudioPlayer from '$components/dictation/AudioPlayer.svelte';
  import TranscriptionReview from '$components/transcription/TranscriptionReview.svelte';
  import LoadingSpinner from '$components/shared/LoadingSpinner.svelte';

  let dictationId: number;
  let transcriptionId: number | null = null;

  onMount(async () => {
    dictationId = parseInt($page.params.id);
    await dictationsStore.loadDictation(dictationId);

    // For doctors: load the transcription if it exists
    // This would require an additional API endpoint to get transcription by dictation ID
    // For now, we'll show the dictation details
  });

  const formatDate = (dateString: string | null) => {
    if (!dateString) return 'N/A';
    return new Date(dateString).toLocaleString();
  };

  const handleDelete = async () => {
    if (confirm('Are you sure you want to delete this dictation?')) {
      try {
        await dictationsStore.delete(dictationId);
        goto('/dashboard');
      } catch (error) {
        // Error handled in store
      }
    }
  };
</script>

<svelte:head>
  <title>Dictation Details - Dictat</title>
</svelte:head>

<div class="mx-auto max-w-5xl px-4 py-8 sm:px-6 lg:px-8">
  {#if $dictationsStore.loading}
    <div class="flex justify-center py-12">
      <LoadingSpinner size="lg" />
    </div>
  {:else if $dictationsStore.current}
    <div class="mb-8 flex items-start justify-between">
      <div>
        <h1 class="text-3xl font-bold text-gray-900">
          {$dictationsStore.current.title || 'Untitled Dictation'}
        </h1>
        <p class="mt-2 text-gray-600">
          Created {formatDate($dictationsStore.current.created_at)}
        </p>
      </div>

      {#if $userRole === UserRole.DOCTOR}
        <button on:click={handleDelete} class="btn-danger btn-sm"> Delete </button>
      {/if}
    </div>

    <div class="grid gap-6 lg:grid-cols-3">
      <!-- Main Content -->
      <div class="space-y-6 lg:col-span-2">
        <!-- Audio Player -->
        <div>
          <h2 class="mb-4 text-lg font-semibold text-gray-900">Audio Recording</h2>
          <AudioPlayer dictationId={dictationId} />
        </div>

        <!-- Transcription (if exists) -->
        {#if $dictationsStore.current.status === 'completed' || $dictationsStore.current.status === 'reviewed'}
          <TranscriptionReview {dictationId} />
        {/if}
      </div>

      <!-- Sidebar - Details -->
      <div class="space-y-4 lg:col-span-1">
        <div class="card">
          <h3 class="mb-4 font-semibold text-gray-900">Details</h3>

          <dl class="space-y-3 text-sm">
            <div>
              <dt class="font-medium text-gray-500">Status</dt>
              <dd class="mt-1">
                <span class="badge status-{$dictationsStore.current.status}">
                  {$dictationsStore.current.status}
                </span>
              </dd>
            </div>

            <div>
              <dt class="font-medium text-gray-500">Priority</dt>
              <dd class="mt-1">
                <span class="badge priority-{$dictationsStore.current.priority}">
                  {$dictationsStore.current.priority}
                </span>
              </dd>
            </div>

            {#if $dictationsStore.current.patient_reference}
              <div>
                <dt class="font-medium text-gray-500">Patient Reference</dt>
                <dd class="mt-1 text-gray-900">{$dictationsStore.current.patient_reference}</dd>
              </div>
            {/if}

            <div>
              <dt class="font-medium text-gray-500">File Size</dt>
              <dd class="mt-1 text-gray-900">
                {($dictationsStore.current.file_size / 1024 / 1024).toFixed(2)} MB
              </dd>
            </div>

            {#if $dictationsStore.current.duration}
              <div>
                <dt class="font-medium text-gray-500">Duration</dt>
                <dd class="mt-1 text-gray-900">
                  {Math.floor($dictationsStore.current.duration / 60)}:{Math.floor($dictationsStore.current.duration % 60)
                    .toString()
                    .padStart(2, '0')}
                </dd>
              </div>
            {/if}

            {#if $dictationsStore.current.claimed_at}
              <div>
                <dt class="font-medium text-gray-500">Claimed At</dt>
                <dd class="mt-1 text-gray-900">{formatDate($dictationsStore.current.claimed_at)}</dd>
              </div>
            {/if}

            {#if $dictationsStore.current.completed_at}
              <div>
                <dt class="font-medium text-gray-500">Completed At</dt>
                <dd class="mt-1 text-gray-900">
                  {formatDate($dictationsStore.current.completed_at)}
                </dd>
              </div>
            {/if}
          </dl>
        </div>

        {#if $dictationsStore.current.notes}
          <div class="card">
            <h3 class="mb-2 font-semibold text-gray-900">Notes</h3>
            <p class="text-sm text-gray-600">{$dictationsStore.current.notes}</p>
          </div>
        {/if}
      </div>
    </div>
  {:else}
    <div class="card text-center">
      <p class="text-gray-600">Dictation not found.</p>
      <a href="/dashboard" class="btn-primary mt-4 inline-block"> Back to Dashboard </a>
    </div>
  {/if}
</div>
