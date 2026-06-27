// Fan-chart geometry for the prediction cone — ported from the claude_design
// Hi-Fi (int-context.jsx). Pure, no React. Median slopes up with CAGR; bands
// widen ~sqrt(t); the downside is skewed fatter.

export const FAN = { W: 420, H: 190, x0: 50, x1: 406, y0: 150 } as const;

export interface FanPaths {
  outer: string;
  mid: string;
  inner: string;
  medLine: string;
  p5: string;
  xs: number[];
  med: number[];
}

export function fanPaths(o: { rise: number; spread: number; skew?: number }): FanPaths {
  const { rise, spread, skew = 1 } = o;
  const { x0, x1, y0 } = FAN;
  const N = 56;
  const xs: number[] = [];
  const med: number[] = [];
  for (let i = 0; i <= N; i++) {
    xs.push(x0 + (x1 - x0) * (i / N));
    med.push(y0 - rise * (i / N));
  }
  const hw = (frac: number, t: number) => spread * frac * t ** 0.58;
  const band = (frac: number) => {
    let d = `M ${xs[0]} ${med[0]}`;
    for (let i = 1; i <= N; i++)
      d += ` L ${xs[i].toFixed(1)} ${(med[i] - hw(frac, i / N)).toFixed(1)}`;
    for (let i = N; i >= 0; i--)
      d += ` L ${xs[i].toFixed(1)} ${(med[i] + hw(frac, i / N) * skew).toFixed(1)}`;
    return `${d} Z`;
  };
  let medLine = `M ${xs[0]} ${med[0]}`;
  let p5 = `M ${xs[0]} ${med[0]}`;
  for (let i = 1; i <= N; i++) {
    medLine += ` L ${xs[i].toFixed(1)} ${med[i].toFixed(1)}`;
    p5 += ` L ${xs[i].toFixed(1)} ${(med[i] + hw(1, i / N) * skew).toFixed(1)}`;
  }
  return { outer: band(1), mid: band(0.6), inner: band(0.3), medLine, p5, xs, med };
}
