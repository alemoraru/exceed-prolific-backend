from app.api.participants import assess_skill_level, assign_intervention_type
from app.utils.enums import InterventionType, SkillLevel


class TestSkillLevelIntervention:
    """Test cases for skill level assessment and intervention type assignment."""

    def test_assess_skill_level_expert_by_correct_count(self):
        """Test assessing skill level as expert based on correct answers."""
        assert assess_skill_level(6, 0) == SkillLevel.EXPERT.value
        assert assess_skill_level(7, 2) == SkillLevel.EXPERT.value
        assert assess_skill_level(8, 10) == SkillLevel.EXPERT.value

    def test_assess_skill_level_novice_by_correct_count(self):
        """Test assessing skill level as novice based on correct answers."""
        assert assess_skill_level(0, 10) == SkillLevel.NOVICE.value
        assert assess_skill_level(3, 0) == SkillLevel.NOVICE.value
        assert assess_skill_level(2, 5) == SkillLevel.NOVICE.value

    def test_assess_skill_level_edge_case_4_5_correct(self):
        """Test edge cases for 4-5 correct answers with years of experience."""

        # 4-5 correct, yoe >= 5 => expert
        assert assess_skill_level(4, 5) == SkillLevel.EXPERT.value
        assert assess_skill_level(5, 5) == SkillLevel.EXPERT.value
        assert assess_skill_level(5, 10) == SkillLevel.EXPERT.value
        # 4-5 correct, yoe < 5 => novice
        assert assess_skill_level(4, 2) == SkillLevel.NOVICE.value
        assert assess_skill_level(5, 0) == SkillLevel.NOVICE.value

    def test_assign_intervention_type_balancing(self):
        """Test assigning the right intervention type in the balancing scenario (i.e. deterministic assignment)."""
        # contingent < pragmatic
        assert assign_intervention_type(1, 2) == InterventionType.CONTINGENT.value
        # pragmatic < contingent
        assert assign_intervention_type(3, 1) == InterventionType.PRAGMATIC.value
