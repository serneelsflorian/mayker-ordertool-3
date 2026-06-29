import { useState, useEffect, useCallback } from 'react';
import { getOrder, addMenuItem, removeMenuItem } from '../api/orders';
import type { MenuItem, MenuItemCreate, OrderRead } from '../api/types';

interface UseOrderResult {
  order: OrderRead | null;
  menuItems: MenuItem[];
  addItem: (item: MenuItemCreate) => Promise<void>;
  removeItem: (itemId: string) => Promise<void>;
  loading: boolean;
  isSubmitting: boolean;
  error: string | null;
  mutationError: string | null;
}

export function useOrder(orderId: string): UseOrderResult {
  const [order, setOrder] = useState<OrderRead | null>(null);
  const [loading, setLoading] = useState(true);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [mutationError, setMutationError] = useState<string | null>(null);

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
      setMutationError(null);
      setIsSubmitting(true);
      try {
        const created = await addMenuItem(orderId, item);
        setOrder((prev) => {
          if (!prev) return prev;
          return { ...prev, menu_items: [...prev.menu_items, created] };
        });
      } catch (err) {
        setMutationError(err instanceof Error ? err.message : 'Failed to add item');
      } finally {
        setIsSubmitting(false);
      }
    },
    [orderId],
  );

  const removeItem = useCallback(
    async (itemId: string) => {
      setMutationError(null);
      setIsSubmitting(true);
      try {
        await removeMenuItem(orderId, itemId);
        setOrder((prev) => {
          if (!prev) return prev;
          return {
            ...prev,
            menu_items: prev.menu_items.filter((item) => item.id !== itemId),
          };
        });
      } catch (err) {
        setMutationError(err instanceof Error ? err.message : 'Failed to remove item');
      } finally {
        setIsSubmitting(false);
      }
    },
    [orderId],
  );

  return {
    order,
    menuItems: order?.menu_items ?? [],
    addItem,
    removeItem,
    loading,
    isSubmitting,
    error,
    mutationError,
  };
}
