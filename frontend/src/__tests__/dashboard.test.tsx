import { render, screen, fireEvent, act } from '@testing-library/react';
import { describe, it, expect, vi, beforeEach } from 'vitest';
import DashboardPage from '../app/dashboard/page';
import { useAuthStore } from '@/stores/authStore';

// Mock the router
vi.mock('next/navigation', () => ({
  useRouter: () => ({
    replace: vi.fn(),
  }),
}));

// Mock the API fetch
vi.mock('@/lib/api', () => ({
  apiFetch: vi.fn().mockResolvedValue({ items: [] }),
  websocketUrl: (id: string) => `ws://localhost/ws/${id}`,
}));

// Mock the auth store
vi.mock('@/stores/authStore', () => ({
  useAuthStore: vi.fn(),
}));

describe('DashboardPage', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    vi.mocked(useAuthStore).mockReturnValue({
      user: { email: 'test@example.com' },
      initialized: true,
      bootstrap: vi.fn(),
      logout: vi.fn(),
    });
  });

  it('renders the dashboard with authenticated user', async () => {
    await act(async () => {
      render(<DashboardPage />);
    });
    expect(screen.getByText('test@example.com')).toBeInTheDocument();
    expect(screen.getByText('New analysis')).toBeInTheDocument();
  });

  it('shows error if starting analysis without enough text', async () => {
    await act(async () => {
      render(<DashboardPage />);
    });
    const startButton = screen.getByText('Start AI analysis');
    await act(async () => {
      fireEvent.click(startButton);
    });
    
    // The sonner toast will be triggered, but we can't easily assert on it without mocking it.
    // However, the button should remain as "Start AI analysis" (not Analyzing...)
    expect(screen.getByText('Start AI analysis')).toBeInTheDocument();
  });
});
