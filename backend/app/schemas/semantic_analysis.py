"""Semantic reasoning over a `DesignStructure` (PROJECT_SPEC.md sections 14-15).

The `SemanticAnalyzer` (a later PR) transforms `DesignStructure` into
`SemanticAnalysis`, describing *why* visible structures exist rather than
merely enumerating them. This module intentionally uses
`implementation_implications` rather than n8n's `muiImplications`: spec
section 15 explicitly forbids MUI-specific naming in this generic layer.
"""

from typing import Literal

from pydantic import BaseModel, Field

from app.schemas.common import Confidence


class SemanticPattern(BaseModel):
    """A named semantic/compositional pattern identified in a `DesignStructure`."""

    name: str
    type: Literal["layout", "interaction", "visual-rhythm", "ux-intent", "composite"]
    visual_evidence: str
    purpose: str
    importance: Literal["low", "medium", "high", "critical"]
    implementation_implications: list[str] = Field(default_factory=list)
    confidence: Confidence


class AmbiguousPattern(BaseModel):
    """A missing or ambiguous pattern where behavior should not be invented."""

    description: str
    reason: str
    confidence: Confidence


class SemanticAnalysis(BaseModel):
    """The full semantic analysis of a `DesignStructure`."""

    semantic_patterns: list[SemanticPattern] = Field(default_factory=list)
    missing_or_ambiguous_patterns: list[AmbiguousPattern] = Field(default_factory=list)
