"""Goals module — read-only API for the editable north-star (Goals tab).

Serves the elgar-stored program mandate (`Objective`) and the edge-library funnel
(aggregated discovery journal). Mounts at root: `/mandate`, `/edges/summary`.
"""

from app.modules.goals.goals_routes import router

__all__ = ["router"]
