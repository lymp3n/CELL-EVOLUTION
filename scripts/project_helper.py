#!/usr/bin/env python3
"""
CELL-EVOLUTION Project Helper
Скрипт для быстрого создания GitHub Issues через CLI.
Требует установки и настройки GitHub CLI (gh).
"""
import subprocess
import sys

TEMPLATES = {
    "1": {"name": "🐛 Баг", "cmd_label": "bug_report"},
    "2": {"name": "🎨 Дизайн", "cmd_label": "design_task"},
    "3": {"name": "💻 Разработка", "cmd_label": "technical_task"},
    "4": {"name": "✨ Фича", "cmd_label": "feature_request"},
}

def run_command(cmd_list):
    """Выполняет shell-команду."""
    try:
        result = subprocess.run(cmd_list, capture_output=True, text=True, check=True)
        return result.stdout
    except subprocess.CalledProcessError as e:
        print(f"Ошибка при выполнении команды: {e.stderr}")
        return None

def create_issue():
    """Интерактивное создание issue."""
    print("\n" + "="*50)
    print("   СОЗДАНИЕ НОВОЙ ЗАДАЧИ ДЛЯ CELL-EVOLUTION")
    print("="*50)

    print("\nВыберите тип задачи:")
    for key, value in TEMPLATES.items():
        print(f"  {key}. {value['name']}")

    choice = input("\nВведите номер (1-4): ").strip()
    if choice not in TEMPLATES:
        print("Неверный выбор.")
        return

    template = TEMPLATES[choice]['cmd_label']
    title = input("Введите заголовок задачи: ").strip()
    if not title:
        print("Заголовок не может быть пустым.")
        return

    # Базовые лейблы в зависимости от типа
    labels_map = {
        "1": "type: bug,status: backlog",
        "2": "type: design,component: assets,status: backlog",
        "3": "type: feature,component: core,status: backlog",
        "4": "type: feature,status: backlog",
    }
    labels = labels_map.get(choice, "")

    # Сборка команды gh
    cmd = ["gh", "issue", "create", "--title", title, "--template", template]
    if labels:
        cmd.extend(["--label", labels])

    assignee = input("Назначить на кого-то? (введите логин GitHub или оставьте пустым): ").strip()
    if assignee:
        cmd.extend(["--assignee", assignee])

    print(f"\nВыполняемая команда: {' '.join(cmd)}")
    confirm = input("Создать задачу? (y/N): ").strip().lower()
    if confirm == 'y':
        output = run_command(cmd)
        if output:
            print(f"✅ Задача успешно создана!\n{output}")
    else:
        print("Создание отменено.")

if __name__ == "__main__":
    create_issue()
