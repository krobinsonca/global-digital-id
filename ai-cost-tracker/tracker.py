"""
AI Cost Tracker - Core tracking module.
Logs every LLM call with timestamp, model, tokens, taskType, and costEstimate.
"""
import json
import os
import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, Any, List
from dataclasses import dataclass, asdict, field
import hashlib


@dataclass
class LLMCall:
    """Represents a single LLM API call."""
    timestamp: str
    model: str
    provider: str
    tokens_in: int
    tokens_out: int
    tokens_total: int
    task_type: str
    cost_estimate: float
    session_id: Optional[str] = None
    request_id: Optional[str] = None
    extra: Optional[Dict[str, Any]] = None
    
    def __post_init__(self):
        if self.tokens_total == 0:
            self.tokens_total = self.tokens_in + self.tokens_out
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        data = asdict(self)
        if self.extra:
            data['extra'] = self.extra
        return data
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'LLMCall':
        """Create LLMCall from dictionary."""
        # Remove fields not in LLMCall dataclass
        data = data.copy()
        data.pop("id", None)
        data.pop("created_at", None)
        extra = data.pop("extra", None)
        return cls(**data, extra=extra)


class PricingEngine:
    """Handles cost calculations based on provider pricing."""
    
    def __init__(self, pricing_file: Optional[str] = None):
        if pricing_file is None:
            # Default to pricing.json in same directory
            pricing_file = Path(__file__).parent / "pricing.json"
        
        with open(pricing_file, 'r') as f:
            self.pricing = json.load(f)
    
    def get_pricing(self, model: str) -> Optional[Dict[str, Any]]:
        """Get pricing for a specific model."""
        for provider_name, provider_data in self.pricing.get("providers", {}).items():
            models = provider_data.get("models", {})
            if model in models:
                return {
                    **models[model],
                    "provider": provider_name
                }
        return None
    
    def calculate_cost(self, model: str, tokens_in: int, tokens_out: int) -> float:
        """Calculate cost estimate for a model call."""
        pricing = self.get_pricing(model)
        if pricing is None:
            return 0.0
        
        input_cost = (tokens_in / 1_000_000) * pricing["input_cost_per_million"]
        output_cost = (tokens_out / 1_000_000) * pricing["output_cost_per_million"]
        
        return round(input_cost + output_cost, 6)
    
    def list_all_models(self) -> List[Dict[str, Any]]:
        """List all available models with pricing."""
        models = []
        for provider_name, provider_data in self.pricing.get("providers", {}).items():
            for model_id, model_data in provider_data.get("models", {}).items():
                models.append({
                    "model": model_id,
                    "provider": provider_name,
                    "description": model_data.get("description", ""),
                    "input_per_million": model_data["input_cost_per_million"],
                    "output_per_million": model_data["output_cost_per_million"]
                })
        return models
    
    def list_providers(self) -> List[str]:
        """List all available providers."""
        return list(self.pricing.get("providers", {}).keys())


