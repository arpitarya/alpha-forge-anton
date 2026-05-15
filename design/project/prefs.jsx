/* Alpha Forge — Preferences screen
   In-product settings UI mounted into #prefs-mount via React portal.
   Receives shared `t` (tweak state) + `setTweak` from the parent app so
   changes round-trip with the dev Tweaks panel and persist via host. */

const PREF_SECTIONS = [
  { id: "appearance", label: "Appearance", badge: "Theme" },
  { id: "display",    label: "Display",    badge: "Orb" },
  { id: "markets",    label: "Markets",    badge: "NSE" },
  { id: "alpha",      label: "Alpha AI",   badge: "Beta" },
  { id: "notif",      label: "Notifications" },
  { id: "account",    label: "Account" },
  { id: "privacy",    label: "Privacy" },
  { id: "about",      label: "About",      badge: "0.9.4" }
];

const ACCENTS_FULL = [
  { slug: "amber",  name: "Amber"  },
  { slug: "ion",    name: "Ion"    },
  { slug: "signal", name: "Signal" },
  { slug: "violet", name: "Violet" }
];

const ICONS = {
  appearance: <svg viewBox="0 0 24 24"><circle cx="12" cy="12" r="9"/><path d="M12 3a9 9 0 0 0 0 18M3 12h18"/></svg>,
  display:    <svg viewBox="0 0 24 24"><rect x="3" y="4" width="18" height="13" rx="2"/><path d="M8 21h8M12 17v4"/></svg>,
  markets:    <svg viewBox="0 0 24 24"><path d="M3 17l5-6 4 4 8-9"/><path d="M16 6h5v5"/></svg>,
  alpha:      <svg viewBox="0 0 24 24"><rect x="5" y="5" width="14" height="14" rx="2"/><path d="M9 9h6v6H9zM2 9h3M2 15h3M19 9h3M19 15h3M9 2v3M15 2v3M9 19v3M15 19v3"/></svg>,
  notif:      <svg viewBox="0 0 24 24"><path d="M6 8a6 6 0 0 1 12 0c0 7 3 9 3 9H3s3-2 3-9M10 21a2 2 0 0 0 4 0"/></svg>,
  account:    <svg viewBox="0 0 24 24"><circle cx="12" cy="8" r="4"/><path d="M4 21a8 8 0 0 1 16 0"/></svg>,
  privacy:    <svg viewBox="0 0 24 24"><path d="M12 3l8 4v6c0 5-4 7-8 8-4-1-8-3-8-8V7l8-4z"/><path d="M9 12l2 2 4-4"/></svg>,
  about:      <svg viewBox="0 0 24 24"><circle cx="12" cy="12" r="9"/><path d="M12 8v4M12 16h.01"/></svg>
};

// ─── Reusable controls ──────────────────────────────────────────────────────
function PSeg({ value, options, onChange }) {
  return (
    <div className="p-seg">
      {options.map(o => {
        const v = typeof o === "object" ? o.value : o;
        const l = typeof o === "object" ? o.label : o;
        return (
          <button key={v} className={value === v ? "active" : ""}
                  onClick={() => onChange(v)}>{l}</button>
        );
      })}
    </div>
  );
}
function PTog({ value, onChange }) {
  return (
    <button className={"p-tog" + (value ? " on" : "")} onClick={() => onChange(!value)}
            role="switch" aria-checked={!!value} />
  );
}
function PSlider({ value, min, max, step = 1, onChange }) {
  return (
    <div className="p-slider">
      <input type="range" min={min} max={max} step={step} value={value}
             onChange={e => onChange(Number(e.target.value))} />
    </div>
  );
}
function PSelect({ value, options, onChange }) {
  return (
    <select className="p-select" value={value} onChange={e => onChange(e.target.value)}>
      {options.map(o => {
        const v = typeof o === "object" ? o.value : o;
        const l = typeof o === "object" ? o.label : o;
        return <option key={v} value={v}>{l}</option>;
      })}
    </select>
  );
}

function PRow({ name, desc, control, tail }) {
  return (
    <div className="prow">
      <div className="pl">
        <span className="n">{name}</span>
        {desc && <span className="d">{desc}</span>}
      </div>
      <div className="pm">{control}</div>
      <div className="pt">{tail}</div>
    </div>
  );
}
function PGroup({ num, title, meta, children }) {
  return (
    <div className="pgroup">
      <div className="ghd">
        <div className="gtitle">
          {num && <span className="num">{num}</span>}
          <span>{title}</span>
        </div>
        {meta && <span className="meta">{meta}</span>}
      </div>
      {children}
    </div>
  );
}

