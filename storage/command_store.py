
"""
Command Store - SQLite-based persistence for commands and history
"""

import sqlite3
import json
from typing import List, Optional, Dict, Any
from datetime import datetime
from dataclasses import dataclass
from pathlib import Path


@dataclass
class StoredCommand:
    """Stored command with metadata."""
    id: int
    command: str
    query: str
    explanation: str
    risk_level: str
    timestamp: datetime
    executed: bool = False
    success: bool = False
    output: str = ""


class CommandStore:
    """SQLite-based storage for commands and metadata."""
    
    def __init__(self, db_path: str = "~/.rllm/commands.db"):
        self.db_path = Path(db_path).expanduser()
        self.db_path.parent.mkdir(exist_ok=True)
        self._initialize_database()
    
    def _initialize_database(self):
        """Initialize the SQLite database."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS commands (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    command TEXT NOT NULL,
                    query TEXT NOT NULL,
                    explanation TEXT,
                    risk_level TEXT,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    executed BOOLEAN DEFAULT FALSE,
                    success BOOLEAN DEFAULT FALSE,
                    output TEXT DEFAULT ''
                )
            """)
            
            conn.execute("""
                CREATE TABLE IF NOT EXISTS sessions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_data TEXT,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_commands_timestamp 
                ON commands(timestamp)
            """)
            
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_commands_query 
                ON commands(query)
            """)
    
    def store_command(
        self,
        command: str,
        query: str,
        explanation: str = "",
        risk_level: str = "low",
        executed: bool = False,
        success: bool = False,
        output: str = ""
    ) -> int:
        """Store a command and return its ID."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("""
                INSERT INTO commands (command, query, explanation, risk_level, executed, success, output)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (command, query, explanation, risk_level, executed, success, output))
            return cursor.lastrowid
    
    def update_command_result(self, command_id: int, success: bool, output: str):
        """Update command execution results."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                UPDATE commands 
                SET executed = TRUE, success = ?, output = ?
                WHERE id = ?
            """, (success, output, command_id))
    
    def get_command(self, command_id: int) -> Optional[StoredCommand]:
        """Get a specific command by ID."""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute("""
                SELECT * FROM commands WHERE id = ?
            """, (command_id,))
            
            row = cursor.fetchone()
            if row:
                return StoredCommand(
                    id=row['id'],
                    command=row['command'],
                    query=row['query'],
                    explanation=row['explanation'] or "",
                    risk_level=row['risk_level'] or "low",
                    timestamp=datetime.fromisoformat(row['timestamp']),
                    executed=bool(row['executed']),
                    success=bool(row['success']),
                    output=row['output'] or ""
                )
        return None
    
    def get_history(self, limit: int = 50, search: Optional[str] = None) -> List[StoredCommand]:
        """Get command history with optional search."""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            
            if search:
                cursor = conn.execute("""
                    SELECT * FROM commands 
                    WHERE query LIKE ? OR command LIKE ?
                    ORDER BY timestamp DESC 
                    LIMIT ?
                """, (f"%{search}%", f"%{search}%", limit))
            else:
                cursor = conn.execute("""
                    SELECT * FROM commands 
                    ORDER BY timestamp DESC 
                    LIMIT ?
                """, (limit,))
            
            commands = []
            for row in cursor.fetchall():
                commands.append(StoredCommand(
                    id=row['id'],
                    command=row['command'],
                    query=row['query'],
                    explanation=row['explanation'] or "",
                    risk_level=row['risk_level'] or "low",
                    timestamp=datetime.fromisoformat(row['timestamp']),
                    executed=bool(row['executed']),
                    success=bool(row['success']),
                    output=row['output'] or ""
                ))
            
            return commands
    
    def search_commands(self, query: str, limit: int = 20) -> List[StoredCommand]:
        """Search commands by query text."""
        return self.get_history(limit=limit, search=query)
    
    def get_similar_commands(self, query: str, limit: int = 5) -> List[StoredCommand]:
        """Get commands similar to the given query."""
        # Simple similarity search using SQL LIKE
        # In a production system, you might want to use full-text search
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            
            # Split query into words for better matching
            words = query.lower().split()
            
            if not words:
                return []
            
            # Build LIKE conditions for each word
            like_conditions = []
            params = []
            
            for word in words:
                like_conditions.append("(query LIKE ? OR command LIKE ?)")
                params.extend([f"%{word}%", f"%{word}%"])
            
            where_clause = " OR ".join(like_conditions)
            params.append(limit)
            
            cursor = conn.execute(f"""
                SELECT * FROM commands 
                WHERE {where_clause}
                ORDER BY timestamp DESC 
                LIMIT ?
            """, params)
            
            commands = []
            for row in cursor.fetchall():
                commands.append(StoredCommand(
                    id=row['id'],
                    command=row['command'],
                    query=row['query'],
                    explanation=row['explanation'] or "",
                    risk_level=row['risk_level'] or "low",
                    timestamp=datetime.fromisoformat(row['timestamp']),
                    executed=bool(row['executed']),
                    success=bool(row['success']),
                    output=row['output'] or ""
                ))
            
            return commands
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get usage statistics."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("""
                SELECT 
                    COUNT(*) as total_commands,
                    COUNT(CASE WHEN executed = 1 THEN 1 END) as executed_commands,
                    COUNT(CASE WHEN success = 1 THEN 1 END) as successful_commands,
                    COUNT(DISTINCT DATE(timestamp)) as active_days
                FROM commands
            """)
            
            row = cursor.fetchone()
            
            # Get risk level distribution
            cursor = conn.execute("""
                SELECT risk_level, COUNT(*) as count
                FROM commands
                GROUP BY risk_level
            """)
            
            risk_distribution = dict(cursor.fetchall())
            
            total = row[0] if row[0] else 1  # Avoid division by zero
            
            return {
                'total_commands': row[0],
                'executed_commands': row[1],
                'successful_commands': row[2],
                'active_days': row[3],
                'execution_rate': row[1] / total,
                'success_rate': row[2] / max(row[1], 1),
                'risk_distribution': risk_distribution
            }
    
    def export_commands(self, output_file: str, format: str = "json") -> bool:
        """Export commands to file."""
        commands = self.get_history(limit=1000)  # Export last 1000 commands
        
        try:
            if format.lower() == "json":
                data = []
                for cmd in commands:
                    data.append({
                        'id': cmd.id,
                        'command': cmd.command,
                        'query': cmd.query,
                        'explanation': cmd.explanation,
                        'risk_level': cmd.risk_level,
                        'timestamp': cmd.timestamp.isoformat(),
                        'executed': cmd.executed,
                        'success': cmd.success,
                        'output': cmd.output
                    })
                
                with open(output_file, 'w') as f:
                    json.dump(data, f, indent=2)
            
            elif format.lower() == "csv":
                import csv
                with open(output_file, 'w', newline='') as f:
                    writer = csv.writer(f)
                    writer.writerow(['ID', 'Query', 'Command', 'Risk Level', 'Timestamp', 'Executed', 'Success'])
                    
                    for cmd in commands:
                        writer.writerow([
                            cmd.id, cmd.query, cmd.command, cmd.risk_level,
                            cmd.timestamp.isoformat(), cmd.executed, cmd.success
                        ])
            
            return True
            
        except Exception as e:
            print(f"Export error: {e}")
            return False
    
    def clear_history(self, older_than_days: Optional[int] = None):
        """Clear command history."""
        with sqlite3.connect(self.db_path) as conn:
            if older_than_days:
                conn.execute("""
                    DELETE FROM commands 
                    WHERE timestamp < datetime('now', '-{} days')
                """.format(older_than_days))
            else:
                conn.execute("DELETE FROM commands")
