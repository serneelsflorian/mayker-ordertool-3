import { TEXT } from '../config/constants';

export function EmptyState() {
  return (
    <div
      data-testid="menu-list-empty"
      className="flex items-center justify-center rounded-lg border-2 border-dashed border-gray-200 p-8 text-center"
    >
      <p className="text-sm text-gray-500">{TEXT.EMPTY_MENU}</p>
    </div>
  );
}
