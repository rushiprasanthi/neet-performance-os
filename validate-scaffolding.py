#!/usr/bin/env python3
"""Validation script to verify scaffolding completeness."""

import os
import sys
from pathlib import Path

def check_file_exists(path: str, description: str) -> bool:
    """Check if a file exists and report."""
    if Path(path).exists():
        print(f"✅ {description}")
        return True
    else:
        print(f"❌ {description} - MISSING: {path}")
        return False

def check_dir_exists(path: str, description: str) -> bool:
    """Check if a directory exists and report."""
    if Path(path).is_dir():
        print(f"✅ {description}")
        return True
    else:
        print(f"❌ {description} - MISSING: {path}")
        return False

def main():
    """Run validation checks."""
    print("🔍 NEET Platform Scaffolding Validation\n")
    
    checks_passed = 0
    checks_failed = 0
    
    # Backend files
    print("📦 Backend Files:")
    backend_files = [
        ("backend/app/main.py", "FastAPI app factory"),
        ("backend/app/config.py", "Pydantic settings"),
        ("backend/app/database.py", "SQLAlchemy async setup"),
        ("backend/app/celery_app.py", "Celery configuration"),
        ("backend/app/__init__.py", "Backend package marker"),
        ("backend/pyproject.toml", "Poetry dependencies"),
        ("backend/alembic.ini", "Alembic configuration"),
        ("backend/alembic/env.py", "Async migration environment"),
        ("backend/conftest.py", "Pytest configuration"),
        ("backend/Dockerfile", "Backend container"),
        ("backend/.env", "Development environment"),
        ("backend/.env.example", "Environment template"),
        ("backend/tests/__init__.py", "Tests package"),
        ("backend/tests/test_health.py", "Health check tests"),
    ]
    
    for path, desc in backend_files:
        if check_file_exists(path, desc):
            checks_passed += 1
        else:
            checks_failed += 1
    
    # Backend directories
    print("\n📁 Backend Directories:")
    backend_dirs = [
        ("backend/app", "App package"),
        ("backend/alembic", "Alembic package"),
        ("backend/alembic/versions", "Migrations directory"),
        ("backend/tests", "Tests package"),
    ]
    
    for path, desc in backend_dirs:
        if check_dir_exists(path, desc):
            checks_passed += 1
        else:
            checks_failed += 1
    
    # Frontend files
    print("\n🎨 Frontend Files:")
    frontend_files = [
        ("frontend/package.json", "NPM dependencies"),
        ("frontend/vite.config.ts", "Vite configuration"),
        ("frontend/tsconfig.json", "TypeScript config"),
        ("frontend/tsconfig.node.json", "Vite TypeScript config"),
        ("frontend/.eslintrc.cjs", "ESLint configuration"),
        ("frontend/index.html", "HTML entry point"),
        ("frontend/Dockerfile", "Frontend container"),
        ("frontend/.env", "Development environment"),
        ("frontend/.env.example", "Environment template"),
        ("frontend/src/main.tsx", "React entry point"),
        ("frontend/src/App.tsx", "Root component"),
        ("frontend/src/api/client.ts", "HTTP client"),
        ("frontend/src/App.css", "Component styles"),
        ("frontend/src/index.css", "Global styles"),
    ]
    
    for path, desc in frontend_files:
        if check_file_exists(path, desc):
            checks_passed += 1
        else:
            checks_failed += 1
    
    # Frontend directories
    print("\n📁 Frontend Directories:")
    frontend_dirs = [
        ("frontend/src", "Source directory"),
        ("frontend/src/api", "API utilities"),
        ("frontend/public", "Public assets"),
    ]
    
    for path, desc in frontend_dirs:
        if check_dir_exists(path, desc):
            checks_passed += 1
        else:
            checks_failed += 1
    
    # Infrastructure files
    print("\n⚙️  Infrastructure Files:")
    infra_files = [
        ("docker-compose.yml", "Docker Compose configuration"),
        (".github/workflows/ci.yml", "GitHub Actions CI/CD"),
        (".gitignore", "Git ignore patterns"),
        ("README.md", "Documentation"),
        ("SCAFFOLDING_COMPLETE.md", "Scaffolding checklist"),
        ("dev-setup.sh", "Linux/Mac setup script"),
        ("dev-setup.bat", "Windows setup script"),
    ]
    
    for path, desc in infra_files:
        if check_file_exists(path, desc):
            checks_passed += 1
        else:
            checks_failed += 1
    
    # Summary
    print(f"\n" + "="*50)
    print(f"✅ Passed: {checks_passed}")
    print(f"❌ Failed: {checks_failed}")
    print(f"📊 Total: {checks_passed + checks_failed}")
    print("="*50)
    
    if checks_failed == 0:
        print("\n✨ All scaffolding files present! Ready to go! 🚀")
        return 0
    else:
        print(f"\n⚠️  {checks_failed} file(s) missing. Please check above.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
