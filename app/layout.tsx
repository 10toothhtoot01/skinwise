import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "Skinwise — Your beauty workspace",
  description: "Plan from your owned kit, compare optional YouCam previews, keep a chosen plan and record your own observations.",
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
