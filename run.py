#!/usr/bin/env python3
"""
Simple script to run the Healthcare Test Case Generation System.
"""

import os
import dotenv
import sys
from pathlib import Path

dotenv.load_dotenv()

# Add the current directory to Python path
sys.path.insert(0, str(Path(__file__).parent))

def main():
    """Main function to run the system."""
    print("Healthcare Test Case Generation System")
    print("=" * 50)
    
    # Check if API keys are set
    google_api_key = os.getenv("GOOGLE_API_KEY")
    tavily_api_key = os.getenv("TAVILY_API_KEY")
    
    if not google_api_key:
        print("ERROR: GOOGLE_API_KEY not found!")
        print("Please set your Gemini API key:")
        print("export GOOGLE_API_KEY='your_api_key_here'")
        return
    
    if not tavily_api_key:
        print("WARNING: TAVILY_API_KEY not found (optional)")
        print("Tavily is used for enhanced search capabilities")
    
    print("API keys configured")
    print("Starting system...")
    
    try:
        from src.testcaseaiagent.main import main as run_main
        run_main()
    except Exception as e:
        print(f"ERROR: Error running system: {e}")
        print("\nTroubleshooting:")
        print("1. Make sure all dependencies are installed: pip install -e .")
        print("2. Check your API keys are valid")
        print("3. Ensure you have internet connection")

if __name__ == "__main__":
    main()
