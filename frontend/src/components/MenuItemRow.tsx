import { Button } from '../ui/button';
import { Badge } from '../ui/badge';
import { Trash2 } from '../icons';
import type { MenuItem } from '../api/types';

interface MenuItemRowProps {
  item: MenuItem;
  onRemove: (itemId: string) => Promise<void>;
}

export function MenuItemRow({ item, onRemove }: MenuItemRowProps) {
  return (
    <li
      data-testid={`menuitem-row-${item.id}`}
      className="flex items-center justify-between gap-3 py-3"
    >
      <div className="flex flex-wrap items-center gap-2 min-w-0">
        <span className="text-sm font-medium text-gray-900 truncate">{item.name}</span>
        {item.price !== null && item.price !== undefined && (
          <span className="text-sm text-gray-600 flex-shrink-0">€{item.price}</span>
        )}
        {item.category && (
          <Badge>{item.category}</Badge>
        )}
      </div>

      <Button
        variant="ghost"
        size="sm"
        data-testid={`menuitem-remove-${item.id}`}
        aria-label={`Remove ${item.name}`}
        onClick={() => { void onRemove(item.id); }}
        className="flex-shrink-0 text-gray-400 hover:text-brand-coral"
      >
        <Trash2 className="h-4 w-4" aria-hidden="true" />
      </Button>
    </li>
  );
}