// ─── Section panels ─────────────────────────────────────────────────────────

function AppearanceSection({ t, setTweak }) {
  return (
    <>
      <PGroup num="01" title="Theme" meta="Live preview">
        <PRow
          name="Color scheme"
          desc="Dark uses the warm-black terminal palette. Light is parchment-toned for daytime trading."
          control={
            <div className="theme-tiles">
              {["dark", "light"].map(mode => (
                <button key={mode} className={"theme-tile " + mode + (t.theme === mode ? " active" : "")}
                        onClick={() => setTweak("theme", mode)} aria-label={mode}>
                  <div className="tt-inner">
                    <div className="tt-bar"><i /><i /><i className="dot" /></div>
                    <div className="tt-row"><div /><div /><div /></div>
                  </div>
                  <span className="tt-label">{mode}</span>
                </button>
              ))}
            </div>
          }
          tail={<>Active <b>{t.theme.toUpperCase()}</b></>}
        />
        <PRow
          name="Accent color"
          desc="Tints the orb, deploy button, alerts, and HUD lines across the terminal."
          control={
            <div className="accent-picker">
              {ACCENTS_FULL.map(a => (
                <button key={a.slug} data-accent={a.slug}
                        className={"accent-sw" + (t.accent === a.slug ? " active" : "")}
                        onClick={() => setTweak("accent", a.slug)} aria-label={a.name}>
                  <span className="name">{a.name}</span>
                </button>
              ))}
            </div>
          }
          tail={<>Active <b>{(ACCENTS_FULL.find(a => a.slug === t.accent) || ACCENTS_FULL[0]).name}</b></>}
        />
      </PGroup>

      <PGroup num="02" title="Layout">
        <PRow
          name="Density"
          desc="Compact fits more data per pane. Comfy gives chart room to breathe."
          control={<PSeg value={t.density} options={["compact", "regular", "comfy"]}
                         onChange={v => setTweak("density", v)} />}
        />
        <PRow
          name="Default screen"
          desc="What loads after the boot sequence completes."
          control={<PSelect value={t.defaultScreen} options={[
              { value: "terminal",  label: "Terminal" },
              { value: "portfolio", label: "Portfolio" },
              { value: "preferences", label: "Preferences" }
            ]} onChange={v => setTweak("defaultScreen", v)} />}
        />
        <PRow
          name="Show command palette hint"
          desc="The ⌘K pill in the top bar."
          control={<PTog value={t.showCmdK} onChange={v => setTweak("showCmdK", v)} />}
          tail={<>{t.showCmdK ? "On" : "Off"}</>}
        />
      </PGroup>

      <PGroup num="03" title="Typography" meta="Space Grotesk · Space Mono">
        <PRow
          name="Type pair"
          desc="Display + monospace pair used everywhere."
          control={<PSelect value={t.typePair} options={[
              { value: "grotesk-mono", label: "Space Grotesk × Space Mono" },
              { value: "ibm-mono",     label: "IBM Plex × Plex Mono" },
              { value: "serif-mono",   label: "Fraunces × Berkeley Mono" }
            ]} onChange={v => setTweak("typePair", v)} />}
          tail={<b>Default</b>}
        />
      </PGroup>
    </>
  );
}

