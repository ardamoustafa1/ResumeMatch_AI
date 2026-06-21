from abc import ABC, abstractmethod
from typing import List

class AbstractScoringStrategy(ABC):
    @abstractmethod
    def calculate_score(self, matched_skills: List[str], missing_skills: List[str]) -> int:
        """Calculate a 0-100 score based on matched and missing skills."""
        pass

class DefaultScoringStrategy(AbstractScoringStrategy):
    def calculate_score(self, matched_skills: List[str], missing_skills: List[str]) -> int:
        total_skills = len(matched_skills) + len(missing_skills)
        if total_skills == 0:
            return 0
        score = (len(matched_skills) / total_skills) * 100
        penalty = len(missing_skills) * 2.5
        return max(0, min(100, int(score - penalty)))

class StrictKeywordScoringStrategy(AbstractScoringStrategy):
    def calculate_score(self, matched_skills: List[str], missing_skills: List[str]) -> int:
        total_skills = len(matched_skills) + len(missing_skills)
        if total_skills == 0:
            return 0
        # Strict penalty: missing a skill heavily drops score
        score = (len(matched_skills) / total_skills) * 100
        penalty = len(missing_skills) * 10
        return max(0, min(100, int(score - penalty)))

def get_scoring_strategy(strategy_name: str) -> AbstractScoringStrategy:
    if strategy_name == "strict_keyword":
        return StrictKeywordScoringStrategy()
    return DefaultScoringStrategy()
