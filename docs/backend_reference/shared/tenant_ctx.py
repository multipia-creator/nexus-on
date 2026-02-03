from __future__ import annotations

from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class TenantCtx:
    """Tenant context for multi-tenant key routing."""

    org_id: str
    project_id: str

    @staticmethod
    def from_headers(
        x_org_id: Optional[str],
        x_project_id: Optional[str],
        *,
        default_org: str = "default",
        default_project: str = "default",
    ) -> "TenantCtx":
        org = (x_org_id or "").strip() or default_org
        proj = (x_project_id or "").strip() or default_project
        return TenantCtx(org_id=org, project_id=proj)

    def as_dict(self) -> dict:
        return {"org_id": self.org_id, "project_id": self.project_id}
