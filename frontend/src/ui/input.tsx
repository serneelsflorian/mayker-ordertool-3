import { forwardRef, type InputHTMLAttributes } from 'react';
import { cn } from '../lib/utils';

interface InputProps extends InputHTMLAttributes<HTMLInputElement> {
  hasError?: boolean;
}

export const Input = forwardRef<HTMLInputElement, InputProps>(
  ({ hasError, className, ...props }, ref) => {
    return (
      <input
        ref={ref}
        className={cn(
          'block w-full rounded-md border border-gray-300 bg-white px-3 py-2 text-sm',
          'placeholder:text-gray-400',
          'focus:border-brand-teal focus:outline-none focus:ring-1 focus:ring-brand-teal',
          'disabled:cursor-not-allowed disabled:bg-gray-50 disabled:text-gray-500',
          hasError && 'border-brand-coral focus:border-brand-coral focus:ring-brand-coral',
          className,
        )}
        {...props}
      />
    );
  },
);

Input.displayName = 'Input';
