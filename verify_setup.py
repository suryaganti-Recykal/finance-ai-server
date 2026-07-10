#!/usr/bin/env python3
"""Verify Finance AI setup is working correctly."""

import subprocess
import sys
import time
from pathlib import Path

def run_command(cmd):
    """Run a shell command and return output."""
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=5)
        return result.returncode, result.stdout, result.stderr
    except subprocess.TimeoutExpired:
        return -1, "", "Command timed out"
    except Exception as e:
        return -1, "", str(e)

def check_backend():
    """Check if backend is running."""
    print("\n" + "="*60)
    print("CHECKING BACKEND (port 8000)")
    print("="*60)

    returncode, stdout, stderr = run_command("curl -s http://localhost:8000/api/v1/health")

    if returncode == 0 and "ok" in stdout:
        print("✅ Backend is RUNNING")
        print(f"   Response: {stdout.strip()}")
        return True
    else:
        print("❌ Backend is NOT RUNNING")
        print("   Fix: Start backend with:")
        print("   cd app")
        print("   python -m venv venv")
        print("   source venv/bin/activate  # Windows: venv\\Scripts\\activate")
        print("   pip install -e .")
        print("   uvicorn src.main:app --reload")
        return False

def check_frontend():
    """Check if frontend is running."""
    print("\n" + "="*60)
    print("CHECKING FRONTEND (port 3000)")
    print("="*60)

    returncode, stdout, stderr = run_command("curl -s http://localhost:3000")

    if returncode == 0 and "html" in stdout.lower():
        print("✅ Frontend is RUNNING")
        print("   Access at: http://localhost:3000")
        return True
    else:
        print("❌ Frontend is NOT RUNNING")
        print("   Fix: Start frontend with:")
        print("   cd frontend")
        print("   npm install")
        print("   npm run dev")
        return False

def check_api_docs():
    """Check if API docs are available."""
    print("\n" + "="*60)
    print("CHECKING API DOCS (Swagger UI)")
    print("="*60)

    returncode, stdout, stderr = run_command("curl -s http://localhost:8000/docs")

    if returncode == 0 and "swagger" in stdout.lower():
        print("✅ API Docs available at: http://localhost:8000/docs")
        return True
    else:
        print("❌ API Docs not available")
        return False

def check_demo_data():
    """Check if demo data is accessible."""
    print("\n" + "="*60)
    print("CHECKING DEMO DATA")
    print("="*60)

    returncode, stdout, stderr = run_command("curl -s http://localhost:8000/api/v1/demo/all")

    if returncode == 0 and "expenses" in stdout.lower():
        print("✅ Demo data is accessible")
        # Count items
        if "Slack" in stdout:
            print("   ✓ Expense data found")
        if "Facebook" in stdout or "Facebook" in stdout:
            print("   ✓ Marketing data found")
        return True
    else:
        print("❌ Demo data not accessible")
        print("   Make sure backend is running and USE_SHEETS_FOR_DEMO=true")
        return False

def check_python():
    """Check Python version."""
    print("\n" + "="*60)
    print("CHECKING PYTHON")
    print("="*60)

    returncode, stdout, stderr = run_command("python --version")

    if returncode == 0:
        print(f"✅ Python: {stdout.strip()}")
        version = stdout.strip().split()[-1]
        major, minor = map(int, version.split('.')[:2])
        if major >= 3 and minor >= 10:
            print("   Version is compatible (3.10+)")
            return True
        else:
            print("   ⚠ Warning: Python 3.12+ recommended")
            return False
    else:
        print("❌ Python not found")
        return False

def check_node():
    """Check Node.js version."""
    print("\n" + "="*60)
    print("CHECKING NODE.JS")
    print("="*60)

    returncode, stdout, stderr = run_command("node --version")

    if returncode == 0:
        print(f"✅ Node.js: {stdout.strip()}")
        return True
    else:
        print("❌ Node.js not found")
        print("   Install from: https://nodejs.org/")
        return False

def check_files():
    """Check if critical files exist."""
    print("\n" + "="*60)
    print("CHECKING PROJECT FILES")
    print("="*60)

    files_to_check = [
        ("app/src/main.py", "Backend app factory"),
        ("app/pyproject.toml", "Backend dependencies"),
        ("frontend/package.json", "Frontend dependencies"),
        ("frontend/src/pages/index.tsx", "Dashboard page"),
        ("docker-compose.yml", "Docker configuration"),
    ]

    all_exist = True
    for file_path, description in files_to_check:
        exists = Path(file_path).exists()
        status = "✅" if exists else "❌"
        print(f"{status} {description}: {file_path}")
        if not exists:
            all_exist = False

    return all_exist

def main():
    """Run all checks."""
    print("\n")
    print("╔" + "="*58 + "╗")
    print("║" + " FINANCE AI SETUP VERIFICATION ".center(58) + "║")
    print("╚" + "="*58 + "╝")

    results = {}

    # Check environment
    results["Python"] = check_python()
    results["Node.js"] = check_node()
    results["Files"] = check_files()

    # Check services
    backend_running = check_backend()
    frontend_running = check_frontend()

    if backend_running:
        results["API Docs"] = check_api_docs()
        results["Demo Data"] = check_demo_data()

    results["Backend"] = backend_running
    results["Frontend"] = frontend_running

    # Summary
    print("\n" + "="*60)
    print("SUMMARY")
    print("="*60)

    passed = sum(1 for v in results.values() if v)
    total = len(results)

    for check, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status}: {check}")

    print(f"\nPassed: {passed}/{total}")

    # Recommendations
    if backend_running and frontend_running:
        print("\n" + "="*60)
        print("SUCCESS!")
        print("="*60)
        print("✅ Dashboard should be visible at: http://localhost:3000")
        print("✅ API documentation at: http://localhost:8000/docs")
        print("✅ Try the demo endpoints in Swagger UI")
    else:
        print("\n" + "="*60)
        print("NEXT STEPS")
        print("="*60)
        if not backend_running:
            print("\n1. Start Backend:")
            print("   cd app")
            print("   python -m venv venv")
            print("   source venv/bin/activate  # Windows: venv\\Scripts\\activate")
            print("   pip install -e .")
            print("   uvicorn src.main:app --reload")

        if not frontend_running:
            print("\n2. Start Frontend (in new terminal):")
            print("   cd frontend")
            print("   npm install")
            print("   npm run dev")

        if backend_running and frontend_running:
            print("\n3. Open http://localhost:3000 in your browser")

    print("\n" + "="*60 + "\n")

    return 0 if (backend_running and frontend_running) else 1

if __name__ == "__main__":
    sys.exit(main())
