export interface Rect {
  left: number;
  top: number;
  width: number;
  height: number;
}

function worst(row: number[], shortSide: number, total: number): number {
  if (!row.length) return Number.POSITIVE_INFINITY;
  const s = row.reduce((a, b) => a + b, 0) || 1e-9;
  const longSide = total ? s / total : 0;
  const shorts = row.map((v) => (v / s) * shortSide);
  const maxS = Math.max(...shorts);
  const minS = Math.min(...shorts);
  if (minS <= 0 || shortSide <= 0) return Number.POSITIVE_INFINITY;
  return Math.max(longSide / minS, maxS / longSide);
}

export function squarify(values: number[], x: number, y: number, w: number, h: number): Rect[] {
  if (!values.length || w <= 0 || h <= 0) return [];
  if (values.length === 1) return [{ left: x, top: y, width: w, height: h }];
  const total = values.reduce((a, b) => a + b, 0);
  if (total <= 0) return values.map(() => ({ left: x, top: y, width: 0, height: 0 }));

  const alongW = w >= h;
  const shortSide = alongW ? h : w;
  const longSide = alongW ? w : h;

  let row: number[] = [];
  const remaining = [...values];
  while (remaining.length) {
    const candidate = [...row, remaining[0]];
    if (!row.length || worst(candidate, shortSide, total) >= worst(row, shortSide, total)) {
      row = candidate;
      remaining.shift();
    } else break;
  }
  const rowTotal = row.reduce((a, b) => a + b, 0);
  const rowLong = (rowTotal / total) * longSide;
  const rects: Rect[] = [];
  let cursor = 0;
  for (const v of row) {
    const size = rowTotal ? (v / rowTotal) * shortSide : 0;
    if (alongW) rects.push({ left: x, top: y + cursor, width: rowLong, height: size });
    else rects.push({ left: x + cursor, top: y, width: size, height: rowLong });
    cursor += size;
  }
  if (remaining.length) {
    rects.push(
      ...(alongW
        ? squarify(remaining, x + rowLong, y, w - rowLong, h)
        : squarify(remaining, x, y + rowLong, w, h - rowLong)),
    );
  }
  return rects;
}
