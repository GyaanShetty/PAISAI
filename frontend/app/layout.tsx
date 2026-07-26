import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "PAISAI — Your AI Financial Operating System",
  description:
    "The most trustworthy AI-powered personal finance platform. If we don't know, we say we don't know.",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body className="min-h-screen bg-ink text-paper antialiased">
        {children}
      </body>
    </html>
  );
}
