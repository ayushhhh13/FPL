"""Simple test script to verify setup."""
import sys
import os

def test_imports():
    """Test if all imports work."""
    print("Testing imports...")
    try:
        from python_backend.database.db import init_db
        from python_backend.classifier import QueryClassifier
        from python_backend.agents.account_agent import AccountAgent
        print("✅ All imports successful")
        return True
    except Exception as e:
        print(f"❌ Import error: {e}")
        return False

def test_database():
    """Test database initialization."""
    print("\nTesting database...")
    try:
        from python_backend.database.db import init_db
        init_db()
        print("✅ Database initialized successfully")
        return True
    except Exception as e:
        print(f"❌ Database error: {e}")
        return False

def test_env():
    """Test environment variables."""
    print("\nTesting environment...")
    from dotenv import load_dotenv
    load_dotenv()
    
    openai_key = os.getenv("OPENAI_API_KEY")
    if not openai_key or openai_key == "your_openai_api_key_here":
        print("⚠️  OPENAI_API_KEY not set (required for classification)")
    else:
        print("✅ OPENAI_API_KEY found")
    
    gcp_path = os.getenv("GCP_CREDENTIALS_PATH")
    if not gcp_path or not os.path.exists(gcp_path):
        print("⚠️  GCP_CREDENTIALS_PATH not set or file not found (required for voice)")
    else:
        print("✅ GCP_CREDENTIALS_PATH found")
    
    return True

if __name__ == "__main__":
    print("🧪 Testing Credit Card Assistant Setup\n")
    
    results = []
    results.append(test_imports())
    results.append(test_database())
    test_env()
    
    if all(results):
        print("\n✅ Setup test passed!")
        sys.exit(0)
    else:
        print("\n❌ Some tests failed. Please check the errors above.")
        sys.exit(1)

