#!/usr/bin/env python3
"""
CELL-EVOLUTION Developer Helper
Основной инструмент для ежедневной работы разработчика.
Интегрируется с GitHub Issues, Projects, Pull Requests.
"""

import os
import sys
import json
import subprocess
import argparse
import re
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, List

class DevHelper:
    def __init__(self):
        self.project_root = Path(__file__).parent.parent
        self.config = self.load_config()
        
    def load_config(self) -> Dict:
        """Загружает конфигурацию разработчика"""
        config_path = self.project_root / ".devhelper.json"
        if config_path.exists():
            try:
                with open(config_path, 'r') as f:
                    return json.load(f)
            except json.JSONDecodeError:
                pass
        
        return {
            "last_branch": "develop",
            "gh_username": None,
            "team_members": {
                "core": ["core-dev-1", "core-dev-2", "core-dev-3"],
                "evolution": ["evo-dev-1", "evo-dev-2", "evo-dev-3"],
                "ai": ["ai-dev-1", "ai-dev-2", "ai-dev-3"],
                "graphics": ["graphics-dev-1", "graphics-dev-2"],
                "design": ["designer-1", "designer-2", "designer-3", "designer-4"]
            }
        }
    
    def save_config(self):
        """Сохраняет конфигурацию"""
        config_path = self.project_root / ".devhelper.json"
        with open(config_path, 'w') as f:
            json.dump(self.config, f, indent=2)
    
    def run_command(self, cmd: List[str], cwd: Optional[Path] = None) -> tuple:
        """Выполняет команду и возвращает (успех, вывод)"""
        try:
            result = subprocess.run(
                cmd,
                cwd=cwd or self.project_root,
                capture_output=True,
                text=True,
                encoding='utf-8'
            )
            return result.returncode == 0, result.stdout.strip()
        except Exception as e:
            return False, str(e)
    
    def get_current_branch(self) -> str:
        """Возвращает текущую ветку Git"""
        success, output = self.run_command(["git", "branch", "--show-current"])
        return output if success else "unknown"
    
    def check_gh_auth(self) -> bool:
        """Проверяет аутентификацию GitHub CLI"""
        success, _ = self.run_command(["gh", "auth", "status"])
        return success
    
    def daily_start(self):
        """Ежедневный старт работы"""
        print("\n" + "="*60)
        print("   🌅 ДОБРОЕ УТРО, РАЗРАБОТЧИК CELL-EVOLUTION!")
        print("="*60)
        print(f"📅 {datetime.now().strftime('%d.%m.%Y %H:%M')}")
        
        # Показываем текущую ветку
        current_branch = self.get_current_branch()
        print(f"🌿 Текущая ветка: {current_branch}")
        
        # Проверяем статус git
        print("\n📊 Статус Git:")
        success, status = self.run_command(["git", "status", "--short"])
        if success and status:
            print(status[:500] + ("..." if len(status) > 500 else ""))
        else:
            print("  Чисто!")
        
        # Проверяем GitHub CLI
        if not self.check_gh_auth():
            print("\n⚠️  GitHub CLI не аутентифицирован!")
            print("   Выполните: gh auth login")
            return
        
        # Показываем назначенные задачи
        print("\n🎯 Ваши задачи на сегодня:")
        self.show_my_issues()
        
        # Предлагаем действия
        self.show_main_menu()
    
    def show_my_issues(self):
        """Показывает задачи, назначенные на текущего пользователя"""
        # Получаем текущего пользователя GitHub
        success, user_output = self.run_command(["gh", "api", "user", "--jq", ".login"])
        if not success:
            print("  Не удалось получить информацию о пользователе")
            return
        
        github_user = user_output.strip()
        
        # Получаем задачи пользователя
        success, issues = self.run_command([
            "gh", "issue", "list",
            "--assignee", github_user,
            "--state", "open",
            "--json", "number,title,url,labels"
        ])
        
        if success and issues:
            try:
                issues_data = json.loads(issues)
                for issue in issues_data[:10]:  # Показываем первые 10
                    labels = [l['name'] for l in issue['labels']]
                    status_label = next((l for l in labels if l.startswith('status:')), 'без статуса')
                    print(f"  #{issue['number']}: {issue['title'][:50]}... [{status_label}]")
                
                if len(issues_data) > 10:
                    print(f"  ... и ещё {len(issues_data) - 10} задач")
            except json.JSONDecodeError:
                print("  Не удалось разобрать ответ GitHub")
        else:
            print("  Нет назначенных задач!")
    
    def show_main_menu(self):
        """Показывает главное меню"""
        print("\n🛠️  Что будем делать сегодня?")
        print("  1. Взять новую задачу из Ready")
        print("  2. Продолжить работу над текущей")
        print("  3. Сделать коммит текущих изменений")
        print("  4. Создать Pull Request")
        print("  5. Сделать Code Review")
        print("  6. Запустить тесты")
        print("  7. Проверить стиль кода")
        print("  8. Выйти")
        
        choice = input("\n👉 Ваш выбор (1-8): ").strip()
        
        if choice == "1":
            self.pick_new_task()
        elif choice == "2":
            self.continue_current_task()
        elif choice == "3":
            self.make_commit()
        elif choice == "4":
            self.create_pr()
        elif choice == "5":
            self.do_code_review()
        elif choice == "6":
            self.run_tests()
        elif choice == "7":
            self.run_lint()
        elif choice == "8":
            print("\n👋 Хорошего рабочего дня!")
            sys.exit(0)
        else:
            print("❌ Неверный выбор")
    
    def pick_new_task(self):
        """Помогает выбрать новую задачу"""
        print("\n📋 Задачи, готовые к работе (status: ready):")
        
        success, issues = self.run_command([
            "gh", "issue", "list",
            "--label", "status: ready",
            "--state", "open",
            "--json", "number,title,assignees,labels"
        ])
        
        if not success or not issues:
            print("  Нет задач со статусом 'ready'")
            return
        
        try:
            issues_data = json.loads(issues)
            for i, issue in enumerate(issues_data[:15], 1):
                assigned = "📌" if issue['assignees'] else "🔓"
                print(f"  {i}. {assigned} #{issue['number']}: {issue['title'][:60]}...")
        except json.JSONDecodeError:
            print("  Ошибка при получении задач")
            return
        
        try:
            choice = int(input("\n🎯 Выберите номер задачи (1-15): ").strip())
            if 1 <= choice <= len(issues_data):
                selected = issues_data[choice - 1]
                self.start_working_on_issue(selected)
            else:
                print("❌ Неверный номер")
        except ValueError:
            print("❌ Введите число")
    
    def start_working_on_issue(self, issue: Dict):
        """Начинает работу над задачей"""
        issue_num = issue['number']
        issue_title = issue['title']
        
        print(f"\n🚀 Начинаем работу над задачей #{issue_num}")
        print(f"   Название: {issue_title}")
        
        # Запрашиваем подтверждение
        confirm = input("\nВзять эту задачу? (y/N): ").strip().lower()
        if confirm != 'y':
            print("Отменено")
            return
        
        # Назначаем задачу на себя
        success, _ = self.run_command(["gh", "issue", "edit", str(issue_num), "--add-assignee", "@me"])
        if not success:
            print("⚠️  Не удалось назначить задачу. Продолжаем...")
        
        # Меняем статус
        self.run_command([
            "gh", "issue", "edit", str(issue_num),
            "--remove-label", "status: ready",
            "--add-label", "status: in progress"
        ])
        
        # Создаем ветку
        self.create_branch_for_issue(issue_num, issue_title)
        
        # Открываем задачу в браузере
        open_browser = input("\nОткрыть задачу в браузере? (y/N): ").strip().lower()
        if open_browser == 'y':
            self.run_command(["gh", "issue", "view", str(issue_num), "--web"])
    
    def create_branch_for_issue(self, issue_num: int, issue_title: str):
        """Создает ветку для задачи"""
        # Очищаем название для имени ветки
        safe_title = re.sub(r'[^\w\s-]', '', issue_title.lower())
        safe_title = re.sub(r'[-\s]+', '-', safe_title)
        branch_name = f"issue-{issue_num}-{safe_title[:40]}".rstrip('-')
        
        print(f"\n🌿 Создаю ветку: {branch_name}")
        
        # Переходим на develop и обновляем
        print("  ↳ Переключаюсь на develop...")
        self.run_command(["git", "checkout", "develop"])
        self.run_command(["git", "pull", "origin", "develop"])
        
        # Создаем новую ветку
        self.run_command(["git", "checkout", "-b", branch_name])
        
        # Сохраняем в конфиг
        self.config["last_branch"] = branch_name
        self.save_config()
        
        print(f"\n✅ Ветка создана!")
        print(f"\n💡 Не забудьте:")
        print(f"   1. Работать в этой ветке: {branch_name}")
        print(f"   2. Делать коммиты с ссылкой на issue")
        print(f"   3. Создать PR в develop когда задача будет готова")
    
    def continue_current_task(self):
        """Продолжение работы над текущей задачей"""
        current_branch = self.get_current_branch()
        print(f"\n📌 Текущая ветка: {current_branch}")
        
        # Ищем номер issue в названии ветки
        match = re.search(r'issue-(\d+)', current_branch)
        if match:
            issue_num = match.group(1)
            print(f"🔗 Связанная задача: #{issue_num}")
            
            # Показываем информацию о задаче
            success, issue_info = self.run_command([
                "gh", "issue", "view", issue_num,
                "--json", "title,state,labels"
            ])
            
            if success:
                try:
                    issue_data = json.loads(issue_info)
                    print(f"   Название: {issue_data['title']}")
                    status_labels = [l['name'] for l in issue_data['labels'] if l['name'].startswith('status:')]
                    if status_labels:
                        print(f"   Статус: {status_labels[0]}")
                except:
                    pass
            
            # Предлагаем действия для текущей задачи
            self.show_task_actions_menu(issue_num)
        else:
            print("❌ Не могу найти номер issue в названии ветки")
            print("💡 Имя ветки должно содержать 'issue-<номер>'")
    
    def show_task_actions_menu(self, issue_num: str):
        """Меню действий для текущей задачи"""
        print("\n🎮 Что делаем с задачей?")
        print("  1. Запустить тесты")
        print("  2. Проверить стиль кода")
        print("  3. Запустить игру")
        print("  4. Показать diff изменений")
        print("  5. Сделать коммит")
        print("  6. Создать/обновить PR")
        print("  7. Вернуться в главное меню")
        
        choice = input("\n👉 Выбор (1-7): ").strip()
        
        if choice == "1":
            self.run_tests()
        elif choice == "2":
            self.run_lint()
        elif choice == "3":
            self.run_game()
        elif choice == "4":
            self.show_git_diff()
        elif choice == "5":
            self.make_commit()
        elif choice == "6":
            self.create_or_update_pr(issue_num)
        elif choice == "7":
            return
        else:
            print("❌ Неверный выбор")
    
    def make_commit(self):
        """Создает коммит"""
        print("\n💾 Создание коммита")
        
        # Показываем статус
        success, status = self.run_command(["git", "status", "--short"])
        if success and status:
            print("Измененные файлы:")
            print(status)
        else:
            print("Нет изменений для коммита")
            return
        
        # Спрашиваем, какие файлы добавить
        print("\n📁 Какие файлы добавить в коммит?")
        print("  * - все изменения")
        print("  . - только отслеживаемые изменения")
        print("  или перечислите файлы через пробел")
        
        files = input("👉 Ваш выбор: ").strip()
        
        if not files:
            print("❌ Не указаны файлы")
            return
        
        # Добавляем файлы
        add_cmd = ["git", "add"]
        if files == "*":
            add_cmd.append("--all")
        elif files == ".":
            add_cmd.append("--update")
        else:
            add_cmd.extend(files.split())
        
        success, output = self.run_command(add_cmd)
        if not success:
            print(f"❌ Ошибка при добавлении файлов: {output}")
            return
        
        # Получаем номер issue из ветки
        current_branch = self.get_current_branch()
        match = re.search(r'issue-(\d+)', current_branch)
        
        commit_msg = input("\n📝 Сообщение коммита: ").strip()
        
        if not commit_msg:
            print("❌ Сообщение коммита не может быть пустым")
            return
        
        # Добавляем ссылку на issue, если есть
        if match:
            issue_num = match.group(1)
            commit_msg = f"{commit_msg}\n\nCloses #{issue_num}"
        
        # Создаем коммит
        success, output = self.run_command(["git", "commit", "-m", commit_msg])
        if success:
            print("✅ Коммит создан!")
            
            # Предлагаем запушить
            push = input("\n🚀 Запушить изменения? (y/N): ").strip().lower()
            if push == 'y':
                success, output = self.run_command(["git", "push", "origin", current_branch])
                if success:
                    print("✅ Изменения отправлены на GitHub!")
                else:
                    print(f"❌ Ошибка: {output}")
        else:
            print(f"❌ Ошибка при создании коммита: {output}")
    
    def create_or_update_pr(self, issue_num: str):
        """Создает или обновляет Pull Request"""
        current_branch = self.get_current_branch()
        
        # Проверяем, существует ли уже PR для этой ветки
        success, prs = self.run_command([
            "gh", "pr", "list",
            "--head", current_branch,
            "--state", "open",
            "--json", "number,title"
        ])
        
        if success and prs:
            try:
                pr_data = json.loads(prs)
                if pr_data:
                    print(f"📌 Уже есть открытый PR: #{pr_data[0]['number']}")
                    update = input("\nОбновить существующий PR? (y/N): ").strip().lower()
                    if update == 'y':
                        self.run_command(["git", "push", "origin", current_branch, "--force-with-lease"])
                        print("✅ PR обновлен!")
                    return
            except:
                pass
        
        # Создаем новый PR
        print(f"\n🔄 Создаю Pull Request для ветки: {current_branch}")
        
        # Получаем информацию о задаче
        success, issue_info = self.run_command([
            "gh", "issue", "view", issue_num,
            "--json", "title"
        ])
        
        if not success:
            print("❌ Не могу получить информацию о задаче")
            return
        
        try:
            issue_data = json.loads(issue_info)
            issue_title = issue_data['title']
            
            pr_title = f"Fix #{issue_num}: {issue_title}"
            pr_body = f"""## Описание
Решает issue #{issue_num}

## Изменения
- [ ] Код написан и отформатирован
- [ ] Тесты проходят
- [ ] Документация обновлена

## Скриншоты
<!-- Если нужно -->

## Проверка
- [ ] Самопроверка кода выполнена
- [ ] Все тесты проходят локально
"""
            
            print(f"\n📝 Заголовок PR: {pr_title}")
            print("\nСоздаю Pull Request...")
            
            success, output = self.run_command([
                "gh", "pr", "create",
                "--title", pr_title,
                "--body", pr_body,
                "--base", "develop",
                "--head", current_branch,
                "--label", "needs-review"
            ])
            
            if success:
                print("✅ PR создан!")
                print(f"\n💡 Не забудьте:")
                print("   1. Добавить ревьюверов")
                print("   2. Проверить, что все тесты проходят в CI")
                print("   3. Ждать аппрувов перед мержем")
                
                # Меняем статус задачи
                self.run_command([
                    "gh", "issue", "edit", issue_num,
                    "--remove-label", "status: in progress",
                    "--add-label", "status: in review"
                ])
            else:
                print(f"❌ Ошибка: {output}")
                
        except json.JSONDecodeError:
            print("❌ Ошибка при разборе данных задачи")
    
    def do_code_review(self):
        """Проводит Code Review"""
        print("\n👀 Code Review")
        
        # Получаем PR, назначенные на меня для ревью
        success, prs = self.run_command([
            "gh", "pr", "list",
            "--review-requested", "@me",
            "--state", "open",
            "--json", "number,title,author"
        ])
        
        if not success or not prs:
            print("  Нет PR, ожидающих вашего ревью")
            return
        
        try:
            pr_data = json.loads(prs)
            print("\n📋 PR, ожидающие вашего ревью:")
            for i, pr in enumerate(pr_data[:10], 1):
                print(f"  {i}. #{pr['number']}: {pr['title'][:60]}... (автор: {pr['author']['login']})")
            
            if len(pr_data) > 10:
                print(f"  ... и ещё {len(pr_data) - 10} PR")
            
            try:
                choice = int(input("\n🎯 Выберите PR для ревью (1-10): ").strip())
                if 1 <= choice <= len(pr_data):
                    selected = pr_data[choice - 1]
                    self.review_specific_pr(selected['number'])
                else:
                    print("❌ Неверный номер")
            except ValueError:
                print("❌ Введите число")
                
        except json.JSONDecodeError:
            print("❌ Ошибка при получении списка PR")
    
    def review_specific_pr(self, pr_number: int):
        """Проводит ревью конкретного PR"""
        print(f"\n🔍 Ревью PR #{pr_number}")
        
        # Показываем изменения
        print("\n📋 Показываю diff...")
        self.run_command(["gh", "pr", "diff", str(pr_number)])
        
        print("\n" + "="*60)
        print("🎯 Ваше решение по этому PR:")
        print("  1. Одобрить (approve)")
        print("  2. Запросить изменения (request changes)")
        print("  3. Прокомментировать (comment)")
        print("  4. Просмотреть в браузере")
        print("  5. Отмена")
        
        choice = input("\n👉 Выбор (1-5): ").strip()
        
        if choice == "1":
            comment = input("Комментарий для аппрува (можно оставить пустым): ").strip()
            if comment:
                self.run_command(["gh", "pr", "review", str(pr_number), "--approve", "--body", comment])
            else:
                self.run_command(["gh", "pr", "review", str(pr_number), "--approve"])
            print("✅ PR одобрен!")
            
        elif choice == "2":
            comment = input("Обязательный комментарий с описанием необходимых изменений: ").strip()
            if comment:
                self.run_command(["gh", "pr", "review", str(pr_number), "--request-changes", "--body", comment])
                print("🔄 Запрошены изменения")
            else:
                print("❌ Комментарий обязателен при запросе изменений")
                
        elif choice == "3":
            comment = input("Ваш комментарий: ").strip()
            if comment:
                self.run_command(["gh", "pr", "review", str(pr_number), "--comment", "--body", comment])
                print("💬 Комментарий добавлен")
            else:
                print("❌ Комментарий не может быть пустым")
                
        elif choice == "4":
            self.run_command(["gh", "pr", "view", str(pr_number), "--web"])
            print("✅ Открываю в браузере...")
            
        elif choice == "5":
            print("Отменено")
            
        else:
            print("❌ Неверный выбор")
    
    def run_tests(self):
        """Запускает тесты"""
        print("\n🧪 Запускаю тесты...")
        os.system(f"cd {self.project_root} && python scripts/run_tests.py")
    
    def run_lint(self):
        """Запускает проверку стиля"""
        print("\n🔍 Проверяю стиль кода...")
        os.system(f"cd {self.project_root} && python scripts/run_tests.py --lint")
    
    def run_game(self):
        """Запускает игру"""
        print("\n🎮 Запускаю игру...")
        main_file = self.project_root / "src" / "cell_genesis" / "main.py"
        if main_file.exists():
            os.system(f"cd {self.project_root} && python {main_file}")
        else:
            print("❌ Файл игры не найден: src/cell_genesis/main.py")
    
    def show_git_diff(self):
        """Показывает изменения"""
        print("\n📋 Изменения в текущей ветке:")
        os.system("git diff --stat")
        print("\n" + "="*60)
        show_full = input("Показать полный diff? (y/N): ").strip().lower()
        if show_full == 'y':
            os.system("git diff")

def main():
    """Основная функция"""
    parser = argparse.ArgumentParser(description="CELL-EVOLUTION Developer Helper")
    parser.add_argument("command", nargs="?", help="Команда для выполнения")
    parser.add_argument("--issue", type=int, help="Номер issue")
    parser.add_argument("--pr", type=int, help="Номер PR")
    
    args = parser.parse_args()
    helper = DevHelper()
    
    if args.command == "start":
        helper.daily_start()
    elif args.command == "commit":
        helper.make_commit()
    elif args.command == "pr" and args.issue:
        helper.create_or_update_pr(str(args.issue))
    elif args.command == "review" and args.pr:
        helper.review_specific_pr(args.pr)
    elif args.command == "test":
        helper.run_tests()
    elif args.command == "lint":
        helper.run_lint()
    elif args.command == "game":
        helper.run_game()
    else:
        # Интерактивный режим
        helper.daily_start()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 Выход...")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Критическая ошибка: {e}")
        sys.exit(1)