function DisplaySection({ t, setTweak }) {
  return (
    <>
      <PGroup num="01" title="Chrome" meta="Top + Voice bars">
        <PRow
          name="Chrome behavior"
          desc="The slim top bar and voice bar appear on every screen. Auto-hide collapses them to a thin accent line — hover to reveal."
          control={<PSeg value={t.chromeMode} options={[
              { value: "fixed",    label: "Always visible" },
              { value: "autohide", label: "Auto-hide" }
            ]} onChange={v => setTweak("chromeMode", v)} />}
          tail={<b>{t.chromeMode === "autohide" ? "Hidden" : "Visible"}</b>}
        />
        <PRow
          name="Show voice bar"
          desc="The global Alpha voice / Deploy bar at the bottom of every screen."
          control={<PTog value={t.showVoice} onChange={v => setTweak("showVoice", v)} />}
          tail={<>{t.showVoice ? "On" : "Off"}</>}
        />
      </PGroup>

      <PGroup num="02" title="Alpha orb" meta="Stage centerpiece">
        <PRow
          name="Orb size"
          desc="Diameter of the central plasma sphere on the terminal."
          control={<PSlider value={t.orbSize} min={180} max={340} step={10}
                            onChange={v => setTweak("orbSize", v)} />}
          tail={<b>{t.orbSize}px</b>}
        />
        <PRow
          name="Pulse speed"
          desc="Lower is calmer. Speed scales with system confidence on real data."
          control={<PSlider value={t.orbSpeed} min={1.5} max={6} step={0.1}
                            onChange={v => setTweak("orbSpeed", +v.toFixed(1))} />}
          tail={<b>{t.orbSpeed.toFixed(1)}s</b>}
        />
        <PRow
          name="HUD chrome"
          desc="Corner brackets, drifting stars and scanline around the orb stage."
          control={<PTog value={t.showHud} onChange={v => setTweak("showHud", v)} />}
          tail={<>{t.showHud ? "Visible" : "Hidden"}</>}
        />
      </PGroup>

      <PGroup num="03" title="Motion">
        <PRow
          name="Ticker speed"
          desc="Time for one full loop across the index ribbon."
          control={<PSlider value={t.tickerSpeed} min={15} max={90} step={1}
                            onChange={v => setTweak("tickerSpeed", v)} />}
          tail={<b>{t.tickerSpeed}s</b>}
        />
        <PRow
          name="Reduce motion"
          desc="Disables ambient pulsing, scanlines, and ticker drift. Recommended for long sessions."
          control={<PTog value={t.reduceMotion} onChange={v => setTweak("reduceMotion", v)} />}
          tail={<>{t.reduceMotion ? "On" : "Off"}</>}
        />
        <PRow
          name="Number jitter"
          desc="Live micro-flicker on watchlist prices between real ticks."
          control={<PTog value={t.numJitter} onChange={v => setTweak("numJitter", v)} />}
          tail={<>{t.numJitter ? "On" : "Off"}</>}
        />
      </PGroup>
    </>
  );
}

function MarketsSection({ t, setTweak }) {
  return (
    <>
      <PGroup num="01" title="Defaults">
        <PRow
          name="Primary exchange"
          desc="Used when you ask Alpha about a symbol without a venue."
          control={<PSelect value={t.defaultExchange} options={[
              { value: "NSE", label: "NSE — India" },
              { value: "BSE", label: "BSE — India" },
              { value: "NASDAQ", label: "NASDAQ — US" },
              { value: "NYSE", label: "NYSE — US" },
              { value: "CRYPTO", label: "Crypto · 24/7" }
            ]} onChange={v => setTweak("defaultExchange", v)} />}
        />
        <PRow
          name="Number format"
          desc="Indian uses lakh / crore grouping (12,84,500). Western uses thousands (1,284,500)."
          control={<PSeg value={t.numberFormat} options={[
              { value: "indian",  label: "Indian" },
              { value: "western", label: "Western" }
            ]} onChange={v => setTweak("numberFormat", v)} />}
        />
        <PRow
          name="Show currency in"
          desc="The currency Alpha quotes net worth and P&L in."
          control={<PSeg value={t.currency} options={["INR", "USD", "Native"]}
                         onChange={v => setTweak("currency", v)} />}
        />
        <PRow
          name="Include after-hours"
          desc="Reflect US after-hours and pre-open in your dashboard."
          control={<PTog value={t.afterHours} onChange={v => setTweak("afterHours", v)} />}
          tail={<>{t.afterHours ? "On" : "Off"}</>}
        />
      </PGroup>

      <PGroup num="02" title="Refresh">
        <PRow
          name="Tick refresh"
          desc="How often Alpha pulls fresh prices in the background."
          control={<PSeg value={t.refresh} options={[
              { value: "1s",  label: "1 s" },
              { value: "5s",  label: "5 s" },
              { value: "30s", label: "30 s" },
              { value: "manual", label: "Manual" }
            ]} onChange={v => setTweak("refresh", v)} />}
        />
      </PGroup>
    </>
  );
}

