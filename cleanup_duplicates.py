#!/usr/bin/env python3
"""
AdCopySurge Cleanup Script - Remove Duplicate Files and Consolidate Architecture

This script removes duplicate analyzer files and obsolete configuration files
that are no longer needed after the tools architecture consolidation.

Run this AFTER verifying the updated main_launch_ready.py works correctly.
"""

import os
import shutil
from pathlib import Path

# Base directory
BASE_DIR = Path(__file__).parent

def backup_file(file_path):
    """Create backup of file before deletion"""
    backup_path = f"{file_path}.backup"
    if os.path.exists(file_path):
        shutil.copy2(file_path, backup_path)
        print(f"✓ Backed up {file_path} -> {backup_path}")
        return True
    return False

def remove_file(file_path, description=""):
    """Safely remove a file with backup"""
    if os.path.exists(file_path):
        if backup_file(file_path):
            os.remove(file_path)
            print(f"🗑️  Removed {description}: {file_path}")
            return True
    else:
        print(f"⚠️  File not found: {file_path}")
    return False

def main():
    print("🧹 AdCopySurge Duplicate Cleanup Script")
    print("=" * 50)
    
    # Files to remove after consolidation
    files_to_remove = [
        # Legacy analyzer files (replaced by unified SDK)
        {
            "path": BASE_DIR / "backend/app/services/readability_analyzer.py",
            "desc": "Legacy readability analyzer"
        },
        {
            "path": BASE_DIR / "backend/app/services/cta_analyzer.py", 
            "desc": "Legacy CTA analyzer"
        },
        {
            "path": BASE_DIR / "backend/app/services/emotion_analyzer.py",
            "desc": "Legacy emotion analyzer"
        },
        
        # Redundant environment files
        {
            "path": BASE_DIR / "backend/.env.local",
            "desc": "Local environment file (use .env.production.template)"
        },
        {
            "path": BASE_DIR / "backend/.env.vps", 
            "desc": "VPS environment file (use .env.production.template)"
        },
        {
            "path": BASE_DIR / "frontend/.env.backup",
            "desc": "Frontend environment backup"
        },
        
        # Obsolete deployment files
        {
            "path": BASE_DIR / "DEPLOY_FLY.md",
            "desc": "Fly.io deployment guide (replaced by Datalix VPS guide)"
        },
        
        # Test files that may cause confusion
        {
            "path": BASE_DIR / "backend/comprehensive_tool_test.py",
            "desc": "Old comprehensive test (use unified SDK tests)"
        },
        {
            "path": BASE_DIR / "backend/simplified_tool_test.py", 
            "desc": "Old simplified test"
        },
        
        # Multiple schema files (keep only one authoritative version)
        {
            "path": BASE_DIR / "clean-supabase-schema.sql",
            "desc": "Duplicate schema file"
        },
        {
            "path": BASE_DIR / "database_migration_safe.sql",
            "desc": "Migration file (should be handled by Alembic)"
        }
    ]
    
    print(f"\n📋 Found {len(files_to_remove)} files to clean up:")
    
    removed_count = 0
    for item in files_to_remove:
        if remove_file(item["path"], item["desc"]):
            removed_count += 1
    
    # Clean up old documentation that might be outdated
    outdated_docs = [
        BASE_DIR / "BLOG_FIX_README.md",
        BASE_DIR / "PHASE2_TOOLS_UNIFICATION_COMPLETE.md", 
        BASE_DIR / "COMPREHENSIVE_FIXES_ANALYSIS.md",
        BASE_DIR / "CORRECT_DEPLOYMENT_FIX.md"
    ]
    
    print(f"\n📚 Archiving outdated documentation:")
    archive_dir = BASE_DIR / "docs_archive"
    archive_dir.mkdir(exist_ok=True)
    
    for doc in outdated_docs:
        if doc.exists():
            shutil.move(str(doc), str(archive_dir / doc.name))
            print(f"📁 Archived {doc.name} -> docs_archive/")
    
    print(f"\n✅ Cleanup completed!")
    print(f"   • Removed {removed_count} duplicate/obsolete files")
    print(f"   • Archived outdated documentation")
    print(f"   • Created backups with .backup extension")
    
    print(f"\n🔄 Next steps:")
    print(f"   1. Test the updated application: python backend/main_launch_ready.py")
    print(f"   2. If everything works, you can delete the .backup files")
    print(f"   3. Commit the cleaned up codebase")
    print(f"   4. Deploy using: DATALIX_VPS_DEPLOYMENT_GUIDE.md")
    
    print(f"\n⚠️  If anything breaks, restore from backups:")
    print(f"   cp file.backup file")

if __name__ == "__main__":
    main()