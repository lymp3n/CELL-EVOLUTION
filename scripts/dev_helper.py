#!/usr/bin/env python3
"""
Умный помощник для разработчиков Cell Genesis
"""
import os
import sys
import json
import subprocess
import argparse
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional

class DevHelper:
    def __init__(self):
        self.project_root = Path(__file__).parent.parent
        self.config_path = self.project_root / ".devhelper.json"
        self.config = self.load_config()
        
    def load_config(self) -> Dict:
        """Загрузить конфигурацию"""
        if self.config_path.exists():
            with open(self.config_path, 'r') as f:
                return json.load(f)
        
        default_config = {
            "last_branch": "develop",
            "common_commands": {
                "test": "pytest src/tests/ -v",
                "lint": "black --check src/ && flake8 src/",
                "type": "mypy src/ --ignore-missing-imports",
                "run": "python src/cell_genesis/main.py",
                "install": "pip install -r requirements/dev.txt"
            },
            "team_members": {
                "core": ["lead-dev-1", "core-dev-1", "core-dev-2"],
                "evolution": ["lead-dev-2", "evolution-dev-1", "evolution-dev-2"],
                "graphics": ["ui-dev-1", "ui-dev-2"],
                "ai": ["ai-dev-1", "ai-dev-2", "ai-dev-3"],
                "design": ["designer-1", "designer-2", "designer-3", "designer-4"]
            }
        }
        
        with open(self.config_path, 'w') as f:
            json.dump(default_config, f, indent=2)
        
        return default_config
    
    def run_command(self, cmd: str, cwd: Optional[Path] = None) -> bool:
        """Выполнить команду"""
        print(f"🚀 {cmd}")
        result = subprocess.run(cmd, shell=True, cwd=cwd or self.project_root)
        return result.returncode == 0
    
    def create_branch(self, issue_number: str, issue_title: str):
        """Создать ветку для issue"""
        # Очищаем название issue для имени ветки
        branch_name = f"issue-{issue_number}-{issue_title.lower()}"
        branch_name = ''.join(c if c.isalnum() else '-' for c in branch_name)[:50]
        
        print(f"🌿 Создаю ветку: {branch_name}")
        
        # Переключаемся на develop
        self.run_command("git checkout develop")
        self.run_command("git pull origin develop")
        
        # Создаем новую ветку
        self.run_command(f"git checkout -b {branch_name}")
        
        # Сохраняем в конфиг
        self.config["last_branch"] = branch_name
        with open(self.config_path, 'w') as f:
            json.dump(self.config, f, indent=2)
        
        print(f"✅ Ветка создана. Не забудьте:")
        print(f"   1. Работать в этой ветке")
        print(f"   2. Делать коммиты с ссылкой на issue")
        print(f"   3. Создать PR в develop когда будет готово")
    
    def start_work(self):
        """Начать рабочий день"""
        print("👋 Доброе утро, разработчик!")
        print(f"📅 {datetime.now().strftime('%d.%m.%Y %H:%M')}")
        
        # Проверяем статус git
        self.run_command("git status")
        
        # Показываем назначенные задачи
        print("\n📋 Ваши задачи на сегодня:")
        self.run_command('gh issue list --assignee "@me" --state open')
        
        # Спрашиваем, что будем делать
        print("\n🎯 Что планируете делать сегодня?")
        print("1. Взять новую задачу из Backlog")
        print("2. Продолжить работу над текущей задачей")
        print("3. Сделать code review")
        print("4. Протестировать готовые фичи")
        
        choice = input("\nВаш выбор (1-4): ").strip()
        
        if choice == "1":
            self.pick_new_task()
        elif choice == "2":
            self.continue_task()
        elif choice == "3":
            self.do_review()
        elif choice == "4":
            self.test_features()
    
    def pick_new_task(self):
        """Выбрать новую задачу"""
        print("\n📋 Доступные задачи:")
        self.run_command('gh issue list --label "status: ready" --state open')
        
        issue_num = input("\nВведите номер issue (только цифры): ").strip()
        
        if issue_num:
            # Получаем информацию о issue
            result = subprocess.run(
                f'gh issue view {issue_num} --json title,body',
                shell=True,
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0:
                issue_data = json.loads(result.stdout)
                print(f"\n🎯 Задача: {issue_data['title']}")
                print(f"\n📝 Описание:\n{issue_data['body'][:500]}...")
                
                confirm = input("\nВзять эту задачу? (y/n): ").lower()
                if confirm == 'y':
                    # Назначаем на себя
                    self.run_command(f'gh issue edit {issue_num} --add-assignee "@me"')
                    # Меняем статус
                    self.run_command(f'gh issue edit {issue_num} --remove-label "status: ready"')
                    self.run_command(f'gh issue edit {issue_num} --add-label "status: in progress"')
                    # Создаем ветку
                    self.create_branch(issue_num, issue_data['title'])
            else:
                print("❌ Не удалось получить информацию о задаче")
    
    def continue_task(self):
        """Продолжить работу над текущей задачей"""
        # Показываем текущую ветку
        result = subprocess.run(
            "git branch --show-current",
            shell=True,
            capture_output=True,
            text=True
        )
        
        current_branch = result.stdout.strip()
        print(f"🌿 Текущая ветка: {current_branch}")
        
        # Ищем номер issue в названии ветки
        import re
        match = re.search(r'issue-(\d+)', current_branch)
        
        if match:
            issue_num = match.group(1)
            print(f"📌 Связанная задача: #{issue_num}")
            
            # Открываем задачу в браузере
            open_browser = input("Открыть задачу в браузере? (y/n): ").lower()
            if open_browser == 'y':
                self.run_command(f'gh issue view {issue_num} --web')
        
        # Спрашиваем, что будем делать
        print("\n🛠️ Выберите действие:")
        print("1. Запустить тесты")
        print("2. Проверить стиль кода")
        print("3. Запустить игру")
        print("4. Сделать коммит")
        print("5. Создать PR")
        
        choice = input("\nВаш выбор (1-5): ").strip()
        
        if choice == "1":
            self.run_command(self.config["common_commands"]["test"])
        elif choice == "2":
            self.run_command(self.config["common_commands"]["lint"])
        elif choice == "3":
            self.run_command(self.config["common_commands"]["run"])
        elif choice == "4":
            self.make_commit()
        elif choice == "5":
            self.create_pr()
    
    def make_commit(self):
        """Сделать коммит"""
        # Показываем изменения
        self.run_command("git status")
        self.run_command("git diff --stat")
        
        files = input("\nКакие файлы добавить в коммит? (через пробел, * для всех): ").strip()
        
        if files:
            self.run_command(f"git add {files}")
            
            # Получаем номер issue из ветки
            result = subprocess.run(
                "git branch --show-current",
                shell=True,
                capture_output=True,
                text=True
            )
            
            branch_name = result.stdout.strip()
            import re
            match = re.search(r'issue-(\d+)', branch_name)
            
            message = input("Сообщение коммита: ").strip()
            
            if match:
                issue_num = match.group(1)
                message = f"{message} (fixes #{issue_num})"
            
            self.run_command(f'git commit -m "{message}"')
            
            # Пушим изменения
            push = input("Запушить изменения? (y/n): ").lower()
            if push == 'y':
                self.run_command(f"git push origin {branch_name}")
    
    def create_pr(self):
        """Создать Pull Request"""
        # Получаем информацию о текущей ветке
        result = subprocess.run(
            "git branch --show-current",
            shell=True,
            capture_output=True,
            text=True
        )
        
        branch_name = result.stdout.strip()
        
        # Ищем номер issue
        import re
        match = re.search(r'issue-(\d+)', branch_name)
        
        if not match:
            print("❌ Не могу найти номер issue в названии ветки")
            return
        
        issue_num = match.group(1)
        
        # Получаем заголовок issue
        result = subprocess.run(
            f'gh issue view {issue_num} --json title',
            shell=True,
            capture_output=True,
            text=True
        )
        
        if result.returncode != 0:
            print("❌ Не могу получить информацию о задаче")
            return
        
        issue_data = json.loads(result.stdout)
        issue_title = issue_data['title']
        
        # Создаем PR
        pr_title = f"Fix #{issue_num}: {issue_title}"
        pr_body = f"## Описание\nРешает issue #{issue_num}\n\n## Изменения\n- [ ] Код написан\n- [ ] Тесты проходят\n- [ ] Документация обновлена\n\n## Скриншоты\n<!-- Если нужно -->"
        
        print(f"\n📝 Создаю PR:")
        print(f"   Заголовок: {pr_title}")
        print(f"   Из ветки: {branch_name} -> develop")
        
        confirm = input("\nСоздать PR? (y/n): ").lower()
        
        if confirm == 'y':
            self.run_command(f'gh pr create --title "{pr_title}" --body "{pr_body}" --base develop --head {branch_name}')
            
            # Меняем статус issue
            self.run_command(f'gh issue edit {issue_num} --remove-label "status: in progress"')
            self.run_command(f'gh issue edit {issue_num} --add-label "status: in review"')
            
            print("✅ PR создан! Не забудьте:")
            print("   1. Добавить ревьюверов")
            print("   2. Проверить, что все тесты проходят")
            print("   3. Ждать аппрувов перед мержем")
    
    def do_review(self):
        """Сделать code review"""
        print("\n👀 Доступные PR для ревью:")
        self.run_command('gh pr list --state open --json number,title,author')
        
        pr_num = input("\nВведите номер PR для ревью (только цифры): ").strip()
        
        if pr_num:
            print(f"\nРевью PR #{pr_num}:")
            
            # Показываем изменения
            self.run_command(f'gh pr diff {pr_num}')
            
            # Открываем в браузере
            open_web = input("\nОткрыть в браузере для детального просмотра? (y/n): ").lower()
            if open_web == 'y':
                self.run_command(f'gh pr view {pr_num} --web')
            
            # Спрашиваем решение
            print("\n🎯 Ваше решение:")
            print("1. Одобрить (approve)")
            print("2. Запросить изменения (request changes)")
            print("3. Прокомментировать (comment)")
            
            choice = input("\nВаш выбор (1-3): ").strip()
            
            if choice == "1":
                self.run_command(f'gh pr review {pr_num} --approve')
                print("✅ PR одобрен!")
            elif choice == "2":
                comment = input("Комментарий с описанием необходимых изменений: ").strip()
                self.run_command(f'gh pr review {pr_num} --request-changes --body "{comment}"')
                print("🔄 Запрошены изменения")
            elif choice == "3":
                comment = input("Ваш комментарий: ").strip()
                self.run_command(f'gh pr review {pr_num} --comment --body "{comment}"')
                print("💬 Комментарий добавлен")
    
    def test_features(self):
        """Тестирование готовых фич"""
        print("\n🧪 Задачи, готовые к тестированию:")
        self.run_command('gh issue list --label "status: testing" --state open')
        
        issue_num = input("\nВведите номер задачи для тестирования: ").strip()
        
        if issue_num:
            # Получаем информацию
            result = subprocess.run(
                f'gh issue view {issue_num} --json title,body',
                shell=True,
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0:
                issue_data = json.loads(result.stdout)
                print(f"\n🎯 Тестируем: {issue_data['title']}")
                print(f"\n📋 Критерии приемки из задачи:")
                
                # Ищем критерии в описании
                import re
                criteria = re.findall(r'\[ \].*', issue_data['body'])
                for c in criteria[:10]:  # Показываем первые 10
                    print(f"  {c}")
                
                print("\n🔄 Шаги для тестирования:")
                print("1. Переключитесь на ветку develop")
                print("2. Обновите код: git pull origin develop")
                print("3. Запустите игру и проверьте фичу")
                print("4. Заполните чек-лист выше")
                
                input("\nНажмите Enter когда протестируете...")
                
                # Спрашиваем результат
                print("\n🎯 Результат тестирования:")
                print("1. Все работает, можно закрывать")
                print("2. Есть проблемы, нужно исправить")
                print("3. Нужны дополнительные проверки")
                
                choice = input("\nВаш выбор (1-3): ").strip()
                
                if choice == "1":
                    self.run_command(f'gh issue edit {issue_num} --remove-label "status: testing"')
                    self.run_command(f'gh issue edit {issue_num} --add-label "status: done"')
                    self.run_command(f'gh issue close {issue_num}')
                    print("✅ Задача закрыта!")
                elif choice == "2":
                    comment = input("Опишите проблемы: ").strip()
                    self.run_command(f'gh issue comment {issue_num} --body "❌ Проблемы при тестировании: {comment}"')
                    self.run_command(f'gh issue edit {issue_num} --remove-label "status: testing"')
                    self.run_command(f'gh issue edit {issue_num} --add-label "status: in progress"')
                    print("🔄 Задача возвращена на доработку")

def main():
    parser = argparse.ArgumentParser(description="Помощник разработчика Cell Genesis")
    parser.add_argument("command", nargs="?", choices=["start", "branch", "commit", "pr", "review", "test"],
                       help="Команда для выполнения")
    parser.add_argument("--issue", type=str, help="Номер issue")
    parser.add_argument("--title", type=str, help="Заголовок issue")
    
    args = parser.parse_args()
    helper = DevHelper()
    
    if args.command == "start":
        helper.start_work()
    elif args.command == "branch" and args.issue and args.title:
        helper.create_branch(args.issue, args.title)
    elif args.command == "commit":
        helper.make_commit()
    elif args.command == "pr":
        helper.create_pr()
    elif args.command == "review":
        helper.do_review()
    elif args.command == "test":
        helper.test_features()
    else:
        # Интерактивный режим
        helper.start_work()

if __name__ == "__main__":
    main()
