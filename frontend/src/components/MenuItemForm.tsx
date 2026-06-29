import { useState, type FormEvent } from 'react';
import { Button } from '../ui/button';
import { Input } from '../ui/input';
import { Plus } from '../icons';
import { TEXT } from '../config/constants';
import type { MenuItemCreate } from '../api/types';

interface MenuItemFormProps {
  onAdd: (item: MenuItemCreate) => Promise<void>;
  isSubmitting?: boolean;
}

interface FormErrors {
  name?: string;
  price?: string;
}

function validatePrice(value: string): string | undefined {
  if (value === '' || value === undefined) {
    return undefined;
  }
  const num = parseFloat(value);
  if (isNaN(num)) {
    return 'Price must be a number';
  }
  if (num <= 0) {
    return 'Price must be greater than 0';
  }
  const decimalPart = value.split('.')[1];
  if (decimalPart && decimalPart.length > 2) {
    return 'Price must have at most 2 decimal places';
  }
  return undefined;
}

export function MenuItemForm({ onAdd, isSubmitting = false }: MenuItemFormProps) {
  const [name, setName] = useState('');
  const [price, setPrice] = useState('');
  const [category, setCategory] = useState('');
  const [errors, setErrors] = useState<FormErrors>({});

  function validate(): FormErrors {
    const newErrors: FormErrors = {};
    if (!name.trim()) {
      newErrors.name = 'Name is required';
    }
    const priceError = validatePrice(price);
    if (priceError) {
      newErrors.price = priceError;
    }
    return newErrors;
  }

  async function handleSubmit(e: FormEvent) {
    e.preventDefault();
    const validationErrors = validate();
    if (Object.keys(validationErrors).length > 0) {
      setErrors(validationErrors);
      return;
    }
    setErrors({});

    const payload: MenuItemCreate = {
      name: name.trim(),
      price: price.trim() !== '' ? price.trim() : null,
      category: category.trim() !== '' ? category.trim() : null,
    };

    await onAdd(payload);
    setName('');
    setPrice('');
    setCategory('');
  }

  return (
    <form onSubmit={(e) => { void handleSubmit(e); }} className="space-y-3" noValidate>
      <div>
        <Input
          data-testid="menuitemform-name"
          type="text"
          placeholder={TEXT.NAME_PLACEHOLDER}
          value={name}
          onChange={(e) => setName(e.target.value)}
          hasError={!!errors.name}
          aria-label="Item name"
          aria-describedby={errors.name ? 'menuitemform-name-error' : undefined}
        />
        {errors.name && (
          <p
            id="menuitemform-name-error"
            data-testid="menuitemform-name-error"
            className="mt-1 text-xs text-brand-coral"
            role="alert"
          >
            {errors.name}
          </p>
        )}
      </div>

      <div className="flex gap-2">
        <div className="flex-1">
          <Input
            data-testid="menuitemform-price"
            type="text"
            inputMode="decimal"
            placeholder={TEXT.PRICE_PLACEHOLDER}
            value={price}
            onChange={(e) => setPrice(e.target.value)}
            hasError={!!errors.price}
            aria-label="Price (optional)"
            aria-describedby={errors.price ? 'menuitemform-price-error' : undefined}
          />
          {errors.price && (
            <p
              id="menuitemform-price-error"
              data-testid="menuitemform-price-error"
              className="mt-1 text-xs text-brand-coral"
              role="alert"
            >
              {errors.price}
            </p>
          )}
        </div>

        <div className="flex-1">
          <Input
            data-testid="menuitemform-category"
            type="text"
            placeholder={TEXT.CATEGORY_PLACEHOLDER}
            value={category}
            onChange={(e) => setCategory(e.target.value)}
            aria-label="Category (optional)"
          />
        </div>
      </div>

      <Button
        type="submit"
        data-testid="menuitemform-add"
        disabled={isSubmitting}
        className="w-full sm:w-auto"
      >
        <Plus className="h-4 w-4" aria-hidden="true" />
        {TEXT.ADD_MENU_ITEM}
      </Button>
    </form>
  );
}
