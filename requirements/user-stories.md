# User Stories — Ecommerce Playground

> These user stories feed into acceptance criteria in `cart.txt` and `search.txt`.
> The pipeline traces every test result back to these stories automatically.

---

## Epic: Shopping Cart

**As a** shopper
**I want** to manage items in my cart
**So that** I can review and modify my purchase before checkout

| Story | Acceptance Criteria |
|-------|-------------------|
| Add item to cart | AC-001: Cart count updates immediately on product add |
| View cart contents | AC-002: Cart dropdown lists all items with names and prices |
| Remove item from cart | AC-003: Removing an item recalculates the cart total |

---

## Epic: Product Discovery

**As a** shopper
**I want** to find products easily
**So that** I can discover what I want to buy

| Story | Acceptance Criteria |
|-------|-------------------|
| Search by keyword | AC-004: Search returns relevant results for a product name |
| Browse catalog | AC-005: Category page shows product tiles with names and prices |
| View product detail | AC-006: Clicking a tile opens the full detail page |
| Filter by category | AC-007: Applying a filter narrows the displayed products |

---

## Traceability chain

```
Epic → User Story → Acceptance Criterion → Scenario ID → Test Case ID → Test Result
                         AC-001         →    SC-001    →    TC-001    →  passed/failed
```

Every failure in HyperExecute is traceable back to the exact user story that broke.
