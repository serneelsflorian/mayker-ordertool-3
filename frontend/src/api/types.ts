export interface MenuItem {
  id: string;
  name: string;
  price: string | null;
  category: string | null;
}

export interface OrderRead {
  id: string;
  status: string;
  restaurant_name: string;
  menu_items: MenuItem[];
}

export interface OrderCreateResponse {
  id: string;
  status: string;
  restaurant_name: string;
}

export interface MenuItemCreate {
  name: string;
  price?: string | null;
  category?: string | null;
}

export interface ApiError {
  error: {
    code: string;
    message: string;
    details: unknown[];
  };
}
