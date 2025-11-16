/**
 * Dictations Store Tests
 */

import { describe, it, expect, beforeEach, vi } from 'vitest';
import { get } from 'svelte/store';
import { dictationsStore } from '$stores/dictations';
import { createMockApi, mockDictationList, mockDictation } from '../../helpers/mockApi';
import { DictationPriority } from '$lib/types/api-types';
import { createMockFile } from '../../helpers/testUtils';

// Mock the API
vi.mock('$lib/api', () => ({
  api: createMockApi()
}));

describe('Dictations Store', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  describe('loadList', () => {
    it('should load dictations list', async () => {
      await dictationsStore.loadList();

      const state = get(dictationsStore);
      expect(state.items).toEqual(mockDictationList.items);
      expect(state.total).toBe(2);
      expect(state.loading).toBe(false);
    });

    it('should load with filters', async () => {
      const { api } = await import('$lib/api');

      await dictationsStore.loadList({
        status: 'pending',
        priority: DictationPriority.HIGH
      });

      expect(api.dictations.list).toHaveBeenCalledWith({
        status: 'pending',
        priority: DictationPriority.HIGH
      });
    });
  });

  describe('loadQueue', () => {
    it('should load work queue', async () => {
      await dictationsStore.loadQueue();

      const state = get(dictationsStore);
      expect(state.items).toEqual(mockDictationList.items);
      expect(state.loading).toBe(false);
    });
  });

  describe('loadDictation', () => {
    it('should load single dictation', async () => {
      await dictationsStore.loadDictation(1);

      const state = get(dictationsStore);
      expect(state.current).toEqual(mockDictation);
      expect(state.loading).toBe(false);
    });
  });

  describe('create', () => {
    it('should create dictation', async () => {
      const file = createMockFile('test.mp3', 1024000);
      const data = {
        file,
        title: 'Test Dictation',
        priority: DictationPriority.NORMAL
      };

      const result = await dictationsStore.create(data);

      expect(result).toEqual(mockDictation);
    });

    it('should track upload progress', async () => {
      const file = createMockFile('test.mp3', 1024000);
      const onProgress = vi.fn();

      await dictationsStore.create({ file }, onProgress);

      // Progress callback should be passed to API
      const { api } = await import('$lib/api');
      expect(api.dictations.create).toHaveBeenCalledWith(
        { file },
        expect.any(Function)
      );
    });
  });

  describe('claim', () => {
    it('should claim dictation', async () => {
      await dictationsStore.claim(1);

      const { api } = await import('$lib/api');
      expect(api.dictations.claim).toHaveBeenCalledWith(1);
    });
  });

  describe('delete', () => {
    it('should delete dictation', async () => {
      await dictationsStore.delete(1);

      const { api } = await import('$lib/api');
      expect(api.dictations.delete).toHaveBeenCalledWith(1);
    });
  });
});
