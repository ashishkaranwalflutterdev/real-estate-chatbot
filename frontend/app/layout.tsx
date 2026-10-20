import type { Metadata } from 'next';
import './globals.css';

export const metadata: Metadata = {
  title: 'Dar Global & Wasalt | Grounded AI Real Estate Assistant',
  description:
    'AI Assistant grounded in official public data from Dar Global (luxury international developments) and Wasalt (Saudi PropTech marketplace). Powered by OpenRouter free models.',
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <head>
        <link rel="preconnect" href="https://fonts.googleapis.com" />
        <link rel="preconnect" href="https://fonts.gstatic.com" crossOrigin="anonymous" />
        <link
          href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700&family=Playfair+Display:wght@600;700&display=swap"
          rel="stylesheet"
        />
      </head>
      <body>{children}</body>
    </html>
  );
}
