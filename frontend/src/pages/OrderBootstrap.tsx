import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { createOrder } from '../api/orders';
import { TEXT } from '../config/constants';

export function OrderBootstrap() {
  const navigate = useNavigate();
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let cancelled = false;

    async function bootstrap() {
      try {
        const order = await createOrder();
        if (!cancelled) {
          navigate(`/order/${order.id}`, { replace: true });
        }
      } catch (err) {
        if (!cancelled) {
          setError(err instanceof Error ? err.message : TEXT.ERROR_CREATING_ORDER);
        }
      }
    }

    void bootstrap();

    return () => {
      cancelled = true;
    };
  }, [navigate]);

  if (error) {
    return (
      <main className="flex min-h-screen items-center justify-center bg-brand-bg-soft p-4">
        <div
          className="rounded-lg border border-brand-coral/30 bg-white p-6 text-center shadow-sm"
          role="alert"
        >
          <p className="text-sm text-brand-coral">{error}</p>
          <button
            onClick={() => window.location.reload()}
            className="mt-3 text-sm text-brand-teal underline"
          >
            Try again
          </button>
        </div>
      </main>
    );
  }

  return (
    <main className="flex min-h-screen items-center justify-center bg-brand-bg-soft">
      <p className="text-sm text-gray-500">{TEXT.LOADING}</p>
    </main>
  );
}
