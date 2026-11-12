import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "ViralClip AI - Automatický generátor Shorts & TikToků",
  description: "Cloudový systém pro automatickou tvorbu virálních YouTube Shorts a TikToků s režimem pro klienty a agresivní monetizací.",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="cs" className="dark">
      <body className="antialiased selection:bg-purple-500 selection:text-white">
        {children}
      </body>
    </html>
  );
}

