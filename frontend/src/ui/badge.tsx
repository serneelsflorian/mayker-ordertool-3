import { type HTMLAttributes } from 'react';
import { cn } from '../lib/utils';

interface BadgeProps extends HTMLAttributes<HTMLSpanElement> {}

export function Badge({ className, children, ...props }: BadgeProps) {
  return (
    <span
      className={cn(
        'inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-medium',
        'bg-brand-bluegrey/20 text-brand-bluegrey',
        className,
      )}
      {...props}
    >
      {children}
    </span>
  );
}
