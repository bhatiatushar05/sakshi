import type { Metadata } from "next";
import { Outfit, IBM_Plex_Mono } from "next/font/google";
import "./globals.css";

const outfit = Outfit({
  subsets: ["latin"],
  variable: "--font-outfit",
});

const mono = IBM_Plex_Mono({
  weight: ["400", "500"],
  subsets: ["latin"],
  variable: "--font-mono",
});

export const metadata: Metadata = {
  title: "HIV-1 Evolution India | Subtype C Analysis",
  description:
    "In-silico evolutionary analysis of HIV-1 subtype C sequences from Indian isolates — conservation, hotspots, and phylogenetic insights.",
  openGraph: {
    title: "HIV-1 Evolution India",
    description: "Subtype C in-silico analysis — Life Sciences project",
    type: "website",
  },
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" className={`${outfit.variable} ${mono.variable}`}>
      <body className="font-sans antialiased relative">
        <div className="grid-bg fixed inset-0 -z-10 opacity-40" />
        {children}
      </body>
    </html>
  );
}
