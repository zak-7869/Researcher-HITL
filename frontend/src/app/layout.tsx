import type { Metadata } from "next";
import "./globals.css";
export const metadata: Metadata = { title: "Researcher AI", description: "A source-grounded research agent" };
export default function RootLayout({ children }: Readonly<{ children: React.ReactNode }>) {
  return <html lang="en"><body>{children}</body></html>;
}
