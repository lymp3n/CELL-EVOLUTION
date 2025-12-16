#!/usr/bin/env python3
"""
Скрипт для настройки окружения разработчика
"""
import os
import sys
import subprocess
import venv
from pathlib import Path

def run_command(cmd, cwd=None):
    """Выполнить команду в shell"""
    print(f"🚀 Выполняю: {cmd}")
    result = subprocess.run(cmd, shell=True, cwd=cwd, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"❌ Ошибка: {result.stderr}")
        return False
    print(f"✅ Успешно: {result.stdout}")
    return True

def main():
    print("=" * 60)
    print("🛠️  Настройка окружения разработчика для Cell Genesis")
    print("=" * 60)
    
    project_root = Path(__file__).parent.parent
    
    # 1. Создание виртуального окружения
    venv_path = project_root / ".venv"
    if not venv_path.exists():
        print("\n1. Создаю виртуальное окружение...")
        venv.create(venv_path, with_pip=True)
    
    # Определяем путь к python/pip в зависимости от ОС
    if sys.platform == "win32":
        python_path = venv_path / "Scripts" / "python.exe"
        pip_path = venv_path / "Scripts" / "pip.exe"
    else:
        python_path = venv_path / "bin" / "python"
        pip_path = venv_path / "bin" / "pip"
    
    # 2. Установка зависимостей
    print("\n2. Устанавливаю зависимости...")
    requirements_files = [
        "requirements/base.txt",
        "requirements/dev.txt"
    ]
    
    for req_file in requirements_files:
        req_path = project_root / req_file
        if req_path.exists():
            run_command(f'"{pip_path}" install -r "{req_path}"')
    
    # 3. Установка pre-commit хуков
    print("\n3. Настраиваю pre-commit хуки...")
    run_command(f'"{pip_path}" install pre-commit')
    run_command(f'"{python_path}" -m pre-commit install')
    
    # 4. Настройка git LFS (если нужно)
    print("\n4. Настраиваю Git LFS для ассетов...")
    run_command("git lfs install")
    run_command("git lfs track 'assets/**'")
    
    # 5. Создание конфигурационных файлов
    print("\n5. Создаю конфигурационные файлы...")
    config_example = project_root / "config.example.yaml"
    config_file = project_root / "config.yaml"
    
    if config_example.exists() and not config_file.exists():
        import shutil
        shutil.copy(config_example, config_file)
        print(f"✅ Создан {config_file}")
    
    # 6. Проверка установки
    print("\n6. Проверяю установку...")
    test_commands = [
        f'"{python_path}" --version',
        f'"{python_path}" -c "import pygame; print(f\"Pygame: {pygame.version.ver}\")"',
        f'"{python_path}" -c "import numpy; print(f\"NumPy: {numpy.__version__}\")"'
    ]
    
    for cmd in test_commands:
        run_command(cmd)
    
    print("\n" + "=" * 60)
    print("🎉 Настройка завершена!")
    print("\nСледующие шаги:")
    print("1. Активируйте виртуальное окружение:")
    if sys.platform == "win32":
        print("   .venv\\Scripts\\activate")
    else:
        print("   source .venv/bin/activate")
    print("2. Запустите игру:")
    print("   python src/cell_genesis/main.py")
    print("3. Запустите тесты:")
    print("   python scripts/run_tests.py")
    print("=" * 60)

if __name__ == "__main__":
    main()
