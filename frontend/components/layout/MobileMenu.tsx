"use client";

import { useState } from "react";
import Link from "next/link";
import { Menu, X } from "lucide-react";

import ThemeToggle from "@/components/common/ThemeToggle";

const links = [
  {
    name: "Home",
    href: "/",
  },
  {
    name: "Features",
    href: "/#features",
  },
  {
    name: "Architecture",
    href: "/#architecture",
  },
  {
    name: "GitHub",
    href: "https://github.com/singh-deepak7/enterprise-ai-knowledge-assistant",
  },
];

export default function MobileMenu() {
  const [open, setOpen] = useState(false);

  return (
    <div className="md:hidden">
      {/* Menu Button */}
      <button
        onClick={() => setOpen(!open)}
        aria-label="Toggle navigation menu"
        className="rounded-lg p-2 transition hover:bg-accent"
      >
        {open ? <X size={24} /> : <Menu size={24} />}
      </button>

      {/* Mobile Drawer */}
      {open && (
        <div className="absolute left-0 top-16 w-full border-b border-border bg-background/95 backdrop-blur-md shadow-lg">
          <div className="flex flex-col gap-6 p-6">

            {links.map((link) =>
              link.href.startsWith("http") ? (
                <a
                  key={link.name}
                  href={link.href}
                  target="_blank"
                  rel="noopener noreferrer"
                  onClick={() => setOpen(false)}
                  className="text-lg font-medium text-muted-foreground transition hover:text-foreground"
                >
                  {link.name}
                </a>
              ) : (
                <Link
                  key={link.name}
                  href={link.href}
                  onClick={() => setOpen(false)}
                  className="text-lg font-medium text-muted-foreground transition hover:text-foreground"
                >
                  {link.name}
                </Link>
              )
            )}

            <div className="flex items-center justify-between border-t pt-4">
              <ThemeToggle />

              <Link
  href="/dashboard"
  onClick={() => setOpen(false)}
  className="rounded-lg bg-cyan-500 px-4 py-2 font-medium text-black transition hover:bg-cyan-400"
>
  Launch App
</Link>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}