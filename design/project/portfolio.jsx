/* Alpha Forge — Portfolio view
   Single React tree that owns:
     · the filter bar (search + sector chips + gainers/losers + sort + view toggle)
     · the squarified Treemap
     · the Ledger table
   Mounts into #pf-mount inside the Portfolio screen. */

const { useState, useMemo, useRef, useEffect, useLayoutEffect } = React;

// ── Data ──────────────────────────────────────────────────────────────────
// `valueINR` is the canonical comparator (for treemap area + Value-sort).
// `valueDisplay` is what's shown for non-INR holdings.
// `source` ties a holding to a broker/wallet (see WALLETS).
const INR_PER_USD = 83.41;

const HOLDINGS = [
  { sym:"RELIANCE",   name:"Reliance Industries", sector:"Energy",  region:"IN", cap:"LC", source:"zerodha",
    qty:120, avg:2410, ltp:2914.05, ccy:"₹", valueINR:349686, dayPct:1.24,  pnlAbs:60480,
    spark:[20,18,22,14,16,10,14,8,12,6,8] },
  { sym:"INFY",       name:"Infosys",             sector:"IT",      region:"IN", cap:"LC", source:"zerodha",
    qty:250, avg:1410, ltp:1612.30, ccy:"₹", valueINR:403075, dayPct:0.82,  pnlAbs:50500,
    spark:[16,18,14,16,12,14,10,12,8,10,6] },
  { sym:"HDFCBANK",   name:"HDFC Bank",           sector:"Banking", region:"IN", cap:"LC", source:"zerodha",
    qty:80,  avg:1560, ltp:1488.10, ccy:"₹", valueINR:119048, dayPct:-0.44, pnlAbs:-5760,
    spark:[8,10,14,12,16,18,14,18,20,16,22] },
  { sym:"TCS",        name:"Tata Consultancy",    sector:"IT",      region:"IN", cap:"LC", source:"zerodha",
    qty:60,  avg:3720, ltp:3962.70, ccy:"₹", valueINR:237762, dayPct:0.21,  pnlAbs:14520,
    spark:[14,12,14,10,12,8,10,6,8,4,8] },
  { sym:"ITC",        name:"ITC Ltd",             sector:"FMCG",    region:"IN", cap:"LC", source:"angelone",
    qty:400, avg:380,  ltp:416,     ccy:"₹", valueINR:166400, dayPct:0.32,  pnlAbs:14400,
    spark:[14,16,18,14,16,12,14,16,12,10,8] },
  { sym:"BHARTIARTL", name:"Bharti Airtel",       sector:"Telecom", region:"IN", cap:"LC", source:"angelone",
    qty:80,  avg:1180, ltp:1342,    ccy:"₹", valueINR:107360, dayPct:1.45,  pnlAbs:12960,
    spark:[16,14,16,12,14,10,12,8,10,6,8] },
  { sym:"TATAMOTORS", name:"Tata Motors",         sector:"Auto",    region:"IN", cap:"LC", source:"angelone",
    qty:60,  avg:780,  ltp:742,     ccy:"₹", valueINR:44520,  dayPct:-0.92, pnlAbs:-2280,
    spark:[10,12,10,14,12,16,14,18,16,20,18] },
  { sym:"NVDA",       name:"NVIDIA",              sector:"Semis",   region:"US", cap:"LC", source:"angelone",
    qty:20,  avg:520,  ltp:894.20,  ccy:"$", valueINR:1491323, valueDisplay:17884, dayPct:1.82, pnlAbs:7484,
    spark:[22,18,16,12,14,8,10,4,6,2,4] },
  { sym:"BTC",        name:"Bitcoin",             sector:"Crypto",  region:"CR", cap:"X", source:"coinbase",
    qty:0.25, avg:48120, ltp:64281, ccy:"$", valueINR:1340396, valueDisplay:16070, dayPct:2.40, pnlAbs:4040,
    spark:[18,14,16,10,12,6,8,4,6,2,4] },
  { sym:"MF · 6 funds", name:"Mutual Fund Basket",sector:"Funds",   region:"IN", cap:"MF", source:"groww",
    qty:6, avg:null, ltp:null,      ccy:"₹", valueINR:1420000, dayPct:0.62,  pnlAbs:8804,
    isFund:true, spark:[14,12,14,10,12,10,12,8,10,6,8] },
];

