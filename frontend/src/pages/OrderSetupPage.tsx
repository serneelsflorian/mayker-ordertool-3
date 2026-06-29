import { useParams } from 'react-router-dom';
import { TopBar } from '../components/TopBar';
import { MenuItemForm } from '../components/MenuItemForm';
import { MenuItemList } from '../components/MenuItemList';
import { GenerateLinkSection } from '../components/GenerateLinkSection';
import { Card, CardContent, CardHeader, CardTitle } from '../ui/card';
import { Separator } from '../ui/separator';
import { useOrder } from '../hooks/useOrder';
import { TEXT } from '../config/constants';

export function OrderSetupPage() {
  const { id } = useParams<{ id: string }>();
  const { order, menuItems, addItem, removeItem, loading, error } = useOrder(id ?? '');

  if (loading) {
    return (
      <div className="flex min-h-screen items-center justify-center bg-brand-bg-soft">
        <p className="text-sm text-gray-500">{TEXT.LOADING}</p>
      </div>
    );
  }

  if (error || !order) {
    return (
      <div className="flex min-h-screen items-center justify-center bg-brand-bg-soft p-4">
        <div
          className="rounded-lg border border-brand-coral/30 bg-white p-6 text-center shadow-sm"
          role="alert"
        >
          <p className="text-sm text-brand-coral">{error ?? TEXT.ERROR_LOADING_ORDER}</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-brand-bg-soft">
      <TopBar restaurantName={order.restaurant_name} status={order.status} />
      <main className="mx-auto max-w-3xl px-4 py-6 space-y-6">
        <Card>
          <CardHeader>
            <CardTitle>Menu items</CardTitle>
          </CardHeader>
          <CardContent className="space-y-5">
            <MenuItemForm onAdd={addItem} />
            <Separator />
            <MenuItemList items={menuItems} onRemove={removeItem} />
          </CardContent>
        </Card>

        <GenerateLinkSection menuItemCount={menuItems.length} />
      </main>
    </div>
  );
}
