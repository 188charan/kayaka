# Demo accounts & personas (local development)

> **These are canonical _local development personas_, not production credentials.**
> Phase 1 has **no authentication, no roles, and no tenancy** — none of these accounts can
> actually sign in yet. They exist to keep naming, roles and intended permissions consistent as
> we build identity, access and tenancy in **Phase 2**.
>
> - **No real passwords or secrets** live in this repo. Do not add any.
> - All `@kayaka.local` / `@demo.kayaka.local` emails and the demo phone number are fictional.
> - Frontend visibility is **not** authorization. When RBAC lands in Phase 2, the **backend**
>   permissions are authoritative; the Phase 1 UI only establishes the visual surfaces.

## Current status (Phase 1)

| Capability                 | Status in Phase 1 | Arrives in |
| -------------------------- | ----------------- | ---------- |
| Authentication (login)     | ❌ Not implemented | Phase 2    |
| Tenancy (tenant model)     | ❌ Not implemented | Phase 2    |
| Memberships                | ❌ Not implemented | Phase 2    |
| Roles & permissions (RBAC) | ❌ Not implemented | Phase 2    |
| Customer accounts          | ❌ Not needed (MVP uses none) | — |

Today there is exactly one user table (`accounts.User`) and no tenant tables. The surfaces at
`/`, `/store/demo-store`, `/dashboard` and `/admin` are **visual shells with demo data only**.

---

## Platform personas

### Charan — Platform Admin

- **Email:** `admin@kayaka.local`
- **Role:** `PLATFORM_ADMIN`
- **Scope:** Entire Kayaka platform
- **Authentication:** None yet (Phase 2)
- **Intended permissions:**
  - View tenants
  - Create / invite tenants
  - Suspend / reactivate tenants
  - View platform metrics
  - View platform health
  - View audit logs
  - Platform support operations
  - Manage platform configuration

---

## Tenant personas — _Anjali Jewellery & Décor_

All four below belong to the same demo tenant, **Anjali Jewellery & Décor**.

### Anjali — Owner

- **Email:** `owner@demo.kayaka.local`
- **Role:** `OWNER`
- **Tenant:** Anjali Jewellery & Décor
- **Authentication:** None yet (Phase 2)
- **Intended permissions:**
  - Manage store profile
  - Manage products
  - Manage categories
  - Manage inquiries
  - View customers
  - View insights
  - Customize storefront
  - Manage WhatsApp configuration
  - Manage team members

### Rahul — Manager

- **Email:** `manager@demo.kayaka.local`
- **Role:** `MANAGER`
- **Tenant:** Anjali Jewellery & Décor
- **Authentication:** None yet (Phase 2)
- **Intended permissions:** products, categories, inquiries, customers, insights
- **Must NOT have:** platform administration, tenant ownership transfer, destructive platform
  operations

### Sneha — Staff

- **Email:** `staff@demo.kayaka.local`
- **Role:** `STAFF`
- **Tenant:** Anjali Jewellery & Décor
- **Authentication:** None yet (Phase 2)
- **Intended permissions:** view/manage products, update stock, view/manage inquiries, view
  customers
- **Must NOT have:** team management, tenant configuration, platform administration

### Karthik — Marketing

- **Email:** `marketing@demo.kayaka.local`
- **Role:** `MARKETING`
- **Tenant:** Anjali Jewellery & Décor
- **Authentication:** None yet (Phase 2)
- **Intended permissions:** storefront content, featured products, promotional content, insights,
  sharing
- **Note:** This is a **future / MVP+** role. It is documented for consistency and **must not**
  trigger a full RBAC implementation in Phase 1.

---

## Customer persona

### Priya — Customer

- **Phone:** `+91 90000 00001`
- **Role:** `CUSTOMER`
- **Authentication:** **None for MVP.** Customers do not need an account.
- **Customer flow (MVP):**

  ```
  Instagram / WhatsApp
          ↓
  Kayaka storefront
          ↓
  Browse
          ↓
  Search
          ↓
  Product
          ↓
  Cart
          ↓
  WhatsApp inquiry
  ```

The storefront is public and anonymous. Selling happens in a WhatsApp conversation, not through
an online checkout.

---

## Intended role model (implemented in Phase 2)

> This hierarchy is **documentation only** in Phase 1. The roles below are **not** enforced yet.
> Phase 2 implements the tenant model, memberships, and role/permission tables; the backend is
> the single source of truth for authorization.

```
PLATFORM
  PLATFORM_ADMIN
  SUPPORT
  ANALYST (future)

TENANT
  OWNER
  MANAGER
  STAFF
  MARKETING

CUSTOMER
  anonymous storefront visitor
```

### Notes for Phase 2 implementers

- Identity is **global** (one `accounts.User` can belong to several tenants via memberships).
- A user's platform role and tenant role(s) are independent concepts.
- `is_staff` on the Django `User` only grants Django-admin access — it is **not** a platform or
  tenant role and must never be used as one.
- Enforce permissions on the backend (DRF permissions + PostgreSQL row-level security per
  ADR 0002). The frontend may hide UI for a cleaner experience, but hiding is never a security
  boundary.
