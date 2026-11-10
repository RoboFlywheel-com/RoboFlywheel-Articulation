// SPDX-License-Identifier: Apache-2.0

import { useEffect, useState, type JSX } from "react";

import { fetchExportCategories } from "@/lib/api";
import type { ExportCategory } from "@/lib/types";
import { useViewer, useViewerDispatch } from "@/lib/viewer-context";

/**
 * Browses the `articraft template gen-seeds` export tree.
 *
 * Exported seeds are not records: each one is a self-contained folder served
 * under /api/exports/<slug>/<seed>/files, which is all the 3D viewer needs.
 */
export function ExportList(): JSX.Element {
  const { selection } = useViewer();
  const dispatch = useViewerDispatch();
  const [categories, setCategories] = useState<ExportCategory[] | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [collapsed, setCollapsed] = useState<Set<string>>(new Set());

  useEffect(() => {
    let cancelled = false;
    fetchExportCategories()
      .then((data) => {
        if (!cancelled) setCategories(data);
      })
      .catch((exc: unknown) => {
        if (!cancelled) setError(exc instanceof Error ? exc.message : String(exc));
      });
    return () => {
      cancelled = true;
    };
  }, []);

  if (error) {
    return (
      <div className="px-4 py-3">
        <p className="text-[11px] text-[var(--destructive)]">{error}</p>
      </div>
    );
  }

  if (categories === null) {
    return (
      <div className="flex flex-1 items-center justify-center">
        <p className="text-[11px] text-[var(--text-quaternary)]">Loading…</p>
      </div>
    );
  }

  if (categories.length === 0) {
    return (
      <div className="px-4 py-3">
        <p className="text-[11px] text-[var(--text-tertiary)]">No exported seeds.</p>
        <p className="mt-2 text-[10px] leading-relaxed text-[var(--text-quaternary)]">
          Generate some with{" "}
          <code className="text-[var(--text-tertiary)]">
            articraft template gen-seeds &lt;slug&gt; --seeds 0-9 --out &lt;dir&gt;
          </code>
          , then start the viewer with{" "}
          <code className="text-[var(--text-tertiary)]">ARTICRAFT_SEED_EXPORTS=&lt;dir&gt;</code>.
        </p>
      </div>
    );
  }

  const toggle = (slug: string): void => {
    setCollapsed((prev) => {
      const next = new Set(prev);
      if (next.has(slug)) next.delete(slug);
      else next.add(slug);
      return next;
    });
  };

  return (
    <div className="min-h-0 flex-1 overflow-y-auto">
      {categories.map((category) => {
        const isCollapsed = collapsed.has(category.slug);
        return (
          <div key={category.slug} className="border-b border-[var(--border-default)]">
            <button
              type="button"
              onClick={() => toggle(category.slug)}
              className="flex w-full items-center justify-between px-3 py-2 text-left transition-colors duration-150 hover:bg-[var(--bg-hover)]"
            >
              <span className="truncate text-[11px] font-medium text-[var(--text-primary)]">
                {category.slug}
              </span>
              <span className="ml-2 shrink-0 text-[10px] text-[var(--text-tertiary)]">
                {category.seeds.length}
                {category.rejected_count > 0 ? (
                  <span className="ml-1 text-[var(--destructive)]">
                    -{category.rejected_count}
                  </span>
                ) : null}
              </span>
            </button>
            {isCollapsed ? null : (
              <div className="pb-1">
                {category.seeds.map((seed) => {
                  const isSelected =
                    selection?.kind === "export" &&
                    selection.slug === category.slug &&
                    selection.seed === seed;
                  return (
                    <button
                      key={seed}
                      type="button"
                      onClick={() =>
                        dispatch({
                          type: "SELECT_ITEM",
                          payload: { kind: "export", slug: category.slug, seed },
                        })
                      }
                      className={`block w-full px-3 py-1 pl-6 text-left text-[11px] transition-colors duration-150 ${
                        isSelected
                          ? "bg-[var(--bg-selected)] text-[var(--text-primary)]"
                          : "text-[var(--text-secondary)] hover:bg-[var(--bg-hover)]"
                      }`}
                    >
                      seed {seed}
                    </button>
                  );
                })}
              </div>
            )}
          </div>
        );
      })}
    </div>
  );
}
