
"""
Context Manager - Handles conversation context and session state
"""

import os
import platform
from typing import Dict, Any, List, Optional
from datetime import datetime
from dataclasses import dataclass, asdict
import json


@dataclass
class HistoryItem:
    """Individual history item."""
    query: str
    command: str
    timestamp: datetime
    executed: bool = False


class ContextManager:
    """Manages conversation context and command history."""

    def __init__(self, max_history: int = 50):
        self.max_history = max_history
        self.history: List[HistoryItem] = []
        self.current_session = {}
        self._initialize_context()

    def _initialize_context(self):
        """Initialize base context information."""
        self.current_session = {
            'current_directory': os.getcwd(),
            'home_directory': os.path.expanduser('~'),
            'os_info': f"{platform.system()} {platform.release()}",
            'shell': os.environ.get('SHELL', '/bin/bash').split('/')[-1],
            'user': os.environ.get('USER', 'unknown'),
            'session_start': datetime.now().isoformat()
        }

    def get_context(self) -> Dict[str, Any]:
        """Get current context for LLM requests."""
        context = self.current_session.copy()
        
        # Add recent commands for context
        recent_commands = [item.command for item in self.history[-5:]]
        context['previous_commands'] = recent_commands
        
        # Update current directory in case it changed
        context['current_directory'] = os.getcwd()
        
        return context

    def add_interaction(self, query: str, command: str, executed: bool = False):
        """Add a new query-command interaction to context."""
        item = HistoryItem(
            query=query,
            command=command,
            timestamp=datetime.now(),
            executed=executed
        )
        
        self.history.append(item)
        
        # Maintain history size limit
        if len(self.history) > self.max_history:
            self.history = self.history[-self.max_history:]

    def add_to_history(self, query: str, command: str, executed: bool = False):
        """Alias for add_interaction for backward compatibility."""
        self.add_interaction(query, command, executed)

    def get_history(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get recent history items."""
        recent_items = self.history[-limit:] if limit > 0 else self.history
        return [
            {
                'query': item.query,
                'command': item.command,
                'timestamp': item.timestamp.isoformat(),
                'executed': item.executed
            }
            for item in reversed(recent_items)
        ]

    def search_history(self, query: str) -> List[HistoryItem]:
        """Search history for matching queries or commands."""
        query_lower = query.lower()
        matches = []
        
        for item in self.history:
            if (query_lower in item.query.lower() or 
                query_lower in item.command.lower()):
                matches.append(item)
        
        return matches

    def get_similar_commands(self, query: str, limit: int = 3) -> List[str]:
        """Get similar commands from history."""
        # Simple similarity based on word overlap
        query_words = set(query.lower().split())
        scored_commands = []
        
        for item in self.history:
            item_words = set(item.query.lower().split())
            overlap = len(query_words.intersection(item_words))
            
            if overlap > 0:
                scored_commands.append((overlap, item.command))
        
        # Sort by overlap score and return top commands
        scored_commands.sort(reverse=True, key=lambda x: x[0])
        return [cmd for _, cmd in scored_commands[:limit]]

    def update_working_directory(self, new_dir: str):
        """Update the current working directory in context."""
        self.current_session['current_directory'] = new_dir

    def clear_history(self):
        """Clear command history."""
        self.history.clear()

    def export_session(self) -> Dict[str, Any]:
        """Export current session data."""
        return {
            'context': self.current_session,
            'history': [asdict(item) for item in self.history]
        }

    def import_session(self, session_data: Dict[str, Any]):
        """Import session data."""
        if 'context' in session_data:
            self.current_session.update(session_data['context'])
        
        if 'history' in session_data:
            self.history = [
                HistoryItem(
                    query=item['query'],
                    command=item['command'],
                    timestamp=datetime.fromisoformat(item['timestamp']),
                    executed=item.get('executed', False)
                )
                for item in session_data['history']
            ]

    def get_session_stats(self) -> Dict[str, Any]:
        """Get statistics about the current session."""
        total_commands = len(self.history)
        executed_commands = sum(1 for item in self.history if item.executed)
        
        return {
            'total_commands': total_commands,
            'executed_commands': executed_commands,
            'success_rate': executed_commands / total_commands if total_commands > 0 else 0,
            'session_duration': (datetime.now() - datetime.fromisoformat(
                self.current_session['session_start']
            )).total_seconds(),
            'current_directory': self.current_session['current_directory'],
            'os_info': self.current_session['os_info']
        }
