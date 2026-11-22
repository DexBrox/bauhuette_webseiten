/** Builds a link that also works under a sub path (preview on GitHub Pages). */
export function withBase(target = ""): string {
  const base = import.meta.env.BASE_URL.replace(/\/$/, "");
  const rest = target.replace(/^\//, "");
  return `${base}/${rest}`;
}
