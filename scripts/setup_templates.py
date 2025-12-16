#!/usr/bin/env python3
"""
Скрипт для настройки и проверки шаблонов GitHub Issues
"""
import os
import sys
import yaml
from pathlib import Path

def check_templates():
    """Проверить корректность шаблонов"""
    templates_dir = Path(".github/ISSUE_TEMPLATE")
    
    if not templates_dir.exists():
        print("❌ Папка .github/ISSUE_TEMPLATE не существует")
        return False
    
    # Проверяем обязательные файлы
    required_files = ["config.yml", "bug_report.md", "design_task.md", 
                      "technical_task.md", "feature_request.md"]
    
    missing_files = []
    for file in required_files:
        if not (templates_dir / file).exists():
            missing_files.append(file)
    
    if missing_files:
        print(f"❌ Отсутствуют файлы: {', '.join(missing_files)}")
        print("Создаю недостающие файлы...")
        create_missing_templates(missing_files)
    
    # Проверяем config.yml
    config_path = templates_dir / "config.yml"
    if config_path.exists():
        with open(config_path, 'r') as f:
            config = yaml.safe_load(f)
        
        if config.get('blank_issues_enabled', True):
            print("⚠️  Предупреждение: blank_issues_enabled=True")
            print("Рекомендуется установить false для принудительного использования шаблонов")
    
    print("✅ Шаблоны проверены")
    return True

def create_missing_templates(missing_files):
    """Создать недостающие шаблоны"""
    templates_dir = Path(".github/ISSUE_TEMPLATE")
    templates_dir.mkdir(parents=True, exist_ok=True)
    
    templates = {
        "config.yml": """blank_issues_enabled: false
contact_links:
  - name: 🤔 Вопрос по разработке
    url: https://github.com/ваш-репозиторий/discussions
    about: Задайте вопрос команде разработки
  - name: 🎨 Вопрос по дизайну
    url: https://github.com/ваш-репозиторий/discussions
    about: Обсудите дизайнерские решения
  - name: 📋 Документация
    url: https://github.com/ваш-репозиторий/wiki
    about: Читайте документацию проекта
""",
        
        "bug_report.md": """---
name: "🐛 Баг-репорт"
description: "Сообщение об ошибке"
title: "[BUG] "
labels: ["bug"]
assignees: ""
---

## 🐛 Описание бага
**Кратко:** [Что случилось]

**Детально:** [Подробное описание]

## 🔄 Шаги для воспроизведения
1. [Шаг 1]
2. [Шаг 2]
3. [Шаг 3]
4. **Ошибка:** [Что пошло не так]

## ✅ Ожидаемое поведение
[Что должно было произойти]

## ❌ Фактическое поведение
[Что произошло]

## 🖥️ Системная информация
- **ОС:** [Windows/Linux/macOS]
- **Python:** [версия]
- **Версия игры:** [версия]
- **Устройство ввода:** [Мышь/Клавиатура]

## 📸 Визуальные доказательства
[Скриншоты/видео/GIF]

## 📋 Логи и ошибки
