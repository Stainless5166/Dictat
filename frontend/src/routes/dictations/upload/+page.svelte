<script lang="ts">
  import { goto } from '$app/navigation';
  import { dictationsStore } from '$stores/dictations';
  import { DictationPriority } from '$lib/api';
  import AudioRecorder from '$components/dictation/AudioRecorder.svelte';
  import LoadingSpinner from '$components/shared/LoadingSpinner.svelte';

  let file: File | null = null;
  let title = '';
  let patientReference = '';
  let priority: DictationPriority = DictationPriority.NORMAL;
  let notes = '';
  let uploading = false;
  let uploadProgress = 0;
  let useRecorder = false;

  const handleFileChange = (e: Event) => {
    const target = e.target as HTMLInputElement;
    if (target.files && target.files[0]) {
      file = target.files[0];
      useRecorder = false;
    }
  };

  const handleRecordingComplete = (blob: Blob) => {
    file = new File([blob], `recording-${Date.now()}.webm`, { type: 'audio/webm' });
    useRecorder = false;
  };

  const handleSubmit = async (e: Event) => {
    e.preventDefault();

    if (!file) {
      return;
    }

    uploading = true;

    try {
      await dictationsStore.create(
        {
          file,
          title: title || undefined,
          patient_reference: patientReference || undefined,
          priority,
          notes: notes || undefined
        },
        (progress) => {
          uploadProgress = progress;
        }
      );

      goto('/dashboard/doctor');
    } catch (error) {
      // Error handled in store
    } finally {
      uploading = false;
      uploadProgress = 0;
    }
  };
</script>

<svelte:head>
  <title>Upload Dictation - Dictat</title>
</svelte:head>

<div class="mx-auto max-w-2xl px-4 py-8 sm:px-6 lg:px-8">
  <div class="mb-8">
    <h1 class="text-3xl font-bold text-gray-900">Upload Dictation</h1>
    <p class="mt-2 text-gray-600">Record or upload your medical dictation</p>
  </div>

  <form on:submit={handleSubmit} class="card space-y-6">
    <!-- Audio Input -->
    <div>
      <label class="label">Audio File *</label>

      {#if useRecorder}
        <AudioRecorder on:complete={(e) => handleRecordingComplete(e.detail)} />
      {:else if file}
        <div class="flex items-center justify-between rounded-md border border-gray-300 bg-gray-50 p-4">
          <div>
            <p class="text-sm font-medium text-gray-900">{file.name}</p>
            <p class="text-sm text-gray-500">
              {(file.size / 1024 / 1024).toFixed(2)} MB
            </p>
          </div>
          <button
            type="button"
            on:click={() => {
              file = null;
            }}
            class="btn-secondary btn-sm"
          >
            Remove
          </button>
        </div>
      {:else}
        <div class="space-y-3">
          <input
            type="file"
            accept="audio/*"
            on:change={handleFileChange}
            class="block w-full rounded-md border border-gray-300 px-3 py-2 text-sm file:mr-4 file:rounded-md file:border-0 file:bg-primary-50 file:px-4 file:py-2 file:text-sm file:font-semibold file:text-primary-700 hover:file:bg-primary-100"
          />
          <div class="text-center">
            <span class="text-sm text-gray-500">or</span>
          </div>
          <button
            type="button"
            on:click={() => {
              useRecorder = true;
            }}
            class="btn-secondary w-full"
          >
            🎤 Record Audio
          </button>
        </div>
      {/if}
    </div>

    <!-- Title -->
    <div>
      <label for="title" class="label">Title</label>
      <input
        id="title"
        type="text"
        bind:value={title}
        class="input"
        placeholder="Patient Visit Notes"
      />
    </div>

    <!-- Patient Reference -->
    <div>
      <label for="patientRef" class="label">Patient Reference</label>
      <input
        id="patientRef"
        type="text"
        bind:value={patientReference}
        class="input"
        placeholder="PAT-12345"
      />
    </div>

    <!-- Priority -->
    <div>
      <label for="priority" class="label">Priority</label>
      <select id="priority" bind:value={priority} class="input">
        <option value={DictationPriority.LOW}>Low</option>
        <option value={DictationPriority.NORMAL}>Normal</option>
        <option value={DictationPriority.HIGH}>High</option>
        <option value={DictationPriority.URGENT}>Urgent</option>
      </select>
    </div>

    <!-- Notes -->
    <div>
      <label for="notes" class="label">Additional Notes</label>
      <textarea
        id="notes"
        bind:value={notes}
        rows="4"
        class="input"
        placeholder="Any additional instructions or notes for the transcriber..."
      />
    </div>

    <!-- Upload Progress -->
    {#if uploading}
      <div>
        <div class="mb-2 flex items-center justify-between text-sm">
          <span class="text-gray-600">Uploading...</span>
          <span class="font-medium text-primary-600">{uploadProgress.toFixed(1)}%</span>
        </div>
        <div class="h-2 overflow-hidden rounded-full bg-gray-200">
          <div
            class="h-full rounded-full bg-primary-600 transition-all duration-300"
            style="width: {uploadProgress}%"
          />
        </div>
      </div>
    {/if}

    <!-- Actions -->
    <div class="flex gap-4">
      <button type="submit" disabled={uploading || !file} class="btn-primary flex-1">
        {#if uploading}
          <div class="flex items-center justify-center gap-2">
            <LoadingSpinner size="sm" />
            <span>Uploading...</span>
          </div>
        {:else}
          Upload Dictation
        {/if}
      </button>
      <a href="/dashboard/doctor" class="btn-secondary">Cancel</a>
    </div>
  </form>
</div>
