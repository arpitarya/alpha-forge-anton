#!/usr/bin/env bash
# Dispatch to a probe script by name.
# Usage: bash probes/probe.sh <name>
#        bash probes/probe.sh          (lists available probes)

set -euo pipefail

PROBES_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

list_probes() {
    cat <<'EOF'
Available probes:

  UI probes (require CDP :9299):
    ui                   ui_probe.py
    ui-portfolio         ui_portfolio_probe.py
    ui-screens           ui_screens.py
    ui-pref-tabs         ui_pref_tabs.py
    ui-concierge         ui_concierge_probe.py
    ui-footer-chat       ui_footer_chat_probe.py
    ui-model-picker      ui_model_picker_probe.py
    ui-notif-time        ui_notification_time_probe.py
    ui-voice             ui_voice_probe.py

  Fux probes (standalone, no CDP required):
    fux-graph            ui_fux_graph_probe.py

  Broker XHR probes (require CDP :9299):
    zerodha              zerodha_probe.py
    zerodha-coin         zerodha_coin_probe.py
    zerodha-cash         zerodha_cash_probe.py
    groww                groww_probe.py
    groww-cash           groww_cash_probe.py
    angelone             angelone_probe.py
    angelone-cash        angelone_cash_probe.py
    indmoney             indmoney_probe.py
    indmoney-cash        indmoney_cash_probe.py
    binance              binance_probe.py
    binance-cash         binance_cash_probe.py
    tickertape           tickertape_probe.py
    gullak               gullak_probe.py

Usage:  just probe <name>
Chrome: just zerodha-chrome   (open CDP browser before running probes)
EOF
}

NAME="${1:-}"

if [[ -z "$NAME" ]]; then
    list_probes
    exit 0
fi

case "$NAME" in
    ui)                SCRIPT="ui_probe.py" ;;
    ui-portfolio)      SCRIPT="ui_portfolio_probe.py" ;;
    ui-screens)        SCRIPT="ui_screens.py" ;;
    ui-pref-tabs)      SCRIPT="ui_pref_tabs.py" ;;
    ui-concierge)      SCRIPT="ui_concierge_probe.py" ;;
    ui-footer-chat)    SCRIPT="ui_footer_chat_probe.py" ;;
    ui-model-picker)   SCRIPT="ui_model_picker_probe.py" ;;
    ui-notif-time)     SCRIPT="ui_notification_time_probe.py" ;;
    ui-voice)          SCRIPT="ui_voice_probe.py" ;;
    fux-graph)         SCRIPT="ui_fux_graph_probe.py" ;;
    zerodha)           SCRIPT="zerodha_probe.py" ;;
    zerodha-coin)      SCRIPT="zerodha_coin_probe.py" ;;
    zerodha-cash)      SCRIPT="zerodha_cash_probe.py" ;;
    groww)             SCRIPT="groww_probe.py" ;;
    groww-cash)        SCRIPT="groww_cash_probe.py" ;;
    angelone)          SCRIPT="angelone_probe.py" ;;
    angelone-cash)     SCRIPT="angelone_cash_probe.py" ;;
    indmoney)          SCRIPT="indmoney_probe.py" ;;
    indmoney-cash)     SCRIPT="indmoney_cash_probe.py" ;;
    binance)           SCRIPT="binance_probe.py" ;;
    binance-cash)      SCRIPT="binance_cash_probe.py" ;;
    tickertape)        SCRIPT="tickertape_probe.py" ;;
    gullak)            SCRIPT="gullak_probe.py" ;;
    *)
        echo "❌ Unknown probe: '$NAME'" >&2
        echo "" >&2
        list_probes >&2
        exit 1
        ;;
esac

FULL_PATH="$PROBES_DIR/$SCRIPT"

if [[ ! -f "$FULL_PATH" ]]; then
    echo "❌ Probe script not found: $FULL_PATH" >&2
    exit 1
fi

echo "▶ Running probe: $NAME  ($SCRIPT)"
uv run python "$FULL_PATH"
