export const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

export const TEXT = {
  APP_NAME: 'Mayker Order Tool',
  ORDER_STATUS_OPEN: 'Group order · Open',
  ORDER_STATUS_CLOSED: 'Group order · Closed',
  ADD_MENU_ITEM: 'Add item',
  REMOVE_MENU_ITEM: 'Remove',
  GENERATE_LINK: 'Generate share link',
  EMPTY_MENU: 'No menu items yet. Add your first item above.',
  ADD_ITEM_FIRST: 'Add at least one menu item first.',
  LOADING: 'Loading…',
  ERROR_CREATING_ORDER: 'Failed to create order. Please try again.',
  ERROR_LOADING_ORDER: 'Failed to load order.',
  NAME_PLACEHOLDER: 'Item name',
  PRICE_PLACEHOLDER: 'Price (optional)',
  CATEGORY_PLACEHOLDER: 'Category (optional)',
} as const;