// ── Brokers / wallets ─────────────────────────────────────────────────────
// Each wallet has free cash + connection metadata. Aggregates (holdings,
// today's P&L) are derived from HOLDINGS at render time.
const WALLETS = [
  { id:"all",      name:"All wallets",  short:"ALL", sub:"5 SOURCES",
    cashINR: null /* sum */, ccy:"₹", connected:true,  sync:"NOW",
    grad:["#FFB454","#D45A1A"] },
  { id:"zerodha",  name:"Zerodha",      short:"KT",  sub:"KITE · EQUITY · F&O",
    cashINR: 84500,  ccy:"₹", connected:true,  sync:"2m",
    grad:["#f17545","#d24316"], note:"Equity & F&O" },
  { id:"angelone", name:"Angel One",    short:"AO",  sub:"SMARTAPI · EQUITY · US",
    cashINR: 42300,  ccy:"₹", connected:true,  sync:"5m",
    grad:["#3b6eea","#0a3d8f"], note:"Equity + US stocks via Vested" },
  { id:"groww",    name:"Groww",        short:"GW",  sub:"MUTUAL FUNDS · SIP",
    cashINR: 12500,  ccy:"₹", connected:true,  sync:"1h",
    grad:["#00d09c","#00735c"], note:"Mutual funds & SIP" },
  { id:"coinbase", name:"Coinbase",     short:"CB",  sub:"CRYPTO · ADVANCED",
    cashINR: 312 * INR_PER_USD,  ccy:"$", cashUSD:312, connected:true,  sync:"24s",
    grad:["#0052ff","#0033a0"], note:"Spot crypto" },
];

const SECTORS = ["All","IT","Banking","Energy","FMCG","Auto","Telecom","Semis","Crypto","Funds"];

const SORTS = [
  { id:"value",  label:"Value",       get:h => h.valueINR },
  { id:"pnl",    label:"P&L",         get:h => h.pnlAbs },
  { id:"daypct", label:"Today %",     get:h => h.dayPct },
  { id:"qty",    label:"Quantity",    get:h => h.qty },
  { id:"alpha",  label:"A → Z",       get:h => h.sym, isString:true },
];

// ── Wallet aggregation ────────────────────────────────────────────────────
function inrPnl(h){ return h.ccy === "$" ? h.pnlAbs * INR_PER_USD : h.pnlAbs; }
function walletAggregate(wallet){
  const items = wallet.id === "all"
    ? HOLDINGS
    : HOLDINGS.filter(h => h.source === wallet.id);
  const holdingsINR = items.reduce((s,h) => s + h.valueINR, 0);
  const todayPnlINR = items.reduce((s,h) => s + inrPnl(h), 0);
  const weightedDay = holdingsINR > 0
    ? items.reduce((s,h) => s + h.dayPct * h.valueINR, 0) / holdingsINR
    : 0;
  return { items, count: items.length, holdingsINR, todayPnlINR, weightedDay };
}
function allWalletsCash(){
  return WALLETS.filter(w => w.id !== "all").reduce((s,w) => s + (w.cashINR || 0), 0);
}

// ── Format helpers ────────────────────────────────────────────────────────
function fmtINR(v){
  if (v >= 10000000) return `₹${(v/10000000).toFixed(2)}Cr`;
  if (v >= 100000)   return `₹${(v/100000).toFixed(2)}L`;
  return "₹" + v.toLocaleString("en-IN");
}
function fmtValue(h){
  if (h.ccy === "$") {
    const v = h.valueDisplay;
    return v >= 1000 ? `$${(v/1000).toFixed(1)}k` : `$${v}`;
  }
  return fmtINR(h.valueINR);
}
function fmtPnL(h){
  const sign = h.pnlAbs >= 0 ? "+" : "−";
  const abs = Math.abs(h.pnlAbs);
  if (h.ccy === "$") {
    return `${sign}$${abs.toLocaleString()}`;
  }
  if (abs >= 100000) return `${sign}₹${(abs/100000).toFixed(2)}L`;
  return `${sign}₹${abs.toLocaleString("en-IN")}`;
}
function fmtPrice(h, key){
  const v = h[key];
  if (v == null) return "—";
  if (h.ccy === "$") return `$${v.toLocaleString(undefined,{minimumFractionDigits:0,maximumFractionDigits:2})}`;
  return `₹${v.toLocaleString("en-IN",{maximumFractionDigits:2})}`;
}
function cellBg(dayPct){
  if (dayPct > 0) {
    const i = Math.min(42, Math.max(8, dayPct * 18));
    return `color-mix(in srgb, var(--green) ${i.toFixed(0)}%, var(--surface))`;
  }
  if (dayPct < 0) {
    const i = Math.min(42, Math.max(8, -dayPct * 18));
    return `color-mix(in srgb, var(--red) ${i.toFixed(0)}%, var(--surface))`;
  }
  return "var(--surface)";
}

