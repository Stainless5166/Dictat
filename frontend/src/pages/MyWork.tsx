import { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import Layout from '@/components/Layout';
import api from '@/lib/api';
import type { DictationListItem } from '@/types/api-types';
import { DictationStatus } from '@/types/api-types';

export default function MyWork() {
  const [dictations, setDictations] = useState<DictationListItem[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadMyWork();
  }, []);

  const loadMyWork = async () => {
    try {
      const response = await api.dictations.list({
        limit: 50,
        status: DictationStatus.IN_PROGRESS,
      });
      setDictations(response.items);
    } catch (error) {
      console.error('Failed to load my work:', error);
    } finally {
      setLoading(false);
    }
  };

  const getStatusBadge = (status: DictationStatus) => {
    const colors = {
      pending: 'bg-yellow-100 text-yellow-800',
      assigned: 'bg-blue-100 text-blue-800',
      in_progress: 'bg-indigo-100 text-indigo-800',
      completed: 'bg-green-100 text-green-800',
      reviewed: 'bg-emerald-100 text-emerald-800',
      rejected: 'bg-red-100 text-red-800',
    };
    return (
      <span className={`rounded-full px-2 py-1 text-xs font-medium ${colors[status]}`}>
        {status.replace('_', ' ')}
      </span>
    );
  };

  return (
    <Layout>
      <div className="space-y-6">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">My Work</h1>
          <p className="mt-1 text-sm text-gray-500">
            Dictations currently being transcribed by you
          </p>
        </div>

        {loading ? (
          <div className="text-center">
            <div className="inline-block h-12 w-12 animate-spin rounded-full border-4 border-solid border-primary-600 border-r-transparent"></div>
            <p className="mt-2 text-gray-600">Loading...</p>
          </div>
        ) : dictations.length === 0 ? (
          <div className="rounded-lg border-2 border-dashed border-gray-300 p-12 text-center">
            <h3 className="mt-2 text-sm font-semibold text-gray-900">No active work</h3>
            <p className="mt-1 text-sm text-gray-500">
              Claim dictations from the work queue to start transcribing.
            </p>
            <div className="mt-6">
              <Link
                to="/queue"
                className="inline-flex items-center rounded-md bg-primary-600 px-3 py-2 text-sm font-semibold text-white shadow-sm hover:bg-primary-500"
              >
                View Work Queue
              </Link>
            </div>
          </div>
        ) : (
          <div className="overflow-hidden bg-white shadow ring-1 ring-black ring-opacity-5 sm:rounded-lg">
            <table className="min-w-full divide-y divide-gray-300">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium uppercase tracking-wide text-gray-500">
                    Title
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium uppercase tracking-wide text-gray-500">
                    Patient Ref
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium uppercase tracking-wide text-gray-500">
                    Status
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium uppercase tracking-wide text-gray-500">
                    Claimed
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium uppercase tracking-wide text-gray-500">
                    Actions
                  </th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-200 bg-white">
                {dictations.map((dictation) => (
                  <tr key={dictation.id} className="hover:bg-gray-50">
                    <td className="px-6 py-4 text-sm font-medium text-gray-900">
                      {dictation.title || 'Untitled'}
                    </td>
                    <td className="whitespace-nowrap px-6 py-4 text-sm text-gray-500">
                      {dictation.patient_reference || '-'}
                    </td>
                    <td className="whitespace-nowrap px-6 py-4 text-sm">
                      {getStatusBadge(dictation.status)}
                    </td>
                    <td className="whitespace-nowrap px-6 py-4 text-sm text-gray-500">
                      {dictation.claimed_at
                        ? new Date(dictation.claimed_at).toLocaleDateString()
                        : '-'}
                    </td>
                    <td className="whitespace-nowrap px-6 py-4 text-sm">
                      <Link
                        to={`/transcribe/${dictation.id}`}
                        className="text-primary-600 hover:text-primary-900"
                      >
                        Continue Transcribing
                      </Link>
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
