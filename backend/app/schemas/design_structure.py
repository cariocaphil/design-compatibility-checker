"""The implementation-neutral design representation (PROJECT_SPEC.md section 11).

`DesignStructure` is the common representation that both input paths (screenshot
vision analysis and Figma normalization) converge on. It must remain independent
of any target component library (PROJECT_SPEC.md section 3).

Dividers/separators are represented as `DesignElement` entries (e.g.
`visual_role="divider"`) rather than as a dedicated model. n8n's original
`Separator` shape (`associatedLabel`, `associatedGroup`) turned out to duplicate
`DesignElement.visible_text` and `DesignGroup.children` once analyzed as domain
concepts rather than JSON-schema artifacts; only the genuinely new properties
(`orientation`, `continuity`, `associated_icon`) were added to `DesignElement`,
as optional metadata that is populated for divider-like elements and left `None`
otherwise. See the PR 2 plan's Discrepancies section for the full rationale.

`confidence` fields throughout this module are diagnostic/monitoring metadata
describing how certain the vision-analysis stage was about a given observation.
This module does not consume them with any logic; later PRs decide whether and
how to act on them. `LayoutDescription` intentionally has no `confidence` field:
it is a single aggregate synthesis per `DesignStructure`, not a discrete,
itemized observation.
"""

from typing import Literal

from pydantic import BaseModel, Field

from app.schemas.common import Confidence


class LayoutDescription(BaseModel):
    """Overall page layout: structure, regions, spacing, alignment, responsive hints."""

    overall_structure: str
    regions: list[str] = Field(default_factory=list)
    spacing: str | None = None
    alignment: str | None = None
    responsive_hints: str | None = None


class DesignGroup(BaseModel):
    """A visually/semantically cohesive grouping of elements or other groups."""

    id: str
    type: str
    children: list[str] = Field(default_factory=list)
    confidence: Confidence


class DesignElement(BaseModel):
    """An atomic visible UI element, or a divider/separator.

    A divider is a `DesignElement` with `visual_role="divider"` and
    `orientation`/`continuity`/`associated_icon` populated; ordinary elements
    leave those three fields `None`.
    """

    id: str
    visual_role: str
    visible_text: str | None = None
    state: str | None = None
    interaction_hint: str | None = None
    orientation: str | None = None
    continuity: str | None = None
    associated_icon: str | None = None
    confidence: Confidence


class RepeatedStructure(BaseModel):
    """A repeated visual pattern (e.g. a list of cards or rows)."""

    id: str
    item_type: str
    item_count: int = Field(ge=0)
    visible_items: list[str] = Field(default_factory=list)
    shared_style: str | None = None
    interaction_pattern: str | None = None
    state: str | None = None
    confidence: Confidence


class Relationship(BaseModel):
    """An arbitrary typed link between two visible structures (by id)."""

    source: str
    target: str
    relationship: str
    confidence: Confidence


class CustomPattern(BaseModel):
    """A visually meaningful structure that doesn't fit cleanly into the other categories."""

    type: str
    description: str
    confidence: Confidence


class DesignStructure(BaseModel):
    """The common, implementation-neutral design representation.

    `source` is optional provenance metadata (which input path produced this
    structure); downstream logic may ignore it, but it is needed to satisfy
    PROJECT_SPEC.md section 22's requirement to show the original screenshot
    for screenshot-derived reports.
    """

    layout: LayoutDescription
    groups: list[DesignGroup] = Field(default_factory=list)
    elements: list[DesignElement] = Field(default_factory=list)
    repeated_structures: list[RepeatedStructure] = Field(default_factory=list)
    relationships: list[Relationship] = Field(default_factory=list)
    custom_patterns: list[CustomPattern] = Field(default_factory=list)
    source: Literal["screenshot", "figma"] | None = None
