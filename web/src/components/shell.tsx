"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { AGENTS } from "@/lib/agents";

export function Shell({ children }: { children: React.ReactNode }) {
  const path = usePathname();

  return (
    <div className="min-h-screen">
      <header className="sticky top-0 z-20 border-b border-rule/80 bg-paper/90 backdrop-blur-sm">
        <div className="mx-auto flex max-w-6xl items-center justify-between gap-6 px-5 py-3">
          <Link href="/" className="flex items-baseline gap-3">
            <span className="font-serif text-xl tracking-tight text-ink">AcreOps</span>
            <span className="hidden text-[11px] uppercase tracking-[0.18em] text-ink-soft sm:inline">
              Field desk
            </span>
          </Link>
          <nav className="flex flex-wrap items-center gap-1 text-[13px]">
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
        <div className="mx-auto flex max-w-6xl items-center gap-3 px-5 py-2 text-[12px] text-copper-deep">
          <span className="inline-flex rounded-full bg-copper px-2 py-0.5 font-mono text-[10px] uppercase tracking-[0.14em] text-white">
            Interactive demo
          </span>
          <span>No real SMS, email, signature, permit, schedule, or tenant record is changed.</span>
        </div>
      </div>
      <main className="mx-auto max-w-6xl px-5 py-8">{children}</main>
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
      className={`rounded-full px-3 py-1 transition ${
        active ? "bg-ink text-paper" : "text-ink-soft hover:bg-paper-2 hover:text-ink"
      }`}
    >
      {children}
    </Link>
  );
}
