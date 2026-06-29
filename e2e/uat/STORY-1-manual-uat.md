# STORY-1 – Manual UAT Script: Admin Starts a Group Order

**Feature:** Admin starts a group order and sets up the menu  
**Pre-conditions:** The full stack (frontend + backend + Postgres) is running via `docker compose up`.  
**Base URL:** http://localhost:5173

---

## AC1 – Application bootstraps and redirects to the order page

- [ ] Open http://localhost:5173 in a browser.
- [ ] Verify that the URL automatically changes to `/order/<uuid>` (e.g. `/order/f47ac10b-58cc-4372-a567-0e02b2c3d479`).
- [ ] Verify that the top bar shows the restaurant name (e.g. "Trattoria Demo").
- [ ] Verify that below the restaurant name the label "Group order · Open" is shown.

---

## AC2 – Admin adds a menu item with price and category

- [ ] On the order setup page, fill in the **Item name** field with `Margherita`.
- [ ] Fill in the **Price** field with `9.99`.
- [ ] Fill in the **Category** field with `Pizza`.
- [ ] Click **Add item**.
- [ ] Verify that a row for "Margherita" appears in the list.
- [ ] Verify that "No menu items yet" message is no longer shown.
- [ ] Refresh the page and verify that the "Margherita" item is still listed (server-persisted).

## AC2 – Admin adds a menu item without a price

- [ ] Fill in the **Item name** field with `House Salad`.
- [ ] Leave the **Price** field blank.
- [ ] Click **Add item**.
- [ ] Verify that a row for "House Salad" appears with no price shown.

---

## AC3 – Validation errors

### Blank item name
- [ ] Leave **Item name** blank and click **Add item**.
- [ ] Verify that an error message appears below the name field.
- [ ] Verify that no item was added to the list.

### Empty price is allowed
- [ ] Fill in **Item name** with `Tiramisu`, leave **Price** blank, click **Add item**.
- [ ] Verify that no price error appears and the item is added.

### Non-numeric price
- [ ] Fill in **Item name** with `Espresso`, fill in **Price** with `abc`, click **Add item**.
- [ ] Verify that an error message appears below the price field.

### Negative price
- [ ] Fill in **Item name** with `Espresso`, fill in **Price** with `-5`, click **Add item**.
- [ ] Verify that an error message appears below the price field.

### Price with more than 2 decimal places
- [ ] Fill in **Item name** with `Espresso`, fill in **Price** with `1.999`, click **Add item**.
- [ ] Verify that an error message appears below the price field.

---

## AC4 – Item row displays all fields correctly

- [ ] Add item: name `Quattro Formaggi`, price `11.50`, category `Pizza`.
- [ ] Verify the row shows `Quattro Formaggi`, `11.50`, and `Pizza` as a badge.
- [ ] Add item: name `House Salad` with no price and no category.
- [ ] Verify the row shows `House Salad` with no price and no badge.

---

## AC5 – Admin removes a menu item

- [ ] Ensure at least one item is in the list.
- [ ] Click the trash/remove icon on any row.
- [ ] Verify the row disappears immediately.
- [ ] Refresh the page and verify the item is gone (persisted server-side).

---

## AC6 – Generate link button state

- [ ] Open a fresh order page with no items.
- [ ] Verify the **Generate share link** button is disabled (greyed out / not clickable).
- [ ] Verify the helper text "Add at least one menu item first." is shown.
- [ ] Add one item.
- [ ] Verify the **Generate share link** button is now enabled (clickable).
- [ ] Verify the helper text is no longer shown.

---

*UAT pass criteria: all checkboxes above are ticked.*
