"""Plugin registry for discovering and executing security checks."""

import asyncio
import importlib
import inspect
import pkgutil
from typing import List, Type

from .base import BaseCheck, CheckContext
from ..models.finding import Finding
from ..models.config import ScanConfig
from ..utils.logger import get_logger

logger = get_logger(__name__)


class CheckRegistry:
    """
    Plugin manager for discovering and executing security checks.
    
    Automatically discovers check classes from the checks/ directory,
    registers them, and executes them with concurrency control and
    error isolation.
    
    Attributes:
        config: Scan configuration
        checks: List of registered check instances
    """
    
    def __init__(self, config: ScanConfig):
        """
        Initialize check registry.
        
        Args:
            config: Scan configuration
        """
        self.config = config
        self.checks: List[BaseCheck] = []
    
    def discover_checks(self) -> None:
        """
        Auto-discover check classes from checks/ directory.
        
        Scans the checks package for Python modules, imports them,
        and finds classes that inherit from BaseCheck.
        """
        import src.checks as checks_package
        
        # Get the package path
        package_path = checks_package.__path__
        package_name = checks_package.__name__
        
        # Iterate through modules in the package
        for importer, modname, ispkg in pkgutil.iter_modules(package_path):
            if modname in ['base', 'registry', '__init__']:
                continue
            
            try:
                # Import the module
                module_name = f"{package_name}.{modname}"
                module = importlib.import_module(module_name)
                
                # Find BaseCheck subclasses
                for name, obj in inspect.getmembers(module, inspect.isclass):
                    if (issubclass(obj, BaseCheck) and 
                        obj is not BaseCheck and
                        obj.__module__ == module_name):
                        
                        # Instantiate and register the check
                        check_instance = obj()
                        self.register_check(check_instance)
                        logger.debug(f"Discovered check: {check_instance.metadata.name}")
            
            except Exception as e:
                logger.error(f"Error discovering checks in module {modname}: {e}")
    
    def register_check(self, check: BaseCheck) -> None:
        """
        Manually register a check.
        
        Args:
            check: BaseCheck instance to register
        """
        # Check if this check should be enabled
        if not self._should_enable_check(check):
            logger.debug(f"Check disabled: {check.metadata.name}")
            return
        
        self.checks.append(check)
        logger.info(f"Registered check: {check.metadata.name}")
    
    def _should_enable_check(self, check: BaseCheck) -> bool:
        """
        Determine if a check should be enabled based on configuration.
        
        Args:
            check: Check to evaluate
        
        Returns:
            True if check should be enabled, False otherwise
        """
        check_name = check.__class__.__name__
        
        # If enabled_checks is specified, only enable those
        if self.config.enabled_checks:
            return check_name in self.config.enabled_checks
        
        # If disabled_checks is specified, disable those
        if self.config.disabled_checks:
            return check_name not in self.config.disabled_checks
        
        # Otherwise, use the check's default enabled status
        return check.metadata.enabled
    
    async def execute_all(self, context: CheckContext) -> List[Finding]:
        """
        Execute all enabled checks.
        
        Runs checks concurrently using asyncio.gather with error isolation.
        Individual check failures do not prevent other checks from running.
        
        Args:
            context: CheckContext with URLs, fetcher, and configuration
        
        Returns:
            List of all findings from all checks
        """
        if not self.checks:
            logger.warning("No checks registered")
            return []
        
        logger.info(f"Executing {len(self.checks)} security checks")
        
        # Execute all checks concurrently
        tasks = [self._execute_check(check, context) for check in self.checks]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Aggregate findings
        all_findings = []
        for i, result in enumerate(results):
            if isinstance(result, list):
                all_findings.extend(result)
            elif isinstance(result, Exception):
                check_name = self.checks[i].metadata.name
                logger.error(f"Check '{check_name}' failed with exception: {result}")
        
        logger.info(f"Security checks complete: {len(all_findings)} findings")
        return all_findings
    
    async def _execute_check(self, check: BaseCheck, context: CheckContext) -> List[Finding]:
        """
        Execute single check with error handling.
        
        Args:
            check: Check to execute
            context: CheckContext for the check
        
        Returns:
            List of findings or empty list on error
        """
        try:
            logger.info(f"Executing check: {check.metadata.name}")
            findings = await check.execute(context)
            logger.info(
                f"Check '{check.metadata.name}' found {len(findings)} issues"
            )
            return findings
        
        except Exception as e:
            logger.error(f"Error in check '{check.metadata.name}': {e}")
            import traceback
            logger.debug(traceback.format_exc())
            return []
    
    def get_registered_checks(self) -> List[str]:
        """
        Get list of registered check names.
        
        Returns:
            List of check names
        """
        return [check.metadata.name for check in self.checks]
    
    def get_check_count(self) -> int:
        """
        Get number of registered checks.
        
        Returns:
            Number of checks
        """
        return len(self.checks)
