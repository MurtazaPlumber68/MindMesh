
"""
Intent Parser - Converts natural language to shell commands
"""

import json
from typing import Optional, Dict, Any, List
from dataclasses import dataclass
from services.llm_service import LLMService


@dataclass
class ParseResult:
    """Result of parsing natural language to command."""
    command: str
    explanation: str
    risk_level: str
    confidence: float
    alternatives: List[str]
    warnings: List[str]


class IntentParser:
    """Parses natural language intents into shell commands."""

    def __init__(self, llm_service: LLMService):
        self.llm_service = llm_service
        self.system_prompt = self._load_system_prompt()

    def _load_system_prompt(self) -> str:
        """Load the system prompt for LLM interaction."""
        return """You are an expert system administrator and shell command generator.

Your task is to convert natural language requests into safe, accurate shell commands.

Rules:
1. Always provide the most appropriate single command
2. Explain what the command does in simple terms
3. Assess risk level: low, medium, high, or critical
4. Provide 1-3 alternative approaches when applicable
5. Include warnings for potentially dangerous operations
6. Consider the user's context (OS, directory, previous commands)

Response format (JSON):
{
    "command": "shell_command_here",
    "explanation": "Clear explanation of what this does",
    "risk_level": "low|medium|high|critical",
    "confidence": 0.95,
    "alternatives": ["alt1", "alt2"],
    "warnings": ["warning1", "warning2"]
}

Examples:
- "list files" → "ls -la"
- "find large files" → "find . -type f -size +10M -exec ls -lh {} +"
- "check disk space" → "df -h"

Be concise but thorough in explanations."""

    async def parse(self, query: str, context: Optional[Dict[str, Any]] = None) -> Optional[ParseResult]:
        """Parse natural language query into shell command."""
        
        # Build the full prompt with context
        messages = [
            {"role": "system", "content": self.system_prompt}
        ]
        
        # Add context if available
        if context:
            context_info = self._format_context(context)
            messages.append({
                "role": "system", 
                "content": f"Current context:\n{context_info}"
            })
        
        # Add user query
        messages.append({
            "role": "user",
            "content": f"Convert this request to a shell command: {query}"
        })
        
        try:
            # Get response from LLM
            response = await self.llm_service.generate_response(messages)
            
            # Parse JSON response
            result_data = json.loads(response)
            
            return ParseResult(
                command=result_data.get("command", ""),
                explanation=result_data.get("explanation", ""),
                risk_level=result_data.get("risk_level", "medium"),
                confidence=result_data.get("confidence", 0.8),
                alternatives=result_data.get("alternatives", []),
                warnings=result_data.get("warnings", [])
            )
            
        except json.JSONDecodeError:
            # Fallback: try to extract command from plain text response
            return await self._fallback_parse(response, query)
        except Exception as e:
            print(f"Parser error: {e}")
            return None

    def _format_context(self, context: Dict[str, Any]) -> str:
        """Format context information for the LLM."""
        lines = []
        
        if "current_directory" in context:
            lines.append(f"Current directory: {context['current_directory']}")
        
        if "os_info" in context:
            lines.append(f"Operating system: {context['os_info']}")
        
        if "shell" in context:
            lines.append(f"Shell: {context['shell']}")
        
        if "previous_commands" in context and context["previous_commands"]:
            lines.append("Recent commands:")
            for cmd in context["previous_commands"][-3:]:  # Last 3 commands
                lines.append(f"  - {cmd}")
        
        return "\n".join(lines)

    async def _fallback_parse(self, response: str, query: str) -> Optional[ParseResult]:
        """Fallback parsing when JSON parsing fails."""
        # Simple heuristic to extract command from response
        lines = response.strip().split('\n')
        
        # Look for lines that might contain commands
        for line in lines:
            line = line.strip()
            if line and not line.startswith('#') and not line.startswith('//'):
                # This might be a command
                return ParseResult(
                    command=line,
                    explanation=f"Generated command for: {query}",
                    risk_level="medium",
                    confidence=0.6,
                    alternatives=[],
                    warnings=["Fallback parsing used - please verify command"]
                )
        
        return None
