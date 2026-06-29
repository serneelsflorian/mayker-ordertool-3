import { createBrowserRouter } from 'react-router-dom';
import { OrderBootstrap } from './pages/OrderBootstrap';
import { OrderSetupPage } from './pages/OrderSetupPage';

export const router = createBrowserRouter([
  {
    path: '/',
    element: <OrderBootstrap />,
  },
  {
    path: '/order/:id',
    element: <OrderSetupPage />,
  },
]);