// ── Squarified treemap layout ─────────────────────────────────────────────
// items must be sorted descending by `.value` before calling.
function squarify(items, x, y, w, h){
  if (!items.length || w <= 0 || h <= 0) return [];
  const total = items.reduce((s,i)=>s+i.value, 0) || 1;
  const scale = (w*h) / total;
  const scaled = items.map(i => ({...i, _area: i.value * scale}));
  const out = [];
  let rect = {x, y, w, h};
  let i = 0;
  while (i < scaled.length) {
    const shorter = Math.min(rect.w, rect.h);
    const row = [];
    let rowArea = 0;
    let prevWorst = Infinity;
    let j = i;
    while (j < scaled.length) {
      const cand = scaled[j];
      const newArea = rowArea + cand._area;
      const worst = worstAspect([...row, cand], shorter, newArea);
      if (row.length > 0 && worst > prevWorst) break;
      row.push(cand);
      rowArea = newArea;
      prevWorst = worst;
      j++;
    }
    // lay out this row along the shorter side
    const rowDim = rowArea / shorter;
    if (rect.w >= rect.h) {
      let yy = rect.y;
      row.forEach(it => {
        const hh = (it._area / rowArea) * rect.h;
        out.push({...it, _x:rect.x, _y:yy, _w:rowDim, _h:hh});
        yy += hh;
      });
      rect = {x:rect.x + rowDim, y:rect.y, w:rect.w - rowDim, h:rect.h};
    } else {
      let xx = rect.x;
      row.forEach(it => {
        const ww = (it._area / rowArea) * rect.w;
        out.push({...it, _x:xx, _y:rect.y, _w:ww, _h:rowDim});
        xx += ww;
      });
      rect = {x:rect.x, y:rect.y + rowDim, w:rect.w, h:rect.h - rowDim};
    }
    i = j;
  }
  return out;
}
function worstAspect(row, shorter, totalArea){
  if (!row.length || totalArea <= 0) return Infinity;
  const rowDim = totalArea / shorter;
  let worst = 0;
  for (const it of row) {
    const other = it._area / rowDim;
    const r = Math.max(rowDim/other, other/rowDim);
    if (r > worst) worst = r;
  }
  return worst;
}

// ── Subcomponents ─────────────────────────────────────────────────────────
function Spark({data, color, w=120, h=26}){
  if (!data || !data.length) return null;
  const max = Math.max(...data);
  const min = Math.min(...data);
  const range = max - min || 1;
  const step = w / (data.length - 1);
  const pts = data.map((v,i) => `${(i*step).toFixed(1)},${(h - ((v-min)/range)*(h-2) - 1).toFixed(1)}`).join(" ");
  return (
    <svg viewBox={`0 0 ${w} ${h}`} preserveAspectRatio="none">
      <polyline points={pts} fill="none" stroke={color} strokeWidth="1.4" strokeLinejoin="round" strokeLinecap="round"/>
    </svg>
  );
}

function SearchBox({value, onChange}){
  const ref = useRef();
  // ⌘F / / focuses
  useEffect(() => {
    const h = (e) => {
      if ((e.metaKey || e.ctrlKey) && e.key.toLowerCase() === "f") {
        e.preventDefault(); ref.current?.focus();
      } else if (e.key === "/" && document.activeElement?.tagName !== "INPUT") {
        e.preventDefault(); ref.current?.focus();
      }
    };
    document.addEventListener("keydown", h);
    return () => document.removeEventListener("keydown", h);
  }, []);
  return (
    <div className={"pf-search" + (value ? " has-q" : "")}>
      <svg className="icon" viewBox="0 0 24 24"><circle cx="11" cy="11" r="7" fill="none" stroke="currentColor" strokeWidth="2"/><path d="M21 21l-4.3-4.3" stroke="currentColor" strokeWidth="2" strokeLinecap="round"/></svg>
      <input ref={ref} type="text" placeholder="Search symbols, sectors, regions…"
             value={value} onChange={e => onChange(e.target.value)} />
      <span className="kbd-hint">/</span>
      {value && (
        <button className="clear" onClick={() => onChange("")} aria-label="Clear">
          <svg viewBox="0 0 24 24" width="12" height="12"><path d="M6 6l12 12M18 6l-12 12" stroke="currentColor" strokeWidth="2" strokeLinecap="round"/></svg>
        </button>
      )}
    </div>
  );
}

function SectorChips({value, counts, onChange}){
  return (
    <div className="pf-chips">
      {SECTORS.map(s => {
        const c = counts[s] || 0;
        const isAll = s === "All";
        if (!isAll && c === 0) return null;
        return (
          <button key={s} className={"pf-chip" + (value === s ? " active" : "")}
                  onClick={() => onChange(s)}>
            <span>{s}</span>
            <span className="count">{c}</span>
          </button>
        );
      })}
    </div>
  );
}

function PnLToggle({value, onChange}){
  return (
    <div className="pf-pnl">
      <button className={"all" + (value === "all" ? " active" : "")} onClick={() => onChange("all")}>All</button>
      <button className={"up"  + (value === "up"  ? " active" : "")} onClick={() => onChange("up")} title="Gainers only">▴ Gain</button>
      <button className={"dn"  + (value === "dn"  ? " active" : "")} onClick={() => onChange("dn")} title="Losers only">▾ Loss</button>
    </div>
  );
}

