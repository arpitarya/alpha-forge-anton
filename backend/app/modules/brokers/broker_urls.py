"""CDP trigger-page URLs and XHR needle strings for every broker adapter.

Import what you need:
    from app.modules.brokers._urls import GROWW_HOLDINGS_PAGE, GROWW_HOLDINGS_URL_NEEDLES
"""

# ── Zerodha ──────────────────────────────────────────────────────────────────
ZERODHA_KITE_BASE = "https://kite.zerodha.com"
ZERODHA_LOGIN_URL = "https://kite.zerodha.com/"
ZERODHA_HOLDINGS_PATH = "/oms/portfolio/holdings"
ZERODHA_MARGINS_PATH = "/oms/user/margins"
ZERODHA_COIN_HOLDINGS_PATH = "/oms/mf/holdings"

# ── Groww ─────────────────────────────────────────────────────────────────────
GROWW_HOLDINGS_PAGE = "https://groww.in/stocks/user/holdings"
GROWW_LOGIN_URL = "https://groww.in/login"
GROWW_HOLDINGS_URL_NEEDLES = ("/v2/api/stocks/holdings/all", "/user/holdings")
GROWW_LTP_URL_NEEDLE = "/tr_live/segment/CASH/latest_aggregated"
GROWW_BALANCE_PAGE = "https://groww.in/user/balance/inr"
GROWW_BALANCE_URL_NEEDLES = (
    "/margin/user_margin_details",
)

# ── Angel One ─────────────────────────────────────────────────────────────────
ANGELONE_HOLDINGS_PAGE = "https://www.angelone.in/trade/portfolio/equity"
ANGELONE_LOGIN_URL = "https://www.angelone.in/login"
ANGELONE_HOLDINGS_URL_NEEDLE = "/family/v2/superportfolio"
ANGELONE_FUNDS_PAGE = "https://www.angelone.in/trade/funds"
ANGELONE_RMS_URL_NEEDLE = "/funds/v2/getRMSLimit"

# ── INDmoney ──────────────────────────────────────────────────────────────────
INDMONEY_HOLDINGS_PAGE = "https://www.indmoney.com/investments/us-stocks/my-us-stocks"
INDMONEY_LOGIN_URL = "https://www.indmoney.com/login"
INDMONEY_HOLDINGS_URL_NEEDLE = "/stocks/dw/user/account/holdings"
INDMONEY_BALANCE_PAGE = INDMONEY_HOLDINGS_PAGE
INDMONEY_BALANCE_URL_NEEDLE = "/stocks/dw/user/account/basic"

# ── Binance ───────────────────────────────────────────────────────────────────
BINANCE_HOLDINGS_PAGE = "https://www.binance.com/en/my/wallet/account/main"
BINANCE_LOGIN_URL = "https://accounts.binance.com/en/login"
BINANCE_HOLDINGS_URL_NEEDLES = (
    "/bapi/asset/v3/private/asset-service/asset/get-user-asset",
)
BINANCE_BALANCE_PAGE = BINANCE_HOLDINGS_PAGE
BINANCE_BALANCE_URL_NEEDLES = (
    "/bapi/accounts/v1/private/account/user/base-detail",
    "/bapi/asset/v2/private/asset-service/wallet/balance",
)

# ── Zerodha Coin (MF) ────────────────────────────────────────────────────────
ZERODHA_COIN_DASHBOARD = "https://coin.zerodha.com/dashboard"
# ZERODHA_COIN_HOLDINGS_PATH is defined above under the Kite constants.

# ── Ticker Tape ───────────────────────────────────────────────────────────────
TICKERTAPE_GOLD_PAGE = "https://www.tickertape.in/portfolio/digital-gold"
TICKERTAPE_LOGIN_URL = "https://www.tickertape.in/login"
TICKERTAPE_GOLD_PROFILE_NEEDLE = "gold.api.tickertape.in/profile/v2"
TICKERTAPE_GOLD_PRICE_NEEDLE = "gold.api.tickertape.in/price?"
