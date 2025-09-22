import sqlite3
import json
from typing import Dict, List, Optional
from dataclasses import asdict

from utils.planner import TaskPlan

class DatabaseManager:
    """Manages SQLite database operations"""
    
    def __init__(self, db_path: str = "task_plans.db"):
        self.db_path = db_path
        self._init_db()
    
    def _init_db(self):
        """Initialize database tables"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS plans (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                goal TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                plan_data TEXT NOT NULL,
                metadata TEXT
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def save_plan(self, plan: TaskPlan) -> int:
        """Save a plan to database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Convert plan to JSON
        plan_dict = {
            'goal': plan.goal,
            'created_at': plan.created_at,
            'total_days': plan.total_days,
            'days': [
                {
                    'day_number': day.day_number,
                    'date': day.date,
                    'theme': day.theme,
                    'steps': [asdict(step) for step in day.steps],
                    'weather_info': day.weather_info
                }
                for day in plan.days
            ],
            'metadata': plan.metadata
        }
        
        cursor.execute('''
            INSERT INTO plans (goal, created_at, plan_data, metadata)
            VALUES (?, ?, ?, ?)
        ''', (
            plan.goal,
            plan.created_at,
            json.dumps(plan_dict),
            json.dumps(plan.metadata)
        ))
        
        plan_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        return plan_id
    
    def get_all_plans(self) -> List[Dict]:
        """Retrieve all plans from database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT id, goal, created_at, plan_data, metadata
            FROM plans
            ORDER BY created_at DESC
        ''')
        
        plans = []
        for row in cursor.fetchall():
            plan_data = json.loads(row[3])
            plans.append({
                'id': row[0],
                'goal': row[1],
                'created_at': row[2],
                'plan': plan_data,
                'metadata': json.loads(row[4]) if row[4] else {}
            })
        
        conn.close()
        return plans
    
    def get_plan_by_id(self, plan_id: int) -> Optional[Dict]:
        """Get a specific plan by ID"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT id, goal, created_at, plan_data, metadata
            FROM plans
            WHERE id = ?
        ''', (plan_id,))
        
        row = cursor.fetchone()
        conn.close()
        
        if row:
            return {
                'id': row[0],
                'goal': row[1],
                'created_at': row[2],
                'plan': json.loads(row[3]),
                'metadata': json.loads(row[4]) if row[4] else {}
            }
        return None
