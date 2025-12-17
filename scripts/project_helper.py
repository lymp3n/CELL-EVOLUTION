#!/usr/bin/env python3
"""
CELL-EVOLUTION Project Helper
Упрощенное создание GitHub Issues через командную строку.
"""

import sys
import subprocess
import json
import argparse
from typing import Optional, Dict, List

class ProjectHelper:
    def __init__(self):
        self.templates = {
            "bug": {
                "name": "🐛 Сообщить об ошибке",
                "labels": ["type: bug", "status: backlog"],
                "template": "bug_report.yml"
            },
            "design": {
                "name": "🎨 Задача для дизайнера",
                "labels": ["type: design", "status: backlog"],
                "template": "designer_task.yml"
            },
            "dev": {
                "name": "👨‍💻 Задача для разработчика",
                "labels": ["type: development", "status: backlog"],
                "template": "developer_task.yml"
            },
            "manager": {
                "name": "📋 Задача менеджера",
                "labels": ["type: management", "status: backlog"],
                "template": "manager_task.yml"
            },
            "feature": {
                "name": "✨ Предложить новую фичу",
                "labels": ["type: enhancement", "status: backlog"],
                "template": "feature_proposal.yml"
            }
        }
    
    def run_gh_command(self, args: List[str], capture_output: bool = True) -> tuple:
        """Выполняет команду GitHub CLI"""
        try:
            result = subprocess.run(
                ["gh"] + args,
                capture_output=capture_output,
                text=True,
                encoding='utf-8'
            )
            return result.returncode == 0, result.stdout.strip()
        except FileNotFoundError:
            return False, "GitHub CLI не установлен. Установите: https://cli.github.com/"
        except Exception as e:
            return False, str(e)
    
    def check_auth(self) -> bool:
        """Проверяет аутентификацию"""
        success, _ = self.run_gh_command(["auth", "status"])
        return success
    
    def list_templates(self):
        """Показывает доступные шаблоны"""
        print("\n📋 Доступные шаблоны задач:")
        for key, template in self.templates.items():
            print(f"  {key:10} - {template['name']}")
        print()
    
    def create_issue(self, template_type: str, title: str, **kwargs):
        """Создает issue с выбранным шаблоном"""
        if template_type not in self.templates:
            print(f"❌ Неизвестный тип шаблона: {template_type}")
            self.list_templates()
            return False
        
        template = self.templates[template_type]
        
        print(f"\n🎯 Создаю задачу: {template['name']}")
        print(f"   Заголовок: {title}")
        
        # Собираем команду
        cmd = [
            "issue", "create",
            "--title", title,
            "--template", template["template"]
        ]
        
        # Добавляем лейблы
        for label in template["labels"]:
            cmd.extend(["--label", label])
        
        # Добавляем дополнительные лейблы
        if "labels" in kwargs:
            for label in kwargs["labels"]:
                cmd.extend(["--label", label])
        
        # Назначаем исполнителя
        if "assignee" in kwargs and kwargs["assignee"]:
            cmd.extend(["--assignee", kwargs["assignee"]])
        
        # Добавляем в проект
        if "project" in kwargs and kwargs["project"]:
            cmd.extend(["--project", kwargs["project"]])
        
        # Выполняем команду
        success, output = self.run_gh_command(cmd)
        
        if success:
            print(f"✅ Задача успешно создана!")
            if output:
                print(f"   {output}")
            return True
        else:
            print(f"❌ Ошибка при создании задачи: {output}")
            return False
    
    def quick_create(self, issue_type: str, title: str):
        """Быстрое создание задачи без дополнительных параметров"""
        # Автоматически определяем тип по началу заголовка
        if not issue_type:
            title_lower = title.lower()
            if title_lower.startswith("[bug]") or "баг" in title_lower or "ошибка" in title_lower:
                issue_type = "bug"
            elif title_lower.startswith("[design]") or "дизайн" in title_lower:
                issue_type = "design"
            elif title_lower.startswith("[manager]") or "управл" in title_lower:
                issue_type = "manager"
            elif title_lower.startswith("[feature]") or "фича" in title_lower:
                issue_type = "feature"
            else:
                issue_type = "dev"  # По умолчанию
        
        # Автоматически добавляем префикс, если его нет
        prefixes = {
            "bug": "[BUG] ",
            "design": "[DESIGN] ",
            "dev": "[DEV] ",
            "manager": "[MANAGER] ",
            "feature": "[FEATURE] "
        }
        
        if issue_type in prefixes and not title.startswith(prefixes[issue_type]):
            title = prefixes[issue_type] + title
        
        # Создаем задачу
        return self.create_issue(issue_type, title)
    
    def interactive_mode(self):
        """Интерактивный режим создания задачи"""
        print("\n" + "="*60)
        print("   🚀 СОЗДАНИЕ НОВОЙ ЗАДАЧИ CELL-EVOLUTION")
        print("="*60)
        
        # Проверяем аутентификацию
        if not self.check_auth():
            print("\n❌ GitHub CLI не аутентифицирован.")
            print("   Выполните: gh auth login")
            return
        
        # Выбираем тип задачи
        print("\n🎯 Выберите тип задачи:")
        for i, (key, template) in enumerate(self.templates.items(), 1):
            print(f"  {i}. {template['name']} ({key})")
        print(f"  {len(self.templates) + 1}. Отмена")
        
        try:
            choice = int(input(f"\n👉 Ваш выбор (1-{len(self.templates) + 1}): ").strip())
            if choice == len(self.templates) + 1:
                print("Отменено")
                return
            elif 1 <= choice <= len(self.templates):
                template_key = list(self.templates.keys())[choice - 1]
            else:
                print("❌ Неверный выбор")
                return
        except ValueError:
            print("❌ Введите число")
            return
        
        # Вводим заголовок
        template = self.templates[template_key]
        default_prefix = {
            "bug": "[BUG] ",
            "design": "[DESIGN] ",
            "dev": "[DEV] ",
            "manager": "[MANAGER] ",
            "feature": "[FEATURE] "
        }.get(template_key, "")
        
        title = input(f"\n📝 Заголовок задачи{'' if default_prefix else ' (можно с префиксом)'}: ").strip()
        if not title:
            print("❌ Заголовок не может быть пустым")
            return
        
        # Добавляем префикс, если его нет
        if default_prefix and not title.startswith(default_prefix):
            title = default_prefix + title
        
        # Дополнительные параметры
        print("\n⚙️  Дополнительные параметры (можно пропускать):")
        
        assignee = input("   Назначить на (логин GitHub): ").strip()
        if assignee:
            # Проверяем, существует ли пользователь
            success, _ = self.run_gh_command(["api", f"users/{assignee}"])
            if not success:
                print(f"   ⚠️  Пользователь '{assignee}' не найден на GitHub")
                assignee = None
        
        extra_labels = []
        print("\n   Дополнительные лейблы (через запятую, например: 'priority: high, component: core'):")
        labels_input = input("   Лейблы: ").strip()
        if labels_input:
            extra_labels = [l.strip() for l in labels_input.split(",") if l.strip()]
        
        # Создаем задачу
        self.create_issue(
            template_key,
            title,
            assignee=assignee,
            labels=extra_labels,
            project="CELL-EVOLUTION"
        )
    
    def list_my_issues(self):
        """Показывает задачи, назначенные на меня"""
        print("\n📋 Задачи, назначенные на вас:")
        
        success, output = self.run_gh_command([
            "issue", "list",
            "--assignee", "@me",
            "--state", "open",
            "--json", "number,title,url"
        ])
        
        if success and output:
            try:
                issues = json.loads(output)
                for issue in issues[:20]:  # Показываем первые 20
                    print(f"  #{issue['number']}: {issue['title'][:70]}...")
                
                if len(issues) > 20:
                    print(f"  ... и ещё {len(issues) - 20} задач")
            except json.JSONDecodeError:
                print("  ❌ Ошибка при получении задач")
        else:
            print("  🎉 Нет назначенных задач!")
    
    def search_issues(self, query: str):
        """Ищет задачи по запросу"""
        print(f"\n🔍 Поиск задач: '{query}'")
        
        success, output = self.run_gh_command([
            "issue", "list",
            "--search", query,
            "--state", "open",
            "--json", "number,title,author,labels"
        ])
        
        if success and output:
            try:
                issues = json.loads(output)
                if issues:
                    for issue in issues[:10]:
                        labels = [l['name'] for l in issue['labels'][:3]]
                        labels_str = ", ".join(labels) if labels else "нет лейблов"
                        print(f"  #{issue['number']}: {issue['title'][:60]}...")
                        print(f"     👤 {issue['author']['login']} | 🏷️  {labels_str}")
                        print()
                    
                    if len(issues) > 10:
                        print(f"  ... и ещё {len(issues) - 10} задач")
                else:
                    print("  🤷 Не найдено задач по запросу")
            except json.JSONDecodeError:
                print("  ❌ Ошибка при поиске задач")
        else:
            print("  🤷 Не найдено задач по запросу")

