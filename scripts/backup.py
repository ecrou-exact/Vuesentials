# backup.py
import argparse
import sqlite3
import shutil
import os
from datetime import datetime
from pathlib import Path

def backup_database(db_path=None, backup_dir='backups'):
    if db_path is None:
        root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        db_path = os.path.join(root_dir, 'instance', 'vueEsential.sqlite')
    
    if not os.path.exists(db_path):
        print(f"Error: Database file '{db_path}' not found")
        return False
    
    os.makedirs(backup_dir, exist_ok=True)
    
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_filename = f"vueEsential_backup_{timestamp}.sqlite"
    backup_path = os.path.join(backup_dir, backup_filename)
    
    try:
        shutil.copy2(db_path, backup_path)
        print(f"✓ Database backed up successfully to: {backup_path}")
        return True
    except Exception as e:
        print(f"✗ Error backing up database: {str(e)}")
        return False

def list_backups(backup_dir='backups'):
    if not os.path.exists(backup_dir):
        print("No backups found")
        return
    
    backups = sorted([f for f in os.listdir(backup_dir) if f.endswith('.sqlite')])
    
    if not backups:
        print("No backups found")
        return
    
    print("\nAvailable backups:")
    for i, backup in enumerate(backups, 1):
        backup_path = os.path.join(backup_dir, backup)
        size = os.path.getsize(backup_path) / 1024
        date = os.path.getmtime(backup_path)
        date_str = datetime.fromtimestamp(date).strftime('%Y-%m-%d %H:%M:%S')
        print(f"{i}. {backup} ({size:.2f} KB) - {date_str}")

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Database backup utility')
    parser.add_argument('-b', '--backup', help='Create a new backup', action='store_true')
    parser.add_argument('-l', '--list', help='List all available backups', action='store_true')
    parser.add_argument('-d', '--backup-dir', default='backups', help='Backup directory (default: backups)')
    parser.add_argument('-db', '--database', default=None, help='Database path')
    
    args = parser.parse_args()
    
    if args.backup:
        backup_database(args.database, args.backup_dir)
    elif args.list:
        list_backups(args.backup_dir)
    else:
        parser.print_help()