function AlphaSection({ t, setTweak }) {
  return (
    <>
      <PGroup num="01" title="Voice & assistant" meta="Neural Interface · v2">
        <PRow
          name="Voice wake"
          desc='Listen for "Hey Alpha" while the terminal is focused.'
          control={<PTog value={t.voiceWake} onChange={v => setTweak("voiceWake", v)} />}
          tail={<>{t.voiceWake ? "Listening" : "Off"}</>}
        />
        <PRow
          name="Reply style"
          desc="How Alpha narrates briefs, alerts, and rebalance suggestions."
          control={<PSeg value={t.aiPersonality} options={[
              { value: "concise",  label: "Concise" },
              { value: "balanced", label: "Balanced" },
              { value: "verbose",  label: "Verbose" }
            ]} onChange={v => setTweak("aiPersonality", v)} />}
        />
        <PRow
          name="LLM provider"
          desc="The gateway routes to your fastest provider — pin one if you want determinism."
          control={<PSelect value={t.llm} options={[
              { value: "auto",   label: "Auto · pick fastest" },
              { value: "gemini", label: "Gemini 2.5 Pro" },
              { value: "groq",   label: "Groq Llama" },
              { value: "local",  label: "Local · Ollama" }
            ]} onChange={v => setTweak("llm", v)} />}
        />
      </PGroup>

      <PGroup num="02" title="Signals & rebalance">
        <PRow
          name="Signal confidence floor"
          desc="Screener picks below this score are hidden from the brief and watchlist."
          control={<PSlider value={t.confidence} min={0.5} max={0.95} step={0.05}
                            onChange={v => setTweak("confidence", +v.toFixed(2))} />}
          tail={<b>{(t.confidence * 100).toFixed(0)}%</b>}
        />
        <PRow
          name="Auto-rebalance"
          desc="When Alpha drafts a rebalance plan automatically. You always confirm before it deploys."
          control={<PSeg value={t.autoRebalance} options={[
              { value: "off",     label: "Off" },
              { value: "weekly",  label: "Weekly" },
              { value: "monthly", label: "Monthly" }
            ]} onChange={v => setTweak("autoRebalance", v)} />}
        />
        <PRow
          name="Show ML screener picks on terminal"
          desc="If off, screener lives only inside the Portfolio rail."
          control={<PTog value={t.showScreener} onChange={v => setTweak("showScreener", v)} />}
          tail={<>{t.showScreener ? "On" : "Off"}</>}
        />
      </PGroup>
    </>
  );
}

function NotifSection({ t, setTweak }) {
  return (
    <>
      <PGroup num="01" title="In-app alerts">
        <PRow name="Price moves" desc="Toast when any watchlist symbol moves more than the threshold."
          control={<PTog value={t.notifPrice} onChange={v => setTweak("notifPrice", v)} />}
          tail={<>{t.notifPrice ? "On" : "Off"}</>} />
        <PRow name="Threshold" desc="Trigger for the price-move alert above."
          control={<PSlider value={t.priceThreshold} min={1} max={10} step={0.5}
                            onChange={v => setTweak("priceThreshold", +v.toFixed(1))} />}
          tail={<b>±{t.priceThreshold}%</b>} />
        <PRow name="Risk alerts" desc="When portfolio drift breaches your target band."
          control={<PTog value={t.notifRisk} onChange={v => setTweak("notifRisk", v)} />}
          tail={<>{t.notifRisk ? "On" : "Off"}</>} />
        <PRow name="New signals" desc="When the ML screener surfaces a new high-confidence pick."
          control={<PTog value={t.notifSignals} onChange={v => setTweak("notifSignals", v)} />}
          tail={<>{t.notifSignals ? "On" : "Off"}</>} />
      </PGroup>

      <PGroup num="02" title="Email">
        <PRow name="Email digest" desc="Summary of your day, signals, and an Alpha note."
          control={<PSeg value={t.emailDigest} options={[
            { value: "off",    label: "Off" },
            { value: "daily",  label: "Daily" },
            { value: "weekly", label: "Weekly" }]}
            onChange={v => setTweak("emailDigest", v)} />}
        />
        <PRow name="Delivery"
          control={<input className="p-input" value={t.email}
                          onChange={e => setTweak("email", e.target.value)} />}
        />
      </PGroup>
    </>
  );
}

