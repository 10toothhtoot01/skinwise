import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "Skinwise — Your skincare observation journal",
  description: "Record routine changes, comfort notes and photo-based cosmetic estimates, with clear limits on what the scores can establish.",
  icons: {
    icon: "/favicon.svg",
    shortcut: "/favicon.svg",
  },
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body className="antialiased">{children}</body>
    </html>
  );
}
