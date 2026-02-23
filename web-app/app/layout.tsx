import type { Metadata } from 'next';
import './globals.css';

export const metadata: Metadata = {
  title: 'RAG Food - Ask About Foods',
  description: 'Explore cuisines from around the world using AI-powered search',
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body className="bg-light text-dark font-sans">
        {children}
      </body>
    </html>
  );
}
