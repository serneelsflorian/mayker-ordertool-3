import { useState, useEffect, useCallback } from 'react';
import { getOrder, addMenuItem, removeMenuItem } from '../api/orders';
import type { MenuItem, MenuItemCreate, OrderRead } from '../api/types';

interface UseOrderResult {
  order: OrderRead | null;
  menuItems: MenuItem[];
  addItem: (item: MenuItemCreate) => Promise<void>;
  removeItem: (itemId: string) => Promise<void>;
  loading: boolean;
  error: string | null;
}

export function useOrder(orderId: string): UseOrderResult {
  const [order, setOrder] = useState<OrderRead | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchOrder = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await getOrder(orderId);
      setOrder(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load order');
    } finally {
      setLoading(false);
    }
  }, [orderId]);

  useEffect(() => {
    void fetchOrder();
  }, [fetchOrder]);

  const addItem = useCallback(
    async (item: MenuItemCreate) => {
      const created = await addMenuItem(orderId, item);
      setOrder((prev) => {
        if (!prev) return prev;
        return { ...prev, menu_items: [...prev.menu_items, created] };
      });
    },
    [orderId],
  );

  const removeItem = useCallback(
    async (itemId: string) => {
      await removeMenuItem(orderId, itemId);
      setOrder((prev) => {
        if (!prev) return prev;
        return {
          ...prev,
          menu_items: prev.menu_items.filter((item) => item.id !== itemId),
        };
      });
    },
    [orderId],
  );

  return {
    order,
    menuItems: order?.menu_items ?? [],
    addItem,
    removeItem,
    loading,
    error,
  };
}
