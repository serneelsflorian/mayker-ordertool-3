import { test, expect } from '@playwright/test';

/**
 * STORY-1 E2E specs: Admin starts a group order and sets up the menu.
 *
 * These tests require the full stack (frontend + backend + Postgres) to be
 * running. When running locally point BASE_URL to the frontend dev server.
 * In CI, the playwright.config.ts webServer block builds and serves the
 * frontend preview, but the backend must be available at VITE_API_URL.
 */

test.describe('STORY-1: Admin starts a group order', () => {
  test('AC1 – visiting / redirects to /order/:id and shows restaurant name', async ({ page }) => {
    await page.goto('/');
    // Wait for the redirect to /order/:id
    await page.waitForURL(/\/order\/.+/, { timeout: 10000 });
    expect(page.url()).toMatch(/\/order\//);

    // Restaurant name is rendered in the TopBar
    await expect(page.getByTestId('topbar-restaurant-name')).toBeVisible();
    const restaurantName = await page.getByTestId('topbar-restaurant-name').textContent();
    expect(restaurantName).toBeTruthy();
  });

  test('AC2 – admin can add a menu item with price', async ({ page }) => {
    await page.goto('/');
    await page.waitForURL(/\/order\/.+/);

    await page.getByTestId('menuitemform-name').fill('Margherita');
    await page.getByTestId('menuitemform-price').fill('9.99');
    await page.getByTestId('menuitemform-category').fill('Pizza');
    await page.getByTestId('menuitemform-add').click();

    // The item should appear in the list
    await expect(page.locator('[data-testid^="menuitem-row-"]').first()).toBeVisible();
    // Empty state should be gone
    await expect(page.getByTestId('menu-list-empty')).not.toBeVisible();
  });

  test('AC2 – admin can add a menu item without price', async ({ page }) => {
    await page.goto('/');
    await page.waitForURL(/\/order\/.+/);

    await page.getByTestId('menuitemform-name').fill('House Salad');
    await page.getByTestId('menuitemform-add').click();

    await expect(page.locator('[data-testid^="menuitem-row-"]').first()).toBeVisible();
  });

  test('AC3 – blank item name shows validation error', async ({ page }) => {
    await page.goto('/');
    await page.waitForURL(/\/order\/.+/);

    await page.getByTestId('menuitemform-add').click();

    await expect(page.getByTestId('menuitemform-name-error')).toBeVisible();
    const errorText = await page.getByTestId('menuitemform-name-error').textContent();
    expect(errorText).toBeTruthy();
  });

  test('AC3 – empty price is allowed (no error shown)', async ({ page }) => {
    await page.goto('/');
    await page.waitForURL(/\/order\/.+/);

    await page.getByTestId('menuitemform-name').fill('Tiramisu');
    // Leave price empty
    await page.getByTestId('menuitemform-add').click();

    await expect(page.getByTestId('menuitemform-price-error')).not.toBeVisible();
    await expect(page.locator('[data-testid^="menuitem-row-"]').first()).toBeVisible();
  });

  test('AC3 – non-numeric price shows validation error', async ({ page }) => {
    await page.goto('/');
    await page.waitForURL(/\/order\/.+/);

    await page.getByTestId('menuitemform-name').fill('Espresso');
    await page.getByTestId('menuitemform-price').fill('abc');
    await page.getByTestId('menuitemform-add').click();

    await expect(page.getByTestId('menuitemform-price-error')).toBeVisible();
  });

  test('AC4 – item row shows name, price and category', async ({ page }) => {
    await page.goto('/');
    await page.waitForURL(/\/order\/.+/);

    await page.getByTestId('menuitemform-name').fill('Quattro Formaggi');
    await page.getByTestId('menuitemform-price').fill('11.50');
    await page.getByTestId('menuitemform-category').fill('Pizza');
    await page.getByTestId('menuitemform-add').click();

    const row = page.locator('[data-testid^="menuitem-row-"]').first();
    await expect(row).toBeVisible();
    await expect(row).toContainText('Quattro Formaggi');
    await expect(row).toContainText('11.50');
    await expect(row).toContainText('Pizza');
  });

  test('AC5 – admin can remove a menu item', async ({ page }) => {
    await page.goto('/');
    await page.waitForURL(/\/order\/.+/);

    await page.getByTestId('menuitemform-name').fill('Bruschetta');
    await page.getByTestId('menuitemform-add').click();

    const row = page.locator('[data-testid^="menuitem-row-"]').first();
    await expect(row).toBeVisible();

    // Get the item id from the data-testid attribute to click the right remove button
    const rowTestId = await row.getAttribute('data-testid');
    const itemId = rowTestId?.replace('menuitem-row-', '') ?? '';
    await page.getByTestId(`menuitem-remove-${itemId}`).click();

    // Item should be gone; empty state should appear if no other items
    await expect(row).not.toBeVisible({ timeout: 5000 });
  });

  test('AC6 – generate link button is disabled until at least one item exists', async ({ page }) => {
    await page.goto('/');
    await page.waitForURL(/\/order\/.+/);

    // Initially no items → button disabled, helper text shown
    await expect(page.getByTestId('generatelink-button')).toBeDisabled();
    await expect(page.getByTestId('generatelink-helper')).toBeVisible();

    // Add one item
    await page.getByTestId('menuitemform-name').fill('Calzone');
    await page.getByTestId('menuitemform-add').click();
    await expect(page.locator('[data-testid^="menuitem-row-"]').first()).toBeVisible();

    // Button should now be enabled, helper text hidden
    await expect(page.getByTestId('generatelink-button')).toBeEnabled();
    await expect(page.getByTestId('generatelink-helper')).not.toBeVisible();
  });
});
