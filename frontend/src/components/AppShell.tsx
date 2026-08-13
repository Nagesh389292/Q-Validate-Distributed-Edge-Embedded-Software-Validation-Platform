'use client';

import React, { useState } from 'react';
import Sidebar from './Sidebar';
import TopBar from './TopBar';
import CommandPalette from './CommandPalette';

interface AppShellProps {
  children: React.ReactNode;
}

export default function AppShell({ children }: AppShellProps) {
  const [cmdOpen, setCmdOpen] = useState<boolean>(false);

  return (
    <div className="flex min-h-screen bg-[#0b0f19] text-gray-100 antialiased font-sans">
      {/* Collapsible Left Sidebar */}
      <Sidebar />

      {/* Main Content Area */}
      <div className="flex-1 flex flex-col min-w-0">
        {/* Top Header Bar */}
        <TopBar onOpenCommandPalette={() => setCmdOpen(true)} />

        {/* Dynamic Route View */}
        <main className="flex-1 p-6 md:p-8 max-w-[1600px] w-full mx-auto">
          {children}
        </main>

        {/* Footer */}
        <footer className="border-t border-gray-800/60 py-4 px-8 text-center text-xs font-mono text-gray-500 bg-[#090d16]">
          Q-Validate Enterprise Embedded & Cloud-Edge Software Validation Platform &bull; Qualcomm Systems Engineering Reference Architecture
        </footer>
      </div>

      {/* Global Command Palette */}
      <CommandPalette isOpen={cmdOpen} onClose={() => setCmdOpen(false)} />
    </div>
  );
}
