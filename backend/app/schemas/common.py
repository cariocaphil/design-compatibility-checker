"""Shared primitive types reused across the domain schemas.

Centralizing these here keeps validation bounds (spec section 19: confidence
0-1, compatibility score 0-100) and closed string sets consistent across
`design_structure.py`, `semantic_analysis.py`, `design_summary.py`, and
`compatibility.py` rather than repeating `Field(ge=..., le=...)` calls or
inline `Literal[...]` definitions in each module.
"""

from typing import Annotated, Literal

from pydantic import Field

Confidence = Annotated[float, Field(ge=0.0, le=1.0)]
"""A vision/model-stage certainty score in the 0.0-1.0 range."""

CompatibilityScore = Annotated[float, Field(ge=0.0, le=100.0)]
"""How closely a design can be reproduced with standard library components (0-100)."""

CustomizationLevel = Literal["none", "minor", "medium", "high"]
"""Customization effort required beyond standard component composition/theming."""

WarningSeverity = Literal["low", "medium", "high"]
"""Severity of a custom-implementation warning."""
