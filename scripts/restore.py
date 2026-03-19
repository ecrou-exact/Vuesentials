# restore.py
import argparse
import sqlite3
import shutil
import os
from datetime import datetime

def confirm_restore(backup_filename):
    print(f"\n⚠️  WARNING: This will overwrite your current database with: {backup_filename}")
    print("This action cannot be undone!")
    
    first_confirm = input("\nAre you sure you want to restore from this backup? (yes/no): ").strip().lower()
    
    if first_confirm != 'yes':
        print("✗ Restore cancelled")
        return False
    
    second_confirm = input("Please type 'RESTORE' to confirm: ").strip()
    
    if second_confirm != 'RESTORE':
        print("✗ Restore cancelled")
        return False
    
    print("✓ Confirmed. Proceeding with restore...")
    return True

def restore_database(backup_path, db_path=None):
    if db_path is None:
        root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        db_path = os.path.join(root_dir, 'instance', 'vueEsential.sqlite')
    
    if not os.path.exists(backup_path):
        print(f"Error: Backup file '{backup_path}' not found")
        return False
    
    if not confirm_restore(os.path.basename(backup_path)):
        return False
    
    try:
        backup_time = datetime.now().strftime('%Y%m%d_%H%M%S')
        current_backup = f"{db_path}.backup_{backup_time}"
        
        if os.path.exists(db_path):
            shutil.copy2(db_path, current_backup)
            print(f"✓ Current database backed up to: {current_backup}")
        
        shutil.copy2(backup_path, db_path)
        print(f"✓ Database restored successfully from: {backup_path}")
        return True
    except Exception as e:
        print(f"✗ Error restoring database: {str(e)}")
        return False

def list_backups(backup_dir='backups'):
    if not os.path.exists(backup_dir):
        print("No backups found")
        return []
    
    backups = sorted([f for f in os.listdir(backup_dir) if f.endswith('.sqlite')])
    
    if not backups:
        print("No backups found")
        return []
    
    print("\nAvailable backups:")
    for i, backup in enumerate(backups, 1):
        backup_path = os.path.join(backup_dir, backup)
        size = os.path.getsize(backup_path) / 1024
        date = os.path.getmtime(backup_path)
        date_str = datetime.fromtimestamp(date).strftime('%Y-%m-%d %H:%M:%S')
        print(f"{i}. {backup} ({size:.2f} KB) - {date_str}")
    
    return backups

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Database restore utility')
    parser.add_argument('-r', '--restore', help='Restore from backup file')
    parser.add_argument('-l', '--list', help='List all available backups', action='store_true')
    parser.add_argument('-i', '--interactive', help='Select backup interactively', action='store_true')
    parser.add_argument('-d', '--backup-dir', default='backups', help='Backup directory (default: backups)')
    parser.add_argument('-db', '--database', default=None, help='Database path')
    
    args = parser.parse_args()
    
    if args.restore:
        restore_database(args.restore, args.database)
    elif args.interactive:
        backups = list_backups(args.backup_dir)
        if backups:
            try:
                choice = int(input("\nEnter backup number to restore: ")) - 1
                if 0 <= choice < len(backups):
                    backup_path = os.path.join(args.backup_dir, backups[choice])
                    restore_database(backup_path, args.database)
                else:
                    print("Invalid choice")
            except ValueError:
                print("Invalid input")
    elif args.list:
        list_backups(args.backup_dir)
    else:
        parser.print_help()