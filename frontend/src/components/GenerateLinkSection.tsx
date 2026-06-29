import { Button } from '../ui/button';
import { Link } from '../icons';
import { TEXT } from '../config/constants';

interface GenerateLinkSectionProps {
  menuItemCount: number;
}

export function GenerateLinkSection({ menuItemCount }: GenerateLinkSectionProps) {
  const isDisabled = menuItemCount === 0;

  return (
    <div className="space-y-2">
      <Button
        data-testid="generatelink-button"
        disabled={isDisabled}
        className="w-full sm:w-auto"
        onClick={() => {
          // STORY-2 will implement the actual link generation
        }}
      >
        <Link className="h-4 w-4" aria-hidden="true" />
        {TEXT.GENERATE_LINK}
      </Button>
      {isDisabled && (
        <p
          data-testid="generatelink-helper"
          className="text-xs text-gray-500"
        >
          {TEXT.ADD_ITEM_FIRST}
        </p>
      )}
    </div>
  );
}