function SortMenu({sortBy, sortDir, onChange}){
  const [open, setOpen] = useState(false);
  const ref = useRef();
  useEffect(() => {
    const h = e => { if (!ref.current?.contains(e.target)) setOpen(false); };
    if (open) document.addEventListener("mousedown", h);
    return () => document.removeEventListener("mousedown", h);
  }, [open]);
  const active = SORTS.find(s => s.id === sortBy) || SORTS[0];
  return (
    <div className="pf-sort" ref={ref}>
      <button className="btn" onClick={() => setOpen(o => !o)}>
        <span>Sort · {active.label}</span>
        <span className="dir">{sortDir === "desc" ? "↓" : "↑"}</span>
      </button>
      {open && (
        <div className="menu">
          {SORTS.map(s => (
            <button key={s.id}
                    className={s.id === sortBy ? "active" : ""}
                    onClick={() => {
                      if (s.id === sortBy) onChange(s.id, sortDir === "desc" ? "asc" : "desc");
                      else onChange(s.id, s.isString ? "asc" : "desc");
                      setOpen(false);
                    }}>
              <span>{s.label}</span>
              <span className="dir">{s.id === sortBy ? (sortDir === "desc" ? "↓" : "↑") : ""}</span>
            </button>
          ))}
        </div>
      )}
    </div>
  );
}

function ViewToggle({value, onChange}){
  return (
    <div className="pf-view">
      <button className={value === "tree" ? "active" : ""} onClick={() => onChange("tree")} title="Treemap">
        <svg viewBox="0 0 24 24"><rect x="3" y="3" width="11" height="13"/><rect x="14" y="3" width="7" height="6"/><rect x="14" y="9" width="7" height="12"/><rect x="3" y="16" width="11" height="5"/></svg>
        <span>Tree</span>
      </button>
      <button className={value === "ledger" ? "active" : ""} onClick={() => onChange("ledger")} title="Ledger">
        <svg viewBox="0 0 24 24"><path d="M4 6h16M4 12h16M4 18h16"/></svg>
        <span>Ledger</span>
      </button>
    </div>
  );
}

// ── Wallet strip ──────────────────────────────────────────────────────────
function WalletCard({ wallet, agg, totalCash, active, onClick }){
  const cashINR = wallet.id === "all" ? totalCash : wallet.cashINR;
  const cashStr = wallet.id === "all"
    ? fmtINR(cashINR)
    : (wallet.ccy === "$"
        ? `$${wallet.cashUSD.toLocaleString()}`
        : fmtINR(cashINR));
  const dayCls = agg.weightedDay >= 0 ? "up" : "dn";
  const daySign = agg.weightedDay >= 0 ? "+" : "";
  return (
    <button className={"wallet " + wallet.id + (active ? " active" : "")} onClick={onClick}>
      <div className="w-head">
        <div className="w-logo" style={{background: `linear-gradient(135deg, ${wallet.grad[0]}, ${wallet.grad[1]})`}}>
          {wallet.short}
        </div>
        <div className="w-name">
          <div className="n">{wallet.name}</div>
          <div className="s">{wallet.sub}</div>
        </div>
        <span className="w-sync" title={`Last sync ${wallet.sync}`}>
          <span className="w-dot" />
          <span className="w-sync-t">{wallet.sync}</span>
        </span>
      </div>
      <div className="w-cash-row">
        <div>
          <div className="w-cash">{cashStr}</div>
          <div className="w-cash-lbl">{wallet.id === "all" ? "TOTAL CASH" : "FREE CASH"}</div>
        </div>
        {wallet.id !== "all" && wallet.ccy === "$" && (
          <div className="w-cash-aux">≈ {fmtINR(cashINR)}</div>
        )}
      </div>
      <div className="w-foot">
        <span className="w-foot-l">
          <span className="v">{fmtINR(agg.holdingsINR)}</span>
          <span className="pos"> · {agg.count} POS</span>
        </span>
        <span className={"w-foot-r " + dayCls}>{daySign}{agg.weightedDay.toFixed(2)}%</span>
      </div>
    </button>
  );
}

function WalletStrip({ source, onChange }){
  const totalCash = useMemo(allWalletsCash, []);
  return (
    <div className="pf-wallets">
      {WALLETS.map(w => (
        <WalletCard key={w.id}
                    wallet={w}
                    agg={walletAggregate(w)}
                    totalCash={totalCash}
                    active={source === w.id}
                    onClick={() => onChange(w.id)} />
      ))}
    </div>
  );
}

