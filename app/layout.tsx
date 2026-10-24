import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "Skinwise — Inspect your skin analysis",
  description: "Choose a visible concern, inspect actual YouCam detection images and regional detail, and save your interpretation without invented recommendations.",
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
