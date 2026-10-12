import { describe, it, expect } from 'vitest';
import { SourceCitation } from './types';

describe('SourceCitation Validation', () => {
  it('correctly validates citation fields and metadata integrity', () => {
    const citation: SourceCitation = {
      title: 'Elena Verna 4.0',
      guest: 'Elena Verna',
      date: '2025-12-18',
      url: 'https://www.lennysnewsletter.com/p/elena-verna-40',
      excerpt: 'We are over 200 million in ARR at Lovable. You have to innovate on growth rather than optimize.',
      score: 0.442,
    };

    expect(citation.title).toBe('Elena Verna 4.0');
    expect(citation.guest).toBe('Elena Verna');
    expect(citation.url).toContain('https://');
    expect(citation.excerpt.length).toBeGreaterThan(20);
    expect(citation.score).toBeGreaterThan(0.2);
  });
});