// ── Source spotlight (only when a specific wallet is selected) ────────────
function SourceSpotlight({ wallet, agg, onClear }){
  const dayCls = agg.weightedDay >= 0 ? "up" : "dn";
  const daySign = agg.weightedDay >= 0 ? "+" : "";
  return (
    <div className="src-spot">
      <div className="ss-logo" style={{background: `linear-gradient(135deg, ${wallet.grad[0]}, ${wallet.grad[1]})`}}>
        {wallet.short}
      </div>
      <div className="ss-name">
        <div className="ss-n">{wallet.name}</div>
        <div className="ss-s">{wallet.note} · last sync {wallet.sync} ago</div>
      </div>
      <div className="ss-stat">
        <div className="ss-l">POSITIONS</div>
        <div className="ss-v">{agg.count}</div>
      </div>
      <div className="ss-stat">
        <div className="ss-l">HOLDINGS</div>
        <div className="ss-v">{fmtINR(agg.holdingsINR)}</div>
      </div>
      <div className="ss-stat">
        <div className="ss-l">TODAY</div>
        <div className={"ss-v " + dayCls}>{daySign}{agg.weightedDay.toFixed(2)}%</div>
      </div>
      <div className="ss-stat">
        <div className="ss-l">CASH</div>
        <div className="ss-v">{wallet.ccy === "$" ? `$${wallet.cashUSD.toLocaleString()}` : fmtINR(wallet.cashINR)}</div>
      </div>
      <div className="ss-acts">
        <button className="ss-btn">⟳ Refresh</button>
        <button className="ss-btn ghost" onClick={onClear}>Show all ×</button>
      </div>
    </div>
  );
}

// ── Static rebalance rail ─────────────────────────────────────────────────
// Was static HTML; now JSX so the wallet strip can span full body width.
function RebalanceRail({ source }){
  // Tweak the headline per source so the rail feels source-aware.
  const headlines = {
    all:      "IT is 38% of equity — concentration flagged.",
    zerodha:  "Bank drag in HDFC. Concentration in IT is 60% of Zerodha.",
    angelone: "NVDA is 82% of this wallet. Trim or hedge.",
    groww:    "MF basket is on target. No drift.",
    coinbase: "BTC up 2.4% today — set a 5% trim alert?"
  };
  const bullets = {
    all:      "INFY and TCS together make up most of the drift. A ~15% trim brings you back inside your target band.",
    zerodha:  "Recommend trimming INFY 15% and adding a debt fund via Groww to balance.",
    angelone: "NVDA is exposed to AI volatility. A 25% trim moves you to a healthier 60% weight.",
    groww:    "Continue your existing SIPs. We'll alert if any fund underperforms its index for 3 quarters.",
    coinbase: "Crypto is +3% over target. A 20% trim books gains and rebalances to equities."
  };
  const chips = {
    all:      ["Trim INFY 15%","Trim TCS 10%","Add BHARTIARTL","Add Debt fund"],
    zerodha:  ["Trim INFY 15%","Trim TCS 10%","Add Banking ETF","Stop INFY SIP"],
    angelone: ["Trim NVDA 25%","Hedge with PUT","Add BHARTIARTL","Lock-in $7.5k"],
    groww:    ["Boost Mid Cap","Pause Gold SIP","Add Debt fund","Tax harvest"],
    coinbase: ["Trim BTC 20%","Buy ETH","Stake idle USDC","Set 5% alert"]
  };
  return (
    <div className="rail">
      <div className="hd">
        <div className="orb-sm"></div>
        <div>
          <div className="tag accent">Alpha · Rebalance</div>
          <h4>{headlines[source] || headlines.all}</h4>
        </div>
      </div>
      <div className="bullet"><p>{bullets[source] || bullets.all}</p></div>
      <div className="chips">
        {(chips[source] || chips.all).map(c => <span key={c} className="chip">{c}</span>)}
      </div>
      <div className="drift">
        <div className="drift-row"><div className="hdr"><span>Equity</span><span className="v">+8%</span></div><div className="bar"><div className="fill" style={{width:"32%"}}></div></div></div>
        <div className="drift-row"><div className="hdr"><span>Debt</span><span className="v">−6%</span></div><div className="bar neg"><div className="fill" style={{width:"24%"}}></div></div></div>
        <div className="drift-row"><div className="hdr"><span>Crypto</span><span className="v">+3%</span></div><div className="bar"><div className="fill" style={{width:"12%"}}></div></div></div>
        <div className="drift-row"><div className="hdr"><span>Gold</span><span className="v">−2%</span></div><div className="bar neg"><div className="fill" style={{width:"8%"}}></div></div></div>
      </div>
      <button className="cta">Simulate & backtest</button>
    </div>
  );
}

