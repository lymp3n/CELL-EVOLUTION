#!/usr/bin/env python3
"""
CELL-EVOLUTION Development Environment Setup
Автоматическая настройка окружения для новых разработчиков.
"""

import os
import sys
import platform
import subprocess
import venv
import shutil
from pathlib import Path
from typing import Optional, Tuple

class DevSetup:
    def __init__(self):
        self.project_root = Path(__file__).parent.parent
        self.venv_path = self.project_root / ".venv"
        
        # Определяем команды в зависимости от ОС
        self.is_windows = platform.system() == "Windows"
        self.is_mac = platform.system() == "Darwin"
        self.is_linux = platform.system() == "Linux"
        
    def print_header(self, text: str):
        """Печатает заголовок"""
        print("\n" + "="*60)
        print(f"   {text}")
        print("="*60)
    
    def run_command(self, cmd: str, cwd: Optional[Path] = None) -> Tuple[bool, str]:
        """Выполняет команду"""
        print(f"  🚀 {cmd}")
        try:
            result = subprocess.run(
                cmd,
                shell=True,
                cwd=cwd or self.project_root,
                capture_output=True,
                text=True,
                encoding='utf-8'
            )
            if result.returncode != 0:
                return False, result.stderr
            return True, result.stdout
        except Exception as e:
            return False, str(e)
    
    def check_prerequisites(self) -> bool:
        """Проверяет системные требования"""
        self.print_header("ПРОВЕРКА СИСТЕМНЫХ ТРЕБОВАНИЙ")
        
        # Проверяем Python
        print("1. Проверяю версию Python...")
        success, output = self.run_command("python --version")
        if not success:
            print("  ❌ Python не найден!")
            print("  💡 Установите Python 3.10 или выше: https://www.python.org/downloads/")
            return False
        
        python_version = output.strip()
        print(f"  ✅ {python_version}")
        
        # Проверяем Git
        print("\n2. Проверяю Git...")
        success, output = self.run_command("git --version")
        if not success:
            print("  ❌ Git не найден!")
            print("  💡 Установите Git: https://git-scm.com/downloads")
            return False
        
        print(f"  ✅ {output.strip()}")
        
        # Проверяем GitHub CLI (рекомендуется)
        print("\n3. Проверяю GitHub CLI...")
        success, output = self.run_command("gh --version")
        if success:
            print(f"  ✅ {output.split('\n')[0]}")
        else:
            print("  ⚠️  GitHub CLI не установлен")
            print("  💡 Рекомендуется установить для удобной работы: https://cli.github.com/")
            print("     Но можно продолжить без него.")
        
        return True
    
    def create_virtual_env(self) -> bool:
        """Создает виртуальное окружение"""
        self.print_header("СОЗДАНИЕ ВИРТУАЛЬНОГО ОКРУЖЕНИЯ")
        
        if self.venv_path.exists():
            print(f"  ✅ Виртуальное окружение уже существует: {self.venv_path}")
            return True
        
        print(f"  Создаю виртуальное окружение в {self.venv_path}...")
        try:
            venv.create(self.venv_path, with_pip=True)
            print("  ✅ Виртуальное окружение создано")
            return True
        except Exception as e:
            print(f"  ❌ Ошибка: {e}")
            return False
    
    def get_python_path(self) -> Path:
        """Возвращает путь к Python в виртуальном окружении"""
        if self.is_windows:
            return self.venv_path / "Scripts" / "python.exe"
        else:
            return self.venv_path / "bin" / "python"
    
    def get_pip_path(self) -> Path:
        """Возвращает путь к pip в виртуальном окружении"""
        if self.is_windows:
            return self.venv_path / "Scripts" / "pip.exe"
        else:
            return self.venv_path / "bin" / "pip"
    
    def install_dependencies(self) -> bool:
        """Устанавливает зависимости"""
        self.print_header("УСТАНОВКА ЗАВИСИМОСТЕЙ")
        
        python_path = self.get_python_path()
        pip_path = self.get_pip_path()
        
        if not python_path.exists():
            print(f"  ❌ Python не найден по пути: {python_path}")
            return False
        
        # Обновляем pip
        print("1. Обновляю pip...")
        success, _ = self.run_command(f'"{pip_path}" install --upgrade pip')
        if not success:
            print("  ⚠️  Не удалось обновить pip, продолжаем...")
        
        # Устанавливаем базовые зависимости
        print("\n2. Устанавливаю базовые зависимости...")
        req_file = self.project_root / "requirements" / "base.txt"
        if req_file.exists():
            success, output = self.run_command(f'"{pip_path}" install -r "{req_file}"')
            if success:
                print("  ✅ Базовые зависимости установлены")
            else:
                print(f"  ❌ Ошибка: {output}")
                return False
        else:
            print(f"  ⚠️  Файл {req_file} не найден")
        
        # Устанавливаем зависимости для разработки
        print("\n3. Устанавливаю зависимости для разработки...")
        req_file = self.project_root / "requirements" / "dev.txt"
        if req_file.exists():
            success, output = self.run_command(f'"{pip_path}" install -r "{req_file}"')
            if success:
                print("  ✅ Зависимости для разработки установлены")
            else:
                print(f"  ❌ Ошибка: {output}")
                return False
        else:
            print(f"  ⚠️  Файл {req_file} не найден")
        
        return True
    
    def setup_pre_commit(self) -> bool:
        """Настраивает pre-commit хуки"""
        self.print_header("НАСТРОЙКА PRE-COMMIT ХУКОВ")
        
        python_path = self.get_python_path()
        
        print("1. Устанавливаю pre-commit...")
        success, output = self.run_command(f'"{python_path}" -m pip install pre-commit')
        if not success:
            print(f"  ⚠️  Не удалось установить pre-commit: {output}")
            return False
        
        print("2. Устанавливаю хуки...")
        success, output = self.run_command(f'"{python_path}" -m pre_commit install')
        if success:
            print("  ✅ Pre-commit хуки установлены")
            
            # Также устанавливаем хуки для коммита-сообщений
            success, _ = self.run_command(f'"{python_path}" -m pre_commit install --hook-type commit-msg')
            if success:
                print("  ✅ Хуки для commit-msg установлены")
        else:
            print(f"  ⚠️  Не удалось установить pre-commit хуки: {output}")
        
        return True
    
    def setup_git_lfs(self) -> bool:
        """Настраивает Git LFS для ассетов"""
        self.print_header("НАСТРОЙКА GIT LFS")
        
        print("1. Проверяю Git LFS...")
        success, output = self.run_command("git lfs version")
        if not success:
            print("  ⚠️  Git LFS не установлен")
            print("  💡 Установите Git LFS: https://git-lfs.github.com/")
            return False
        
        print(f"  ✅ {output.strip()}")
        
        print("\n2. Инициализирую Git LFS в проекте...")
        success, output = self.run_command("git lfs install")
        if not success:
            print(f"  ⚠️  Не удалось инициализировать Git LFS: {output}")
            return False
        
        print("3. Настраиваю отслеживание файлов...")
        assets_patterns = [
            '*.png', '*.jpg', '*.jpeg', '*.gif', '*.psd', '*.ai',
            '*.wav', '*.mp3', '*.ogg', '*.ttf', '*.otf', '*.blend'
        ]
        
        for pattern in assets_patterns:
            self.run_command(f'git lfs track "assets/**/{pattern}"')
        
        print("  ✅ Git LFS настроен для ассетов")
        return True
    
    def create_config_files(self) -> bool:
        """Создает конфигурационные файлы"""
        self.print_header("СОЗДАНИЕ КОНФИГУРАЦИОННЫХ ФАЙЛОВ")
        
        configs = {
            "config.example.yaml": """# Конфигурация CELL-EVOLUTION
game:
  window:
    width: 1200
    height: 800
    title: "Cell Evolution"
    fps: 60
  
  world:
    size: 1000
    food_count: 200
    npc_count: 5
  
  cell:
    start_energy: 100
    metabolism_rate: 0.1
    movement_cost: 0.05

graphics:
  show_fps: true
  show_debug: false
  particle_effects: true

sound:
  enabled: true
  volume: 0.7
""",
            
            ".env.example": """# Environment variables for CELL-EVOLUTION
DEBUG=true
LOG_LEVEL=INFO
SAVE_PATH=./saves/

# GitHub API (for automation)
# GITHUB_TOKEN=your_token_here
# GITHUB_USER=your_username
"""
        }
        
        for filename, content in configs.items():
            filepath = self.project_root / filename
            if not filepath.exists():
                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write(content)
                print(f"  ✅ Создан {filename}")
            else:
                print(f"  ⚠️  {filename} уже существует, пропускаю")
        
        # Создаем папки, если их нет
        folders = [
            "saves",
            "logs",
            "exports",
            "assets/sprites",
            "assets/sounds",
            "assets/fonts"
        ]
        
        for folder in folders:
            folder_path = self.project_root / folder
            folder_path.mkdir(parents=True, exist_ok=True)
        
        return True
    
    def setup_github_cli(self) -> bool:
        """Настраивает GitHub CLI"""
        self.print_header("НАСТРОЙКА GITHUB CLI")
        
        print("1. Проверяю аутентификацию...")
        success, output = self.run_command("gh auth status")
        if success:
            print("  ✅ GitHub CLI уже аутентифицирован")
            return True
        
        print("  ⚠️  GitHub CLI не аутентифицирован")
        print("\n2. Для полной функциональности выполните:")
        print("   gh auth login")
        print("\n   Выберите:")
        print("   - GitHub.com")
        print("   - HTTPS")
        print("   - Login with a web browser")
        print("\n   Или используйте токен:")
        print("   - Создайте токен в GitHub Settings > Developer settings")
        print("   - Выберите scopes: repo, workflow, project")
        print("   - Выполните: gh auth login --with-token < token.txt")
        
        auto_auth = input("\n🎯 Попробовать настроить автоматически? (y/N): ").strip().lower()
        if auto_auth == 'y':
            print("\n  Открываю браузер для аутентификации...")
            self.run_command("gh auth login --web")
        
        return True
    
    def run_sanity_check(self) -> bool:
        """Запускает проверку установки"""
        self.print_header("ПРОВЕРКА УСТАНОВКИ")
        
        python_path = self.get_python_path()
        tests_passed = 0
        total_tests = 5
        
        print("1. Проверяю Python...")
        success, output = self.run_command(f'"{python_path}" --version')
        if success:
            print(f"  ✅ {output.strip()}")
            tests_passed += 1
        else:
            print("  ❌ Ошибка")
        
        print("\n2. Проверяю установку PyGame...")
        success, output = self.run_command(f'"{python_path}" -c "import pygame; print(f\"Pygame: {pygame.version.ver}\")"')
        if success:
            print(f"  ✅ {output.strip()}")
            tests_passed += 1
        else:
            print("  ❌ PyGame не установлен")
        
        print("\n3. Проверяю установку NumPy...")
        success, output = self.run_command(f'"{python_path}" -c "import numpy; print(f\"NumPy: {numpy.__version__}\")"')
        if success:
            print(f"  ✅ {output.strip()}")
            tests_passed += 1
        else:
            print("  ❌ NumPy не установлен")
        
        print("\n4. Проверяю запуск тестов...")
        test_script = self.project_root / "scripts" / "run_tests.py"
        if test_script.exists():
            success, output = self.run_command(f'"{python_path}" "{test_script}" --help')
            if success:
                print("  ✅ Тестовый скрипт работает")
                tests_passed += 1
            else:
                print("  ❌ Тестовый скрипт не работает")
        else:
            print("  ⚠️  Тестовый скрипт не найден")
        
        print("\n5. Проверяю структуру проекта...")
        required_dirs = ["src", "assets", "requirements"]
        missing_dirs = []
        for dir_name in required_dirs:
            if not (self.project_root / dir_name).exists():
                missing_dirs.append(dir_name)
        
        if not missing_dirs:
            print("  ✅ Структура проекта в порядке")
            tests_passed += 1
        else:
            print(f"  ❌ Отсутствуют папки: {', '.join(missing_dirs)}")
        
        print(f"\n📊 ИТОГ: {tests_passed}/{total_tests} проверок пройдено")
        return tests_passed >= 3
    
    def print_success_message(self):
        """Печатает сообщение об успешной настройке"""
        self.print_header("🎉 НАСТРОЙКА ЗАВЕРШЕНА!")
        
        python_path = self.get_python_path()
        
        print("\n✅ Ваше окружение готово к работе над CELL-EVOLUTION!")
        print("\n📋 Следующие шаги:")
        print(f"\n1. АКТИВИРУЙТЕ ВИРТУАЛЬНОЕ ОКРУЖЕНИЕ:")
        if self.is_windows:
            print(f"   {self.venv_path}\\Scripts\\activate")
        else:
            print(f"   source {self.venv_path}/bin/activate")
        
        print("\n2. ПРОВЕРЬТЕ УСТАНОВКУ:")
        print(f"   python scripts/run_tests.py --quick")
        
        print("\n3. ЗАПУСТИТЕ ПОМОЩНИКА РАЗРАБОТЧИКА:")
        print(f"   python scripts/dev_helper.py start")
        
        print("\n4. ЕСЛИ НУЖНО, НАСТРОЙТЕ GITHUB CLI:")
        print(f"   gh auth login")
        
        print("\n5. СКОПИРУЙТЕ КОНФИГУРАЦИОННЫЕ ФАЙЛЫ:")
        print(f"   cp config.example.yaml config.yaml")
        print(f"   cp .env.example .env")
        
        print("\n" + "="*60)
        print("   🚀 УДАЧНОЙ РАЗРАБОТКИ!")
        print("="*60)
    
    def run(self) -> bool:
        """Запускает полную настройку"""
        print("\n" + "="*60)
        print("   🛠️  НАСТРОЙКА ОКРУЖЕНИЯ CELL-EVOLUTION")
        print("="*60)
        
        # Проверяем системные требования
        if not self.check_prerequisites():
            return False
        
        # Создаем виртуальное окружение
        if not self.create_virtual_env():
            return False
        
        # Устанавливаем зависимости
        if not self.install_dependencies():
            return False
        
        # Настраиваем pre-commit
        self.setup_pre_commit()
        
        # Настраиваем Git LFS
        self.setup_git_lfs()
        
        # Создаем конфигурационные файлы
        self.create_config_files()
        
        # Настраиваем GitHub CLI
        self.setup_github_cli()
        
        # Запускаем проверку
        self.run_sanity_check()
        
        # Печатаем успешное сообщение
        self.print_success_message()
        
        return True

def main():
    """Основная функция"""
    try:
        setup = DevSetup()
        success = setup.run()
        
        if not success:
            print("\n❌ Настройка не завершена успешно.")
            print("💡 Проверьте сообщения об ошибках выше.")
            sys.exit(1)
            
    except KeyboardInterrupt:
        print("\n\n👋 Настройка прервана пользователем.")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Неожиданная ошибка: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