def main():
    """Основная функция"""
    parser = argparse.ArgumentParser(
        description="CELL-EVOLUTION Project Helper - создание и управление задачами",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Примеры использования:
  %(prog)s                            # Интерактивный режим
  %(prog)s --quick "[BUG] Игра падает при запуске"
  %(prog)s --type dev "Реализовать движение клетки"
  %(prog)s --list                     # Мои задачи
  %(prog)s --search "эволюция"        # Поиск задач
  %(prog)s --templates                # Список шаблонов
        """
    )
    
    parser.add_argument(
        "--quick", "-q",
        type=str,
        help="Быстрое создание задачи (автоопределение типа по заголовку)"
    )
    
    parser.add_argument(
        "--type", "-t",
        choices=["bug", "design", "dev", "manager", "feature"],
        help="Тип задачи для создания"
    )
    
    parser.add_argument(
        "--title", "-T",
        type=str,
        help="Заголовок задачи (используется с --type)"
    )
    
    parser.add_argument(
        "--assignee", "-a",
        type=str,
        help="Назначить задачу на пользователя (логин GitHub)"
    )
    
    parser.add_argument(
        "--labels", "-l",
        type=str,
        help="Дополнительные лейблы через запятую"
    )
    
    parser.add_argument(
        "--list", "-L",
        action="store_true",
        help="Показать задачи, назначенные на меня"
    )
    
    parser.add_argument(
        "--search", "-s",
        type=str,
        help="Поиск задач"
    )
    
    parser.add_argument(
        "--templates",
        action="store_true",
        help="Показать доступные шаблоны"
    )
    
    args = parser.parse_args()
    helper = ProjectHelper()
    
    # Проверяем аутентификацию для команд, требующих GitHub CLI
    needs_auth = any([args.quick, args.type, args.list, args.search, args.templates])
    
    if needs_auth and not helper.check_auth():
        print("❌ GitHub CLI не аутентифицирован.")
        print("💡 Выполните: gh auth login")
        sys.exit(1)
    
    # Обрабатываем аргументы
    if args.templates:
        helper.list_templates()
    
    elif args.list:
        helper.list_my_issues()
    
    elif args.search:
        helper.search_issues(args.search)
    
    elif args.quick:
        helper.quick_create(None, args.quick)
    
    elif args.type:
        if not args.title:
            print("❌ Необходимо указать заголовок с --title")
            sys.exit(1)
        
        labels = []
        if args.labels:
            labels = [l.strip() for l in args.labels.split(",") if l.strip()]
        
        helper.create_issue(
            args.type,
            args.title,
            assignee=args.assignee,
            labels=labels
        )
    
    else:
        # Интерактивный режим
        helper.interactive_mode()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 Выход...")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Ошибка: {e}")
        sys.exit(1)