// ── Treemap view ──────────────────────────────────────────────────────────
function Treemap({items}){
  const ref = useRef();
  const [size, setSize] = useState({w:0, h:0});
  useLayoutEffect(() => {
    if (!ref.current) return;
    const ro = new ResizeObserver(es => {
      const r = es[0].contentRect;
      setSize({w: r.width, h: r.height});
    });
    ro.observe(ref.current);
    return () => ro.disconnect();
  }, []);

  const cells = useMemo(() => {
    if (!size.w || !size.h || !items.length) return [];
    // Use INR as the sizing comparator across asset classes.
    const sorted = [...items]
      .map(it => ({...it, value: it.valueINR}))
      .sort((a,b) => b.value - a.value);
    return squarify(sorted, 0, 0, size.w, size.h);
  }, [items, size.w, size.h]);

  const GAP = 3;
  return (
    <div ref={ref} className="treemap">
      {cells.map(c => {
        const w = Math.max(0, c._w - GAP);
        const h = Math.max(0, c._h - GAP);
        const big = w * h > 28000;
        const compact = h < 60 || w < 90;
        const dir = c.dayPct >= 0 ? "up" : "dn";
        const color = c.dayPct >= 0 ? "var(--green)" : "var(--red)";
        return (
          <div key={c.sym}
               className={"tm-cell" + (big ? " big" : "") + (compact ? " compact" : "")}
               style={{left:c._x, top:c._y, width:w, height:h, background: cellBg(c.dayPct)}}
               title={`${c.sym} · ${c.sector} · ${fmtValue(c)} · ${c.dayPct >= 0 ? "+" : ""}${c.dayPct.toFixed(2)}%`}>
            <div className="tm-top">
              <div className="sym">{c.sym}</div>
              {!compact && <div className="sub">{c.sector} · {fmtValue(c)}</div>}
            </div>
            {big && c.spark && (
              <div className="tm-spark">
                <Spark data={c.spark} color={color} w={48} h={20}/>
              </div>
            )}
            <div className="bot">
              <div className="val mono">{fmtPnL(c)}</div>
              <div className={"chg mono " + dir}>{c.dayPct >= 0 ? "+" : ""}{c.dayPct.toFixed(2)}%</div>
            </div>
          </div>
        );
      })}
    </div>
  );
}

