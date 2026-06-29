import type { Cone } from "@/modules/contracts";

/** Map the cone's p5/p50/p95 cumulative-return paths to SVG polyline points on a shared
 *  scale, so the band renders the REAL series (not a procedural fan). Pure, deterministic. */
export interface ConePoints {
  p5: string;
  p50: string;
  p95: string;
  band: string; // closed polygon: p95 forward, p5 back — the shaded cone
}

export function conePaths(cone: Cone, w: number, h: number): ConePoints {
  const all = [...cone.p5, ...cone.p50, ...cone.p95];
  if (all.length === 0) return { p5: "", p50: "", p95: "", band: "" };
  const lo = Math.min(...all);
  const hi = Math.max(...all);
  const span = hi - lo || 1;
  const n = Math.max(cone.p50.length, 1);
  const x = (i: number) => (i / Math.max(n - 1, 1)) * w;
  const y = (v: number) => h - ((v - lo) / span) * h; // invert: higher value = higher on screen
  const pts = (xs: number[]) => xs.map((v, i) => `${x(i).toFixed(1)},${y(v).toFixed(1)}`).join(" ");
  const back = cone.p5
    .map((v, i) => `${x(i).toFixed(1)},${y(v).toFixed(1)}`)
    .reverse()
    .join(" ");
  return {
    p5: pts(cone.p5),
    p50: pts(cone.p50),
    p95: pts(cone.p95),
    band: `${pts(cone.p95)} ${back}`,
  };
}
