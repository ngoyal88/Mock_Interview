/**
 * Stylesheet injected into the transcript iframe.
 * Parent-page CSS variables do not apply — define the semantic tokens in :root here
 * (aligned with DESIGN.md / index.css), then use only var() below.
 */
export const transcriptOverlayStyles = `
:root {
  color-scheme: dark;
  --color-background: #0b1326;
  --color-on-surface: #dae2fd;
  --color-on-surface-variant: #c2c6d6;
  --color-surface-container-low: #131b2e;
  --color-surface-container-highest: #2d3449;
  --color-primary: #adc6ff;
  --color-primary-container: #4d8eff;
  --color-on-primary-container: #00285d;
  --color-secondary: #4fdbc8;
  --color-success: #4edea3;
  --color-tertiary-fixed: #6ffbbe;
  --color-bubble-text: #f5f8ff;
  --border: rgba(255, 255, 255, 0.08);
  --border-strong: rgba(255, 255, 255, 0.12);
  --border-subtle: rgba(255, 255, 255, 0.05);
  --indigo-dim: rgba(173, 198, 255, 0.12);
  --indigo-border: rgba(173, 198, 255, 0.35);
  --indigo-glow: rgba(173, 198, 255, 0.18);
  --emerald-dim: rgba(78, 222, 163, 0.12);
  --emerald-border: rgba(78, 222, 163, 0.35);
  --primary-soft: rgba(86, 156, 255, 0.12);
  --primary-softer: rgba(86, 156, 255, 0.03);
  --primary-line: rgba(86, 156, 255, 0.35);
  --primary-fill: rgba(77, 142, 255, 0.92);
  --primary-fill-dim: rgba(77, 142, 255, 0.88);
  --primary-line-strong: rgba(77, 142, 255, 0.4);
  --topbar-bg: color-mix(in srgb, var(--color-background) 86%, transparent);
  --panel-bg: color-mix(in srgb, var(--color-surface-container-low) 72%, transparent);
  --input-bg: color-mix(in srgb, var(--color-surface-container-highest) 30%, transparent);
  --glass-fill: rgba(255, 255, 255, 0.03);
  --glass-fill-soft: rgba(255, 255, 255, 0.02);
  --scroll-thumb: rgba(255, 255, 255, 0.16);
  --scroll-track: rgba(255, 255, 255, 0.02);
  --shadow-line: 0 12px 30px color-mix(in srgb, var(--color-background) 70%, transparent);
  --wrap-glow: radial-gradient(1200px 600px at 10% -10%, color-mix(in srgb, var(--color-primary-container) 12%, transparent), transparent),
    radial-gradient(1200px 600px at 90% -10%, color-mix(in srgb, var(--color-secondary) 10%, transparent), transparent),
    var(--color-background);
  --font-sans: "Plus Jakarta Sans", Inter, system-ui, -apple-system, Segoe UI, Roboto, sans-serif;
}
* { box-sizing: border-box; }
body {
  margin: 0;
  font-family: var(--font-sans);
  background: var(--color-background);
  color: var(--color-on-surface);
  padding: 0;
}
.wrap {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  background: var(--wrap-glow);
}
.top {
  position: relative;
  z-index: 2;
  border-bottom: 1px solid color-mix(in srgb, var(--color-on-surface) 10%, transparent);
  background: var(--topbar-bg);
  backdrop-filter: blur(14px);
  padding: 14px 20px 12px;
}
.title {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 10px;
}
.meta {
  margin-top: 6px;
  display: flex;
  gap: 12px;
  flex-wrap: wrap;
  font-size: 12px;
  color: color-mix(in srgb, var(--color-on-surface-variant) 92%, transparent);
}
.meta-accent {
  color: var(--color-tertiary-fixed);
}
h1 {
  margin: 0;
  font-size: 34px;
  font-weight: 700;
  letter-spacing: -0.01em;
}
.dot {
  width: 4px;
  height: 4px;
  border-radius: 999px;
  background: color-mix(in srgb, var(--color-on-surface-variant) 65%, transparent);
}
.searchbar {
  display: flex;
  gap: 10px;
  border-bottom: 1px solid color-mix(in srgb, var(--color-on-surface) 6%, transparent);
  background: var(--panel-bg);
  padding: 10px 20px;
}
.searchbar input {
  width: 100%;
  border: 1px solid var(--border-strong);
  border-radius: 10px;
  background: var(--input-bg);
  color: var(--color-on-surface);
  padding: 10px 12px;
  outline: none;
  font-size: 14px;
}
.searchbar input:focus {
  border-color: color-mix(in srgb, var(--color-primary) 55%, transparent);
  box-shadow: 0 0 0 2px var(--indigo-glow);
}
.btn {
  border: 1px solid color-mix(in srgb, var(--color-on-surface) 14%, transparent);
  border-radius: 10px;
  background: var(--glass-fill);
  color: var(--color-on-surface);
  padding: 0 14px;
  min-height: 38px;
  font-size: 12px;
  font-weight: 600;
  white-space: nowrap;
  cursor: pointer;
}
.btn--accent {
  border-color: var(--emerald-border);
  background: var(--emerald-dim);
  color: var(--color-tertiary-fixed);
}
.btn--primary {
  border-color: color-mix(in srgb, var(--color-primary) 45%, transparent);
  background: color-mix(in srgb, var(--color-primary) 18%, transparent);
}
.stream {
  flex: 1;
  overflow-y: auto;
  padding: 14px 20px 18px;
  scrollbar-width: thin;
  scrollbar-color: var(--scroll-thumb) transparent;
}
.stream::-webkit-scrollbar { width: 6px; }
.stream::-webkit-scrollbar-track { background: var(--scroll-track); }
.stream::-webkit-scrollbar-thumb { background: var(--scroll-thumb); border-radius: 4px; }
.session-start {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 16px;
  font-size: 12px;
  letter-spacing: 0.08em;
  text-transform: uppercase;
  color: color-mix(in srgb, var(--color-on-surface-variant) 80%, transparent);
}
.session-start:before,
.session-start:after {
  content: "";
  height: 1px;
  flex: 1;
  background: var(--border);
}
.row {
  display: flex;
  width: 100%;
  gap: 12px;
  margin-bottom: 16px;
  align-items: flex-start;
  position: relative;
}
.row--you {
  flex-direction: row-reverse;
}
.avatar-col {
  width: 42px;
  display: flex;
  align-items: center;
  justify-content: flex-start;
  flex-shrink: 0;
  padding-top: 4px;
}
.avatar {
  width: 36px;
  height: 36px;
  border-radius: 999px;
  display: flex;
  align-items: center;
  justify-content: center;
  border: 1px solid color-mix(in srgb, var(--color-on-surface) 20%, transparent);
  box-shadow: inset 0 0 16px var(--border-subtle);
}
.avatar svg {
  width: 18px;
  height: 18px;
  fill: currentColor;
}
.avatar--ai {
  background: var(--indigo-dim);
  color: var(--color-primary);
  border-color: var(--indigo-border);
  position: relative;
}
.avatar--ai::after {
  content: "";
  position: absolute;
  right: -1px;
  bottom: -1px;
  width: 8px;
  height: 8px;
  border-radius: 999px;
  background: var(--color-success);
  box-shadow: 0 0 0 0 color-mix(in srgb, var(--color-success) 40%, transparent);
  animation: ai-pulse 2s ease-in-out infinite;
}
.avatar--you {
  background: var(--emerald-dim);
  color: var(--color-tertiary-fixed);
  border-color: color-mix(in srgb, var(--color-success) 36%, transparent);
}
.line {
  width: min(80%, 860px);
  border: 1px solid var(--border-strong);
  border-radius: 14px;
  background: var(--glass-fill);
  padding: 14px 16px;
  box-shadow: var(--shadow-line);
}
.line--ai {
  border-color: var(--primary-line);
  background: linear-gradient(180deg, var(--primary-soft), var(--primary-softer));
  border-top-left-radius: 6px;
}
.line--you {
  border-color: var(--primary-line-strong);
  background: linear-gradient(180deg, var(--primary-fill), var(--primary-fill-dim));
  border-top-right-radius: 6px;
}
.time {
  margin-top: 8px;
  display: block;
  text-align: right;
  font-size: 11px;
  color: color-mix(in srgb, var(--color-on-surface) 72%, transparent);
}
p {
  margin: 0;
  white-space: pre-wrap;
  line-height: 1.62;
  font-size: 14px;
  color: var(--color-bubble-text);
}
.line--you p {
  color: var(--color-on-primary-container);
  font-weight: 500;
}
.metric-badge {
  margin-top: 10px;
  margin-left: auto;
  width: fit-content;
  border-radius: 8px;
  border: 1px solid var(--emerald-border);
  background: var(--emerald-dim);
  color: var(--color-tertiary-fixed);
  padding: 4px 8px;
  font-size: 11px;
  font-weight: 600;
}
.empty {
  font-size: 14px;
  color: color-mix(in srgb, var(--color-on-surface-variant) 90%, transparent);
  text-align: center;
  padding: 22px;
  border: 1px dashed color-mix(in srgb, var(--color-on-surface) 20%, transparent);
  border-radius: 12px;
  background: var(--glass-fill-soft);
}
.footer {
  border-top: 1px solid var(--border);
  background: var(--panel-bg);
  padding: 12px 20px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
}
.footer-note {
  font-size: 12px;
  color: color-mix(in srgb, var(--color-on-surface-variant) 90%, transparent);
}
.footer-actions {
  display: flex;
  gap: 8px;
}
@keyframes ai-pulse {
  0% { transform: scale(1); box-shadow: 0 0 0 0 color-mix(in srgb, var(--color-success) 40%, transparent); }
  70% { transform: scale(1.1); box-shadow: 0 0 0 6px transparent; }
  100% { transform: scale(1); box-shadow: 0 0 0 0 transparent; }
}
@media (max-width: 900px) {
  .top { padding-inline: 14px; }
  h1 { font-size: 26px; }
  .searchbar { padding-inline: 14px; }
  .stream { padding-inline: 14px; }
  .line { width: min(88%, 100%); }
  .footer { padding-inline: 14px; }
}
@media (max-width: 520px) {
  .line { width: 100%; padding: 12px 14px; }
  .avatar-col { display: none; }
}
`;
