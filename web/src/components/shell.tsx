"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { AGENTS } from "@/lib/agents";
import { ResetDemoButton } from "@/components/reset-demo";

export function Shell({ children }: { children: React.ReactNode }) {
  const path = usePathname();

  return (
    <div className="min-h-screen">
      <header className="sticky top-0 z-20 border-b border-rule/80 bg-paper/90 backdrop-blur-sm">
        <div className="mx-auto flex max-w-6xl flex-col gap-3 px-4 py-3 sm:px-5">
          <div className="flex items-center justify-between gap-3">
            <Link href="/" className="flex min-w-0 items-baseline gap-3">
              <span className="font-serif text-xl tracking-tight text-ink">AcreOps</span>
              <span className="hidden text-[11px] uppercase tracking-[0.18em] text-ink-soft sm:inline">
                Interview demo
              </span>
            </Link>
            <ResetDemoButton />
          </div>
          <nav className="flex items-center gap-1 overflow-x-auto pb-0.5 text-[13px] [-ms-overflow-style:none] [scrollbar-width:none] [&::-webkit-scrollbar]:hidden">
            <NavLink href="/" active={path === "/"}>
              Desk
            </NavLink>
            {AGENTS.map((agent) => (
              <NavLink key={agent.href} href={agent.href} active={path === agent.href}>
                {agent.name}
              </NavLink>
            ))}
          </nav>
        </div>
      </header>
      <div className="border-b border-copper/25 bg-[#f4dfcf]">
        <div className="mx-auto flex max-w-6xl flex-col gap-1 px-4 py-2 text-[12px] text-copper-deep sm:flex-row sm:items-center sm:gap-3 sm:px-5">
          <span className="inline-flex w-fit rounded-full bg-copper px-2 py-0.5 font-mono text-[10px] uppercase tracking-[0.14em] text-white">
            Simulated demo
          </span>
          <span>
            No real email, SMS, PandaDoc, Airtable, Notion, or vendor dispatch is performed.
          </span>
        </div>
      </div>
      <main className="mx-auto max-w-6xl px-4 py-6 sm:px-5 sm:py-8">{children}</main>
    </div>
  );
}

function NavLink({
  href,
  active,
  children,
}: {
  href: string;
  active: boolean;
  children: React.ReactNode;
}) {
  return (
    <Link
      href={href}
      className={`shrink-0 rounded-full px-3 py-1 transition ${
        active ? "bg-ink text-paper" : "text-ink-soft hover:bg-paper-2 hover:text-ink"
      }`}
    >
      {children}
    </Link>
  );
}
