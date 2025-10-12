#!/usr/bin/env python3
"""
AdCopySurge Database Diagnostic Script
=====================================
This script analyzes your Supabase database structure and data
to ensure the dashboard endpoints return the correct format.
"""

import os
import sys
from datetime import datetime, timedelta
from typing import Dict, Any
import json

# Load environment variables
try:
    from dotenv import load_dotenv
    load_dotenv()
    print("✅ Environment variables loaded")
except ImportError:
    print("⚠️ python-dotenv not found. Install with: pip install python-dotenv")

# Import Supabase
try:
    from supabase import create_client, Client
    print("✅ Supabase client available")
except ImportError:
    print("❌ Supabase not found. Install with: pip install supabase")
    sys.exit(1)

def connect_to_supabase():
    """Initialize Supabase client"""
    SUPABASE_URL = os.getenv('SUPABASE_URL')
    SUPABASE_SERVICE_KEY = os.getenv('SUPABASE_SERVICE_ROLE_KEY')
    
    if not SUPABASE_URL or not SUPABASE_SERVICE_KEY:
        print("❌ Missing Supabase environment variables")
        print("   Required: SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY")
        return None
    
    try:
        client = create_client(SUPABASE_URL, SUPABASE_SERVICE_KEY)
        print(f"✅ Connected to Supabase: {SUPABASE_URL[:30]}...")
        return client
    except Exception as e:
        print(f"❌ Failed to connect to Supabase: {e}")
        return None

def analyze_table_structure(client: Client, table_name: str):
    """Analyze table structure and sample data"""
    print(f"\n🔍 Analyzing table: {table_name}")
    
    try:
        # Get sample records
        response = client.table(table_name).select("*").limit(3).execute()
        data = response.data
        
        if not data:
            print(f"   📊 Table '{table_name}' is empty")
            return None
        
        print(f"   📊 Found {len(data)} sample records")
        
        # Analyze columns
        if data:
            sample_record = data[0]
            print(f"   📋 Columns ({len(sample_record.keys())}):")
            for key, value in sample_record.items():
                value_type = type(value).__name__
                value_preview = str(value)[:50] + "..." if len(str(value)) > 50 else str(value)
                print(f"      - {key}: {value_type} = {value_preview}")
        
        return data
    
    except Exception as e:
        print(f"   ❌ Error analyzing {table_name}: {e}")
        return None

def analyze_user_data(client: Client, user_id: str):
    """Analyze data for specific user"""
    print(f"\n👤 Analyzing data for user: {user_id}")
    
    # Analyze ad_analyses
    try:
        analyses = client.table('ad_analyses').select("*").eq('user_id', user_id).execute()
        analyses_data = analyses.data
        print(f"   📊 User has {len(analyses_data)} ad analyses")
        
        if analyses_data:
            # Analyze score columns
            score_columns = ['overall_score', 'clarity_score', 'persuasion_score', 
                           'emotion_score', 'cta_strength', 'platform_fit_score']
            
            print("   📈 Score column analysis:")
            for col in score_columns:
                values = [a.get(col) for a in analyses_data if a.get(col) is not None]
                if values:
                    print(f"      - {col}: {len(values)} records, range {min(values):.1f}-{max(values):.1f}")
                else:
                    print(f"      - {col}: NO DATA")
            
            # Platform analysis
            platforms = [a.get('platform') for a in analyses_data if a.get('platform')]
            unique_platforms = set(platforms)
            print(f"   🎯 Platforms: {unique_platforms}")
            
            # Date range analysis
            dates = [a.get('created_at') for a in analyses_data if a.get('created_at')]
            if dates:
                print(f"   📅 Date range: {min(dates)} to {max(dates)}")
        
        return analyses_data
    
    except Exception as e:
        print(f"   ❌ Error analyzing user data: {e}")
        return []

def analyze_projects(client: Client, user_id: str):
    """Analyze projects for user"""
    try:
        projects = client.table('projects').select("*").eq('user_id', user_id).execute()
        projects_data = projects.data
        print(f"   📁 User has {len(projects_data)} projects")
        
        if projects_data:
            for project in projects_data:
                print(f"      - {project.get('name', 'Unnamed')}: {project.get('description', 'No description')[:50]}")
        
        return projects_data
    
    except Exception as e:
        print(f"   ❌ Error analyzing projects: {e}")
        return []

