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
    ui-objective         ui_objective_probe.py
    ui-footer-chat       ui_footer_chat_probe.py
    ui-model-picker      ui_model_picker_probe.py
    ui-notif-time        ui_notification_time_probe.py
    ui-voice             ui_voice_probe.py
    ui-deep-search       ui_deep_search_probe.py

  Fux probes (standalone, no CDP required):
    fux-graph            ui_fux_graph_probe.py
    plan-safety          plan_safety_probe.py
    holdings-disclosure  holdings_disclosure_probe.py
    memory-context       memory_context_probe.py
    context-drift        context_drift_probe.py
    claude-stream        claude_stream_probe.py
    claude-cache         claude_cache_probe.py
    claude-tiering       claude_tiering_probe.py
    plan-api             plan_api_probe.py
    compose-registry     compose_registry_probe.py
    concierge-events     concierge_events_probe.py
    claude-import        claude_import_probe.py
    plan-projection      plan_projection_probe.py
    parallel-keys        parallel_keys_probe.py
    deep-search          deep_search_probe.py
    signals-review       signals_review_probe.py
    signals-screen       signals_screen_probe.py
    signals-replan       signals_replan_probe.py
    signals-pnl          signals_pnl_probe.py
    signals-backtest     signals_backtest_probe.py
    objective            objective_probe.py
    concierge-tools      concierge_tools_probe.py

  Release-health probes (require CDP :9299):
    pypi-publish         pypi_publish_probe.py
    github-publish       github_publish_probe.py

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
    ui-objective)      SCRIPT="ui_objective_probe.py" ;;
    ui-footer-chat)    SCRIPT="ui_footer_chat_probe.py" ;;
    ui-model-picker)   SCRIPT="ui_model_picker_probe.py" ;;
    ui-notif-time)     SCRIPT="ui_notification_time_probe.py" ;;
    ui-voice)          SCRIPT="ui_voice_probe.py" ;;
    ui-deep-search)    SCRIPT="ui_deep_search_probe.py" ;;
    fux-graph)         SCRIPT="ui_fux_graph_probe.py" ;;
    plan-safety)       SCRIPT="plan_safety_probe.py" ;;
    holdings-disclosure) SCRIPT="holdings_disclosure_probe.py" ;;
    memory-context)    SCRIPT="memory_context_probe.py" ;;
    context-drift)     SCRIPT="context_drift_probe.py" ;;
    claude-stream)     SCRIPT="claude_stream_probe.py" ;;
    claude-cache)      SCRIPT="claude_cache_probe.py" ;;
    claude-tiering)    SCRIPT="claude_tiering_probe.py" ;;
    plan-api)          SCRIPT="plan_api_probe.py" ;;
    compose-registry)  SCRIPT="compose_registry_probe.py" ;;
    concierge-events)  SCRIPT="concierge_events_probe.py" ;;
    claude-import)     SCRIPT="claude_import_probe.py" ;;
    plan-projection)   SCRIPT="plan_projection_probe.py" ;;
    parallel-keys)     SCRIPT="parallel_keys_probe.py" ;;
    deep-search)       SCRIPT="deep_search_probe.py" ;;
    signals-review)    SCRIPT="signals_review_probe.py" ;;
    signals-screen)    SCRIPT="signals_screen_probe.py" ;;
    signals-replan)    SCRIPT="signals_replan_probe.py" ;;
    signals-pnl)       SCRIPT="signals_pnl_probe.py" ;;
    signals-backtest)  SCRIPT="signals_backtest_probe.py" ;;
    objective)         SCRIPT="objective_probe.py" ;;
    concierge-tools)   SCRIPT="concierge_tools_probe.py" ;;
    pypi-publish)      SCRIPT="pypi_publish_probe.py" ;;
    github-publish)    SCRIPT="github_publish_probe.py" ;;
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