function AccountSection({ t, setTweak }) {
  const initial = (t.userName || "A").trim().charAt(0).toUpperCase();
  return (
    <>
      <PGroup num="01" title="Profile" meta="Pro · since Apr 2024">
        <div className="acct-hero">
          <div className="avatar">{initial}</div>
          <div className="meta">
            <div className="name">{t.userName || "Trader"}</div>
            <div className="info">
              <b>arjun.k@protonmail.com</b>
              <span className="dot"></span>NODE_MUMBAI_01
              <span className="dot"></span>2FA ON
            </div>
          </div>
          <span className="badge-pro">★ Pro</span>
        </div>
        <PRow name="Display name" desc="Shown in the top bar and on Alpha's spoken replies."
          control={<input className="p-input" value={t.userName}
                          onChange={e => setTweak("userName", e.target.value)} />}
        />
        <PRow name="Status label" desc="The tagline next to the live dot in the top bar."
          control={<input className="p-input" value={t.statusLabel}
                          onChange={e => setTweak("statusLabel", e.target.value)} />}
        />
      </PGroup>

      <PGroup num="02" title="Connected brokers">
        <div className="broker">
          <div className="b-ico kite">KT</div>
          <div>
            <div className="b-name">Zerodha · Kite</div>
            <div className="b-sub">Equity · F&O · MF · 12 positions synced</div>
          </div>
          <span className="b-stat on"><span className="b-dot" /> Connected</span>
          <button className="b-link muted">Manage</button>
        </div>
        <div className="broker">
          <div className="b-ico coin">CB</div>
          <div>
            <div className="b-name">Coinbase</div>
            <div className="b-sub">Crypto · 4 holdings</div>
          </div>
          <span className="b-stat on"><span className="b-dot" /> Connected</span>
          <button className="b-link muted">Manage</button>
        </div>
        <div className="broker">
          <div className="b-ico fyer">FY</div>
          <div>
            <div className="b-name">Fyers</div>
            <div className="b-sub">Not connected</div>
          </div>
          <span className="b-stat off">— Idle</span>
          <button className="b-link">Connect</button>
        </div>
      </PGroup>

      <PGroup num="03" title="Hotkeys">
        <PRow name="Command palette" control={<div className="p-keys"><span className="key">⌘</span><span className="plus">+</span><span className="key">K</span></div>} />
        <PRow name="Toggle terminal" control={<div className="p-keys"><span className="key">⌘</span><span className="plus">+</span><span className="key">1</span></div>} />
        <PRow name="Toggle portfolio" control={<div className="p-keys"><span className="key">⌘</span><span className="plus">+</span><span className="key">2</span></div>} />
        <PRow name="Open preferences" control={<div className="p-keys"><span className="key">⌘</span><span className="plus">+</span><span className="key">,</span></div>} />
        <PRow name="Activate Alpha voice" control={<div className="p-keys"><span className="key">Space</span><span className="plus">(hold)</span></div>} />
      </PGroup>
    </>
  );
}

function PrivacySection({ t, setTweak }) {
  return (
    <>
      <PGroup num="01" title="Telemetry">
        <PRow name="Anonymous usage analytics"
          desc="Helps us tune which screens are slow. No order data or holdings are ever sent."
          control={<PTog value={t.telemetry} onChange={v => setTweak("telemetry", v)} />}
          tail={<>{t.telemetry ? "On" : "Off"}</>} />
        <PRow name="Crash reports"
          desc="Send stack traces when the terminal crashes."
          control={<PTog value={t.crashReports} onChange={v => setTweak("crashReports", v)} />}
          tail={<>{t.crashReports ? "On" : "Off"}</>} />
        <PRow name="Share trades with Alpha for training"
          desc="Off by default. Your fills never leave the local DB unless you turn this on."
          control={<PTog value={t.shareTrades} onChange={v => setTweak("shareTrades", v)} />}
          tail={<>{t.shareTrades ? "Shared" : "Local only"}</>} />
      </PGroup>

      <PGroup num="02" title="Data">
        <PRow name="Local history retention"
          desc="How long to keep tick history and chat transcripts on this machine."
          control={<PSelect value={t.retention} options={[
            { value: "30",  label: "30 days" },
            { value: "90",  label: "90 days" },
            { value: "365", label: "1 year" },
            { value: "all", label: "Forever" }
          ]} onChange={v => setTweak("retention", v)} />}
        />
        <PRow name="Clear cache" desc="Wipes local screener features, sparkline buffers, and ticker history."
          control={<button className="p-danger">Clear local cache</button>} />
        <PRow name="Sign out everywhere"
          desc="Revokes broker tokens and signs you out of every device."
          control={<button className="p-danger">Sign out all sessions</button>} />
      </PGroup>
    </>
  );
}

