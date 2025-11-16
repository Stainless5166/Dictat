import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import AudioPlayer from '../AudioPlayer';

describe('AudioPlayer', () => {
  const mockAudioURL = 'http://example.com/audio.mp3';

  beforeEach(() => {
    // Mock HTMLAudioElement methods
    HTMLAudioElement.prototype.play = vi.fn();
    HTMLAudioElement.prototype.pause = vi.fn();
  });

  it('should render audio player', () => {
    render(<AudioPlayer audioURL={mockAudioURL} />);

    // Check for play button (SVG with play icon)
    const playButton = screen.getByRole('button', { name: /play|pause/i });
    expect(playButton).toBeInTheDocument();
  });

  it('should render playback speed controls', () => {
    render(<AudioPlayer audioURL={mockAudioURL} />);

    // Check for playback speed buttons
    expect(screen.getByText('0.5x')).toBeInTheDocument();
    expect(screen.getByText('0.75x')).toBeInTheDocument();
    expect(screen.getByText('1x')).toBeInTheDocument();
    expect(screen.getByText('1.25x')).toBeInTheDocument();
    expect(screen.getByText('1.5x')).toBeInTheDocument();
    expect(screen.getByText('2x')).toBeInTheDocument();
  });

  it('should render skip backward and forward buttons', () => {
    render(<AudioPlayer audioURL={mockAudioURL} />);

    const buttons = screen.getAllByRole('button');
    // Should have: skip back, play/pause, skip forward, and 6 speed buttons = 9 total
    expect(buttons.length).toBeGreaterThanOrEqual(9);
  });

  it('should toggle play/pause when play button is clicked', async () => {
    const user = userEvent.setup();
    render(<AudioPlayer audioURL={mockAudioURL} />);

    const playButton = screen.getAllByRole('button')[1]; // Middle button is play/pause
    await user.click(playButton);

    expect(HTMLAudioElement.prototype.play).toHaveBeenCalled();
  });

  it('should change playback rate when speed button is clicked', async () => {
    const user = userEvent.setup();
    render(<AudioPlayer audioURL={mockAudioURL} />);

    const speed2xButton = screen.getByText('2x');
    await user.click(speed2xButton);

    // Check if button is highlighted (active)
    expect(speed2xButton.className).toContain('bg-primary-600');
  });

  it('should render time display', () => {
    render(<AudioPlayer audioURL={mockAudioURL} />);

    // Should show 0:00 / 0:00 initially
    expect(screen.getByText(/0:00/)).toBeInTheDocument();
  });

  it('should render progress slider', () => {
    render(<AudioPlayer audioURL={mockAudioURL} />);

    const slider = screen.getByRole('slider', { hidden: true });
    expect(slider).toBeInTheDocument();
  });

  it('should have accessible audio element', () => {
    const { container } = render(<AudioPlayer audioURL={mockAudioURL} />);

    const audio = container.querySelector('audio');
    expect(audio).toBeInTheDocument();
    expect(audio?.getAttribute('src')).toBe(mockAudioURL);
  });
});
