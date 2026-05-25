"use client";

import { useState, useEffect } from "react";
import { Dna, Menu, X } from "lucide-react";
import { motion, AnimatePresence } from "framer-motion";

const LINKS = [
  { href: "#overview", label: "Overview" },
  { href: "#pipeline", label: "Pipeline" },
  { href: "#results", label: "Results" },
  { href: "#genes", label: "Genes" },
  { href: "#downloads", label: "Downloads" },
  { href: "#about", label: "About" },
];

export function Navbar() {
  const [open, setOpen] = useState(false);
  const [scrolled, setScrolled] = useState(false);

  useEffect(() => {
    const onScroll = () => setScrolled(window.scrollY > 24);
    window.addEventListener("scroll", onScroll);
    return () => window.removeEventListener("scroll", onScroll);
  }, []);

  return (
    <header
      className={`fixed top-0 left-0 right-0 z-50 transition-all duration-300 ${
        scrolled ? "glass shadow-card py-3" : "py-5 bg-transparent"
      }`}
    >
      <nav className="mx-auto flex max-w-6xl items-center justify-between px-4 md:px-6">
        <a href="#" className="flex items-center gap-2.5 group">
          <span className="flex h-10 w-10 items-center justify-center rounded-xl bg-mint/15 text-mint ring-1 ring-mint/30 group-hover:shadow-glow transition-shadow">
            <Dna className="h-5 w-5" />
          </span>
          <div>
            <p className="font-semibold text-white text-sm leading-tight">
              HIV-1 India
            </p>
            <p className="text-[11px] text-muted font-mono">Subtype C · In-silico</p>
          </div>
        </a>

        <ul className="hidden md:flex items-center gap-1">
          {LINKS.map((l) => (
            <li key={l.href}>
              <a
                href={l.href}
                className="px-3 py-2 text-sm text-muted hover:text-mint rounded-lg transition-colors"
              >
                {l.label}
              </a>
            </li>
          ))}
        </ul>

        <a
          href="#results"
          className="hidden md:inline-flex items-center rounded-full bg-mint/90 px-4 py-2 text-sm font-medium text-canvas hover:bg-mint transition-colors"
        >
          View findings
        </a>

        <button
          type="button"
          className="md:hidden p-2 text-muted"
          onClick={() => setOpen(!open)}
          aria-label="Menu"
        >
          {open ? <X /> : <Menu />}
        </button>
      </nav>

      <AnimatePresence>
        {open && (
          <motion.div
            initial={{ opacity: 0, height: 0 }}
            animate={{ opacity: 1, height: "auto" }}
            exit={{ opacity: 0, height: 0 }}
            className="md:hidden glass border-t border-border mx-4 mt-2 rounded-2xl overflow-hidden"
          >
            <ul className="p-3 space-y-1">
              {LINKS.map((l) => (
                <li key={l.href}>
                  <a
                    href={l.href}
                    onClick={() => setOpen(false)}
                    className="block px-4 py-3 rounded-xl text-sm hover:bg-white/5"
                  >
                    {l.label}
                  </a>
                </li>
              ))}
            </ul>
          </motion.div>
        )}
      </AnimatePresence>
    </header>
  );
}
