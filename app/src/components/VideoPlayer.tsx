import React from 'react';
import { cx, useDark } from '../ui';

interface VideoPlayerProps {
  videoId: string;
  title?: string;
}

export const VideoPlayer: React.FC<VideoPlayerProps> = ({ videoId, title }) => {
  const dark = useDark();

  if (!videoId) {
    return (
      <div className={cx(
        'aspect-video w-full flex items-center justify-center rounded-[3px] border',
        dark ? 'bg-neutral-900 border-neutral-700 text-neutral-400' : 'bg-neutral-100 border-neutral-300 text-neutral-600'
      )}>
        <p className="text-sm">Unable to load video</p>
      </div>
    );
  }

  return (
    <div className="relative aspect-video w-full overflow-hidden rounded-[3px]">
      <iframe
        src={`https://player.vimeo.com/video/${videoId}?title=0&byline=0&portrait=0`}
        className="absolute inset-0 w-full h-full"
        frameBorder="0"
        allow="autoplay; fullscreen; picture-in-picture"
        allowFullScreen
        title={title || 'Vimeo video player'}
      />
    </div>
  );
};
