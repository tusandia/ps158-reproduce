"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";

const TABS = [
  { href: "/", label: "California bills" },
  { href: "/federal/", label: "Federal law" },
  { href: "/news/", label: "News" },
  { href: "/codebook/", label: "Codebook" },
];

export default function Nav() {
  const path = usePathname() || "/";
  const norm = (p) => (p.endsWith("/") ? p : p + "/");
  return (
    <nav className="tabs" aria-label="Sections">
      {TABS.map((t) => (
        <Link key={t.href} href={t.href} aria-current={norm(path) === norm(t.href) ? "page" : undefined}>
          {t.label}
        </Link>
      ))}
    </nav>
  );
}
