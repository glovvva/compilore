import type { LayoutStorage } from "react-resizable-panels";

/** Persists react-resizable-panels layout under the product key (brief: workspace shell). */
export const COMPILORE_PANEL_STATE_KEY = "compilore-panel-state";

/**
 * Adapts the library's internal storage keys to a single localStorage key
 * so operators can clear or inspect `compilore-panel-state` directly.
 */
export function createCompilorePanelStorage(): LayoutStorage {
  return {
    getItem() {
      if (typeof window === "undefined") return null;
      return window.localStorage.getItem(COMPILORE_PANEL_STATE_KEY);
    },
    setItem(_key: string, value: string) {
      if (typeof window === "undefined") return;
      window.localStorage.setItem(COMPILORE_PANEL_STATE_KEY, value);
    },
  };
}
