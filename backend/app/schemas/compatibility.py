"""Structured compatibility-matching output (PROJECT_SPEC.md sections 18-19).

The compatibility matcher (a later PR) evaluates `DesignSummary` + retrieved
Material UI context and returns a `CompatibilityAssessment`. Unlike the
generic `design_structure`/`semantic_analysis` layers, MUI-specific naming
(`mui_components`, `mui_container_component`, ...) is intentional here: per
PROJECT_SPEC.md section 3, component-library knowledge is allowed to enter the
pipeline at the retrieval/matching boundary.

n8n's structured-output schema caps array lengths (`maxItems: 2/5/3/4/3`).
Those caps are prompt/tool-schema tuning for the future matcher LLM call
(PR 8), not a domain invariant, so the list fields below are intentionally
left unbounded at the schema layer.
"""

from pydantic import BaseModel, Field

from app.schemas.common import CompatibilityScore, Confidence, CustomizationLevel, WarningSeverity


class CompatibilitySummary(BaseModel):
    """The overall compatibility assessment summary."""

    compatibility_score: CompatibilityScore
    customization_effort: CustomizationLevel
    overall_compatibility: str
    confidence: Confidence


class LayoutMapping(BaseModel):
    """A layout region mapped to one or more Material UI components."""

    layout_id: str
    mui_components: list[str]
    customization_level: CustomizationLevel
    reason: str
    confidence: Confidence


class ElementMapping(BaseModel):
    """A single element mapped to a Material UI component/variant."""

    element_id: str
    mui_component: str
    variant: str
    customization_level: CustomizationLevel
    reason: str
    confidence: Confidence


class GroupMapping(BaseModel):
    """A group mapped to a container/child Material UI component pair."""

    group_id: str
    mui_container_component: str
    mui_child_component: str
    customization_level: CustomizationLevel
    reason: str
    confidence: Confidence


class SemanticImplementationMapping(BaseModel):
    """A semantic pattern mapped to a Material UI implementation strategy."""

    semantic_pattern_name: str
    semantic_type: str
    mui_strategy: list[str]
    reason: str
    customization_level: CustomizationLevel
    confidence: Confidence


class CustomImplementationWarning(BaseModel):
    """An implementation risk or open question, ordered by severity for the report."""

    target: str
    reason: str
    severity: WarningSeverity


class CompatibilityAssessment(BaseModel):
    """The full structured output of the compatibility matcher."""

    summary: CompatibilitySummary
    layout_mappings: list[LayoutMapping] = Field(default_factory=list)
    element_mappings: list[ElementMapping] = Field(default_factory=list)
    group_mappings: list[GroupMapping] = Field(default_factory=list)
    semantic_implementation_mappings: list[SemanticImplementationMapping] = Field(
        default_factory=list
    )
    custom_implementation_warnings: list[CustomImplementationWarning] = Field(default_factory=list)