class CostTracker:
    """Main tracker class for logging LLM calls."""
    
    def __init__(
        self,
        data_dir: Optional[str] = None,
        pricing_file: Optional[str] = None,
        db_file: Optional[str] = None
    ):
        # Set up directories
        if data_dir is None:
            data_dir = Path.home() / ".ai-cost-tracker"
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        # Set up pricing
        self.pricing_engine = PricingEngine(pricing_file)
        
        # Set up SQLite database
        if db_file is None:
            db_file = self.data_dir / "ai_costs.db"
        self.db_file = Path(db_file)
        self._init_db()
        
        # Set up JSONL file
        self.jsonl_file = self.data_dir / "llm_calls.jsonl"
    
    def _init_db(self):
        """Initialize SQLite database schema."""
        conn = sqlite3.connect(self.db_file)
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS llm_calls (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                model TEXT NOT NULL,
                provider TEXT,
                tokens_in INTEGER,
                tokens_out INTEGER,
                tokens_total INTEGER,
                task_type TEXT,
                cost_estimate REAL,
                session_id TEXT,
                request_id TEXT,
                extra TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_timestamp ON llm_calls(timestamp)
        ''')
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_model ON llm_calls(model)
        ''')
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_task_type ON llm_calls(task_type)
        ''')
        
        conn.commit()
        conn.close()
    
    def log_call(
        self,
        model: str,
        tokens_in: int,
        tokens_out: int,
        task_type: str,
        provider: Optional[str] = None,
        session_id: Optional[str] = None,
        request_id: Optional[str] = None,
        extra: Optional[Dict[str, Any]] = None
    ) -> LLMCall:
        """Log an LLM API call."""
        # Determine provider if not provided
        if provider is None:
            pricing = self.pricing_engine.get_pricing(model)
            provider = pricing["provider"] if pricing else "unknown"
        
        # Calculate cost
        cost = self.pricing_engine.calculate_cost(model, tokens_in, tokens_out)
        
        # Create record
        call = LLMCall(
            timestamp=datetime.utcnow().isoformat() + "Z",
            model=model,
            provider=provider,
            tokens_in=tokens_in,
            tokens_out=tokens_out,
            tokens_total=tokens_in + tokens_out,
            task_type=task_type,
            cost_estimate=cost,
            session_id=session_id,
            request_id=request_id,
            extra=extra
        )
        
        # Write to JSONL
        with open(self.jsonl_file, 'a') as f:
            f.write(json.dumps(call.to_dict()) + '\n')
        
        # Insert into SQLite
        conn = sqlite3.connect(self.db_file)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO llm_calls (
                timestamp, model, provider, tokens_in, tokens_out,
                tokens_total, task_type, cost_estimate, session_id,
                request_id, extra
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            call.timestamp, call.model, call.provider,
            call.tokens_in, call.tokens_out, call.tokens_total,
            call.task_type, call.cost_estimate, call.session_id,
            call.request_id, json.dumps(call.extra) if call.extra else None
        ))
        
        conn.commit()
        conn.close()
        
        return call
    
    def log_simple(
        self,
        model: str,
        prompt_tokens: int,
        completion_tokens: int,
        task_type: str
    ) -> LLMCall:
        """Simple logging method with auto-detected provider."""
        return self.log_call(
            model=model,
            tokens_in=prompt_tokens,
            tokens_out=completion_tokens,
            task_type=task_type
        )
    
    def get_stats(
        self,
        days: Optional[int] = None,
        model: Optional[str] = None,
        task_type: Optional[str] = None
    ) -> Dict[str, Any]:
        """Get aggregated statistics."""
        conn = sqlite3.connect(self.db_file)
        cursor = conn.cursor()
        
        query = "SELECT COUNT(*), SUM(tokens_in), SUM(tokens_out), SUM(cost_estimate) FROM llm_calls WHERE 1=1"
        params = []
        
        if days:
            query += f" AND timestamp >= datetime('now', '-{days} days')"
        if model:
            query += " AND model = ?"
            params.append(model)
        if task_type:
            query += " AND task_type = ?"
            params.append(task_type)
        
        cursor.execute(query, params)
        row = cursor.fetchone()
        
        conn.close()
        
        return {
            "total_calls": row[0] or 0,
            "total_tokens_in": row[1] or 0,
            "total_tokens_out": row[2] or 0,
            "total_cost": row[3] or 0.0
        }
    
    def get_recent_calls(
        self,
        limit: int = 100,
        days: Optional[int] = None
    ) -> List[LLMCall]:
        """Get recent LLM calls."""
        conn = sqlite3.connect(self.db_file)
        cursor = conn.cursor()
        
        query = "SELECT * FROM llm_calls ORDER BY timestamp DESC"
        params = []
        
        if days:
            query += f" WHERE timestamp >= datetime('now', '-{days} days')"
        
        query += f" LIMIT {limit}"
        
        cursor.execute(query, params)
        rows = cursor.fetchall()
        
        conn.close()
        
        columns = [desc[0] for desc in cursor.description]
        calls = []
        for row in rows:
            data = dict(zip(columns, row))
            calls.append(LLMCall.from_dict(data))
        
        return calls
    
    def export_to_jsonl(self, output_file: Optional[str] = None) -> int:
        """Export all data to JSONL format."""
        if output_file is None:
            output_file = self.data_dir / "export.jsonl"
        
        conn = sqlite3.connect(self.db_file)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM llm_calls ORDER BY timestamp")
        rows = cursor.fetchall()
        conn.close()
        
        columns = ["id", "timestamp", "model", "provider", "tokens_in", "tokens_out",
                   "tokens_total", "task_type", "cost_estimate", "session_id",
                   "request_id", "extra", "created_at"]
        
        count = 0
        with open(output_file, 'w') as f:
            for row in rows:
                data = dict(zip(columns, row))
                # Remove id and created_at for cleaner output
                data.pop("id", None)
                data.pop("created_at", None)
                f.write(json.dumps(data) + '\n')
                count += 1
        
        return count
    
    def import_from_jsonl(self, input_file: str) -> int:
        """Import data from JSONL file."""
        count = 0
        with open(input_file, 'r') as f:
            for line in f:
                data = json.loads(line)
                self.log_call(
                    model=data.get("model", ""),
                    tokens_in=data.get("tokens_in", 0),
                    tokens_out=data.get("tokens_out", 0),
                    task_type=data.get("task_type", "unknown"),
                    provider=data.get("provider"),
                    session_id=data.get("session_id"),
                    request_id=data.get("request_id"),
                    extra=data.get("extra")
                )
                count += 1
        return count
    
    def get_daily_costs(self, days: int = 30) -> List[Dict[str, Any]]:
        """Get daily cost breakdown."""
        conn = sqlite3.connect(self.db_file)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT 
                DATE(timestamp) as date,
                COUNT(*) as calls,
                SUM(tokens_in) as tokens_in,
                SUM(tokens_out) as tokens_out,
                SUM(cost_estimate) as cost
            FROM llm_calls
            WHERE timestamp >= datetime('now', '-{} days')
            GROUP BY DATE(timestamp)
            ORDER BY date DESC
        '''.format(days))
        
        rows = cursor.fetchall()
        conn.close()
        
        return [
            {
                "date": row[0],
                "calls": row[1],
                "tokens_in": row[2] or 0,
                "tokens_out": row[3] or 0,
                "cost": row[4] or 0.0
            }
            for row in rows
        ]
    
    def get_model_breakdown(self, days: Optional[int] = None) -> List[Dict[str, Any]]:
        """Get cost breakdown by model."""
        conn = sqlite3.connect(self.db_file)
        cursor = conn.cursor()
        
        query = '''
            SELECT 
                model,
                provider,
                COUNT(*) as calls,
                SUM(tokens_in) as tokens_in,
                SUM(tokens_out) as tokens_out,
                SUM(cost_estimate) as cost
            FROM llm_calls
        '''
        params = []
        
        if days:
            query += " WHERE timestamp >= datetime('now', '-{} days')".format(days)
        
        query += ' GROUP BY model ORDER BY cost DESC'
        
        cursor.execute(query, params)
        rows = cursor.fetchall()
        conn.close()
        
        return [
            {
                "model": row[0],
                "provider": row[1],
                "calls": row[2],
                "tokens_in": row[3] or 0,
                "tokens_out": row[4] or 0,
                "cost": row[5] or 0.0
            }
            for row in rows
        ]
    
    def get_task_breakdown(self, days: Optional[int] = None) -> List[Dict[str, Any]]:
        """Get cost breakdown by task type."""
        conn = sqlite3.connect(self.db_file)
        cursor = conn.cursor()
        
        query = '''
            SELECT 
                task_type,
                COUNT(*) as calls,
                SUM(tokens_in) as tokens_in,
                SUM(tokens_out) as tokens_out,
                SUM(cost_estimate) as cost
            FROM llm_calls
        '''
        params = []
        
        if days:
            query += " WHERE timestamp >= datetime('now', '-{} days')".format(days)
        
        query += ' GROUP BY task_type ORDER BY cost DESC'
        
        cursor.execute(query, params)
        rows = cursor.fetchall()
        conn.close()
        
        return [
            {
                "task_type": row[0],
                "calls": row[1],
                "tokens_in": row[2] or 0,
                "tokens_out": row[3] or 0,
                "cost": row[4] or 0.0
            }
            for row in rows
        ]
    
    def cleanup_old_records(self, days: int = 90) -> int:
        """Remove records older than specified days."""
        conn = sqlite3.connect(self.db_file)
        cursor = conn.cursor()
        
        cursor.execute('''
            DELETE FROM llm_calls WHERE timestamp < datetime('now', '-{} days')
        '''.format(days))
        
        count = cursor.rowcount
        conn.commit()
        conn.close()
        
        return count
    
    def vacuum(self):
        """Vacuum the database to reclaim space."""
        conn = sqlite3.connect(self.db_file)
        conn.execute("VACUUM")
        conn.close()


# Convenience function for quick logging
_default_tracker: Optional[CostTracker] = None


def get_tracker() -> CostTracker:
    """Get the default tracker instance."""
    global _default_tracker
    if _default_tracker is None:
        _default_tracker = CostTracker()
    return _default_tracker


def log_llm_call(
    model: str,
    tokens_in: int,
    tokens_out: int,
    task_type: str,
    **kwargs
) -> LLMCall:
    """Log an LLM call using the default tracker."""
    return get_tracker().log_call(
        model=model,
        tokens_in=tokens_in,
        tokens_out=tokens_out,
        task_type=task_type,
        **kwargs
    )
