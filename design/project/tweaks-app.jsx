/* Alpha Forge — Tweaks panel app
   Single React root that owns the Tweaks dev panel AND renders the
   in-product Preferences screen (via portal into #prefs-mount).
   Both surfaces share the same useTweaks state so changes round-trip. */

const TWEAK_DEFAULTS = /*EDITMODE-BEGIN*/{
  "theme": "dark",
  "accent": "amber",
  "density": "regular",
  "orbSize": 260,
  "orbSpeed": 3.4,
  "tickerSpeed": 48,
  "showHud": true,
  "reduceMotion": false,
  "numJitter": true,
  "userName": "ARJUN",
  "statusLabel": "LIVE · NSE",
  "email": "arjun.k@protonmail.com",
  "defaultScreen": "terminal",
  "showCmdK": true,
  "typePair": "grotesk-mono",
  "defaultExchange": "NSE",
  "numberFormat": "indian",
  "currency": "INR",
  "afterHours": false,
  "refresh": "5s",
  "voiceWake": true,
  "aiPersonality": "balanced",
  "llm": "auto",
  "confidence": 0.75,
  "autoRebalance": "weekly",
  "showScreener": true,
  "notifPrice": true,
  "priceThreshold": 2.5,
  "notifRisk": true,
  "notifSignals": true,
  "emailDigest": "daily",
  "telemetry": true,
  "crashReports": true,
  "shareTrades": false,
  "retention": "90",
  "chromeMode": "fixed",
  "showVoice": true
}/*EDITMODE-END*/;

const ACCENTS = [
  { slug: "amber",  hex: "#ff8f00", name: "Amber"  },
  { slug: "ion",    hex: "#2ee7c2", name: "Ion"    },
  { slug: "signal", hex: "#ff3d5c", name: "Signal" },
  { slug: "violet", hex: "#a678ff", name: "Violet" }
];

