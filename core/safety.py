
"""
Safety Validator - Analyzes commands for potential risks
"""

import re
from typing import List, Dict, Set
from dataclasses import dataclass
from enum import Enum


class RiskLevel(Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high" 
    CRITICAL = "critical"


@dataclass
class RiskAssessment:
    """Assessment of command risk level."""
    risk_level: str
    score: int  # 0-100
    warnings: List[str]
    blocked_patterns: List[str]


class SafetyValidator:
    """Validates shell commands for safety and security risks."""

    def __init__(self):
        self.dangerous_patterns = self._load_dangerous_patterns()
        self.system_paths = {'/etc', '/usr', '/boot', '/sys', '/proc', '/dev'}
        self.destructive_commands = {'rm', 'dd', 'mkfs', 'fdisk', 'wipefs'}

    def _load_dangerous_patterns(self) -> Dict[str, Dict]:
        """Load patterns that indicate dangerous operations."""
        return {
            # Destructive file operations
            r'rm\s+.*-rf?\s+/': {
                'risk': RiskLevel.CRITICAL,
                'message': 'Recursive deletion from root directory'
            },
            r'rm\s+.*-rf?\s+\*': {
                'risk': RiskLevel.HIGH,
                'message': 'Recursive deletion with wildcard'
            },
            r'dd\s+.*of=/dev/': {
                'risk': RiskLevel.CRITICAL,
                'message': 'Writing directly to device'
            },
            
            # Permission changes
            r'chmod\s+777': {
                'risk': RiskLevel.HIGH,
                'message': 'Setting world-writable permissions'
            },
            r'chown\s+.*:.*\s+/': {
                'risk': RiskLevel.MEDIUM,
                'message': 'Changing ownership of system files'
            },
            
            # Network operations
            r'curl\s+.*\|\s*sh': {
                'risk': RiskLevel.CRITICAL,
                'message': 'Downloading and executing remote script'
            },
            r'wget\s+.*\|\s*sh': {
                'risk': RiskLevel.CRITICAL,
                'message': 'Downloading and executing remote script'
            },
            
            # System modifications
            r'sudo\s+.*rm': {
                'risk': RiskLevel.HIGH,
                'message': 'Elevated deletion command'
            },
            r'mkfs\s+': {
                'risk': RiskLevel.CRITICAL,
                'message': 'Filesystem creation (destructive)'
            },
            
            # Process manipulation
            r'kill\s+-9\s+1': {
                'risk': RiskLevel.CRITICAL,
                'message': 'Attempting to kill init process'
            },
            r'killall\s+': {
                'risk': RiskLevel.MEDIUM,
                'message': 'Killing processes by name'
            },
            
            # Configuration files
            r'>\s*/etc/': {
                'risk': RiskLevel.HIGH,
                'message': 'Overwriting system configuration'
            },
            r'>>\s*/etc/': {
                'risk': RiskLevel.MEDIUM,
                'message': 'Modifying system configuration'
            }
        }

    def validate(self, command: str) -> RiskAssessment:
        """Validate a command and return risk assessment."""
        warnings = []
        blocked_patterns = []
        max_risk = RiskLevel.LOW
        score = 0

        # Check against dangerous patterns
        for pattern, config in self.dangerous_patterns.items():
            if re.search(pattern, command, re.IGNORECASE):
                risk_level = config['risk']
                message = config['message']
                
                warnings.append(message)
                blocked_patterns.append(pattern)
                
                if self._risk_level_score(risk_level) > self._risk_level_score(max_risk):
                    max_risk = risk_level
                
                score += self._risk_level_score(risk_level) * 10

        # Additional heuristic checks
        additional_warnings = self._heuristic_checks(command)
        warnings.extend(additional_warnings)
        
        # Adjust score based on additional warnings
        score += len(additional_warnings) * 5

        # Determine final risk level
        if score >= 80:
            final_risk = RiskLevel.CRITICAL
        elif score >= 60:
            final_risk = RiskLevel.HIGH
        elif score >= 30:
            final_risk = RiskLevel.MEDIUM
        else:
            final_risk = max_risk if max_risk != RiskLevel.LOW else RiskLevel.LOW

        return RiskAssessment(
            risk_level=final_risk.value,
            score=min(score, 100),
            warnings=warnings,
            blocked_patterns=blocked_patterns
        )

    def _heuristic_checks(self, command: str) -> List[str]:
        """Additional heuristic safety checks."""
        warnings = []
        
        # Check for multiple commands chained together
        if ';' in command or '&&' in command or '||' in command:
            warnings.append("Command contains multiple operations")
        
        # Check for redirections to important locations
        if re.search(r'>\s*/\w+', command):
            warnings.append("Redirecting output to root-level directory")
        
        # Check for wildcard usage in potentially dangerous contexts
        if '*' in command and any(cmd in command for cmd in self.destructive_commands):
            warnings.append("Using wildcards with destructive commands")
        
        # Check for sudo usage
        if command.strip().startswith('sudo'):
            warnings.append("Command requires elevated privileges")
        
        # Check for operations on system paths
        for path in self.system_paths:
            if path in command:
                warnings.append(f"Operating on system directory: {path}")
                break
        
        # Check for unusual characters that might indicate injection
        suspicious_chars = ['`', '$(' , '${', '$(', '||', '&&']
        for char in suspicious_chars:
            if char in command:
                warnings.append("Command contains potentially suspicious characters")
                break
        
        return warnings

    def _risk_level_score(self, risk_level: RiskLevel) -> int:
        """Convert risk level to numeric score."""
        scores = {
            RiskLevel.LOW: 1,
            RiskLevel.MEDIUM: 3,
            RiskLevel.HIGH: 7,
            RiskLevel.CRITICAL: 10
        }
        return scores.get(risk_level, 1)

    def is_command_blocked(self, command: str) -> bool:
        """Check if command should be completely blocked."""
        assessment = self.validate(command)
        return assessment.risk_level == RiskLevel.CRITICAL.value and assessment.score >= 90
