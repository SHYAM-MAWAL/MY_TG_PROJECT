import type { Metadata } from 'next';
import './globals.css';

export const metadata: Metadata = {
  title: 'SHYAMAI Learning Hub',
  description: 'Learn. Build. Grow. — SHYAMAI Learning Hub',
  openGraph: {
    title: 'SHYAMAI Learning Hub',
    description: 'Learn. Build. Grow.',
    type: 'website',
  },
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body className="min-h-screen antialiased">{children}</body>
    </html>
  );
}