// ── Ledger view ───────────────────────────────────────────────────────────
function Ledger({items, sortBy, sortDir, onSort, query}){
  const cols = [
    { key:null,     label:"Symbol" },
    { key:"qty",    label:"Qty" },
    { key:null,     label:"Avg" },
    { key:null,     label:"LTP" },
    { key:"value",  label:"Value" },
    { key:"pnl",    label:"P&L" },
    { key:null,     label:"7D" },
    { key:null,     label:"Alpha" },
  ];
  function highlight(text){
    if (!query) return text;
    const q = query.toLowerCase();
    const t = String(text);
    const i = t.toLowerCase().indexOf(q);
    if (i < 0) return text;
    return <>{t.slice(0,i)}<mark>{t.slice(i, i+q.length)}</mark>{t.slice(i+q.length)}</>;
  }
  return (
    <div className="ledger">
      <table>
        <thead>
          <tr>
            {cols.map((c,i) => {
              const sortable = !!c.key;
              const active = c.key === sortBy;
              return (
                <th key={i}
                    className={sortable ? "sortable" : ""}
                    onClick={() => {
                      if (!sortable) return;
                      if (active) onSort(c.key, sortDir === "desc" ? "asc" : "desc");
                      else onSort(c.key, "desc");
                    }}>
                  <span>{c.label}</span>
                  {sortable && <span className={"th-arrow" + (active ? " on" : "")}>
                    {active ? (sortDir === "desc" ? "↓" : "↑") : "·"}
                  </span>}
                </th>
              );
            })}
          </tr>
        </thead>
        <tbody>
          {items.map(h => (
            <tr key={h.sym}>
              <td>
                <div className="sym-cell">
                  <div className="ico">{h.sym.charAt(0)}</div>
                  <div className="meta">
                    <span className="n">{highlight(h.sym)}</span>
                    <span className="s">{highlight(h.sector)} · {h.region}</span>
                  </div>
                </div>
              </td>
              <td>{h.qty}</td>
              <td>{fmtPrice(h, "avg")}</td>
              <td>{fmtPrice(h, "ltp")}</td>
              <td>{fmtValue(h)}</td>
              <td className={h.pnlAbs >= 0 ? "up" : "dn"}>{fmtPnL(h)}</td>
              <td className="spark-cell">
                <Spark data={h.spark} color={h.dayPct >= 0 ? "var(--green)" : "var(--red)"} w={120} h={26}/>
              </td>
              <td><span className="ask" title={`Ask Alpha about ${h.sym}`}>⚡</span></td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

// ── Empty state ───────────────────────────────────────────────────────────
function Empty({onReset}){
  return (
    <div className="pf-empty">
      <div className="hint">No positions match these filters</div>
      <div>Try widening the sector or clearing the search.</div>
      <span className="reset" onClick={onReset}>Reset all filters →</span>
    </div>
  );
}

// ── Compact summary bar (always visible) ──────────────────────────────────
// One slim row: 4 portfolio totals + wallet pills + expand caret. Replaces
// the old large stat cards + 5-wallet strip that ate the page.
function CompactSummary({ expanded, onToggle, source, onSourceChange }){
  const totalCash = useMemo(allWalletsCash, []);
  return (
    <div className={"pf-summary-bar" + (expanded ? " expanded" : "")}>
      <button className="ps-toggle" onClick={onToggle}
              title={expanded ? "Collapse summary" : "Expand summary"}>
        <span className="car">▸</span>
        <span>{expanded ? "Less" : "More"}</span>
      </button>
      <div className="pf-sum-totals">
        <span className="ps-stat">
          <span className="k">TOTAL</span>
          <span className="v">₹12.84L</span>
          <span className="d up">▲ 1.24%</span>
        </span>
        <span className="ps-sep" />
        <span className="ps-stat">
          <span className="k">INVESTED</span>
          <span className="v">₹98.20L</span>
        </span>
        <span className="ps-sep" />
        <span className="ps-stat">
          <span className="k">P&L</span>
          <span className="v up">+₹30.25L</span>
          <span className="d up">+30.8%</span>
        </span>
        <span className="ps-sep" />
        <span className="ps-stat">
          <span className="k">XIRR</span>
          <span className="v">17.4%</span>
          <span className="d muted">vs NIFTY 14.1%</span>
        </span>
      </div>
      <div className="pf-wallet-strip" role="tablist" aria-label="Wallets">
        {WALLETS.map(w => {
          const agg = walletAggregate(w);
          const cashINR = w.id === "all" ? totalCash : (w.cashINR || 0);
          const val = w.id === "all" ? fmtINR(agg.holdingsINR) : fmtINR(agg.holdingsINR);
          return (
            <button key={w.id}
                    className={"wpill" + (source === w.id ? " active" : "")}
                    onClick={() => onSourceChange(w.id)}
                    title={`${w.name} — ${agg.count} positions · cash ${fmtINR(cashINR)}`}>
              <span className="wp-logo" style={{background:`linear-gradient(135deg,${w.grad[0]},${w.grad[1]})`}}>
                {w.short}
              </span>
              <span className="wp-name">{w.id === "all" ? "All" : w.name}</span>
              <span className="wp-val">{val}</span>
            </button>
          );
        })}
      </div>
    </div>
  );
}

// ── Full stat cards (revealed when expanded) ──────────────────────────────
function FullStats(){
  return (
    <div className="pf-head">
      <div className="stat">
        <div className="lbl">Total Value</div>
        <div className="val">₹12,84,500</div>
        <div className="delta up">▲ ₹1,52,330 · 1.24% today</div>
        <svg className="spark" viewBox="0 0 400 40" preserveAspectRatio="none">
          <defs><linearGradient id="sp2x" x1="0" x2="0" y1="0" y2="1">
            <stop offset="0%" stopColor="var(--accent)" stopOpacity=".5"/>
            <stop offset="100%" stopColor="var(--accent)" stopOpacity="0"/>
          </linearGradient></defs>
          <path d="M0,30 C40,28 60,32 100,25 C140,18 180,22 220,15 C260,8 300,18 340,10 L400,5 L400,40 L0,40Z" fill="url(#sp2x)"/>
          <path d="M0,30 C40,28 60,32 100,25 C140,18 180,22 220,15 C260,8 300,18 340,10 L400,5" stroke="var(--accent)" strokeWidth="1.5" fill="none"/>
        </svg>
      </div>
      <div className="stat">
        <div className="lbl">Invested</div>
        <div className="val">₹98,20,000</div>
        <div className="delta" style={{color:"var(--fg-3)"}}>since 2021 · 34 lots</div>
      </div>
      <div className="stat">
        <div className="lbl">Unrealized P&L</div>
        <div className="val" style={{color:"var(--green)"}}>+₹30,25,000</div>
        <div className="delta up">+30.8% overall</div>
      </div>
      <div className="stat">
        <div className="lbl">XIRR</div>
        <div className="val">17.4%</div>
        <div className="delta" style={{color:"var(--fg-3)"}}>vs NIFTY 14.1%</div>
      </div>
    </div>
  );
}

// ── Outer ─────────────────────────────────────────────────────────────────
function PortfolioView(){
  const [query, setQuery]   = useState("");
  const [sector, setSector] = useState("All");
  const [pnl, setPnl]       = useState("all");           // all | up | dn
  const [sortBy, setSortBy] = useState("value");
  const [sortDir, setSortDir] = useState("desc");
  const [view, setView]     = useState("tree");
  const [source, setSource] = useState("all");           // wallet id
  const [expanded, setExpanded] = useState(false);       // compact summary toggle

  // Sector counts always reflect search+pnl+source (so chips help you see what's left).
  const counts = useMemo(() => {
    const base = HOLDINGS.filter(h => {
      if (source !== "all" && h.source !== source) return false;
      if (pnl === "up" && h.pnlAbs <= 0) return false;
      if (pnl === "dn" && h.pnlAbs >= 0) return false;
      if (query.trim()) {
        const q = query.trim().toLowerCase();
        const hit =
          h.sym.toLowerCase().includes(q) ||
          h.name.toLowerCase().includes(q) ||
          h.sector.toLowerCase().includes(q) ||
          h.region.toLowerCase().includes(q);
        if (!hit) return false;
      }
      return true;
    });
    const out = { All: base.length };
    for (const s of SECTORS) if (s !== "All") out[s] = 0;
    base.forEach(h => { out[h.sector] = (out[h.sector] || 0) + 1; });
    return out;
  }, [query, pnl, source]);

  const filtered = useMemo(() => {
    let r = HOLDINGS.filter(h => {
      if (source !== "all" && h.source !== source) return false;
      if (sector !== "All" && h.sector !== sector) return false;
      if (pnl === "up" && h.pnlAbs <= 0) return false;
      if (pnl === "dn" && h.pnlAbs >= 0) return false;
      if (query.trim()) {
        const q = query.trim().toLowerCase();
        const hit =
          h.sym.toLowerCase().includes(q) ||
          h.name.toLowerCase().includes(q) ||
          h.sector.toLowerCase().includes(q) ||
          h.region.toLowerCase().includes(q);
        if (!hit) return false;
      }
      return true;
    });
    const sortDef = SORTS.find(s => s.id === sortBy) || SORTS[0];
    const dir = sortDir === "asc" ? 1 : -1;
    r = [...r].sort((a,b) => {
      const va = sortDef.get(a), vb = sortDef.get(b);
      if (sortDef.isString) return va.localeCompare(vb) * dir;
      return (va - vb) * dir;
    });
    return r;
  }, [query, sector, pnl, source, sortBy, sortDir]);

  const totalValue = useMemo(() => filtered.reduce((s,h) => s + h.valueINR, 0), [filtered]);
  const grand = useMemo(() => HOLDINGS.reduce((s,h) => s + h.valueINR, 0), []);
  const pctOfPort = grand > 0 ? (totalValue / grand) * 100 : 0;

  const reset = () => { setQuery(""); setSector("All"); setPnl("all"); /* keep source */ };

  // Header sort handler — used by both Sort menu and ledger column headers.
  const onSort = (id, dir) => { setSortBy(id); setSortDir(dir); };

  const activeWallet = WALLETS.find(w => w.id === source);
  const showSpotlight = source !== "all";

  return (
    <>
      {/* ── Compact summary bar (always) ── */}
      <CompactSummary expanded={expanded}
                      onToggle={() => setExpanded(e => !e)}
                      source={source}
                      onSourceChange={setSource} />

      {/* ── Expanded detail: full stat cards + wallet cards ── */}
      {expanded && (
        <div className="pf-detail-expand">
          <FullStats />
          <WalletStrip source={source} onChange={setSource} />
        </div>
      )}

      <div className="pf-grid">
        <div className="pf-main">

          {/* ── Source detail banner ── */}
          {showSpotlight && (
            <SourceSpotlight wallet={activeWallet}
                             agg={walletAggregate(activeWallet)}
                             onClear={() => setSource("all")} />
          )}

          {/* ── Filter bar ── */}
          <div className="pf-filter">
            <SearchBox value={query} onChange={setQuery}/>
            <div className="pf-divider"/>
            <SectorChips value={sector} counts={counts} onChange={setSector}/>
            <div className="pf-divider"/>
            <PnLToggle value={pnl} onChange={setPnl}/>
            <SortMenu sortBy={sortBy} sortDir={sortDir} onChange={onSort}/>
            <div className="pf-divider"/>
            <ViewToggle value={view} onChange={setView}/>
          </div>

          {/* ── Result summary strip ── */}
          <div className="pf-summary">
            <span className="pf-stat">
              Showing <b>{filtered.length}</b> of {HOLDINGS.length} positions
              {source !== "all" && <> · source <b>{activeWallet.name}</b></>}
              {sector !== "All" && <> · sector <b>{sector}</b></>}
              {pnl === "up" && <> · <b style={{color:"var(--green)"}}>Gainers</b></>}
              {pnl === "dn" && <> · <b style={{color:"var(--red)"}}>Losers</b></>}
              {query && <> · matching <b>"{query}"</b></>}
            </span>
            <span className="pf-stat">
              {fmtINR(totalValue)} <span style={{color:"var(--fg-4)"}}>·</span> {pctOfPort.toFixed(1)}% of portfolio
            </span>
            {(query || sector !== "All" || pnl !== "all") && (
              <button className="pf-clearall" onClick={reset}>Clear filters ×</button>
            )}
          </div>

          {/* ── Body ── */}
          {filtered.length === 0
            ? <Empty onReset={() => { reset(); setSource("all"); }}/>
            : (view === "tree"
                ? <>
                    <Treemap items={filtered}/>
                    <div className="tm-legend">
                      <span>TODAY P&L</span>
                      <span style={{color:"var(--red)"}}>−2%</span>
                      <div className="bar"></div>
                      <span style={{color:"var(--green)"}}>+2%</span>
                      <span>· size = INR value</span>
                    </div>
                  </>
                : <Ledger items={filtered} sortBy={sortBy} sortDir={sortDir} onSort={onSort} query={query.trim()}/>)
          }
        </div>

        {/* ── Source-aware rebalance rail ── */}
        <RebalanceRail source={source} />
      </div>
    </>
  );
}

// ── Mount ─────────────────────────────────────────────────────────────────
(function(){
  const node = document.getElementById("pf-mount");
  if (node) ReactDOM.createRoot(node).render(<PortfolioView/>);
})();
