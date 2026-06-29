import { EmptyState } from './EmptyState';
import { MenuItemRow } from './MenuItemRow';
import type { MenuItem } from '../api/types';

interface MenuItemListProps {
  items: MenuItem[];
  onRemove: (itemId: string) => Promise<void>;
}

export function MenuItemList({ items, onRemove }: MenuItemListProps) {
  if (items.length === 0) {
    return <EmptyState />;
  }

  return (
    <ul className="divide-y divide-gray-100" role="list">
      {items.map((item) => (
        <MenuItemRow key={item.id} item={item} onRemove={onRemove} />
      ))}
    </ul>
  );
}
