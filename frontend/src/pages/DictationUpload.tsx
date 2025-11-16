import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import Layout from '@/components/Layout';
import { useToast } from '@/hooks/useToast';
import api from '@/lib/api';
import { DictationPriority } from '@/types/api-types';

export default function DictationUpload() {
  const [file, setFile] = useState<File | null>(null);
  const [title, setTitle] = useState('');
  const [patientReference, setPatientReference] = useState('');
  const [priority, setPriority] = useState(DictationPriority.NORMAL);
  const [notes, setNotes] = useState('');
  const [uploading, setUploading] = useState(false);
  const [progress, setProgress] = useState(0);

  const navigate = useNavigate();
  const { showToast, ToastContainer } = useToast();

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const selectedFile = e.target.files?.[0];
    if (selectedFile) {
      setFile(selectedFile);
      // Auto-set duration if audio file
      if (selectedFile.type.startsWith('audio/')) {
        const audio = document.createElement('audio');
        audio.src = URL.createObjectURL(selectedFile);
        audio.addEventListener('loadedmetadata', () => {
          console.log('Audio duration:', audio.duration);
        });
      }
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!file) {
      showToast('Please select an audio file', 'error');
      return;
    }

    setUploading(true);
    setProgress(0);

    try {
      const dictation = await api.dictations.create(
        {
          file,
          title: title || undefined,
          patient_reference: patientReference || undefined,
          priority,
          notes: notes || undefined,
        },
        (uploadProgress) => setProgress(uploadProgress)
      );

      showToast('Dictation uploaded successfully!', 'success');

      // Reset form
      setFile(null);
      setTitle('');
      setPatientReference('');
      setPriority(DictationPriority.NORMAL);
      setNotes('');
      setProgress(0);

      // Navigate to dictation detail after a brief delay
      setTimeout(() => {
        navigate(`/dictations/${dictation.id}`);
      }, 1500);
    } catch (error: any) {
      console.error('Upload failed:', error);
      showToast(error?.error?.detail || 'Upload failed. Please try again.', 'error');
    } finally {
      setUploading(false);
    }
  };

  return (
    <Layout>
      <ToastContainer />
      <div className="mx-auto max-w-2xl">
        <div className="mb-8">
          <h1 className="text-2xl font-bold text-gray-900">Upload Dictation</h1>
          <p className="mt-1 text-sm text-gray-500">
            Upload a new audio dictation for transcription
          </p>
        </div>

        <form onSubmit={handleSubmit} className="space-y-6">
          <div className="rounded-lg bg-white p-6 shadow ring-1 ring-black ring-opacity-5">
            <div className="space-y-6">
              <div>
                <label htmlFor="file" className="block text-sm font-medium text-gray-700">
                  Audio File *
                </label>
                <div className="mt-2">
                  <input
                    type="file"
                    id="file"
                    accept="audio/*"
                    onChange={handleFileChange}
                    required
                    disabled={uploading}
                    className="block w-full text-sm text-gray-900 file:mr-4 file:rounded-md file:border-0 file:bg-primary-600 file:px-4 file:py-2 file:text-sm file:font-semibold file:text-white hover:file:bg-primary-500"
                  />
                </div>
                {file && (
                  <p className="mt-2 text-sm text-gray-500">
                    Selected: {file.name} ({(file.size / 1024 / 1024).toFixed(2)} MB)
                  </p>
                )}
              </div>

              <div>
                <label htmlFor="title" className="block text-sm font-medium text-gray-700">
                  Title
                </label>
                <input
                  type="text"
                  id="title"
                  value={title}
                  onChange={(e) => setTitle(e.target.value)}
                  disabled={uploading}
                  className="mt-1 block w-full rounded-md border-0 px-3 py-2 text-gray-900 ring-1 ring-inset ring-gray-300 placeholder:text-gray-400 focus:ring-2 focus:ring-inset focus:ring-primary-600 sm:text-sm sm:leading-6"
                  placeholder="Patient Visit Notes"
                />
              </div>

              <div>
                <label
                  htmlFor="patientReference"
                  className="block text-sm font-medium text-gray-700"
                >
                  Patient Reference
                </label>
                <input
                  type="text"
                  id="patientReference"
                  value={patientReference}
                  onChange={(e) => setPatientReference(e.target.value)}
                  disabled={uploading}
                  className="mt-1 block w-full rounded-md border-0 px-3 py-2 text-gray-900 ring-1 ring-inset ring-gray-300 placeholder:text-gray-400 focus:ring-2 focus:ring-inset focus:ring-primary-600 sm:text-sm sm:leading-6"
                  placeholder="PAT-12345"
                />
              </div>

              <div>
                <label htmlFor="priority" className="block text-sm font-medium text-gray-700">
                  Priority
                </label>
                <select
                  id="priority"
                  value={priority}
                  onChange={(e) => setPriority(e.target.value as DictationPriority)}
                  disabled={uploading}
                  className="mt-1 block w-full rounded-md border-0 px-3 py-2 text-gray-900 ring-1 ring-inset ring-gray-300 focus:ring-2 focus:ring-inset focus:ring-primary-600 sm:text-sm sm:leading-6"
                >
                  <option value={DictationPriority.LOW}>Low</option>
                  <option value={DictationPriority.NORMAL}>Normal</option>
                  <option value={DictationPriority.HIGH}>High</option>
                  <option value={DictationPriority.URGENT}>Urgent</option>
                </select>
              </div>

              <div>
                <label htmlFor="notes" className="block text-sm font-medium text-gray-700">
                  Notes
                </label>
                <textarea
                  id="notes"
                  rows={4}
                  value={notes}
                  onChange={(e) => setNotes(e.target.value)}
                  disabled={uploading}
                  className="mt-1 block w-full rounded-md border-0 px-3 py-2 text-gray-900 ring-1 ring-inset ring-gray-300 placeholder:text-gray-400 focus:ring-2 focus:ring-inset focus:ring-primary-600 sm:text-sm sm:leading-6"
                  placeholder="Additional notes for the secretary..."
                />
              </div>

              {uploading && (
                <div>
                  <div className="mb-2 flex justify-between text-sm text-gray-600">
                    <span>Uploading...</span>
                    <span>{progress.toFixed(1)}%</span>
                  </div>
                  <div className="h-2 w-full overflow-hidden rounded-full bg-gray-200">
                    <div
                      className="h-full bg-primary-600 transition-all duration-300"
                      style={{ width: `${progress}%` }}
                    />
                  </div>
                </div>
              )}
            </div>
          </div>

          <div className="flex justify-end space-x-3">
            <button
              type="button"
              onClick={() => navigate('/dashboard')}
              disabled={uploading}
              className="rounded-md bg-white px-4 py-2 text-sm font-semibold text-gray-900 shadow-sm ring-1 ring-inset ring-gray-300 hover:bg-gray-50 disabled:opacity-50"
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={uploading || !file}
              className="rounded-md bg-primary-600 px-4 py-2 text-sm font-semibold text-white shadow-sm hover:bg-primary-500 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-primary-600 disabled:opacity-50"
            >
              {uploading ? `Uploading (${progress.toFixed(0)}%)...` : 'Upload Dictation'}
            </button>
          </div>
        </form>
      </div>
    </Layout>
  );
}
