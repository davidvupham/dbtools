from abc import ABC, abstractmethod
from typing import Any, Dict

from .models import BenchmarkResult


class BenchmarkRunner(ABC):
    """Abstract base class for benchmark runners."""

    @abstractmethod
    def run(self, config: Dict[str, Any]) -> BenchmarkResult:
        """
        Execute the benchmark with the given configuration.

        Args:
            config: A dictionary of configuration parameters specific to the benchmark tool.

        Returns:
            BenchmarkResult: The result of the benchmark run.
        """
        pass

    @abstractmethod
    def validate_config(self, config: Dict[str, Any]) -> bool:
        """
        Validate the configuration before running.

        Args:
            config: Configuration dictionary.

        Returns:
            bool: True if valid, raises exception otherwise.
        """
        pass
