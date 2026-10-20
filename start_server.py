#!/usr/bin/env python3
"""
Prospector Backend Server Starter
Starts the FastAPI backend on port 8000
"""

import os
import sys
import subprocess

def main():
    # Get project root directory
    project_root = os.path.dirname(os.path.abspath(__file__))

    print("🚀 Starting Prospector Backend Server...")
    print(f"📁 Project root: {project_root}")

    # Kill any existing process on port 8000
    print("🔍 Checking for existing server on port 8001...")
    try:
        subprocess.run(
            ["lsof", "-ti:8001"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=True
        )
        print("⚠️  Found existing server, stopping it...")
        subprocess.run("lsof -ti:8001 | xargs kill -9", shell=True)
        print("✅ Stopped existing server")
    except subprocess.CalledProcessError:
        print("✅ Port 8001 is available")

    print("🌐 Server will be available at: http://localhost:8001")
    print("📚 API docs will be available at: http://localhost:8001/docs")
    print("\n" + "="*60)

    # Change to project root
    os.chdir(project_root)

    # Start uvicorn server
    try:
        subprocess.run([
            sys.executable, "-m", "uvicorn",
            "backend_api.main:app",
            "--host", "0.0.0.0",
            "--port", "8001",
            "--reload"  # Auto-reload on code changes
        ], check=True)
    except KeyboardInterrupt:
        print("\n\n👋 Server stopped by user")
    except subprocess.CalledProcessError as e:
        print(f"\n❌ Server failed to start: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
