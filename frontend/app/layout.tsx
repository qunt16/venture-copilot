import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "Venture Copilot",
  description: "Chinese entrepreneurship competition business plan workspace",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="zh-CN">
      <body>{children}</body>
    </html>
  );
}
