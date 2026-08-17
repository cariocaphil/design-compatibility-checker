"""Domain schema contracts for the design-compatibility pipeline.

Re-exports every public model so callers can do e.g. `from app.schemas import
DesignStructure` rather than reaching into individual submodules.
"""

from app.schemas.common import (
    CompatibilityScore,
    Confidence,
    CustomizationLevel,
    WarningSeverity,
)
from app.schemas.compatibility import (
    CompatibilityAssessment,
    CompatibilitySummary,
    CustomImplementationWarning,
    ElementMapping,
    GroupMapping,
    LayoutMapping,
    SemanticImplementationMapping,
)
from app.schemas.design_structure import (
    CustomPattern,
    DesignElement,
    DesignGroup,
    DesignStructure,
    LayoutDescription,
    Relationship,
    RepeatedStructure,
)
from app.schemas.design_summary import (
    DesignSummary,
    SummaryAmbiguousPattern,
    SummaryCustomPattern,
    SummaryElement,
    SummaryGroup,
    SummaryLayout,
    SummaryRelationship,
    SummaryRepeatedStructure,
    SummarySemanticPattern,
)
from app.schemas.semantic_analysis import AmbiguousPattern, SemanticAnalysis, SemanticPattern

__all__ = [
    "AmbiguousPattern",
    "CompatibilityAssessment",
    "CompatibilityScore",
    "CompatibilitySummary",
    "Confidence",
    "CustomImplementationWarning",
    "CustomPattern",
    "CustomizationLevel",
    "DesignElement",
    "DesignGroup",
    "DesignStructure",
    "DesignSummary",
    "ElementMapping",
    "GroupMapping",
    "LayoutDescription",
    "LayoutMapping",
    "RepeatedStructure",
    "Relationship",
    "SemanticAnalysis",
    "SemanticImplementationMapping",
    "SemanticPattern",
    "SummaryAmbiguousPattern",
    "SummaryCustomPattern",
    "SummaryElement",
    "SummaryGroup",
    "SummaryLayout",
    "SummaryRelationship",
    "SummaryRepeatedStructure",
    "SummarySemanticPattern",
    "WarningSeverity",
]
