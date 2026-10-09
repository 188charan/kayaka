import Link from "next/link";
import { Suspense } from "react";

import { ApiStatus } from "@/components/shared/api-status";
import { BrandMark } from "@/components/shared/brand-mark";
import {
  ArrowRightIcon,
  BagIcon,
  ChartIcon,
  CheckIcon,
  SearchIcon,
  SparkleIcon,
  StoreIcon,
  WhatsAppIcon,
} from "@/components/shared/icons";
import { ProductCard } from "@/components/shared/product-card";
import { StatusBadge } from "@/components/shared/status-badge";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { DEMO_PRODUCTS, DEMO_STORE } from "@/lib/demo-data";

const STEPS = [
  {
    icon: StoreIcon,
    title: "Set up your store",
    body: "Add your products, categories and brand in minutes. Your store gets its own link.",
  },
  {
    icon: SearchIcon,
    title: "Customers browse & search",
    body: "A fast, mobile-first storefront your customers can browse, search and save from.",
  },
  {
    icon: WhatsAppIcon,
    title: "They inquire on WhatsApp",
    body: "No checkout friction. Customers send their cart as a WhatsApp inquiry you can close.",
  },
];

const FEATURES = [
  {
    icon: StoreIcon,
    title: "Your own storefront",
    body: "A persistent, searchable store with your branding — not just another social post.",
  },
  {
    icon: BagIcon,
    title: "Cart to inquiry",
    body: "Customers build a cart and hand off to WhatsApp, so you keep the conversation.",
  },
  {
    icon: ChartIcon,
    title: "Insights that matter",
    body: "See views, inquiries and handoffs at a glance to understand what's selling.",
  },
  {
    icon: SparkleIcon,
    title: "Made for small business",
    body: "Plain, friendly tools built for entrepreneurs — no technical setup required.",
  },
];

