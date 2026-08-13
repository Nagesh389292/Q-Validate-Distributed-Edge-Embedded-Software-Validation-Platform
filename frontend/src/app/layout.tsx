import './globals.css';
import QueryProvider from '@/providers/QueryProvider';
import AppShell from '@/components/AppShell';

export const metadata = {
  title: 'Q-Validate — Enterprise Embedded Validation Platform',
  description: 'Enterprise Validation Command Center for Simulated Edge/Embedded Software',
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body className="bg-[#0b0f19] text-gray-100 antialiased min-h-screen">
        <QueryProvider>
          <AppShell>
            {children}
          </AppShell>
        </QueryProvider>
      </body>
    </html>
  );
}
