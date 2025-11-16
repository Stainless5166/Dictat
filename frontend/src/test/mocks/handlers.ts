import { http, HttpResponse } from 'msw';
import {
  mockDoctor,
  mockSecretary,
  mockTokens,
  mockDictation,
  mockDictationList,
  mockTranscription,
} from '../mockData';

const BASE_URL = 'http://localhost:8000/api/v1';

export const handlers = [
  // Authentication
  http.post(`${BASE_URL}/auth/login`, () => {
    return HttpResponse.json(mockTokens);
  }),

  http.post(`${BASE_URL}/auth/register`, () => {
    return HttpResponse.json(mockDoctor);
  }),

  http.get(`${BASE_URL}/auth/me`, () => {
    return HttpResponse.json(mockDoctor);
  }),

  http.post(`${BASE_URL}/auth/logout`, () => {
    return HttpResponse.json({ message: 'Logged out successfully' });
  }),

  http.post(`${BASE_URL}/auth/refresh`, () => {
    return HttpResponse.json(mockTokens);
  }),

  // Dictations
  http.get(`${BASE_URL}/dictations`, () => {
    return HttpResponse.json({
      items: mockDictationList,
      total: mockDictationList.length,
      page: 1,
      page_size: 100,
      total_pages: 1,
    });
  }),

  http.get(`${BASE_URL}/dictations/queue`, () => {
    return HttpResponse.json({
      items: mockDictationList.filter((d) => d.status === 'pending'),
      total: 1,
      page: 1,
      page_size: 100,
      total_pages: 1,
    });
  }),

  http.get(`${BASE_URL}/dictations/:id`, ({ params }) => {
    return HttpResponse.json({
      ...mockDictation,
      id: Number(params.id),
    });
  }),

  http.post(`${BASE_URL}/dictations`, () => {
    return HttpResponse.json(mockDictation);
  }),

  http.post(`${BASE_URL}/dictations/:id/claim`, ({ params }) => {
    return HttpResponse.json({
      ...mockDictation,
      id: Number(params.id),
      secretary_id: 2,
      status: 'in_progress',
      claimed_at: new Date().toISOString(),
    });
  }),

  http.post(`${BASE_URL}/dictations/:id/unclaim`, () => {
    return HttpResponse.json({ message: 'Dictation unclaimed successfully' });
  }),

  http.patch(`${BASE_URL}/dictations/:id`, () => {
    return HttpResponse.json(mockDictation);
  }),

  http.delete(`${BASE_URL}/dictations/:id`, () => {
    return HttpResponse.json({ message: 'Dictation deleted successfully' });
  }),

  // Transcriptions
  http.get(`${BASE_URL}/transcriptions/:id`, ({ params }) => {
    return HttpResponse.json({
      ...mockTranscription,
      id: Number(params.id),
    });
  }),

  http.post(`${BASE_URL}/transcriptions`, () => {
    return HttpResponse.json(mockTranscription);
  }),

  http.patch(`${BASE_URL}/transcriptions/:id`, () => {
    return HttpResponse.json({
      ...mockTranscription,
      updated_at: new Date().toISOString(),
      last_autosave_at: new Date().toISOString(),
    });
  }),

  http.post(`${BASE_URL}/transcriptions/:id/submit`, () => {
    return HttpResponse.json({
      ...mockTranscription,
      status: 'submitted',
      submitted_at: new Date().toISOString(),
    });
  }),

  http.post(`${BASE_URL}/transcriptions/:id/review`, () => {
    return HttpResponse.json({
      ...mockTranscription,
      status: 'approved',
      reviewer_id: 1,
      reviewed_at: new Date().toISOString(),
    });
  }),
];