def expected_dashboard_format():
    """Show what the UI expects"""
    print("\n🎯 Expected Dashboard API Response Format:")
    
    expected_metrics = {
        "adsAnalyzed": "int - number of ads analyzed in period",
        "adsAnalyzedChange": "float - percentage change vs previous period", 
        "avgImprovement": "float - average score improvement",
        "avgImprovementChange": "float - change in improvement",
        "avgScore": "float - average overall score",
        "avgScoreChange": "float - change in average score",
        "topPerforming": "float - highest score in period",
        "topPerformingChange": "float - change in top score",
        "periodStart": "string - ISO date",
        "periodEnd": "string - ISO date",
        "periodDays": "int - period length"
    }
    
    expected_summary = {
        "totalAnalyses": "int - lifetime total",
        "lifetimeAvgScore": "float - all-time average",
        "bestScore": "float - highest ever score", 
        "analysesLast30Days": "int - recent activity",
        "platformsUsed": "int - number of platforms",
        "projectsCount": "int - number of projects",
        "firstAnalysisDate": "string - ISO date",
        "lastAnalysisDate": "string - ISO date",
        "isNewUser": "bool - less than 7 days"
    }
    
    print("📊 /api/dashboard/metrics:")
    for key, desc in expected_metrics.items():
        print(f"   - {key}: {desc}")
    
    print("\n📋 /api/dashboard/metrics/summary:")
    for key, desc in expected_summary.items():
        print(f"   - {key}: {desc}")

def generate_test_response(client: Client, user_id: str):
    """Generate test response based on actual data"""
    print(f"\n🧪 Generating test response for user: {user_id}")
    
    try:
        # Get all analyses
        analyses = client.table('ad_analyses').select("*").eq('user_id', user_id).execute()
        analyses_data = analyses.data
        
        # Get projects
        projects = client.table('projects').select("*").eq('user_id', user_id).execute()
        projects_data = projects.data
        
        # Calculate metrics
        total_analyses = len(analyses_data)
        
        if analyses_data:
            scores = [a.get('overall_score') for a in analyses_data if a.get('overall_score')]
            if scores:
                avg_score = sum(scores) / len(scores)
                best_score = max(scores)
            else:
                avg_score = 0
                best_score = 0
        else:
            avg_score = 0
            best_score = 0
        
        test_response = {
            "metrics": {
                "adsAnalyzed": total_analyses,
                "adsAnalyzedChange": 12.5,
                "avgImprovement": 15.2,
                "avgImprovementChange": 8.3,
                "avgScore": round(avg_score, 1),
                "avgScoreChange": 3.2,
                "topPerforming": round(best_score, 1),
                "topPerformingChange": 1.5,
                "periodStart": (datetime.now() - timedelta(days=30)).isoformat(),
                "periodEnd": datetime.now().isoformat(),
                "periodDays": 30
            },
            "summary": {
                "totalAnalyses": total_analyses,
                "lifetimeAvgScore": round(avg_score, 1),
                "bestScore": round(best_score, 1),
                "analysesLast30Days": total_analyses,
                "platformsUsed": len(set(a.get('platform') for a in analyses_data if a.get('platform'))),
                "projectsCount": len(projects_data),
                "firstAnalysisDate": analyses_data[0].get('created_at') if analyses_data else datetime.now().isoformat(),
                "lastAnalysisDate": analyses_data[-1].get('created_at') if analyses_data else datetime.now().isoformat(),
                "isNewUser": total_analyses < 5
            }
        }
        
        print("✅ Generated test response:")
        print(json.dumps(test_response, indent=2))
        
        return test_response
    
    except Exception as e:
        print(f"❌ Error generating test response: {e}")
        return None

def main():
    """Main diagnostic function"""
    print("🔍 AdCopySurge Database Diagnostic")
    print("=" * 50)
    
    # Connect to Supabase
    client = connect_to_supabase()
    if not client:
        return
    
    # Analyze table structures
    tables_to_analyze = ['ad_analyses', 'projects', 'user_profiles']
    for table in tables_to_analyze:
        analyze_table_structure(client, table)
    
    # Show expected format
    expected_dashboard_format()
    
    # Test with specific user ID
    test_user_id = "af439000-8685-4181-be9c-173157ee8031"  # Your actual user ID
    print(f"\n🔬 Detailed Analysis for User: {test_user_id}")
    
    user_analyses = analyze_user_data(client, test_user_id)
    user_projects = analyze_projects(client, test_user_id)
    
    # Generate test response
    test_response = generate_test_response(client, test_user_id)
    
    print(f"\n✅ Diagnostic Complete!")
    print(f"📊 Found {len(user_analyses) if user_analyses else 0} analyses")
    print(f"📁 Found {len(user_projects) if user_projects else 0} projects")
    print(f"🎯 Test response generated: {'Yes' if test_response else 'No'}")

if __name__ == "__main__":
    main()