import React, { useState, useEffect } from 'react';
import { VimeoMovie } from '../types';
import { Page, PageHeader, Section, Button, Input, Toolbar, Badge, useDark, useTheme, cx } from '../ui';
import { MovieCard } from './MovieCard';
import { VideoPlayer } from './VideoPlayer';

export const MovieBrowser: React.FC = () => {
  const [movies, setMovies] = useState<VimeoMovie[]>([]);
  const [filteredMovies, setFilteredMovies] = useState<VimeoMovie[]>([]);
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedMovie, setSelectedMovie] = useState<VimeoMovie | null>(null);
  const [loading, setLoading] = useState(true);
  const dark = useDark();
  const { setDark } = useTheme();

  useEffect(() => {
    // Load movies from AI-enhanced movies JSON file
    fetch('/ai_enhanced_movies.json')
      .then(res => res.json())
      .then(data => {
        setMovies(data);
        setFilteredMovies(data);
        setLoading(false);
      })
      .catch(err => {
        console.error('Failed to load movies:', err);
        setLoading(false);
      });
  }, []);

  useEffect(() => {
    // Filter movies based on search query
    if (searchQuery.trim() === '') {
      setFilteredMovies(movies);
    } else {
      const query = searchQuery.toLowerCase();
      const filtered = movies.filter(movie =>
        movie.title.toLowerCase().includes(query) ||
        movie.description.toLowerCase().includes(query) ||
        movie.user.toLowerCase().includes(query)
      );
      setFilteredMovies(filtered);
    }
  }, [searchQuery, movies]);

  const extractVideoId = (url: string): string | null => {
    // Extract video ID from Vimeo URL
    // Formats: https://vimeo.com/123456789 or https://vimeo.com/user/video_id
    const match = url.match(/vimeo\.com\/(?:.*\/)?(\d+)/);
    return match ? match[1] : null;
  };

  if (loading) {
    return (
      <Page>
        <PageHeader title="Classic Movies on Vimeo" subtitle="Loading..." />
      </Page>
    );
  }

  return (
    <Page>
      <PageHeader
        title="Classic Movies on Vimeo"
        subtitle={`Browse ${movies.length} vintage films from Vimeo's archive`}
        right={
          <Button onClick={() => setDark(!dark)}>
            {dark ? '☀️ light' : '🌙 dark'}
          </Button>
        }
      />

      {/* Video Player Section */}
      {selectedMovie && (
        <Section title={selectedMovie.title}>
          <VideoPlayer
            videoId={extractVideoId(selectedMovie.url) || ''}
            title={selectedMovie.title}
          />
          <div className={cx('mt-4 p-3 border rounded-[3px]', dark ? 'border-neutral-700 bg-neutral-900' : 'border-neutral-200 bg-neutral-50')}>
            <div className="flex items-start justify-between gap-4 mb-2">
              <div className="flex-1">
                <h3 className="text-sm font-bold mb-1">{selectedMovie.user}</h3>
                <div className="flex items-center gap-2 mb-2 flex-wrap">
                  <Badge tone="info">{selectedMovie.duration_formatted}</Badge>
                  {selectedMovie.estimated_production_year && (
                    <Badge tone="note">{selectedMovie.estimated_production_year}</Badge>
                  )}
                  {selectedMovie.genre && (
                    <Badge tone="neutral">{selectedMovie.genre}</Badge>
                  )}
                  {selectedMovie.tmdb_verification?.verified && (
                    <Badge tone="positive">✓ TMDB Verified</Badge>
                  )}
                  {selectedMovie.quality_score && (
                    <Badge tone="caution">⭐ {selectedMovie.quality_score}/10</Badge>
                  )}
                  {selectedMovie.final_score && (
                    <Badge tone="info">Score: {selectedMovie.final_score.toFixed(1)}</Badge>
                  )}
                </div>
              </div>
              <div className="flex gap-2">
                <Button
                  onClick={() => window.open(selectedMovie.url, '_blank')}
                  variant="solid"
                >
                  Open on Vimeo
                </Button>
                <Button onClick={() => setSelectedMovie(null)}>
                  Close
                </Button>
              </div>
            </div>
            {selectedMovie.description && (
              <p className={cx('text-sm mt-2', dark ? 'text-neutral-300' : 'text-neutral-600')}>
                {selectedMovie.description}
              </p>
            )}
            {selectedMovie.tmdb_verification?.verified && (
              <div className={cx('text-xs mt-3 pt-3 border-t', dark ? 'border-neutral-700 text-neutral-400' : 'border-neutral-200 text-neutral-600')}>
                <div className="grid grid-cols-2 gap-2">
                  <div>
                    <strong className={dark ? 'text-neutral-300' : 'text-neutral-700'}>TMDB Title:</strong> {selectedMovie.tmdb_verification.tmdb_title}
                  </div>
                  <div>
                    <strong className={dark ? 'text-neutral-300' : 'text-neutral-700'}>Release Year:</strong> {selectedMovie.tmdb_verification.release_year}
                  </div>
                  {selectedMovie.tmdb_verification.production_companies.length > 0 && (
                    <div className="col-span-2">
                      <strong className={dark ? 'text-neutral-300' : 'text-neutral-700'}>Production:</strong> {selectedMovie.tmdb_verification.production_companies.join(', ')}
                    </div>
                  )}
                  <div>
                    <strong className={dark ? 'text-neutral-300' : 'text-neutral-700'}>Confidence:</strong> {selectedMovie.tmdb_verification.confidence.toFixed(1)}%
                  </div>
                  <div>
                    <strong className={dark ? 'text-neutral-300' : 'text-neutral-700'}>Runtime:</strong> {selectedMovie.tmdb_verification.runtime_minutes} min
                  </div>
                </div>
              </div>
            )}
          </div>
        </Section>
      )}

      {/* Search and Filters */}
      <Section title="Search & Browse">
        <Toolbar>
          <Input
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            placeholder="Search by title, description, or user..."
            className="flex-1 min-w-[200px]"
          />
          <Badge tone="neutral">{filteredMovies.length} movies</Badge>
          {searchQuery && (
            <Button onClick={() => setSearchQuery('')}>clear</Button>
          )}
        </Toolbar>
      </Section>

      {/* Movie Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
        {filteredMovies.map((movie, index) => (
          <MovieCard
            key={index}
            movie={movie}
            onSelect={() => {
              setSelectedMovie(movie);
              window.scrollTo({ top: 0, behavior: 'smooth' });
            }}
          />
        ))}
      </div>

      {filteredMovies.length === 0 && (
        <Section title="No Results">
          <p className={cx('text-sm', dark ? 'text-neutral-400' : 'text-neutral-600')}>
            No movies found matching "{searchQuery}". Try a different search term.
          </p>
        </Section>
      )}
    </Page>
  );
};
