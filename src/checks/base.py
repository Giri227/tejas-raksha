"""Base interface for security checks."""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, Dict, List, Set

from ..models.finding import Finding
from ..crawler.fetcher import Fetcher
from ..models.config import ScanConfig


@dataclass
class CheckMetadata:
    """
    Metadata about a security check.
    
    Attributes:
        name: Human-readable name of the check
        description: Detailed description of what the check does
        category: Category of security issue (e.g., "Information Disclosure")
        enabled: Whether the check is enabled by default
    """
    
    name: str
    description: str
    category: str
    enabled: bool = True


@dataclass
class CheckContext:
    """
    Context provided to security checks during execution.
    
    Attributes:
        urls: Set of all discovered URLs from crawling
        fetcher: HTTP fetcher for making additional requests
        config: Scan configuration
        scan_metadata: Additional metadata about the scan
    """
    
    urls: Set[str]
    fetcher: Fetcher
    config: ScanConfig
    scan_metadata: Dict[str, Any]


class BaseCheck(ABC):
    """
    Abstract base class for all security checks.
    
    All security check plugins must inherit from this class and implement
    the metadata property and execute method.
    
    Example:
        >>> class MyCheck(BaseCheck):
        ...     @property
        ...     def metadata(self) -> CheckMetadata:
        ...         return CheckMetadata(
        ...             name="My Security Check",
        ...             description="Checks for my vulnerability",
        ...             category="My Category"
        ...         )
        ...     
        ...     async def execute(self, context: CheckContext) -> List[Finding]:
        ...         findings = []
        ...         # Perform security checks
        ...         return findings
    """
    
    @property
    @abstractmethod
    def metadata(self) -> CheckMetadata:
        """
        Return check metadata.
        
        Returns:
            CheckMetadata with name, description, category, and enabled status
        """
        pass
    
    @abstractmethod
    async def execute(self, context: CheckContext) -> List[Finding]:
        """
        Execute security check and return findings.
        
        Args:
            context: CheckContext with URLs, fetcher, and configuration
        
        Returns:
            List of Finding objects for discovered security issues
        
        Raises:
            Exception: If check encounters an error (will be caught by registry)
        """
        pass
    
    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(name='{self.metadata.name}')"
