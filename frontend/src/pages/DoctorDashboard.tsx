import { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import Layout from '@/components/Layout';
import api from '@/lib/api';
import type { DictationListItem } from '@/types/api-types';
import { DictationStatus, DictationPriority } from '@/types/api-types';

export default function DoctorDashboard() {
  const [dictations, setDictations] = useState<DictationListItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [filter, setFilter] = useState<DictationStatus | 'all'>('all');

  useEffect(() => {
    loadDictations();
  }, [filter]);

  const loadDictations = async () => {
    try {
      setLoading(true);
      const response = await api.dictations.list({
        limit: 50,
        ...(filter !== 'all' && { status: filter }),
      });
      setDictations(response.items);
    } catch (error) {
      console.error('Failed to load dictations:', error);
    } finally {
      setLoading(false);
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
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-bold text-gray-900">My Dictations</h1>
            <p className="mt-1 text-sm text-gray-500">
              Manage your medical dictations and transcriptions
            </p>
          </div>
          <Link
            to="/upload"
            className="rounded-md bg-primary-600 px-4 py-2 text-sm font-semibold text-white shadow-sm hover:bg-primary-500"
          >
            Upload New Dictation
          </Link>
        </div>

        <div className="flex space-x-2">
          <button
            onClick={() => setFilter('all')}
            className={`rounded-md px-3 py-2 text-sm font-medium ${
              filter === 'all'
                ? 'bg-primary-600 text-white'
                : 'bg-white text-gray-700 ring-1 ring-inset ring-gray-300 hover:bg-gray-50'
            }`}
          >
            All
          </button>
          <button
            onClick={() => setFilter(DictationStatus.PENDING)}
            className={`rounded-md px-3 py-2 text-sm font-medium ${
              filter === DictationStatus.PENDING
                ? 'bg-primary-600 text-white'
                : 'bg-white text-gray-700 ring-1 ring-inset ring-gray-300 hover:bg-gray-50'
            }`}
          >
            Pending
          </button>
          <button
            onClick={() => setFilter(DictationStatus.IN_PROGRESS)}
            className={`rounded-md px-3 py-2 text-sm font-medium ${
              filter === DictationStatus.IN_PROGRESS
                ? 'bg-primary-600 text-white'
                : 'bg-white text-gray-700 ring-1 ring-inset ring-gray-300 hover:bg-gray-50'
            }`}
          >
            In Progress
          </button>
          <button
            onClick={() => setFilter(DictationStatus.COMPLETED)}
            className={`rounded-md px-3 py-2 text-sm font-medium ${
              filter === DictationStatus.COMPLETED
                ? 'bg-primary-600 text-white'
                : 'bg-white text-gray-700 ring-1 ring-inset ring-gray-300 hover:bg-gray-50'
            }`}
          >
            Completed
          </button>
        </div>

        {loading ? (
          <div className="text-center">
            <div className="inline-block h-12 w-12 animate-spin rounded-full border-4 border-solid border-primary-600 border-r-transparent"></div>
            <p className="mt-2 text-gray-600">Loading...</p>
          </div>
        ) : dictations.length === 0 ? (
          <div className="rounded-lg border-2 border-dashed border-gray-300 p-12 text-center">
            <h3 className="mt-2 text-sm font-semibold text-gray-900">No dictations</h3>
            <p className="mt-1 text-sm text-gray-500">
              Get started by uploading your first dictation.
            </p>
            <div className="mt-6">
              <Link
                to="/upload"
                className="inline-flex items-center rounded-md bg-primary-600 px-3 py-2 text-sm font-semibold text-white shadow-sm hover:bg-primary-500"
              >
                Upload Dictation
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
                    Priority
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium uppercase tracking-wide text-gray-500">
                    Status
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
                {dictations.map((dictation) => (
                  <tr key={dictation.id} className="hover:bg-gray-50">
                    <td className="whitespace-nowrap px-6 py-4 text-sm font-medium text-gray-900">
                      {dictation.title || 'Untitled'}
                      {dictation.patient_reference && (
                        <span className="ml-2 text-xs text-gray-500">
                          ({dictation.patient_reference})
                        </span>
                      )}
                    </td>
                    <td className="whitespace-nowrap px-6 py-4 text-sm">
                      {getPriorityBadge(dictation.priority)}
                    </td>
                    <td className="whitespace-nowrap px-6 py-4 text-sm">
                      {getStatusBadge(dictation.status)}
                    </td>
                    <td className="whitespace-nowrap px-6 py-4 text-sm text-gray-500">
                      {dictation.duration ? `${Math.round(dictation.duration)}s` : '-'}
                    </td>
                    <td className="whitespace-nowrap px-6 py-4 text-sm text-gray-500">
                      {new Date(dictation.created_at).toLocaleDateString()}
                    </td>
                    <td className="whitespace-nowrap px-6 py-4 text-sm">
                      <Link
                        to={`/dictations/${dictation.id}`}
                        className="text-primary-600 hover:text-primary-900"
                      >
                        View
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
