import { ReactNode } from 'react';
import { RefreshCw } from 'lucide-react';
import { usePullToRefresh } from '@/hooks/use-pull-to-refresh';

interface PullToRefreshProps {
  children: ReactNode;
  onRefresh: () => Promise<void>;
}

export const PullToRefresh = ({ children, onRefresh }: PullToRefreshProps) => {
  const { containerRef, isRefreshing, pullDistance, progress } = usePullToRefresh({
    onRefresh,
    threshold: 80,
  });

  return (
    <div ref={containerRef} className="relative">
      {/* Pull indicator */}
      <div 
        className="absolute left-0 right-0 flex justify-center items-center pointer-events-none z-10 transition-opacity duration-200"
        style={{ 
          top: -50,
          transform: `translateY(${pullDistance}px)`,
          opacity: progress > 0.2 ? 1 : 0,
        }}
      >
        <div className="bg-card border border-border rounded-full p-2 shadow-lg">
          <RefreshCw 
            className={`w-5 h-5 text-primary transition-transform duration-200 ${isRefreshing ? 'animate-spin' : ''}`}
            style={{ 
              transform: isRefreshing ? undefined : `rotate(${progress * 360}deg)`,
            }}
          />
        </div>
      </div>

      {/* Content with transform */}
      <div 
        className="transition-transform duration-200 ease-out"
        style={{ 
          transform: pullDistance > 0 ? `translateY(${pullDistance * 0.3}px)` : undefined,
        }}
      >
        {children}
      </div>
    </div>
  );
};
