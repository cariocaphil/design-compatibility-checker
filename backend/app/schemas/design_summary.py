"""The deterministic, reduced projection consumed by compatibility matching.

`DesignSummary` reduces `DesignStructure` + `SemanticAnalysis` to the
information necessary for compatibility matching while preserving
implementation-relevant structure (PROJECT_SPEC.md section 16). This module
only defines the `DesignSummary` *shape*; the transformation that produces one
is PR 6's "Summary Projection" responsibility, which must be deterministic
Python with no LLM call.

Every model in this module is deliberately trimmed relative to its
`design_structure`/`semantic_analysis` counterpart, and none of them carry a
`confidence` field -- this is a uniform rule for the whole module, not an
artifact of which fields happened to get trimmed. Whatever role confidence
ends up playing in how PR 6 builds a `DesignSummary` (if any) is not re-exposed
to the compatibility matcher.

`SummaryGroup` and `SummaryAmbiguousPattern` exist as their own types (rather
than reusing `DesignGroup`/`AmbiguousPattern`) specifically so their
`confidence` fields do not leak into the summary as a side effect of type
sharing. `SummaryRelationship` and `SummaryCustomPattern` are preserved here
even though n8n's original projector dropped both entirely: a relationship
such as "this label belongs to that control" and a detected custom pattern
("cannot be represented cleanly by the preceding categories") both carry
information a compatibility matcher can materially use, that isn't
recoverable from any other summary field.
"""

from typing import Literal

from pydantic import BaseModel, Field


class SummaryLayout(BaseModel):
    """Trimmed layout description; `responsive_hints` is not propagated."""

    overall_structure: str
    regions: list[str] = Field(default_factory=list)
    alignment: str | None = None
    spacing: str | None = None


class SummaryGroup(BaseModel):
    """Trimmed group; confidence-free (see module docstring)."""

    id: str
    type: str
    children: list[str] = Field(default_factory=list)


class SummaryElement(BaseModel):
    """Trimmed element/divider.

    `orientation`/`continuity`/`associated_icon` are carried through, unlike
    the rest of the trim, because the compatibility matcher (PR 8) needs them
    to decide between a plain `Divider` and `Divider` + `Stack`/`Typography`
    composition.
    """

    id: str
    role: str
    text: str | None = None
    state: str | None = None
    orientation: str | None = None
    continuity: str | None = None
    associated_icon: str | None = None


class SummaryRepeatedStructure(BaseModel):
    """Trimmed repeated structure."""

    id: str
    item_type: str
    count: int = Field(ge=0)
    visible_text_list: list[str] = Field(default_factory=list)
    interaction_pattern: str | None = None
    shared_style: str | None = None


class SummarySemanticPattern(BaseModel):
    """Trimmed semantic pattern; `visual_evidence`/`purpose` are not propagated."""

    name: str
    type: str
    importance: Literal["low", "medium", "high", "critical"]
    implementation_implications: list[str] = Field(default_factory=list)


class SummaryRelationship(BaseModel):
    """Trimmed relationship, preserved because it carries matcher-relevant links
    (e.g. "label belongs to control") not recoverable from any other summary field.
    """

    source: str
    target: str
    relationship: str


class SummaryCustomPattern(BaseModel):
    """Trimmed custom pattern, preserved because it is close to a direct proxy for
    "this needs custom implementation" -- exactly the signal `CustomImplementationWarning`
    (see `compatibility.py`) exists to surface.
    """

    type: str
    description: str


class SummaryAmbiguousPattern(BaseModel):
    """Trimmed ambiguous/missing pattern; confidence-free like the rest of this module.

    Distinct from `semantic_analysis.AmbiguousPattern` (which carries `confidence`)
    specifically so that field cannot leak into `DesignSummary` via type sharing --
    the same rationale as `SummaryGroup` vs. `DesignGroup`.
    """

    description: str
    reason: str


class DesignSummary(BaseModel):
    """The reduced projection of a `DesignStructure` + `SemanticAnalysis` pair."""

    layout: SummaryLayout
    groups: list[SummaryGroup] = Field(default_factory=list)
    elements: list[SummaryElement] = Field(default_factory=list)
    repeated_structures: list[SummaryRepeatedStructure] = Field(default_factory=list)
    semantic_patterns: list[SummarySemanticPattern] = Field(default_factory=list)
    missing_or_ambiguous_patterns: list[SummaryAmbiguousPattern] = Field(default_factory=list)
    relationships: list[SummaryRelationship] = Field(default_factory=list)
    custom_patterns: list[SummaryCustomPattern] = Field(default_factory=list)
    source: Literal["screenshot", "figma"] | None = None
