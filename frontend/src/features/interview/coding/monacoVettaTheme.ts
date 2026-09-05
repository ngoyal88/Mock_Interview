import type { Monaco } from "@monaco-editor/react";

export const VETTA_MONACO_THEME = "vetta-dark";

let themeReady = false;

/**
 * Monaco's theme API requires concrete #RRGGBB[AA] strings (no CSS vars).
 * Fallbacks mirror DESIGN.md / index.css :root — lasting hex exception (see project rules).
 * When the document is available, prefer live computed tokens so theme tracks palette changes.
 */
const FALLBACK = {
  surfaceLowest: "#060e20",
  onSurface: "#dae2fd",
  outlineVariant: "#424754",
  primary: "#adc6ff",
  surfaceLow: "#131b2e",
  primaryContainer: "#4d8eff",
  surfaceHigh: "#222a3d",
  secondary: "#4fdbc8",
  success: "#4edea3",
  warning: "#e8a941",
  primaryFixed: "#d8e2ff",
  outline: "#8c909f",
  comment: "#6a7388",
} as const;

function cssVar(name: string, fallback: string): string {
  if (typeof document === "undefined") return fallback;
  const raw = getComputedStyle(document.documentElement).getPropertyValue(name).trim();
  if (!raw) return fallback;
  // Monaco wants #hex; computed values are often rgb()/rgba().
  const rgb = raw.match(/^rgba?\(\s*([\d.]+)\s*,\s*([\d.]+)\s*,\s*([\d.]+)(?:\s*,\s*([\d.]+))?\s*\)$/i);
  if (!rgb) return raw.startsWith("#") ? raw : fallback;
  const r = Math.round(Number(rgb[1]));
  const g = Math.round(Number(rgb[2]));
  const b = Math.round(Number(rgb[3]));
  const a = rgb[4] === undefined ? 1 : Number(rgb[4]);
  const hex = (n: number) => n.toString(16).padStart(2, "0");
  if (a >= 1) return `#${hex(r)}${hex(g)}${hex(b)}`;
  return `#${hex(r)}${hex(g)}${hex(b)}${hex(Math.round(a * 255))}`;
}

function withAlpha(hex: string, alphaHex: string): string {
  const base = hex.replace("#", "").slice(0, 6);
  return `#${base}${alphaHex}`;
}

export function defineVettaMonacoTheme(monaco: Monaco): void {
  if (themeReady) return;

  const surfaceLowest = cssVar("--color-surface-container-lowest", FALLBACK.surfaceLowest);
  const onSurface = cssVar("--color-on-surface", FALLBACK.onSurface);
  const outlineVariant = cssVar("--color-outline-variant", FALLBACK.outlineVariant);
  const primary = cssVar("--color-primary", FALLBACK.primary);
  const surfaceLow = cssVar("--color-surface-container-low", FALLBACK.surfaceLow);
  const primaryContainer = cssVar("--color-primary-container", FALLBACK.primaryContainer);
  const surfaceHigh = cssVar("--color-surface-container-high", FALLBACK.surfaceHigh);
  const secondary = cssVar("--color-secondary", FALLBACK.secondary);
  const success = cssVar("--color-success", FALLBACK.success);
  const warning = cssVar("--color-warning", FALLBACK.warning);
  const primaryFixed = cssVar("--color-primary-fixed", FALLBACK.primaryFixed);
  const outline = cssVar("--color-outline", FALLBACK.outline);

  monaco.editor.defineTheme(VETTA_MONACO_THEME, {
    base: "vs-dark",
    inherit: true,
    rules: [
      { token: "comment", foreground: FALLBACK.comment.replace("#", ""), fontStyle: "italic" },
      { token: "keyword", foreground: primary.replace("#", "").slice(0, 6) },
      { token: "string", foreground: success.replace("#", "").slice(0, 6) },
      { token: "number", foreground: warning.replace("#", "").slice(0, 6) },
      { token: "type", foreground: secondary.replace("#", "").slice(0, 6) },
      { token: "function", foreground: primaryFixed.replace("#", "").slice(0, 6) },
      { token: "delimiter", foreground: outline.replace("#", "").slice(0, 6) },
    ],
    colors: {
      "editor.background": surfaceLowest,
      "editor.foreground": onSurface,
      "editorLineNumber.foreground": outlineVariant,
      "editorLineNumber.activeForeground": primary,
      "editor.lineHighlightBackground": withAlpha(surfaceLow, "88"),
      "editor.selectionBackground": withAlpha(primaryContainer, "55"),
      "editor.inactiveSelectionBackground": withAlpha(primaryContainer, "28"),
      "editorCursor.foreground": primary,
      "editorIndentGuide.background": surfaceHigh,
      "editorIndentGuide.activeBackground": outlineVariant,
      "editorGutter.background": surfaceLowest,
      "scrollbarSlider.background": withAlpha(outlineVariant, "66"),
      "scrollbarSlider.hoverBackground": withAlpha(outlineVariant, "aa"),
      "scrollbarSlider.activeBackground": withAlpha(primary, "44"),
    },
  });
  themeReady = true;
}