function AboutSection() {
  return (
    <PGroup num="01" title="Alpha Forge" meta="v0.9.4 · alpha">
      <PRow name="Build" desc="Latest deploy to your terminal."
        control={<span className="p-input" style={{ width: "auto", display: "inline-flex" }}>0.9.4-alpha · 2026-05-12</span>}
        tail={<b>Stable</b>} />
      <PRow name="Backend" desc="FastAPI on :8000"
        control={<span className="p-input" style={{ width: "auto", display: "inline-flex" }}>node_mumbai_01 · 8ms</span>}
        tail={<b>Online</b>} />
      <PRow name="License"
        control={<span className="p-input" style={{ width: "auto", display: "inline-flex" }}>Pro — seat #00142</span>}
        tail={<b>Valid</b>} />
      <PRow name="Documentation"
        control={<a className="b-link" href="#" onClick={e => e.preventDefault()}>Open docs →</a>} />
      <PRow name="Reset all preferences"
        desc="Restores every setting on this page to its default. Account and broker connections are kept."
        control={<button className="p-danger" id="prefs-reset-btn">Reset preferences</button>} />
    </PGroup>
  );
}

// ─── Outer screen ───────────────────────────────────────────────────────────

function PreferencesScreen({ t, setTweak, onReset }) {
  const [active, setActive] = React.useState("appearance");
  const [saved, setSaved] = React.useState(false);
  const lastEditRef = React.useRef(0);

  // Tiny "saved" pulse whenever t changes.
  React.useEffect(() => {
    lastEditRef.current = Date.now();
    setSaved(true);
    const id = setTimeout(() => {
      if (Date.now() - lastEditRef.current >= 900) setSaved(false);
    }, 1000);
    return () => clearTimeout(id);
  }, [t]);

  const sec = PREF_SECTIONS.find(s => s.id === active) || PREF_SECTIONS[0];

  let pane = null;
  switch (active) {
    case "appearance": pane = <AppearanceSection t={t} setTweak={setTweak} />; break;
    case "display":    pane = <DisplaySection    t={t} setTweak={setTweak} />; break;
    case "markets":    pane = <MarketsSection    t={t} setTweak={setTweak} />; break;
    case "alpha":      pane = <AlphaSection      t={t} setTweak={setTweak} />; break;
    case "notif":      pane = <NotifSection      t={t} setTweak={setTweak} />; break;
    case "account":    pane = <AccountSection    t={t} setTweak={setTweak} />; break;
    case "privacy":    pane = <PrivacySection    t={t} setTweak={setTweak} />; break;
    case "about":      pane = <AboutSection />;                                break;
  }

  return (
    <>
      <aside className="prefs-side">
        <div className="ph">
          <div className="eyebrow">· SYSTEM</div>
          <div className="h">Preferences</div>
          <div className="sub">v0.9.4 · LIVE</div>
        </div>
        {PREF_SECTIONS.map(s => (
          <button key={s.id}
                  className={"prefs-tab" + (active === s.id ? " active" : "")}
                  onClick={() => setActive(s.id)}>
            {ICONS[s.id]}
            <span>{s.label}</span>
            {s.badge && <span className="badge">{s.badge}</span>}
          </button>
        ))}
        <div className="foot">
          <div><span className="k">SEAT</span> <span className="v">#00142</span></div>
          <div><span className="k">TIER</span> <span className="v">PRO</span></div>
          <div><span className="k">NODE</span> <span className="v">MUMBAI_01</span></div>
        </div>
      </aside>

      <div className="prefs-main">
        <div className="prefs-topline">
          <div className="crumb">PREFERENCES · <b>{sec.label.toUpperCase()}</b></div>
          <div className="acts">
            <span className={"saved" + (saved ? " on" : "")}>
              <span className="blob" />Saved
            </span>
            <button className="pbtn" onClick={onReset}>Reset section</button>
          </div>
        </div>
        <div className="prefs-pane">
          {pane}
        </div>
      </div>
    </>
  );
}

window.AlphaForgePrefs = PreferencesScreen;
