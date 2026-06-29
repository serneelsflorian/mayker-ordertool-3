import { apiFetch } from './client';
import type { MenuItemCreate, MenuItem, OrderCreateResponse, OrderRead } from './types';

export async function createOrder(): Promise<OrderCreateResponse> {
  return apiFetch<OrderCreateResponse>('/api/orders', { method: 'POST' });
}

export async function getOrder(id: string): Promise<OrderRead> {
  return apiFetch<OrderRead>(`/api/orders/${id}`);
}

export async function addMenuItem(orderId: string, item: MenuItemCreate): Promise<MenuItem> {
  return apiFetch<MenuItem>(`/api/orders/${orderId}/menu-items`, {
    method: 'POST',
    body: JSON.stringify(item),
  });
}

export async function removeMenuItem(orderId: string, itemId: string): Promise<void> {
  return apiFetch<void>(`/api/orders/${orderId}/menu-items/${itemId}`, {
    method: 'DELETE',
  });
}
