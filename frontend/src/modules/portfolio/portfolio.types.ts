export type AssetClass =
  | "equity"
  | "mutual_fund"
  | "etf"
  | "bond"
  | "gold"
  | "crypto"
  | "cash"
  | "other";

export interface HoldingDTO {
  source: string;
  asset_class: AssetClass;
  symbol: string;
  name: string | null;
  isin: string | null;
  quantity: number;
  avg_price: number;
  last_price: number;
  invested: number;
  current_value: number;
  pnl: number;
  pnl_pct: number;
  currency: string;
  exchange: string | null;
  sector: string | null;
  as_of: string;
}

export interface AllocationSliceDTO {
  asset_class: AssetClass;
  value: number;
  pct: number;
}

export interface PortfolioTotalsDTO {
  invested: number;
  current_value: number;
  pnl: number;
  pnl_pct: number;
  count: number;
}

export interface HoldingsResponseDTO {
  totals: PortfolioTotalsDTO;
  allocation: AllocationSliceDTO[];
  holdings: HoldingDTO[];
}

export interface TreemapCellDTO {
  symbol: string;
  sublabel: string;
  value: number;
  pct: number;
  pnl: number;
  pnl_pct: number;
  asset_class: AssetClass;
  left_pct: number;
  top_pct: number;
  width_pct: number;
  height_pct: number;
}

export interface TreemapResponseDTO {
  totals: PortfolioTotalsDTO;
  cells: TreemapCellDTO[];
}

export interface RebalanceResponseDTO {
  drift: Array<{
    asset_class: AssetClass;
    target_pct: number;
    actual_pct: number;
    drift_pct: number;
  }>;
  suggestions: Array<{ action: string }>;
  targets: Record<string, number>;
}

export type SourceKind = "api";
export type SourceStatus = "unconfigured" | "ready" | "syncing" | "error";

export interface SourceInfoDTO {
  slug: string;
  label: string;
  kind: SourceKind;
  status: SourceStatus;
  holdings_count: number;
  last_synced_at: string | null;
  error_message: string | null;
  notes: string | null;
}

export interface SyncAllResultDTO {
  results: Record<string, { ok: boolean; count?: number; error?: string }>;
  totals: PortfolioTotalsDTO;
}

export interface WalletInfoDTO {
  slug: string;
  label: string;
  supports_cash: boolean;
  cash: number;
  currency: string;
  cash_available: boolean;
  cash_error: string | null;
  cash_as_of: string | null;
  holdings_value: number;
  holdings_count: number;
  pnl: number;
  pnl_pct: number;
  last_synced_at: string | null;
}

export interface WalletsResponseDTO {
  wallets: WalletInfoDTO[];
}
