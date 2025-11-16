import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import Layout from '@/components/Layout';
import { useToast } from '@/hooks/useToast';
import api from '@/lib/api';
import type { DictationListItem } from '@/types/api-types';
import { DictationPriority } from '@/types/api-types';

export default function SecretaryWorkQueue() {
  const [queue, setQueue] = useState<DictationListItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [claiming, setClaiming] = useState<number | null>(null);

  const navigate = useNavigate();
  const { showToast, ToastContainer } = useToast();

  useEffect(() => {
    loadQueue();
    // Poll for updates every 30 seconds
    const interval = setInterval(loadQueue, 30000);
    return () => clearInterval(interval);
  }, []);

  const loadQueue = async () => {
    try {
      const response = await api.dictations.queue({ limit: 50 });
      setQueue(response.items);
    } catch (error) {
      console.error('Failed to load queue:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleClaim = async (id: number) => {
    setClaiming(id);
    try {
      await api.dictations.claim(id);
      showToast('Dictation claimed successfully!', 'success');
      // Navigate to transcription page
      navigate(`/transcribe/${id}`);
    } catch (error: any) {
      showToast(error?.error?.detail || 'Failed to claim dictation', 'error');
    } finally {
      setClaiming(null);
    }
  };

  const getPriorityBadge = (priority: DictationPriority) => {
    const colors = {
      urgent: 'bg-red-100 text-red-800',
      high: 'bg-orange-100 text-orange-800',
      normal: 'bg-blue-100 text-blue-800',
      low: 'bg-gray-100 text-gray-800',
    };
    return (
      <span className={`rounded-full px-2 py-1 text-xs font-medium ${colors[priority]}`}>
        {priority}
      </span>
    );
  };

  return (
    <Layout>
      <ToastContainer />
      <div className="space-y-6">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Work Queue</h1>
          <p className="mt-1 text-sm text-gray-500">
            Available dictations ready for transcription
          </p>
        </div>

        {loading ? (
          <div className="text-center">
            <div className="inline-block h-12 w-12 animate-spin rounded-full border-4 border-solid border-primary-600 border-r-transparent"></div>
            <p className="mt-2 text-gray-600">Loading queue...</p>
          </div>
        ) : queue.length === 0 ? (
          <div className="rounded-lg border-2 border-dashed border-gray-300 p-12 text-center">
            <h3 className="mt-2 text-sm font-semibold text-gray-900">No dictations available</h3>
            <p className="mt-1 text-sm text-gray-500">
              Check back later for new dictations to transcribe.
            </p>
          </div>
        ) : (
          <div className="overflow-hidden bg-white shadow ring-1 ring-black ring-opacity-5 sm:rounded-lg">
            <table className="min-w-full divide-y divide-gray-300">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium uppercase tracking-wide text-gray-500">
                    Priority
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium uppercase tracking-wide text-gray-500">
                    Title
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium uppercase tracking-wide text-gray-500">
                    Patient Ref
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium uppercase tracking-wide text-gray-500">
                    Duration
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium uppercase tracking-wide text-gray-500">
                    Created
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium uppercase tracking-wide text-gray-500">
                    Actions
                  </th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-200 bg-white">
                {queue.map((item) => (
                  <tr key={item.id} className="hover:bg-gray-50">
                    <td className="whitespace-nowrap px-6 py-4 text-sm">
                      {getPriorityBadge(item.priority)}
                    </td>
                    <td className="px-6 py-4 text-sm font-medium text-gray-900">
                      {item.title || 'Untitled'}
                    </td>
                    <td className="whitespace-nowrap px-6 py-4 text-sm text-gray-500">
                      {item.patient_reference || '-'}
                    </td>
                    <td className="whitespace-nowrap px-6 py-4 text-sm text-gray-500">
                      {item.duration ? `${Math.round(item.duration)}s` : '-'}
                    </td>
                    <td className="whitespace-nowrap px-6 py-4 text-sm text-gray-500">
                      {new Date(item.created_at).toLocaleDateString()}
                      <div className="text-xs text-gray-400">
                        {new Date(item.created_at).toLocaleTimeString()}
                      </div>
                    </td>
                    <td className="whitespace-nowrap px-6 py-4 text-sm">
                      <button
                        onClick={() => handleClaim(item.id)}
                        disabled={claiming === item.id}
                        className="rounded-md bg-primary-600 px-3 py-1.5 text-sm font-semibold text-white shadow-sm hover:bg-primary-500 disabled:opacity-50"
                      >
                        {claiming === item.id ? 'Claiming...' : 'Claim & Transcribe'}
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </Layout>
  );
}
