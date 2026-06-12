"""Schemas for the plans module — save-to-store and projection payloads."""

from __future__ import annotations

from datetime import date

from pydantic import BaseModel, Field


class PlanSaveRequest(BaseModel):
    """A plan document headed for the private elgar store — full content allowed
    (figures included); it never touches this repo. See `plan-store`."""

    title: str = Field(min_length=1, max_length=120)
    content: str = Field(min_length=1, max_length=200_000)
    plan_id: str | None = None  # derived from title when omitted


class PlanSaveResponse(BaseModel):
    ref: str  # elgar://plan/<id>
    plan_id: str


def frontmatter(plan_id: str, title: str) -> str:
    """Standard store-doc frontmatter (same dialect as Fux entries)."""
    today = date.today().isoformat()
    return (f"---\nid: {plan_id}\nstatus: draft\ncreated: {today}\n"
            f"updated: {today}\nsource: orff\n---\n# {title}\n\n")
