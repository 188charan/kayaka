/**
 * Static demo data for the Phase 1 visual shell. None of this is fetched or persisted — the real
 * tenant/product/metric APIs arrive in later phases. Kept in src/lib so every surface can share it
 * without crossing the route-group import boundary (ADR 0001).
 */

export type DemoProduct = {
  id: string;
  name: string;
  category: string;
  price: number;
  compareAtPrice?: number;
  badge?: "New" | "Bestseller" | "Low stock";
  rating: number;
};

export const DEMO_STORE = {
  slug: "demo-store",
  name: "Anjali Jewellery & Décor",
  tagline: "Handcrafted jewellery and home décor, made to order in Jaipur.",
  location: "Jaipur, India",
  whatsapp: "+91 90000 00001",
} as const;

export const DEMO_CATEGORIES = [
  "All",
  "Earrings",
  "Necklaces",
  "Bracelets",
  "Pendants",
  "Hair accessories",
] as const;

export const DEMO_PRODUCTS: DemoProduct[] = [
  {
    id: "gold-pearl-jhumka",
    name: "Gold Pearl Jhumka",
    category: "Earrings",
    price: 2499,
    compareAtPrice: 2999,
    badge: "Bestseller",
    rating: 4.8,
  },
  {
    id: "minimal-stone-necklace",
    name: "Minimal Stone Necklace",
    category: "Necklaces",
    price: 3299,
    badge: "New",
    rating: 4.6,
  },
  {
    id: "rose-gold-bracelet",
    name: "Rose Gold Bracelet",
    category: "Bracelets",
    price: 1899,
    compareAtPrice: 2299,
    rating: 4.7,
  },
  {
    id: "handcrafted-earrings",
    name: "Handcrafted Earrings",
    category: "Earrings",
    price: 1499,
    rating: 4.5,
  },
  {
    id: "temple-pendant",
    name: "Temple Pendant",
    category: "Pendants",
    price: 2799,
    badge: "Low stock",
    rating: 4.9,
  },
  {
    id: "pearl-hair-accessories",
    name: "Pearl Hair Accessories",
    category: "Hair accessories",
    price: 999,
    compareAtPrice: 1299,
    rating: 4.4,
  },
];

/** INR formatting for demo prices. */
export function formatPrice(value: number): string {
  return new Intl.NumberFormat("en-IN", {
    style: "currency",
    currency: "INR",
    maximumFractionDigits: 0,
  }).format(value);
}

export type DemoMetric = {
  key: string;
  label: string;
  value: string;
  delta?: string;
  trend?: "up" | "down" | "flat";
};

export const DASHBOARD_METRICS: DemoMetric[] = [
  { key: "products", label: "Products", value: "128", delta: "+6 this week", trend: "up" },
  { key: "views", label: "Store views", value: "2,430", delta: "+18%", trend: "up" },
  { key: "inquiries", label: "Inquiries", value: "37", delta: "+4", trend: "up" },
  { key: "handoffs", label: "WhatsApp handoffs", value: "24", delta: "+2", trend: "up" },
];

export const ADMIN_METRICS: DemoMetric[] = [
  { key: "tenants", label: "Tenants", value: "24", delta: "+3 this month", trend: "up" },
  { key: "active", label: "Active tenants", value: "19", delta: "79% active", trend: "flat" },
  { key: "products", label: "Products", value: "3,842", delta: "+211", trend: "up" },
  { key: "inquiries-7d", label: "Inquiries (7d)", value: "612", delta: "+9%", trend: "up" },
];

export const DASHBOARD_ACTIVITY = [
  { id: 1, text: "New inquiry on Gold Pearl Jhumka", time: "12 min ago" },
  { id: 2, text: "Minimal Stone Necklace viewed 40 times today", time: "1 hr ago" },
  { id: 3, text: "Rose Gold Bracelet stock updated to 8", time: "3 hrs ago" },
  { id: 4, text: "Temple Pendant shared to WhatsApp status", time: "Yesterday" },
];

export const DASHBOARD_SETUP = [
  { id: "profile", label: "Add your store profile", done: true },
  { id: "products", label: "Add your first 5 products", done: true },
  { id: "whatsapp", label: "Connect WhatsApp number", done: true },
  { id: "theme", label: "Customize storefront theme", done: false },
  { id: "share", label: "Share your store link", done: false },
];

export const ADMIN_RECENT_TENANTS = [
  { id: 1, name: "Anjali Jewellery & Décor", plan: "Growth", status: "Active", joined: "2d ago" },
  { id: 2, name: "Meera Handlooms", plan: "Starter", status: "Active", joined: "4d ago" },
  { id: 3, name: "Urban Clay Studio", plan: "Growth", status: "Active", joined: "6d ago" },
  { id: 4, name: "The Spice Pantry", plan: "Starter", status: "Trial", joined: "1w ago" },
  { id: 5, name: "Nova Sneakers", plan: "Growth", status: "Suspended", joined: "2w ago" },
];

export const ADMIN_HEALTH = [
  { id: "api", label: "API", status: "Operational", detail: "p95 142ms" },
  { id: "db", label: "Database", status: "Operational", detail: "12% load" },
  { id: "jobs", label: "Background jobs", status: "Operational", detail: "0 queued" },
  { id: "storage", label: "Media storage", status: "Degraded", detail: "elevated latency" },
];

export const ADMIN_AUDIT = [
  { id: 1, actor: "Charan", action: "Reactivated tenant Nova Sneakers", time: "08:42" },
  { id: 2, actor: "system", action: "Nightly backup completed", time: "03:00" },
  { id: 3, actor: "Anjali", action: "Updated store profile", time: "Yesterday" },
];
