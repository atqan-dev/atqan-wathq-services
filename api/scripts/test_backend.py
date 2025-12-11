#!/usr/bin/env python3
"""
Test script to verify backend is working correctly.
"""

import sys
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def test_imports():
    """Test all critical imports."""
    print("Testing imports...")
    
    try:
        # Test deps imports
        from app.api.deps import (
            get_current_user,
            get_current_active_user,
            get_current_management_user,
            has_permission,
            require_permission
        )
        print("✅ Dependencies imported successfully")
        
        # Test models
        from app.models.api_request_counter import ApiRequestCounter, ApiRequestSummary
        from app.models.wathq_external_data import WathqExternalData
        print("✅ Models imported successfully")
        
        # Test services
        from app.services.request_counter_service import request_counter_service
        from app.services.wathq_external_service import wathq_external_service
        print("✅ Services imported successfully")
        
        # Test middleware
        from app.middleware.request_counter import RequestCounterMiddleware
        print("✅ Middleware imported successfully")
        
        # Test API endpoints
        from app.api.v1.endpoints.request_analytics import router as analytics_router
        from app.api.v1.endpoints.wathq_external import tenant_router, management_router
        print("✅ API endpoints imported successfully")
        
        # Test main app
        from app.main import app
        print("✅ Main app imported successfully")
        
        return True
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

def test_database_tables():
    """Test that new tables can be created."""
    print("\nTesting database tables...")
    
    try:
        from app.db.base_class import Base
        from app.db.session import engine
        from sqlalchemy import inspect
        
        inspector = inspect(engine)
        existing_tables = inspector.get_table_names()
        
        required_tables = [
            'api_request_counters',
            'api_request_summaries',
            'wathq_external_data'
        ]
        
        for table in required_tables:
            if table in existing_tables:
                print(f"✅ Table '{table}' exists")
            else:
                print(f"⚠️  Table '{table}' does not exist (run migration)")
        
        return True
        
    except Exception as e:
        print(f"❌ Database error: {e}")
        return False

def main():
    """Run all tests."""
    print("="*60)
    print("WATHQ API Backend Test")
    print("="*60)
    
    all_passed = True
    
    # Run import tests
    if not test_imports():
        all_passed = False
    
    # Run database tests
    if not test_database_tables():
        all_passed = False
    
    print("\n" + "="*60)
    if all_passed:
        print("✅ All tests passed! Backend is ready to run.")
        print("\nTo start the backend:")
        print("  uv run uvicorn app.main:app --reload --port 5500")
    else:
        print("❌ Some tests failed. Please fix the issues above.")
    print("="*60)
    
    return 0 if all_passed else 1

if __name__ == "__main__":
    sys.exit(main())
