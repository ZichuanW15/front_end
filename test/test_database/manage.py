"""
Test database manager class for programmatic access.
"""

import os
import subprocess
import sys
from pathlib import Path


class TestDatabaseManager:
    """Manager class for test database operations."""
    
    def __init__(self):
        self.script_path = Path(__file__).parent / 'manage_test_db.py'
    
    def create(self):
        """Create test database."""
        return self._run_command('create')
    
    def drop(self):
        """Drop test database."""
        return self._run_command('drop')
    
    def reset(self):
        """Reset test database."""
        return self._run_command('reset')
    
    def setup(self):
        """Setup schema only."""
        return self._run_command('setup')
    
    def seed(self):
        """Seed with sample data only."""
        return self._run_command('seed')
    
    def info(self):
        """Get database information."""
        return self._run_command('info')
    
    def full_setup(self):
        """Full setup (create + schema + seed)."""
        return self._run_command('full-setup')
    
    def _run_command(self, command):
        """Run a test database management command."""
        try:
            result = subprocess.run([sys.executable, str(self.script_path), command], 
                                  capture_output=True, text=True)
            return {
                'success': result.returncode == 0,
                'output': result.stdout,
                'error': result.stderr
            }
        except Exception as e:
            return {
                'success': False,
                'output': '',
                'error': str(e)
            }