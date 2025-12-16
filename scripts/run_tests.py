#!/usr/bin/env python3
"""
Скрипт для запуска тестов с разными опциями
"""
import argparse
import subprocess
import sys
from pathlib import Path

def run_tests(test_path=None, coverage=False, verbose=False, specific_test=None):
    """Запустить тесты"""
    cmd = [sys.executable, "-m", "pytest"]
    
    if verbose:
        cmd.append("-v")
    
    if coverage:
        cmd.extend(["--cov=src/cell_genesis", "--cov-report=html", "--cov-report=term"])
    
    if specific_test:
        cmd.append(specific_test)
    elif test_path:
        cmd.append(str(test_path))
    else:
        cmd.append("src/tests/")
    
    print(f"🔧 Запускаю: {' '.join(cmd)}")
    result = subprocess.run(cmd)
    return result.returncode

def run_lint():
    """Запустить проверку стиля"""
    print("\n🔍 Проверяю стиль кода...")
    cmds = [
        [sys.executable, "-m", "black", "--check", "src/cell_genesis"],
        [sys.executable, "-m", "flake8", "src/cell_genesis", "--max-line-length=127"],
        [sys.executable, "-m", "mypy", "src/cell_genesis", "--ignore-missing-imports"]
    ]
    
    for cmd in cmds:
        print(f"  Запускаю: {' '.join(cmd)}")
        subprocess.run(cmd)

def main():
    parser = argparse.ArgumentParser(description="Запуск тестов Cell Genesis")
    parser.add_argument("--unit", action="store_true", help="Только юнит-тесты")
    parser.add_argument("--integration", action="store_true", help="Только интеграционные тесты")
    parser.add_argument("--coverage", action="store_true", help="С покрытием кода")
    parser.add_argument("--lint", action="store_true", help="Только проверка стиля")
    parser.add_argument("--verbose", "-v", action="store_true", help="Подробный вывод")
    parser.add_argument("--test", "-t", help="Запустить конкретный тест")
    
    args = parser.parse_args()
    
    if args.lint:
        run_lint()
        return
    
    test_path = None
    if args.unit:
        test_path = Path("src/tests/unit")
    elif args.integration:
        test_path = Path("src/tests/integration")
    
    return_code = run_tests(
        test_path=test_path,
        coverage=args.coverage,
        verbose=args.verbose,
        specific_test=args.test
    )
    
    sys.exit(return_code)

if __name__ == "__main__":
    main()