export default function HomePage() {
  const previewProducts = DEMO_PRODUCTS.slice(0, 4);

  return (
    <div className="flex min-h-dvh flex-col">
      <header className="sticky top-0 z-20 border-b bg-background/80 backdrop-blur">
        <div className="mx-auto flex h-16 max-w-6xl items-center justify-between px-4">
          <h1 className="text-lg">
            <BrandMark label="Kayaka" />
          </h1>
          <nav aria-label="Surfaces" className="flex items-center gap-1 sm:gap-2">
            <Button asChild variant="ghost" size="sm" className="hidden sm:inline-flex">
              <Link href="/store/demo-store">Demo store</Link>
            </Button>
            <Button asChild variant="ghost" size="sm">
              <Link href="/login">Sign in</Link>
            </Button>
            <Button asChild size="sm">
              <Link href="/dashboard">
                Open dashboard
                <ArrowRightIcon className="size-4" />
              </Link>
            </Button>
          </nav>
        </div>
      </header>

      <main className="flex-1">
        {/* Hero */}
        <section className="relative overflow-hidden border-b">
          <div
            aria-hidden="true"
            className="pointer-events-none absolute inset-0 -z-10 bg-[radial-gradient(60%_60%_at_80%_-10%,var(--brand)_0%,transparent_55%)] opacity-15"
          />
          <div className="mx-auto grid max-w-6xl items-center gap-12 px-4 py-16 md:grid-cols-2 md:py-24">
            <div className="animate-rise space-y-6">
              <Badge variant="brand">
                <SparkleIcon className="size-3" />
                WhatsApp-first commerce
              </Badge>
              <p className="text-4xl font-semibold leading-[1.08] tracking-tight md:text-5xl">
                Your own online store for your business.
              </p>
              <p className="max-w-md text-lg text-muted-foreground">
                Kayaka gives small businesses a persistent, searchable storefront. Customers browse,
                add to cart, and send an inquiry on WhatsApp — no checkout required.
              </p>
              <div className="flex flex-col gap-3 sm:flex-row">
                <Button asChild size="lg">
                  <Link href={`/store/${DEMO_STORE.slug}`}>
                    Explore the demo store
                    <ArrowRightIcon className="size-4" />
                  </Link>
                </Button>
                <Button asChild size="lg" variant="outline">
                  <Link href="/dashboard">See the dashboard</Link>
                </Button>
              </div>
              <Suspense fallback={<StatusBadge status="loading" label="Checking API…" />}>
                <ApiStatus />
              </Suspense>
            </div>

            {/* Store preview */}
            <div className="animate-rise">
              <Card className="overflow-hidden p-0 shadow-lg">
                <div className="flex items-center justify-between gap-2 border-b bg-muted/40 px-4 py-3">
                  <div className="flex items-center gap-2">
                    <StoreIcon className="size-4 text-brand" />
                    <span className="text-sm font-medium">{DEMO_STORE.name}</span>
                  </div>
                  <span className="flex items-center gap-1 text-xs text-muted-foreground">
                    <SearchIcon className="size-3.5" />
                    Search
                  </span>
                </div>
                <div className="grid grid-cols-2 gap-3 p-4">
                  {previewProducts.map((product) => (
                    <ProductCard key={product.id} product={product} />
                  ))}
                </div>
              </Card>
            </div>
          </div>
        </section>

        {/* How Kayaka works */}
        <section className="mx-auto max-w-6xl px-4 py-16 md:py-20">
          <div className="max-w-2xl space-y-3">
            <Badge variant="muted">How Kayaka works</Badge>
            <h2 className="text-3xl font-semibold tracking-tight">
              From first visit to WhatsApp inquiry
            </h2>
            <p className="text-muted-foreground">
              The whole journey is built around how small businesses already sell.
            </p>
          </div>
          <ol className="mt-10 grid gap-6 md:grid-cols-3">
            {STEPS.map((step, index) => (
              <li key={step.title}>
                <Card className="h-full gap-4">
                  <div className="flex items-center justify-between px-6">
                    <span className="grid size-10 place-items-center rounded-lg bg-accent text-accent-foreground">
                      <step.icon className="size-5" />
                    </span>
                    <span className="text-sm font-semibold text-muted-foreground">
                      0{index + 1}
                    </span>
                  </div>
                  <div className="space-y-1.5 px-6">
                    <h3 className="font-semibold">{step.title}</h3>
                    <p className="text-sm text-muted-foreground">{step.body}</p>
                  </div>
                </Card>
              </li>
            ))}
          </ol>
        </section>

        {/* Feature highlights */}
        <section className="border-y bg-muted/30">
          <div className="mx-auto max-w-6xl px-4 py-16 md:py-20">
            <div className="max-w-2xl space-y-3">
              <Badge variant="muted">Why Kayaka</Badge>
              <h2 className="text-3xl font-semibold tracking-tight">
                Everything your store needs, nothing it doesn&apos;t
              </h2>
            </div>
            <div className="mt-10 grid gap-6 sm:grid-cols-2 lg:grid-cols-4">
              {FEATURES.map((feature) => (
                <Card key={feature.title} className="h-full gap-3">
                  <div className="px-6">
                    <span className="grid size-10 place-items-center rounded-lg bg-brand/10 text-brand">
                      <feature.icon className="size-5" />
                    </span>
                  </div>
                  <div className="space-y-1.5 px-6">
                    <h3 className="font-semibold">{feature.title}</h3>
                    <p className="text-sm text-muted-foreground">{feature.body}</p>
                  </div>
                </Card>
              ))}
            </div>
          </div>
        </section>

        {/* WhatsApp-first selling concept */}
        <section className="mx-auto max-w-6xl px-4 py-16 md:py-20">
          <Card className="overflow-hidden border-brand/20 bg-gradient-to-br from-brand/5 to-transparent">
            <div className="grid items-center gap-10 p-2 md:grid-cols-2 md:p-6">
              <div className="space-y-5 px-6 md:px-2">
                <span className="grid size-11 place-items-center rounded-xl bg-success/15 text-success">
                  <WhatsAppIcon className="size-6" />
                </span>
                <h2 className="text-2xl font-semibold tracking-tight md:text-3xl">
                  Selling happens where your customers already are
                </h2>
                <p className="text-muted-foreground">
                  Instead of forcing online payments, Kayaka hands the cart off to WhatsApp. You
                  answer questions, confirm details and close the sale in a conversation — exactly
                  how trusted local businesses already work.
                </p>
                <ul className="space-y-2.5">
                  {[
                    "No payment gateway friction for your customers",
                    "Keep every inquiry as a direct conversation",
                    "Works from a phone, built mobile-first",
                  ].map((item) => (
                    <li key={item} className="flex items-start gap-2.5 text-sm">
                      <CheckIcon className="mt-0.5 size-4 shrink-0 text-success" />
                      {item}
                    </li>
                  ))}
                </ul>
              </div>
              <div className="px-6 md:px-2">
                <div className="mx-auto max-w-xs space-y-3">
                  {[
                    { from: "customer", text: "Hi! Is the Gold Pearl Jhumka available?" },
                    { from: "store", text: "Yes! In stock, ships in 2 days. ₹2,499." },
                    { from: "customer", text: "Perfect, I'll take one 😊" },
                  ].map((bubble, index) => (
                    <div
                      key={index}
                      className={
                        bubble.from === "store"
                          ? "ml-auto max-w-[85%] rounded-2xl rounded-br-sm bg-success px-3.5 py-2 text-sm text-success-foreground"
                          : "max-w-[85%] rounded-2xl rounded-bl-sm bg-card px-3.5 py-2 text-sm shadow-xs"
                      }
                    >
                      {bubble.text}
                    </div>
                  ))}
                </div>
              </div>
            </div>
          </Card>
        </section>

        {/* Surfaces CTA */}
        <section className="border-t bg-muted/30">
          <div className="mx-auto max-w-6xl px-4 py-16 md:py-20">
            <div className="max-w-2xl space-y-3">
              <h2 className="text-3xl font-semibold tracking-tight">
                Explore the Phase 1 surfaces
              </h2>
              <p className="text-muted-foreground">
                These are development surfaces for the current walking-skeleton phase. Sign-in,
                roles and real data arrive in later phases.
              </p>
            </div>
            <div className="mt-10 grid gap-6 md:grid-cols-3">
              {[
                {
                  icon: StoreIcon,
                  title: "Demo storefront",
                  body: "A realistic customer-facing store with products, search and WhatsApp inquiry.",
                  href: `/store/${DEMO_STORE.slug}`,
                  cta: "Open storefront",
                },
                {
                  icon: ChartIcon,
                  title: "Tenant dashboard",
                  body: "The entrepreneur's console for managing a store, with a demo overview.",
                  href: "/dashboard",
                  cta: "Open dashboard",
                },
                {
                  icon: StoreIcon,
                  title: "Platform admin",
                  body: "The operations console for running Kayaka across every tenant.",
                  href: "/admin",
                  cta: "Open admin",
                },
              ].map((surface) => (
                <Card key={surface.title} className="group h-full justify-between gap-6">
                  <div className="space-y-3 px-6">
                    <span className="grid size-10 place-items-center rounded-lg bg-accent text-accent-foreground">
                      <surface.icon className="size-5" />
                    </span>
                    <h3 className="font-semibold">{surface.title}</h3>
                    <p className="text-sm text-muted-foreground">{surface.body}</p>
                  </div>
                  <div className="px-6">
                    <Button asChild variant="outline" className="w-full">
                      <Link href={surface.href}>
                        {surface.cta}
                        <ArrowRightIcon className="size-4" />
                      </Link>
                    </Button>
                  </div>
                </Card>
              ))}
            </div>
          </div>
        </section>
      </main>

      <footer className="border-t">
        <div className="mx-auto flex max-w-6xl flex-col items-center justify-between gap-3 px-4 py-8 text-sm text-muted-foreground sm:flex-row">
          <BrandMark label="Kayaka" className="text-foreground" />
          <p>Phase 1 · walking skeleton · demo content only</p>
        </div>
      </footer>
    </div>
  );
}
