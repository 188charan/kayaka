# Demo accounts & personas (local development)

> **These are canonical _local development personas_, not production credentials.**
> As of **Phase 2**, authentication, tenancy, memberships and RBAC are implemented — these
> personas can sign in at `/login` once the demo data is seeded (below). They keep naming, roles
> and permissions consistent across the codebase.
>
> - **No real passwords or secrets** live in this repo. Seed with a password you supply via
>   `KAYAKA_DEMO_PASSWORD`; it is never stored in source. Do not add any.
> - All `@kayaka.local` / `@demo.kayaka.local` emails and the demo phone number are fictional.
> - Frontend visibility is **not** authorization. The **backend** permissions are authoritative
>   (permission-code RBAC + PostgreSQL RLS); the UI only reflects them.

## Current status (Phase 2)

| Capability                 | Status            | Implemented in |
| -------------------------- | ----------------- | -------------- |
| Authentication (login)     | ✅ Implemented (allauth headless, session) | Phase 2 |
| Tenancy (tenant model)     | ✅ Implemented     | Phase 2        |
| Memberships                | ✅ Implemented     | Phase 2        |
| Roles & permissions (RBAC) | ✅ Implemented (permission codes) | Phase 2 |
| Row-level security (RLS)   | ✅ Implemented     | Phase 2        |
| Customer accounts          | ❌ Not needed (MVP uses none) | — |

See [identity-and-tenancy.md](identity-and-tenancy.md) for the full model. Business features
(catalog, inquiries, customers, analytics) are still later phases.

### Seeding and signing in

```bash
docker compose up --build --wait
KAYAKA_DEMO_PASSWORD='change-me-locally' \
  docker compose run --rm -T backend python manage.py seed_demo_data
# then: cd frontend && npm run dev  → sign in at http://localhost:3000/login
```

---

## Platform personas

### Charan — Platform Admin

- **Email:** `admin@kayaka.local`
- **Role:** `PLATFORM_ADMIN`
- **Scope:** Entire Kayaka platform
- **Authentication:** Yes — sign in at /login (Phase 2)
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
- **Authentication:** Yes — sign in at /login (Phase 2)
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
- **Authentication:** Yes — sign in at /login (Phase 2)
- **Intended permissions:** products, categories, inquiries, customers, insights
- **Must NOT have:** platform administration, tenant ownership transfer, destructive platform
  operations

### Sneha — Staff

- **Email:** `staff@demo.kayaka.local`
- **Role:** `STAFF`
- **Tenant:** Anjali Jewellery & Décor
- **Authentication:** Yes — sign in at /login (Phase 2)
- **Intended permissions:** view/manage products, update stock, view/manage inquiries, view
  customers
- **Must NOT have:** team management, tenant configuration, platform administration

### Karthik — Marketing

- **Email:** `marketing@demo.kayaka.local`
- **Role:** `MARKETING`
- **Tenant:** Anjali Jewellery & Décor
- **Authentication:** Yes — sign in at /login (Phase 2)
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

> As of Phase 2 this hierarchy is **implemented and enforced**: the tenant model, memberships,
> platform-role assignments and permission-code RBAC exist, and the backend is the single source
> of truth for authorization. `ANALYST` is reserved and currently grants no permissions.

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
