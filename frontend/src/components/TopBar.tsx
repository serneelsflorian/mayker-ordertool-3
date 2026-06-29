import { ShoppingBag } from '../icons';
import { TEXT } from '../config/constants';

interface TopBarProps {
  restaurantName: string;
  status: string;
}

export function TopBar({ restaurantName, status }: TopBarProps) {
  const isOpen = status === 'open';
  const statusLabel = isOpen ? TEXT.ORDER_STATUS_OPEN : TEXT.ORDER_STATUS_CLOSED;

  return (
    <header className="bg-brand-teal text-white shadow-sm">
      <div className="mx-auto max-w-3xl px-4 py-3 flex items-center gap-3">
        <ShoppingBag className="h-6 w-6 flex-shrink-0" aria-hidden="true" />
        <div>
          <p
            className="text-base font-semibold leading-tight"
            data-testid="topbar-restaurant-name"
          >
            {restaurantName}
          </p>
          <p className="text-xs text-white/80 leading-tight">{statusLabel}</p>
        </div>
      </div>
    </header>
  );
}
