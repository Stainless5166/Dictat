<script lang="ts">
  import { onMount } from 'svelte';
  import { page } from '$app/stores';
  import { goto } from '$app/navigation';
  import { dictationsStore } from '$stores/dictations';
  import { transcriptionsStore } from '$stores/transcriptions';
  import AudioPlayer from '$components/dictation/AudioPlayer.svelte';
  import MarkdownEditor from '$components/transcription/MarkdownEditor.svelte';
  import LoadingSpinner from '$components/shared/LoadingSpinner.svelte';

  let dictationId: number;
  let content = '';
  let submitting = false;

  onMount(async () => {
    dictationId = parseInt($page.params.id);

    // Load dictation details
    await dictationsStore.loadDictation(dictationId);

    // Check if transcription already exists
    // If so, load it. Otherwise, create a new one.
    // For simplicity, we'll just start with empty content
  });

  const handleAutosave = (e: CustomEvent) => {
    const newContent = e.detail;

    if ($transcriptionsStore.current) {
      transcriptionsStore.autosave($transcriptionsStore.current.id, newContent);
    }
  };

  const handleSave = async () => {
    try {
      if (!$transcriptionsStore.current) {
        // Create new transcription
        await transcriptionsStore.create({
          dictation_id: dictationId,
          content
        });
      } else {
        // Update existing transcription
        await transcriptionsStore.update($transcriptionsStore.current.id, { content });
      }
    } catch (error) {
      // Error handled in store
    }
  };

  const handleSubmit = async () => {
    submitting = true;

    try {
      // Save first if needed
      if (!$transcriptionsStore.current) {
        await transcriptionsStore.create({
          dictation_id: dictationId,
          content
        });
      }

      if ($transcriptionsStore.current) {
        await transcriptionsStore.submit($transcriptionsStore.current.id);
        goto('/dashboard/secretary');
      }
    } catch (error) {
      // Error handled in store
    } finally {
      submitting = false;
    }
  };
</script>

<svelte:head>
  <title>Create Transcription - Dictat</title>
</svelte:head>

<div class="mx-auto max-w-7xl px-4 py-8 sm:px-6 lg:px-8">
  <div class="mb-8">
    <h1 class="text-3xl font-bold text-gray-900">Transcribe Dictation</h1>
    {#if $dictationsStore.current}
      <p class="mt-2 text-gray-600">
        {$dictationsStore.current.title || 'Untitled'} -
        {$dictationsStore.current.patient_reference || 'No patient reference'}
      </p>
    {/if}
  </div>

  {#if $dictationsStore.loading}
    <div class="flex justify-center py-12">
      <LoadingSpinner size="lg" />
    </div>
  {:else if $dictationsStore.current}
    <div class="grid gap-6 lg:grid-cols-3">
      <!-- Audio Player (Sidebar) -->
      <div class="lg:col-span-1">
        <div class="sticky top-20">
          <AudioPlayer dictationId={dictationId} />

          {#if $dictationsStore.current.notes}
            <div class="card mt-4">
              <h3 class="mb-2 font-semibold text-gray-900">Notes</h3>
              <p class="text-sm text-gray-600">{$dictationsStore.current.notes}</p>
            </div>
          {/if}

          {#if $transcriptionsStore.autosaving}
            <div class="mt-4 text-center text-sm text-gray-500">
              <span>Autosaving...</span>
            </div>
          {/if}
        </div>
      </div>

      <!-- Editor (Main) -->
      <div class="lg:col-span-2">
        <div class="card">
          <MarkdownEditor
            bind:content
            autosave={true}
            on:autosave={handleAutosave}
            on:change={(e) => {
              content = e.detail;
            }}
          />

          <div class="mt-6 flex gap-4">
            <button
              type="button"
              on:click={handleSave}
              disabled={$transcriptionsStore.saving}
              class="btn-secondary"
            >
              {$transcriptionsStore.saving ? 'Saving...' : 'Save Draft'}
            </button>

            <button
              type="button"
              on:click={handleSubmit}
              disabled={submitting || !content}
              class="btn-primary flex-1"
            >
              {#if submitting}
                <div class="flex items-center justify-center gap-2">
                  <LoadingSpinner size="sm" />
                  <span>Submitting...</span>
                </div>
              {:else}
                Submit for Review
              {/if}
            </button>

            <a href="/dashboard/secretary" class="btn-secondary">Cancel</a>
          </div>
        </div>
      </div>
    </div>
  {:else}
    <div class="card text-center">
      <p class="text-gray-600">Dictation not found.</p>
      <a href="/dashboard/secretary" class="btn-primary mt-4 inline-block">
        Back to Dashboard
      </a>
    </div>
  {/if}
</div>
