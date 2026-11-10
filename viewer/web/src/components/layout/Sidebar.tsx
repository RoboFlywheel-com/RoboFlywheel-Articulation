// SPDX-License-Identifier: Apache-2.0

import { type JSX, type ReactNode } from "react";

interface SidebarProps {
  children: ReactNode;
}

export function Sidebar({ children }: SidebarProps): JSX.Element {
  return (
    <aside className="relative z-10 flex h-full min-w-0 flex-col overflow-x-visible overflow-y-hidden bg-[var(--surface-0)]">
      {children}
    </aside>
  );
}
