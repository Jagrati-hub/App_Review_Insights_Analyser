import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "Play Store Review Analyzer",
  description: "Weekly pulse reports from Google Play Store reviews",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body className="bg-gradient-to-br from-primary-500 to-secondary-500 min-h-screen">
        {children}
      </body>
    </html>
  );
}
