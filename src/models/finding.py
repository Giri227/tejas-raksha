"""Data models for security findings."""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, Optional


class Severity(Enum):
    """Severity levels for security findings."""
    
    HIGH = "High"
    MEDIUM = "Medium"
    LOW = "Low"
    INFO = "Info"
    
    def __str__(self) -> str:
        return self.value


@dataclass
class Finding:
    """
    Represents a security finding discovered during a scan.
    
    Attributes:
        severity: Risk classification level
        title: Short descriptive title of the finding
        url: URL where the issue was discovered
        description: Detailed description of the security issue
        remediation: Guidance on how to fix the vulnerability
        category: Category of the security issue
        check_name: Name of the security check that discovered this finding
        timestamp: When the finding was discovered
        metadata: Additional context-specific information
    """
    
    severity: Severity
    title: str
    url: str
    description: str
    remediation: str
    category: str
    check_name: str
    timestamp: datetime = field(default_factory=datetime.now)
    metadata: Optional[Dict[str, Any]] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert Finding to dictionary for serialization.
        
        Returns:
            Dictionary representation of the finding
        """
        return {
            'severity': self.severity.value,
            'title': self.title,
            'url': self.url,
            'description': self.description,
            'remediation': self.remediation,
            'category': self.category,
            'check_name': self.check_name,
            'timestamp': self.timestamp.isoformat(),
            'metadata': self.metadata or {},
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Finding':
        """
        Create Finding from dictionary.
        
        Args:
            data: Dictionary containing finding data
        
        Returns:
            Finding instance
        
        Raises:
            KeyError: If required fields are missing
            ValueError: If severity value is invalid
        """
        return cls(
            severity=Severity(data['severity']),
            title=data['title'],
            url=data['url'],
            description=data['description'],
            remediation=data['remediation'],
            category=data['category'],
            check_name=data['check_name'],
            timestamp=datetime.fromisoformat(data['timestamp']),
            metadata=data.get('metadata'),
        )
    
    def __repr__(self) -> str:
        return (
            f"Finding(severity={self.severity.value}, title='{self.title}', "
            f"url='{self.url}', check='{self.check_name}')"
        )
