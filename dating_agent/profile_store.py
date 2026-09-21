"""
Profile storage and database management.
Stores profiles from all dating apps in SQLite.
"""

import sqlite3
import json
from typing import List, Dict, Optional, Any
from datetime import datetime
from pathlib import Path
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class profile_store:
    """Manages profile storage in SQLite database."""
    
    def __init__(self, db_path: str = "dating_agent.db"):
        self.db_path = Path(db_path)
        self.conn = None
        self._init_database()
    
    def _init_database(self):
        """Initialize database with required tables."""
        self.conn = sqlite3.connect(str(self.db_path))
        self.conn.row_factory = sqlite3.Row
        
        cursor = self.conn.cursor()
        
        # Profiles table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS profiles (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                platform TEXT NOT NULL,
                platform_id TEXT NOT NULL,
                name TEXT,
                age INTEGER,
                bio TEXT,
                photos TEXT,  -- JSON array of photo URLs
                interests TEXT,  -- JSON array
                location TEXT,
                distance_km REAL,
                job TEXT,
                education TEXT,
                height_cm INTEGER,
                religion TEXT,
                politics TEXT,
                smoking BOOLEAN,
                drugs BOOLEAN,
                match_status TEXT,
                fetched_at TEXT,
                UNIQUE(platform, platform_id)
            )
        """)
        
        # Duplicates table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS duplicates (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                profile_1_id INTEGER,
                profile_2_id INTEGER,
                similarity_score REAL,
                detected_at TEXT,
                FOREIGN KEY (profile_1_id) REFERENCES profiles(id),
                FOREIGN KEY (profile_2_id) REFERENCES profiles(id)
            )
        """)
        
        # Sync history
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS sync_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                platform TEXT NOT NULL,
                started_at TEXT,
                completed_at TEXT,
                profiles_count INTEGER,
                errors_count INTEGER,
                status TEXT
            )
        """)
        
        self.conn.commit()
        logger.info(f"Database initialized: {self.db_path}")
    
    def store_profile(self, profile_data: Dict[str, Any]) -> int:
        """Store a single profile in the database."""
        cursor = self.conn.cursor()
        
        cursor.execute("""
            INSERT OR REPLACE INTO profiles (
                platform, platform_id, name, age, bio, photos, interests,
                location, distance_km, job, education, height_cm,
                religion, politics, smoking, drugs, match_status, fetched_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            profile_data.get('platform'),
            profile_data.get('platform_id'),
            profile_data.get('name'),
            profile_data.get('age'),
            profile_data.get('bio'),
            json.dumps(profile_data.get('photos', [])),
            json.dumps(profile_data.get('interests', [])),
            profile_data.get('location'),
            profile_data.get('distance_km'),
            profile_data.get('job'),
            profile_data.get('education'),
            profile_data.get('height_cm'),
            profile_data.get('religion'),
            profile_data.get('politics'),
            profile_data.get('smoking'),
            profile_data.get('drugs'),
            profile_data.get('match_status'),
            datetime.now().isoformat()
        ))
        
        self.conn.commit()
        return cursor.lastrowid
    
    def get_all_profiles(self, platform: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get all profiles, optionally filtered by platform."""
        cursor = self.conn.cursor()
        
        if platform:
            cursor.execute("SELECT * FROM profiles WHERE platform = ?", (platform,))
        else:
            cursor.execute("SELECT * FROM profiles")
        
        rows = cursor.fetchall()
        return [dict(row) for row in rows]
    
    def get_duplicates(self) -> List[Dict[str, Any]]:
        """Get all detected duplicate profiles."""
        cursor = self.conn.cursor()
        
        cursor.execute("""
            SELECT 
                d.id, d.similarity_score, d.detected_at,
                p1.platform as platform_1, p1.name as name_1, p1.age as age_1,
                p2.platform as platform_2, p2.name as name_2, p2.age as age_2
            FROM duplicates d
            JOIN profiles p1 ON d.profile_1_id = p1.id
            JOIN profiles p2 ON d.profile_2_id = p2.id
        """)
        
        rows = cursor.fetchall()
        return [dict(row) for row in rows]
    
    def store_duplicate(self, profile_1_id: int, profile_2_id: int, similarity: float):
        """Record a duplicate profile pair."""
        cursor = self.conn.cursor()
        
        cursor.execute("""
            INSERT INTO duplicates (profile_1_id, profile_2_id, similarity_score, detected_at)
            VALUES (?, ?, ?, ?)
        """, (profile_1_id, profile_2_id, similarity, datetime.now().isoformat()))
        
        self.conn.commit()
    
    def get_stats(self) -> Dict[str, Any]:
        """Get database statistics."""
        cursor = self.conn.cursor()
        
        # Total profiles
        cursor.execute("SELECT COUNT(*) as total FROM profiles")
        total = cursor.fetchone()['total']
        
        # By platform
        cursor.execute("SELECT platform, COUNT(*) as count FROM profiles GROUP BY platform")
        by_platform = {row['platform']: row['count'] for row in cursor.fetchall()}
        
        # Duplicates
        cursor.execute("SELECT COUNT(*) as total FROM duplicates")
        duplicate_pairs = cursor.fetchone()['total']
        
        return {
            'total_profiles': total,
            'by_platform': by_platform,
            'duplicate_pairs': duplicate_pairs
        }
    
    def close(self):
        """Close database connection."""
        if self.conn:
            self.conn.close()
    
    def __del__(self):
        """Cleanup on deletion."""
        self.close()
