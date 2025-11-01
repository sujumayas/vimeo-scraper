import React from 'react';
import { VimeoMovie } from '../types';
import { Badge, cx, useDark } from '../ui';

interface MovieCardProps {
  movie: VimeoMovie;
  onSelect: () => void;
}

export const MovieCard: React.FC<MovieCardProps> = ({ movie, onSelect }) => {
  const dark = useDark();

  // Extract video ID from URL
  const extractVideoId = (url: string): string | null => {
    const match = url.match(/vimeo\.com\/(?:.*\/)?(\d+)/);
    return match ? match[1] : null;
  };

  const videoId = extractVideoId(movie.url);
  const thumbnailUrl = videoId
    ? `https://vumbnail.com/${videoId}.jpg`
    : null;

  return (
    <button
      onClick={onSelect}
      className={cx(
        'block w-full text-left border rounded-[3px] overflow-hidden transition-all hover:scale-[1.02]',
        dark
          ? 'border-neutral-700 bg-neutral-900 hover:border-neutral-600 hover:bg-neutral-800'
          : 'border-neutral-300 bg-white hover:border-neutral-400 hover:shadow-md'
      )}
    >
      {/* Thumbnail */}
      {thumbnailUrl ? (
        <div className="relative aspect-video w-full overflow-hidden bg-neutral-800">
          <img
            src={thumbnailUrl}
            alt={movie.title}
            className="w-full h-full object-cover"
            loading="lazy"
            onError={(e) => {
              // Fallback to placeholder if thumbnail fails
              (e.target as HTMLImageElement).style.display = 'none';
            }}
          />
          <div className="absolute inset-0 flex items-center justify-center bg-black/30">
            <svg
              className="w-12 h-12 text-white opacity-80"
              fill="currentColor"
              viewBox="0 0 24 24"
            >
              <path d="M8 5v14l11-7z"/>
            </svg>
          </div>
        </div>
      ) : (
        <div className={cx(
          'aspect-video w-full flex items-center justify-center',
          dark ? 'bg-neutral-800' : 'bg-neutral-200'
        )}>
          <svg
            className={cx('w-12 h-12', dark ? 'text-neutral-600' : 'text-neutral-400')}
            fill="currentColor"
            viewBox="0 0 24 24"
          >
            <path d="M8 5v14l11-7z"/>
          </svg>
        </div>
      )}

      {/* Content */}
      <div className="p-3">
        <h3 className={cx(
          'text-sm font-bold mb-2 line-clamp-2 min-h-[2.5rem]',
          dark ? 'text-neutral-100' : 'text-neutral-800'
        )}>
          {movie.title}
        </h3>

        <div className="flex flex-wrap items-center gap-1 mb-2">
          <Badge tone="info">{movie.duration_formatted}</Badge>
          {movie.estimated_production_year && (
            <Badge tone="note">{movie.estimated_production_year}</Badge>
          )}
          {movie.genre && (
            <Badge tone="neutral">{movie.genre}</Badge>
          )}
          {movie.tmdb_verification?.verified && (
            <Badge tone="positive">✓ TMDB</Badge>
          )}
          {movie.quality_score && movie.quality_score >= 8 && (
            <Badge tone="caution">⭐ {movie.quality_score}/10</Badge>
          )}
        </div>

        <p className={cx(
          'text-xs mb-2',
          dark ? 'text-neutral-400' : 'text-neutral-600'
        )}>
          by {movie.user}
        </p>

        {movie.description && (
          <p className={cx(
            'text-xs line-clamp-2',
            dark ? 'text-neutral-500' : 'text-neutral-500'
          )}>
            {movie.description}
          </p>
        )}
      </div>
    </button>
  );
};
