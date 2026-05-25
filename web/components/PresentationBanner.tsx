"use client";

import { Presentation } from "lucide-react";

export function PresentationBanner() {
  return (
    <div className="fixed bottom-4 left-4 right-4 md:left-auto md:right-6 md:max-w-sm z-40">
      <div className="glass rounded-2xl px-4 py-3 flex items-center gap-3 shadow-card border-mint/20">
        <Presentation className="h-5 w-5 text-mint shrink-0" />
        <p className="text-xs text-muted leading-snug">
          <span className="text-white font-medium">Presentation tip:</span> Start at
          Overview → Pipeline → Key findings → Gene map. All numbers are from your
          live NCBI run.
        </p>
      </div>
    </div>
  );
}
