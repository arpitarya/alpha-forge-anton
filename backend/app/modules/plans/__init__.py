"""Plans module — the plan store plane: loader, drift, REST endpoints.

Plan documents live in the private elgar store (`ELGAR_DIR`); this module reads
them, joins them with live actuals, and serves percentages-only results.
"""

from app.modules.plans.plan_routes import router

__all__ = ["router"]
