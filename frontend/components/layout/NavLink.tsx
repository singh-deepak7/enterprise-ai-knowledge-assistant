"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";

interface NavLinkProps {
  href: string;
  children: React.ReactNode;
}

export default function NavLink({
  href,
  children,
}: NavLinkProps) {
  const pathname = usePathname();

  const route = href.split("#")[0] || "/";

  const isActive = pathname === route;

  return (
    <Link
      href={href}
      className={`transition ${
        isActive
          ? "font-semibold text-cyan-400"
          : "text-muted-foreground hover:text-foreground"
      }`}
    >
      {children}
    </Link>
  );
}