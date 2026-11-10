// SPDX-License-Identifier: Apache-2.0

import { type JSX } from "react";
import { Search } from "lucide-react";

import { useViewer, useViewerDispatch } from "@/lib/viewer-context";
import { Input } from "@/components/ui/input";

interface RecordSearchProps {
  placeholder?: string;
}

export function RecordSearch({
  placeholder = "Search records…",
}: RecordSearchProps): JSX.Element {
  const { searchQuery } = useViewer();
  const dispatch = useViewerDispatch();

  return (
    <div className="relative">
      <Search className="absolute left-2.5 top-1/2 size-3.5 -translate-y-1/2 text-[var(--text-quaternary)]" />
      <Input
        type="text"
        placeholder={placeholder}
        value={searchQuery}
        onChange={(e) => dispatch({ type: "SET_SEARCH", payload: e.target.value })}
        className="h-8 pl-8 text-[12px]"
      />
    </div>
  );
}
