import { describe, it, expect, vi, beforeEach } from 'vitest';
import { screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { renderWithProviders } from '@/test/utils';
import DoctorDashboard from '../DoctorDashboard';
import { mockDictationList } from '@/test/mockData';

vi.mock('@/lib/api', () => ({
  default: {
    dictations: {
      list: vi.fn(),
    },
  },
}));

describe('DoctorDashboard', () => {
  beforeEach(() => {
    const api = require('@/lib/api').default;
    vi.mocked(api.dictations.list).mockResolvedValue({
      items: mockDictationList,
      total: mockDictationList.length,
      page: 1,
      page_size: 100,
      total_pages: 1,
    });
  });

  it('should render dashboard header', async () => {
    renderWithProviders(<DoctorDashboard />);

    expect(screen.getByText('My Dictations')).toBeInTheDocument();
    expect(screen.getByText(/manage your medical dictations/i)).toBeInTheDocument();
  });

  it('should render upload button', async () => {
    renderWithProviders(<DoctorDashboard />);

    expect(screen.getByText('Upload New Dictation')).toBeInTheDocument();
  });

  it('should display dictation list', async () => {
    renderWithProviders(<DoctorDashboard />);

    await waitFor(() => {
      expect(screen.getByText('Patient Visit Notes')).toBeInTheDocument();
      expect(screen.getByText('Follow-up Consultation')).toBeInTheDocument();
      expect(screen.getByText('Procedure Notes')).toBeInTheDocument();
    });
  });

  it('should display patient references', async () => {
    renderWithProviders(<DoctorDashboard />);

    await waitFor(() => {
      expect(screen.getByText(/PAT-12345/)).toBeInTheDocument();
      expect(screen.getByText(/PAT-67890/)).toBeInTheDocument();
    });
  });

  it('should render filter buttons', async () => {
    renderWithProviders(<DoctorDashboard />);

    expect(screen.getByRole('button', { name: 'All' })).toBeInTheDocument();
    expect(screen.getByRole('button', { name: 'Pending' })).toBeInTheDocument();
    expect(screen.getByRole('button', { name: 'In Progress' })).toBeInTheDocument();
    expect(screen.getByRole('button', { name: 'Completed' })).toBeInTheDocument();
  });

  it('should filter dictations when filter button is clicked', async () => {
    const user = userEvent.setup();
    const api = require('@/lib/api').default;

    renderWithProviders(<DoctorDashboard />);

    const pendingButton = screen.getByRole('button', { name: 'Pending' });
    await user.click(pendingButton);

    await waitFor(() => {
      expect(api.dictations.list).toHaveBeenCalledWith(
        expect.objectContaining({
          status: 'pending',
        })
      );
    });
  });

  it('should show priority badges', async () => {
    renderWithProviders(<DoctorDashboard />);

    await waitFor(() => {
      expect(screen.getByText('normal')).toBeInTheDocument();
      expect(screen.getByText('urgent')).toBeInTheDocument();
      expect(screen.getByText('high')).toBeInTheDocument();
    });
  });

  it('should show status badges', async () => {
    renderWithProviders(<DoctorDashboard />);

    await waitFor(() => {
      expect(screen.getByText('pending')).toBeInTheDocument();
      expect(screen.getByText('in progress')).toBeInTheDocument();
      expect(screen.getByText('completed')).toBeInTheDocument();
    });
  });

  it('should show loading state while fetching', () => {
    const api = require('@/lib/api').default;
    vi.mocked(api.dictations.list).mockImplementation(
      () => new Promise(() => {}) // Never resolves
    );

    renderWithProviders(<DoctorDashboard />);

    expect(screen.getByText('Loading...')).toBeInTheDocument();
  });

  it('should show empty state when no dictations', async () => {
    const api = require('@/lib/api').default;
    vi.mocked(api.dictations.list).mockResolvedValue({
      items: [],
      total: 0,
      page: 1,
      page_size: 100,
      total_pages: 0,
    });

    renderWithProviders(<DoctorDashboard />);

    await waitFor(() => {
      expect(screen.getByText('No dictations')).toBeInTheDocument();
      expect(screen.getByText(/get started by uploading/i)).toBeInTheDocument();
    });
  });
});