function AlphaForgeApp() {
  const [t, setTweak] = useTweaks(TWEAK_DEFAULTS);
  const [portalReady, setPortalReady] = React.useState(false);

  // Wait for the prefs mount node to exist (it lives inside an HTML section,
  // so it's there on first paint — but guard in case scripts order shifts).
  React.useEffect(() => {
    const tryMount = () => {
      if (document.getElementById("prefs-mount")) setPortalReady(true);
      else requestAnimationFrame(tryMount);
    };
    tryMount();
  }, []);

  // Apply state to the DOM each time t changes.
  React.useEffect(() => {
    const root = document.documentElement;
    root.dataset.theme = t.theme;
    root.dataset.accent = t.accent;
    root.dataset.density = t.density;
    root.style.setProperty("--orb-size", t.orbSize + "px");
    root.style.setProperty("--orb-speed", t.orbSpeed + "s");
    root.style.setProperty("--ticker-speed", t.tickerSpeed + "s");
    document.body.classList.toggle("reduce-motion", !!t.reduceMotion);
    document.body.classList.toggle("hide-hud", !t.showHud);
    document.body.classList.toggle("chrome-autohide", t.chromeMode === "autohide");
    document.body.classList.toggle("no-voice", !t.showVoice);
    root.dataset.numJitter = t.numJitter ? "on" : "off";

    const userEl = document.getElementById("userName");
    if (userEl) userEl.textContent = "◉ " + (t.userName || "");
    const statusEl = document.getElementById("statusLabel");
    if (statusEl) {
      statusEl.innerHTML = "";
      const dot = document.createElement("span");
      dot.className = "dot";
      statusEl.appendChild(dot);
      statusEl.appendChild(document.createTextNode(t.statusLabel || ""));
    }
    // ⌘K pill visibility
    document.querySelectorAll(".top-right .kbd").forEach(el => {
      el.style.display = t.showCmdK ? "" : "none";
    });
  }, [t]);

  const resetAll = React.useCallback(() => {
    setTweak({ ...TWEAK_DEFAULTS });
  }, [setTweak]);

  // Wire the "Reset preferences" danger button inside the About section
  // (rendered by prefs.jsx — we listen at document level so we don't need to
  // thread the callback through every section).
  React.useEffect(() => {
    const onClick = (e) => {
      if (e.target && e.target.id === "prefs-reset-btn") resetAll();
    };
    document.addEventListener("click", onClick);
    return () => document.removeEventListener("click", onClick);
  }, [resetAll]);

  const accentMeta = ACCENTS.find(a => a.slug === t.accent) || ACCENTS[0];

  const Prefs = window.AlphaForgePrefs;
  const mount = portalReady && document.getElementById("prefs-mount");

  return (
    <>
      {/* In-product Preferences screen — rendered via portal */}
      {mount && Prefs && ReactDOM.createPortal(
        <Prefs t={t} setTweak={setTweak} onReset={resetAll} />,
        mount
      )}

      {/* Dev Tweaks panel (toolbar toggle) */}
      <TweaksPanel title="Tweaks">
        <TweakSection label="Quick" />
        <TweakRadio label="Theme" value={t.theme} options={["dark", "light"]}
                    onChange={v => setTweak("theme", v)} />

        <div className="twk-row">
          <div className="twk-lbl">
            <span>Accent</span>
            <span className="twk-val">{accentMeta.name}</span>
          </div>
          <div style={{ display: "flex", gap: 8, paddingTop: 2 }}>
            {ACCENTS.map(a => {
              const active = t.accent === a.slug;
              return (
                <button key={a.slug} title={a.name}
                  onClick={() => setTweak("accent", a.slug)}
                  style={{
                    width: 26, height: 26, borderRadius: "50%",
                    background: a.hex,
                    border: active ? "2px solid #29261b" : ".5px solid rgba(0,0,0,.18)",
                    boxShadow: active ? "0 0 0 2px rgba(255,255,255,.7), 0 0 12px " + a.hex + "55" : "none",
                    cursor: "pointer", padding: 0, transition: "transform .15s"
                  }} />
              );
            })}
          </div>
        </div>

        <TweakRadio label="Density" value={t.density}
                    options={["compact", "regular", "comfy"]}
                    onChange={v => setTweak("density", v)} />

        <TweakSection label="Orb" />
        <TweakSlider label="Size" value={t.orbSize} min={180} max={340} step={10} unit="px"
                     onChange={v => setTweak("orbSize", v)} />
        <TweakSlider label="Pulse" value={t.orbSpeed} min={1.5} max={6} step={0.1} unit="s"
                     onChange={v => setTweak("orbSpeed", +v.toFixed(1))} />
        <TweakToggle label="HUD chrome" value={t.showHud}
                     onChange={v => setTweak("showHud", v)} />

        <TweakSection label="Chrome" />
        <TweakRadio label="Top + voice" value={t.chromeMode}
                    options={[{value:"fixed",label:"Fixed"},{value:"autohide",label:"Auto-hide"}]}
                    onChange={v => setTweak("chromeMode", v)} />
        <TweakToggle label="Voice bar" value={t.showVoice}
                     onChange={v => setTweak("showVoice", v)} />

        <TweakSection label="Motion" />
        <TweakSlider label="Ticker" value={t.tickerSpeed} min={15} max={90} step={1} unit="s"
                     onChange={v => setTweak("tickerSpeed", v)} />
        <TweakToggle label="Reduce motion" value={t.reduceMotion}
                     onChange={v => setTweak("reduceMotion", v)} />

        <TweakSection label="Identity" />
        <TweakText label="User" value={t.userName}
                   onChange={v => setTweak("userName", v)} />
        <TweakText label="Status" value={t.statusLabel}
                   onChange={v => setTweak("statusLabel", v)} />

        <p style={{ margin: "10px 2px 0", fontSize: 10.5, color: "rgba(41,38,27,.55)", lineHeight: 1.5 }}>
          Full settings live in <b>Preferences</b> in the app.
        </p>
      </TweaksPanel>
    </>
  );
}

(function mount() {
  const host = document.createElement("div");
  host.id = "tweaks-root";
  document.body.appendChild(host);
  ReactDOM.createRoot(host).render(<AlphaForgeApp />);
})();
