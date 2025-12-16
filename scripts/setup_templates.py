#!/usr/bin/env python3
"""
CELL-EVOLUTION Issue Templates Validator
Проверяет и настраивает шаблоны GitHub Issues.
"""

import os
import sys
import yaml
import json
import subprocess
from pathlib import Path
from typing import Dict, List, Tuple, Optional

class TemplateValidator:
    def __init__(self):
        self.project_root = Path(__file__).parent.parent
        self.template_dir = self.project_root / ".github" / "ISSUE_TEMPLATE"
        
        # Обязательные файлы
        self.required_files = [
            "config.yml",
            "bug_report.yml",
            "designer_task.yml",
            "developer_task.yml",
            "manager_task.yml",
            "feature_proposal.yml"
        ]
        
        # Обязательные поля в шаблонах
        self.required_fields = ["name", "description", "title", "labels"]
        
        # Разрешенные типы полей в body
        self.allowed_body_types = [
            "markdown", "textarea", "input", "dropdown",
            "checkboxes", "text"
        ]
    
    def print_header(self, text: str):
        """Печатает заголовок"""
        print("\n" + "="*60)
        print(f"   {text}")
        print("="*60)
    
    def check_directory_structure(self) -> Tuple[bool, List[str]]:
        """Проверяет структуру директории"""
        missing_files = []
        
        if not self.template_dir.exists():
            return False, ["Папка .github/ISSUE_TEMPLATE не существует"]
        
        for filename in self.required_files:
            if not (self.template_dir / filename).exists():
                missing_files.append(filename)
        
        return len(missing_files) == 0, missing_files
    
    def validate_yaml_file(self, filepath: Path) -> Tuple[bool, str]:
        """Проверяет YAML файл на валидность"""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                content = yaml.safe_load(f)
            
            if content is None:
                return False, "Файл пустой или содержит только комментарии"
            
            return True, "OK"
        except yaml.YAMLError as e:
            return False, f"Ошибка YAML: {e}"
        except Exception as e:
            return False, f"Ошибка чтения: {e}"
    
    def validate_template_structure(self, filepath: Path) -> Tuple[bool, str]:
        """Проверяет структуру шаблона задачи"""
        if filepath.name == "config.yml":
            return True, "Config file"
        
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                template = yaml.safe_load(f)
            
            # Проверяем обязательные поля
            for field in self.required_fields:
                if field not in template:
                    return False, f"Отсутствует обязательное поле: {field}"
            
            # Проверяем name и description
            if not isinstance(template.get("name"), str):
                return False, "Поле 'name' должно быть строкой"
            
            if not isinstance(template.get("description"), str):
                return False, "Поле 'description' должно быть строкой"
            
            # Проверяем labels
            labels = template.get("labels", [])
            if not isinstance(labels, list):
                return False, "Поле 'labels' должно быть списком"
            
            # Проверяем assignees
            assignees = template.get("assignees", [])
            if assignees is not None and not isinstance(assignees, list):
                return False, "Поле 'assignees' должно быть списком или null"
            
            # Проверяем body
            if "body" in template:
                body = template["body"]
                if not isinstance(body, list):
                    return False, "Поле 'body' должно быть списком"
                
                for i, field in enumerate(body):
                    if not isinstance(field, dict):
                        return False, f"Элемент body[{i}] должен быть словарем"
                    
                    if "type" not in field:
                        return False, f"Элемент body[{i}] не имеет типа"
                    
                    if field["type"] not in self.allowed_body_types:
                        return False, f"Неизвестный тип поля: {field['type']}"
            
            return True, "OK"
            
        except Exception as e:
            return False, f"Ошибка валидации: {e}"
    
    def validate_config_file(self, filepath: Path) -> Tuple[bool, str]:
        """Проверяет config.yml"""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                config = yaml.safe_load(f)
            
            # Проверяем обязательные поля config.yml
            if config is None:
                return False, "Config файл пустой"
            
            if "blank_issues_enabled" not in config:
                return False, "Отсутствует blank_issues_enabled"
            
            if not isinstance(config["blank_issues_enabled"], bool):
                return False, "blank_issues_enabled должен быть boolean"
            
            # Проверяем contact_links
            if "contact_links" in config:
                contact_links = config["contact_links"]
                if not isinstance(contact_links, list):
                    return False, "contact_links должен быть списком"
                
                for i, link in enumerate(contact_links):
                    if not isinstance(link, dict):
                        return False, f"contact_links[{i}] должен быть словарем"
                    
                    required = ["name", "url", "about"]
                    for field in required:
                        if field not in link:
                            return False, f"contact_links[{i}] отсутствует поле: {field}"
            
            return True, "OK"
            
        except Exception as e:
            return False, f"Ошибка валидации config: {e}"
    
    def check_github_api(self) -> bool:
        """Проверяет доступность GitHub API"""
        try:
            result = subprocess.run(
                ["gh", "api", "repos/lymp3n/CELL-EVOLUTION"],
                capture_output=True,
                text=True
            )
            return result.returncode == 0
        except:
            return False
    
    def create_test_issue(self, template_name: str) -> Tuple[bool, str]:
        """Создает тестовую задачу"""
        try:
            # Генерируем уникальное название
            import time
            timestamp = int(time.time())
            title = f"[TEST] Validation Test {timestamp}"
            
            cmd = [
                "gh", "issue", "create",
                "--title", title,
                "--body", f"Тестовая задача для проверки шаблона {template_name}",
                "--template", template_name,
                "--label", "test"
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                # Получаем номер созданной задачи
                issue_url = result.stdout.strip()
                issue_num = issue_url.split("/")[-1]
                
                # Сразу закрываем тестовую задачу
                subprocess.run([
                    "gh", "issue", "close", issue_num,
                    "--comment", "Тестовая задача, автоматически закрыта"
                ], capture_output=True)
                
                return True, f"Создана и закрыта тестовая задача #{issue_num}"
            else:
                return False, f"Ошибка: {result.stderr}"
                
        except Exception as e:
            return False, f"Исключение: {e}"
    
    def fix_common_issues(self, filepath: Path) -> Tuple[bool, str]:
        """Исправляет распространенные проблемы в шаблонах"""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
            
            fixes_made = []
            
            # Исправляем assignees: "" на assignees: []
            if 'assignees: ""' in content:
                content = content.replace('assignees: ""', 'assignees: []')
                fixes_made.append("Исправлены assignees")
            
            # Исправляем неправильные отступы YAML
            lines = content.split('\n')
            fixed_lines = []
            in_body = False
            body_indent = 0
            
            for line in lines:
                # Обнаруживаем начало body
                if line.strip() == 'body:':
                    in_body = True
                    fixed_lines.append(line)
                    continue
                
                if in_body and line.strip().startswith('- type:'):
                    # Это поле в body
                    if '  ' not in line[:2]:  # Проверяем отступ
                        line = '  ' + line
                    fixed_lines.append(line)
                else:
                    fixed_lines.append(line)
            
            content = '\n'.join(fixed_lines)
            
            # Сохраняем исправления
            if fixes_made:
                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write(content)
                return True, ", ".join(fixes_made)
            else:
                return False, "Не требуется исправлений"
                
        except Exception as e:
            return False, f"Ошибка при исправлении: {e}"
    
    def generate_template_report(self) -> Dict:
        """Генерирует отчет о всех шаблонах"""
        report = {
            "timestamp": str(datetime.now()),
            "templates": {},
            "summary": {
                "total": 0,
                "valid": 0,
                "invalid": 0
            }
        }
        
        for filepath in self.template_dir.glob("*.yml"):
            yaml_valid, yaml_msg = self.validate_yaml_file(filepath)
            
            if filepath.name == "config.yml":
                struct_valid, struct_msg = self.validate_config_file(filepath)
            else:
                struct_valid, struct_msg = self.validate_template_structure(filepath)
            
            report["templates"][filepath.name] = {
                "yaml_valid": yaml_valid,
                "yaml_message": yaml_msg,
                "structure_valid": struct_valid,
                "structure_message": struct_msg,
                "fully_valid": yaml_valid and struct_valid
            }
            
            report["summary"]["total"] += 1
            if yaml_valid and struct_valid:
                report["summary"]["valid"] += 1
            else:
                report["summary"]["invalid"] += 1
        
        return report
    
    def run_full_validation(self) -> bool:
        """Запускает полную проверку"""
        self.print_header("🔍 ПРОВЕРКА ШАБЛОНОВ GITHUB ISSUES")
        
        # 1. Проверяем структуру директории
        print("\n1. Проверяю структуру директории...")
        dir_ok, missing = self.check_directory_structure()
        
        if not dir_ok:
            print(f"  ❌ Отсутствуют файлы: {', '.join(missing)}")
            
            # Предлагаем создать недостающие файлы
            create_missing = input("\n  Создать недостающие файлы? (y/N): ").strip().lower()
            if create_missing == 'y':
                self.create_missing_templates(missing)
                # Повторная проверка
                dir_ok, missing = self.check_directory_structure()
        
        if dir_ok:
            print("  ✅ Все обязательные файлы на месте")
        
        # 2. Проверяем каждый файл
        print("\n2. Проверяю файлы шаблонов:")
        all_valid = True
        
        for filepath in self.template_dir.glob("*.yml"):
            print(f"\n  📄 {filepath.name}:")
            
            # Проверяем YAML
            yaml_valid, yaml_msg = self.validate_yaml_file(filepath)
            if yaml_valid:
                print(f"    ✅ Валидный YAML")
            else:
                print(f"    ❌ {yaml_msg}")
                all_valid = False
                
                # Предлагаем исправить
                if "assignees" in yaml_msg or "YAML" in yaml_msg:
                    fix = input(f"    Попробовать исправить автоматически? (y/N): ").strip().lower()
                    if fix == 'y':
                        fixed, fix_msg = self.fix_common_issues(filepath)
                        if fixed:
                            print(f"    🔧 {fix_msg}")
                            # Повторная проверка
                            yaml_valid, yaml_msg = self.validate_yaml_file(filepath)
                            if yaml_valid:
                                print(f"    ✅ Теперь валидный YAML")
                                all_valid = True
                        else:
                            print(f"    ❌ Не удалось исправить: {fix_msg}")
            
            # Проверяем структуру
            if yaml_valid:
                if filepath.name == "config.yml":
                    struct_valid, struct_msg = self.validate_config_file(filepath)
                else:
                    struct_valid, struct_msg = self.validate_template_structure(filepath)
                
                if struct_valid:
                    print(f"    ✅ Корректная структура")
                else:
                    print(f"    ❌ {struct_msg}")
                    all_valid = False
        
        # 3. Проверяем GitHub API доступность
        print("\n3. Проверяю доступность GitHub API...")
        if self.check_github_api():
            print("  ✅ GitHub API доступен")
            
            # 4. Тестируем создание задачи
            print("\n4. Тестирую создание задачи...")
            test_template = "bug_report.yml"
            success, message = self.create_test_issue(test_template)
            
            if success:
                print(f"  ✅ {message}")
                print(f"  🎉 Шаблоны работают корректно!")
            else:
                print(f"  ⚠️  {message}")
                print(f"  💡 Проверьте права доступа GitHub CLI")
        else:
            print("  ⚠️  GitHub API недоступен")
            print("  💡 Проверьте аутентификацию: gh auth login")
        
        # Генерируем отчет
        report = self.generate_template_report()
        
        print("\n" + "="*60)
        print(f"   📊 ОТЧЕТ: {report['summary']['valid']}/{report['summary']['total']} шаблонов валидны")
        print("="*60)
        
        if report["summary"]["invalid"] > 0:
            print("\n❌ Проблемные шаблоны:")
            for filename, data in report["templates"].items():
                if not data["fully_valid"]:
                    print(f"  {filename}:")
                    if not data["yaml_valid"]:
                        print(f"    - {data['yaml_message']}")
                    if not data["structure_valid"]:
                        print(f"    - {data['structure_message']}")
        
        return all_valid and report["summary"]["invalid"] == 0
    
    def create_missing_templates(self, missing_files: List[str]):
        """Создает недостающие файлы шаблонов"""
        templates_content = {
            "config.yml": """blank_issues_enabled: false
contact_links:
  - name: 📖 Документация по шаблонам
    url: https://github.com/lymp3n/CELL-EVOLUTION/blob/main/.github/ISSUE_TEMPLATE/README_TEMPLATES.md
    about: Руководство по использованию шаблонов задач
""",
            
            "bug_report.yml": """name: "🐛 Сообщить об ошибке"
description: "Сообщить о баге или неожиданном поведении в игре"
title: "[BUG] "
labels: ["type: bug", "status: backlog"]
assignees: []
body:
  - type: markdown
    attributes:
      value: "## 🐛 Описание бага"
  
  - type: textarea
    id: description
    attributes:
      label: "Что произошло?"
      description: "Подробное описание проблемы"
    validations:
      required: true
""",
            
            "developer_task.yml": """name: "👨‍💻 Задача для разработчика"
description: "Техническая задача для разработчиков"
title: "[DEV] "
labels: ["type: development", "status: backlog"]
assignees: []
body:
  - type: markdown
    attributes:
      value: "## 🎯 Техническое задание"
  
  - type: textarea
    id: description
    attributes:
      label: "Описание задачи"
      description: "Что нужно сделать?"
    validations:
      required: true
""",
            
            "designer_task.yml": """name: "🎨 Задача для дизайнера"
description: "Задача для дизайнеров (UI, спрайты, анимации)"
title: "[DESIGN] "
labels: ["type: design", "status: backlog"]
assignees: []
body:
  - type: markdown
    attributes:
      value: "## 🎯 Дизайн-бриф"
  
  - type: textarea
    id: description
    attributes:
      label: "Описание задачи"
      description: "Что нужно создать?"
    validations:
      required: true
""",
            
            "manager_task.yml": """name: "📋 Задача менеджера"
description: "Организационная задача для менеджеров"
title: "[MANAGER] "
labels: ["type: management", "status: backlog"]
assignees: []
body:
  - type: markdown
    attributes:
      value: "## 📊 Организационная задача"
  
  - type: textarea
    id: description
    attributes:
      label: "Описание задачи"
      description: "Что нужно организовать или скоординировать?"
    validations:
      required: true
""",
            
            "feature_proposal.yml": """name: "✨ Предложить новую фичу"
description: "Предложение новой функциональности для игры"
title: "[FEATURE] "
labels: ["type: enhancement", "status: backlog"]
assignees: []
body:
  - type: markdown
    attributes:
      value: "## 💡 Идея новой фичи"
  
  - type: textarea
    id: description
    attributes:
      label: "Описание идеи"
      description: "Что вы хотите предложить?"
    validations:
      required: true
"""
        }
        
        self.template_dir.mkdir(parents=True, exist_ok=True)
        
        for filename in missing_files:
            if filename in templates_content:
                filepath = self.template_dir / filename
                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write(templates_content[filename])
                print(f"  ✅ Создан {filename}")
    
    def create_custom_template(self):
        """Создает кастомный шаблон"""
        print("\n🎨 Создание кастомного шаблона")
        
        name = input("Название шаблона (с эмодзи): ").strip()
        if not name:
            print("❌ Название обязательно")
            return
        
        description = input("Описание: ").strip()
        prefix = input("Префикс заголовка (например, [CUSTOM]): ").strip()
        
        filename = input("Имя файла (без .yml): ").strip()
        if not filename:
            filename = name.lower().replace(' ', '_').replace(':', '')
        filename = f"{filename}.yml"
        
        # Создаем простой шаблон
        template = f"""name: "{name}"
description: "{description}"
title: "{prefix} "
labels: ["type: custom", "status: backlog"]
assignees: []
body:
  - type: markdown
    attributes:
      value: "## 🎯 Задача"
  
  - type: textarea
    id: description
    attributes:
      label: "Описание"
      description: "Подробное описание задачи"
    validations:
      required: true
"""
        
        filepath = self.template_dir / filename
        if filepath.exists():
            overwrite = input(f"Файл {filename} уже существует. Перезаписать? (y/N): ").strip().lower()
            if overwrite != 'y':
                print("Отменено")
                return
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(template)
        
        print(f"✅ Шаблон создан: {filepath}")
    
    def export_templates(self, output_file: str):
        """Экспортирует шаблоны в JSON файл"""
        templates = {}
        
        for filepath in self.template_dir.glob("*.yml"):
            with open(filepath, 'r', encoding='utf-8') as f:
                try:
                    content = yaml.safe_load(f)
                    templates[filepath.name] = content
                except:
                    templates[filepath.name] = {"error": "Invalid YAML"}
        
        export_path = Path(output_file)
        with open(export_path, 'w', encoding='utf-8') as f:
            json.dump(templates, f, indent=2, ensure_ascii=False)
        
        print(f"✅ Шаблоны экспортированы в {export_path}")

def main():
    """Основная функция"""
    from datetime import datetime
    
    parser = argparse.ArgumentParser(
        description="CELL-EVOLUTION Issue Templates Validator",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Примеры использования:
  %(prog𝑠) check                    # Полная проверка
  %(prog𝑠) fix                      # Исправить common issues
  %(prog𝑠) create-custom            # Создать кастомный шаблон
  %(prog𝑠) export templates.json    # Экспортировать шаблоны
  %(prog𝑠) report                   # Показать отчет
        """
    )
    
    parser.add_argument(
        "command",
        nargs="?",
        default="check",
        choices=["check", "fix", "create-custom", "export", "report", "test"],
        help="Команда для выполнения"
    )
    
    parser.add_argument(
        "output",
        nargs="?",
        help="Выходной файл для экспорта"
    )
    
    args = parser.parse_args()
    validator = TemplateValidator()
    
    try:
        if args.command == "check":
            success = validator.run_full_validation()
            sys.exit(0 if success else 1)
            
        elif args.command == "fix":
            print("\n🔧 Исправление common issues...")
            for filepath in validator.template_dir.glob("*.yml"):
                print(f"\n  {filepath.name}:")
                fixed, message = validator.fix_common_issues(filepath)
                if fixed:
                    print(f"    ✅ {message}")
                else:
                    print(f"    ℹ️  {message}")
            
        elif args.command == "create-custom":
            validator.create_custom_template()
            
        elif args.command == "export":
            if not args.output:
                print("❌ Укажите имя файла для экспорта")
                sys.exit(1)
            validator.export_templates(args.output)
            
        elif args.command == "report":
            report = validator.generate_template_report()
            print(json.dumps(report, indent=2, ensure_ascii=False))
            
        elif args.command == "test":
            print("\n🧪 Тестирую создание задачи...")
            success, message = validator.create_test_issue("bug_report.yml")
            if success:
                print(f"✅ {message}")
            else:
                print(f"❌ {message}")
                sys.exit(1)
                
    except KeyboardInterrupt:
        print("\n\n👋 Выход...")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Ошибка: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
