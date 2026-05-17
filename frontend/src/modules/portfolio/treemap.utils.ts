export interface Rect {
  left: number;
  top: number;
  width: number;
  height: number;
}

// Aspect ratio of a rectangle: always >= 1 (longer/shorter).
function aspectRatio(a: number, b: number): number {
  if (a <= 0 || b <= 0) return Number.POSITIVE_INFINITY;
  return a > b ? a / b : b / a;
}

// Worst aspect ratio in a candidate row laid along `strip` (pixels).
// `rowSum` is the sum of the row values, `total` is the sum of all values,
// `longSide` is the full length of the axis we're laying along (pixels).
function worstAspect(row: number[], rowSum: number, total: number, longSide: number, shortSide: number): number {
  if (!row.length || rowSum <= 0 || total <= 0) return Number.POSITIVE_INFINITY;
  // The row occupies this fraction of the long axis.
  const stripLen = (rowSum / total) * longSide;
  let worst = 0;
  for (const v of row) {
    // Each item gets (v/rowSum) of the short side.
    const itemShort = (v / rowSum) * shortSide;
    worst = Math.max(worst, aspectRatio(stripLen, itemShort));
  }
  return worst;
}

export function squarify(values: number[], x: number, y: number, w: number, h: number): Rect[] {
  if (!values.length || w <= 0 || h <= 0) return [];
  if (values.length === 1) return [{ left: x, top: y, width: w, height: h }];

  const total = values.reduce((a, b) => a + b, 0);
  if (total <= 0) return values.map(() => ({ left: x, top: y, width: 0, height: 0 }));

  // Lay strips along the longer axis so items fill the short axis.
  const alongW = w >= h;
  const longSide  = alongW ? w : h;
  const shortSide = alongW ? h : w;

  let row: number[] = [];
  let rowSum = 0;
  const remaining = [...values];

  while (remaining.length) {
    const next = remaining[0];
    const candidateRow = [...row, next];
    const candidateSum = rowSum + next;
    const currentWorse = worstAspect(row, rowSum, total, longSide, shortSide);
    const candidateWorse = worstAspect(candidateRow, candidateSum, total, longSide, shortSide);
    if (!row.length || candidateWorse <= currentWorse) {
      row = candidateRow;
      rowSum = candidateSum;
      remaining.shift();
    } else {
      break;
    }
  }

  // Place the finalised row.
  const stripLen = (rowSum / total) * longSide;
  const rects: Rect[] = [];
  let cursor = 0;
  for (const v of row) {
    const itemShort = rowSum > 0 ? (v / rowSum) * shortSide : 0;
    if (alongW) {
      rects.push({ left: x, top: y + cursor, width: stripLen, height: itemShort });
    } else {
      rects.push({ left: x + cursor, top: y, width: itemShort, height: stripLen });
    }
    cursor += itemShort;
  }

  // Recurse on the remaining rectangle.
  if (remaining.length) {
    const remainingTotal = remaining.reduce((a, b) => a + b, 0);
    const scale = remainingTotal / total;
    if (alongW) {
      rects.push(...squarify(remaining, x + stripLen, y, w - stripLen, h));
    } else {
      rects.push(...squarify(remaining, x, y + stripLen, w, h - stripLen));
    }
    // Fix: remaining values must be re-scaled against their own total in the recursion,
    // but squarify already handles that since it recomputes total from values.
    void scale;
  }

  return rects;
}
