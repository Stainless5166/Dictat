import { useState, useEffect, useCallback, useRef } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import Layout from '@/components/Layout';
import AudioPlayer from '@/components/AudioPlayer';
import { useToast } from '@/hooks/useToast';
import api from '@/lib/api';
import type { DictationResponse, TranscriptionResponse } from '@/types/api-types';
import ReactMarkdown from 'react-markdown';

export default function TranscriptionEditor() {
  const { id } = useParams<{ id: string }>();
  const dictationId = Number(id);

  const [dictation, setDictation] = useState<DictationResponse | null>(null);
  const [transcription, setTranscription] = useState<TranscriptionResponse | null>(null);
  const [content, setContent] = useState('');
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [submitting, setSubmitting] = useState(false);
  const [showPreview, setShowPreview] = useState(false);
  const [lastSaved, setLastSaved] = useState<Date | null>(null);

  const autosaveTimerRef = useRef<NodeJS.Timeout | null>(null);
  const navigate = useNavigate();
  const { showToast, ToastContainer } = useToast();

  useEffect(() => {
    loadDictationAndTranscription();
  }, [dictationId]);

  const loadDictationAndTranscription = async () => {
    try {
      setLoading(true);
      const dictationData = await api.dictations.get(dictationId);
      setDictation(dictationData);

      // Try to load existing transcription
      try {
        const transcriptionData = await api.transcriptions.get(dictationId);
        setTranscription(transcriptionData);
        setContent(transcriptionData.content);
      } catch (error: any) {
        // No transcription yet, create one
        if (error?.status === 404) {
          const newTranscription = await api.transcriptions.create({
            dictation_id: dictationId,
            content: '',
          });
          setTranscription(newTranscription);
          setContent('');
        }
      }
    } catch (error: any) {
      showToast(error?.error?.detail || 'Failed to load dictation', 'error');
      navigate('/queue');
    } finally {
      setLoading(false);
    }
  };

  const handleContentChange = useCallback(
    (newContent: string) => {
      setContent(newContent);

      // Clear existing timer
      if (autosaveTimerRef.current) {
        clearTimeout(autosaveTimerRef.current);
      }

      // Set new autosave timer (2 seconds after last keystroke)
      autosaveTimerRef.current = setTimeout(() => {
        performAutosave(newContent);
      }, 2000);
    },
    [transcription]
  );

  const performAutosave = async (contentToSave: string) => {
    if (!transcription) return;

    try {
      setSaving(true);
      await api.transcriptions.update(
        transcription.id,
        { content: contentToSave },
        true // isAutosave
      );
      setLastSaved(new Date());
    } catch (error) {
      console.error('Autosave failed:', error);
    } finally {
      setSaving(false);
    }
  };

  const handleManualSave = async () => {
    if (!transcription) return;

    try {
      setSaving(true);
      await api.transcriptions.update(transcription.id, { content }, false);
      setLastSaved(new Date());
      showToast('Transcription saved successfully', 'success');
    } catch (error: any) {
      showToast(error?.error?.detail || 'Failed to save transcription', 'error');
    } finally {
      setSaving(false);
    }
  };

  const handleSubmit = async () => {
    if (!transcription) return;

    if (!content.trim()) {
      showToast('Please enter transcription content before submitting', 'warning');
      return;
    }

    setSubmitting(true);
    try {
      // Save first
      await api.transcriptions.update(transcription.id, { content }, false);
      // Then submit
      await api.transcriptions.submit(transcription.id);
      showToast('Transcription submitted for review!', 'success');
      setTimeout(() => navigate('/my-work'), 1500);
    } catch (error: any) {
      showToast(error?.error?.detail || 'Failed to submit transcription', 'error');
    } finally {
      setSubmitting(false);
    }
  };

  const handleUnclaim = async () => {
    if (!dictation) return;

    if (
      confirm(
        'Are you sure you want to release this dictation? Any unsaved changes will be lost.'
      )
    ) {
      try {
        await api.dictations.unclaim(dictation.id);
        showToast('Dictation released back to queue', 'info');
        navigate('/queue');
      } catch (error: any) {
        showToast(error?.error?.detail || 'Failed to unclaim dictation', 'error');
      }
    }
  };

  if (loading) {
    return (
      <Layout>
        <div className="text-center">
          <div className="inline-block h-12 w-12 animate-spin rounded-full border-4 border-solid border-primary-600 border-r-transparent"></div>
          <p className="mt-2 text-gray-600">Loading...</p>
        </div>
      </Layout>
    );
  }

  const audioURL = dictation ? api.dictations.getAudioURL(dictation.id) : '';

  return (
    <Layout>
      <ToastContainer />
      <div className="space-y-6">
        {/* Header */}
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-bold text-gray-900">
              {dictation?.title || 'Untitled Dictation'}
            </h1>
            <div className="mt-1 flex items-center space-x-4 text-sm text-gray-500">
              {dictation?.patient_reference && (
                <span>Patient: {dictation.patient_reference}</span>
              )}
              {lastSaved && (
                <span className="text-green-600">
                  Last saved: {lastSaved.toLocaleTimeString()}
                </span>
              )}
              {saving && <span className="text-blue-600">Saving...</span>}
            </div>
          </div>
          <div className="flex space-x-3">
            <button
              onClick={() => setShowPreview(!showPreview)}
              className="rounded-md bg-white px-4 py-2 text-sm font-semibold text-gray-900 shadow-sm ring-1 ring-inset ring-gray-300 hover:bg-gray-50"
            >
              {showPreview ? 'Edit' : 'Preview'}
            </button>
            <button
              onClick={handleUnclaim}
              className="rounded-md bg-white px-4 py-2 text-sm font-semibold text-gray-900 shadow-sm ring-1 ring-inset ring-gray-300 hover:bg-gray-50"
            >
              Release
            </button>
            <button
              onClick={handleManualSave}
              disabled={saving}
              className="rounded-md bg-white px-4 py-2 text-sm font-semibold text-gray-900 shadow-sm ring-1 ring-inset ring-gray-300 hover:bg-gray-50 disabled:opacity-50"
            >
              {saving ? 'Saving...' : 'Save'}
            </button>
            <button
              onClick={handleSubmit}
              disabled={submitting || !content.trim()}
              className="rounded-md bg-primary-600 px-4 py-2 text-sm font-semibold text-white shadow-sm hover:bg-primary-500 disabled:opacity-50"
            >
              {submitting ? 'Submitting...' : 'Submit for Review'}
            </button>
          </div>
        </div>

        {/* Audio Player */}
        <AudioPlayer audioURL={audioURL} />

        {/* Editor/Preview */}
        <div className="rounded-lg bg-white shadow ring-1 ring-black ring-opacity-5">
          {showPreview ? (
            <div className="prose max-w-none p-6">
              {content ? (
                <ReactMarkdown>{content}</ReactMarkdown>
              ) : (
                <p className="text-gray-400">No content yet</p>
              )}
            </div>
          ) : (
            <textarea
              value={content}
              onChange={(e) => handleContentChange(e.target.value)}
              className="block min-h-[500px] w-full rounded-lg border-0 p-6 font-mono text-sm text-gray-900 focus:ring-2 focus:ring-inset focus:ring-primary-600"
              placeholder="# Patient Visit Notes

Patient presented with...

## History
- Previous conditions
- Current medications

## Examination
- Physical findings

## Assessment
- Diagnosis

## Plan
- Treatment recommendations
"
            />
          )}
        </div>

        {/* Notes from doctor */}
        {dictation?.notes && (
          <div className="rounded-lg bg-yellow-50 p-4">
            <h3 className="text-sm font-medium text-yellow-800">Doctor's Notes:</h3>
            <p className="mt-1 text-sm text-yellow-700">{dictation.notes}</p>
          </div>
        )}
      </div>
    </Layout>
  );
}
