import { type HTMLAttributes } from 'react';
import { cn } from '../lib/utils';

interface SeparatorProps extends HTMLAttributes<HTMLHRElement> {}

export function Separator({ className, ...props }: SeparatorProps) {
  return (
    <hr
      className={cn('border-t border-gray-200', className)}
      {...props}
    />
  );
}
