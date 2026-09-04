"""Registry for correction families that require post-execution verification."""

from __future__ import annotations

from server.router.domain.entities.correction_policy import CorrectionCategory
from server.router.domain.entities.postcondition import PostconditionRequirement


class PostconditionRegistry:
    """Registry of high-risk correction categories and their verification requirements."""

    def __init__(self) -> None:
        self._requirements = {
            CorrectionCategory.PRECONDITION_MODE: PostconditionRequirement(
                correction_category=CorrectionCategory.PRECONDITION_MODE,
                verification_key="verify_mode",
                reason="Mode corrections must verify the final interaction mode.",
            ),
            CorrectionCategory.PRECONDITION_ACTIVE_OBJECT: PostconditionRequirement(
                correction_category=CorrectionCategory.PRECONDITION_ACTIVE_OBJECT,
                verification_key="verify_active_object",
                reason="Active-object corrections must verify the final target object.",
            ),
            CorrectionCategory.PRECONDITION_SELECTION: PostconditionRequirement(
                correction_category=CorrectionCategory.PRECONDITION_SELECTION,
                verification_key="verify_selection",
                reason="Selection injection must verify the final selected geometry/object set.",
            ),
            CorrectionCategory.PARAMETER_CLAMP: PostconditionRequirement(
                correction_category=CorrectionCategory.PARAMETER_CLAMP,
                verification_key="verify_geometric_clamp",
                reason="Visible geometric clamps should verify the intended bounded outcome.",
            ),
        }

    def get(self, category: CorrectionCategory) -> PostconditionRequirement | None:
        """Return the postcondition requirement for a correction category, if any."""

        return self._requirements.get(category)

    def requires_verification(self, category: CorrectionCategory) -> bool:
        """Return True when the category must trigger post-execution verification."""

        requirement = self.get(category)
        return bool(requirement and requirement.required)
