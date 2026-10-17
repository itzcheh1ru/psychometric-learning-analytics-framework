"""
app/services/sem_analysis/result_service.py

Service interface for loading and providing SEM analytical outputs.

IMPORTANT:
This service strictly prevents the generation or display of artificial
or simulated SEM results. All result access methods raise
SemResultsNotAvailableError until actual R/lavaan analyses are completed
on validated research data.

Status: Prototype – results not available until research data is analysed.
"""

from typing import Any, Dict


class SemResultsNotAvailableError(RuntimeError):
    """
    Raised when SEM analytical outputs are requested before
    empirical analysis has been conducted on validated research data.
    """


class SemResultService:
    """
    Interface for future integration with validated R/lavaan SEM outputs.
    """

    def results_available(self) -> bool:
        """
        Return whether empirical SEM analytical results are ready.

        Returns:
            bool: Always False during data collection and prototype development.
        """
        return False

    def get_results(self) -> Dict[str, Any]:
        """
        Retrieve empirical SEM results once available.

        Raises:
            SemResultsNotAvailableError: Always, until empirical results are validated.
        """
        raise SemResultsNotAvailableError(
            "SEM results are not available until validated research data has been analysed."
        )


# Singleton service instance
result_service = SemResultService()
