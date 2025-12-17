#!/usr/bin/env python3
"""
CELL-EVOLUTION Manager Task Creator
Создание типовых менеджерских и организационных задач.
"""

import sys
import json
import subprocess
import argparse
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from pathlib import Path

class ManagerTaskCreator:
    def __init__(self):
        self.project_root = Path(__file__).parent.parent
        
        # Шаблоны типовых менеджерских задач
        self.task_templates = {
            "sprint_planning": {
                "name": "📋 Планирование спринта",
                "category": "Планирование и оценка (Planning)",
                "default_labels": ["type: management", "component: infrastructure", "priority: critical", "status: backlog"],
                "questions": [
                    ("sprint_info", "Спринт / Этап (например: 'Спринт #2: Эволюция клетки')"),
                    ("goals", "Цели спринта (Sprint Goals)"),
                    ("participants", "Участники планирования"),
                    ("deadline", "Дедлайн завершения планирования (ДД.ММ.ГГГГ)")
                ]
            },
            
            "daily_standup": {
                "name": "🔄 Ежедневный стендап",
                "category": "Координация команды (Coordination)",
                "default_labels": ["type: management", "component: infrastructure", "priority: high", "status: backlog"],
                "questions": [
                    ("date", "Дата стендапа (ДД.ММ.ГГГГ)"),
                    ("time", "Время (например: 9:00)"),
                    ("duration", "Продолжительность (например: 15 минут)"),
                    ("format", "Формат (очно/онлайн, канал)"),
                    ("facilitator", "Фасилитатор (кто ведет)")
                ]
            },
            
            "retrospective": {
                "name": "📊 Ретроспектива спринта",
                "category": "Процессы и улучшения (Process Improvement)",
                "default_labels": ["type: management", "component: infrastructure", "priority: high", "status: backlog"],
                "questions": [
                    ("sprint_info", "Спринт для ретроспективы"),
                    ("date", "Дата проведения"),
                    ("format", "Формат (например: Start/Stop/Continue, Glad/Sad/Mad)"),
                    ("facilitator", "Фасилитатор"),
                    ("deadline_actions", "Дедлайн для action items")
                ]
            },
            
            "progress_report": {
                "name": "📈 Отчет о прогрессе",
                "category": "Анализ и отчётность (Analytics)",
                "default_labels": ["type: management", "component: infrastructure", "priority: medium", "status: backlog"],
                "questions": [
                    ("period", "Отчетный период (например: 'Неделя 48, 25.11-01.12')"),
                    ("audience", "Аудитория (кому отчет)"),
                    ("metrics", "Ключевые метрики для отчета"),
                    ("deadline", "Дедлайн подготовки отчета"),
                    ("presentation_date", "Дата презентации (если требуется)")
                ]
            },
            
            "risk_management": {
                "name": "⚠️  Анализ рисков",
                "category": "Риск-менеджмент (Risk Management)",
                "default_labels": ["type: management", "component: infrastructure", "priority: high", "status: backlog"],
                "questions": [
                    ("scope", "Область анализа (например: 'Технические риски спринта #2')"),
                    ("date", "Дата проведения анализа"),
                    ("participants", "Участники анализа"),
                    ("previous_risks", "Статус предыдущих рисков (если есть)")
                ]
            },
            
            "coordination": {
                "name": "🤝 Координация между командами",
                "category": "Координация команды (Coordination)",
                "default_labels": ["type: management", "component: infrastructure", "priority: medium", "status: backlog"],
                "questions": [
                    ("teams", "Какие команды нужно скоординировать?"),
                    ("topic", "Тема координации"),
                    ("date", "Дата/время встречи"),
                    ("expected_outcome", "Ожидаемый результат")
                ]
            },
            
            "documentation": {
                "name": "📚 Работа с документацией",
                "category": "Процессы и улучшения (Process Improvement)",
                "default_labels": ["type: management", "component: infrastructure", "priority: medium", "status: backlog"],
                "questions": [
                    ("doc_type", "Тип документации (архитектура, процессы, руководства)"),
                    ("purpose", "Цель создания/обновления"),
                    ("owner", "Владелец документа"),
                    ("reviewers", "Ревьюверы"),
                    ("deadline", "Дедлайн")
                ]
            }
        }
    
    def run_gh_command(self, args: List[str]) -> tuple:
        """Выполняет команду GitHub CLI"""
        try:
            result = subprocess.run(
                ["gh"] + args,
                capture_output=True,
                text=True,
                encoding='utf-8'
            )
            return result.returncode == 0, result.stdout.strip()
        except FileNotFoundError:
            return False, "GitHub CLI не установлен"
        except Exception as e:
            return False, str(e)
    
    def check_auth(self) -> bool:
        """Проверяет аутентификацию"""
        success, _ = self.run_gh_command(["auth", "status"])
        return success
    
    def get_current_sprint(self) -> Dict[str, str]:
        """Определяет текущий спринт"""
        # Простая логика - можно улучшить
        today = datetime.now()
        
        # Предполагаем, что спринты начинаются по понедельникам
        start_of_week = today - timedelta(days=today.weekday())
        sprint_start = start_of_week
        sprint_end = sprint_start + timedelta(days=13)  # 2 недели
        
        # Номер спринта можно вычислять от даты начала проекта
        # Пока используем простую логику
        days_since_project_start = (today - datetime(2024, 1, 1)).days
        sprint_number = (days_since_project_start // 14) + 1
        
        return {
            "number": sprint_number,
            "start": sprint_start.strftime("%d.%m.%Y"),
            "end": sprint_end.strftime("%d.%m.%Y"),
            "display": f"Спринт #{sprint_number} ({sprint_start.strftime('%d.%m')}-{sprint_end.strftime('%d.%m.%Y')})"
        }
    
    def gather_template_info(self, template_type: str) -> Dict[str, Any]:
        """Собирает информацию для шаблона"""
        if template_type not in self.task_templates:
            raise ValueError(f"Неизвестный тип задачи: {template_type}")
        
        template = self.task_templates[template_type]
        info = {"template_type": template_type}
        
        print(f"\n🎯 Создаю: {template['name']}")
        print(f"   Категория: {template['category']}")
        print("\n" + "-"*40)
        
        # Запрашиваем ответы на вопросы
        for field, question in template["questions"]:
            value = input(f"{question}: ").strip()
            info[field] = value
        
        # Дополнительная информация
        print("\n📝 Дополнительная информация (можно пропустить):")
        
        info["additional_context"] = input("Дополнительный контекст/примечания: ").strip()
        
        assignee = input("Назначить на (логин GitHub, Enter - оставить пустым): ").strip()
        if assignee:
            info["assignee"] = assignee
        
        extra_labels = input("Дополнительные лейблы (через запятую): ").strip()
        if extra_labels:
            info["extra_labels"] = [l.strip() for l in extra_labels.split(",") if l.strip()]
        
        return info
    
    def generate_issue_body(self, template_type: str, info: Dict[str, Any]) -> str:
        """Генерирует тело задачи на основе шаблона"""
        template = self.task_templates[template_type]
        
        body_lines = []
        body_lines.append("## 🎯 Организационная задача")
        body_lines.append(f"*Тип: {template['name']}*")
        body_lines.append("")
        
        # Добавляем ответы на вопросы
        for field, question in template["questions"]:
            if field in info and info[field]:
                body_lines.append(f"### {question}")
                body_lines.append(info[field])
                body_lines.append("")
        
        # Добавляем дополнительные поля
        if info.get("additional_context"):
            body_lines.append("### 📌 Дополнительный контекст")
            body_lines.append(info["additional_context"])
            body_lines.append("")
        
        # Добавляем стандартные разделы
        body_lines.append("### 📋 Ожидаемые результаты / Деливераблы")
        
        # Генерируем деливераблы в зависимости от типа задачи
        deliverables = self.generate_deliverables(template_type, info)
        for deliverable in deliverables:
            body_lines.append(f"- [ ] {deliverable}")
        
        body_lines.append("")
        
        body_lines.append("### ✅ Критерии успеха")
        success_criteria = self.generate_success_criteria(template_type, info)
        for criterion in success_criteria:
            body_lines.append(f"- {criterion}")
        
        body_lines.append("")
        
        # Добавляем информацию об участниках, если есть
        if "participants" in info and info["participants"]:
            body_lines.append("### 👥 Участники")
            body_lines.append(info["participants"])
            body_lines.append("")
        
        return "\n".join(body_lines)
    
    def generate_deliverables(self, template_type: str, info: Dict) -> List[str]:
        """Генерирует список деливераблов"""
        deliverables = []
        
        if template_type == "sprint_planning":
            deliverables = [
                "Проведена встреча планирования спринта",
                "Сформирован и приоритизирован бэклог спринта",
                "Все задачи спринта оценены и назначены на исполнителей",
                "Цели спринта (Sprint Goals) сформулированы и задокументированы",
                "Команда понимает план работ на спринт"
            ]
        
        elif template_type == "daily_standup":
            deliverables = [
                "Проведён ежедневный стендап (15 минут максимум)",
                "Обновлены статусы задач в GitHub Projects",
                "Выявленные блокеры зафиксированы",
                "Команда синхронизирована по текущему прогрессу"
            ]
        
        elif template_type == "retrospective":
            deliverables = [
                "Проведена встреча ретроспективы",
                "Собраны фидбеки от всех участников команды",
                "Выявлены точки улучшения процессов",
                "Созданы action items с ответственными и сроками",
                "Результаты ретроспективы задокументированы"
            ]
        
        elif template_type == "progress_report":
            deliverables = [
                "Собраны метрики спринта/проекта",
                "Подготовлен отчёт/презентация",
                "Отчёт представлен стейкхолдерам",
                "Получен и обработан feedback",
                "Скорректирован план при необходимости"
            ]
        
        elif template_type == "risk_management":
            deliverables = [
                "Проведён анализ рисков",
                "Риски оценены по вероятности и влиянию",
                "Разработаны mitigation strategies",
                "Создан/обновлён risk register",
                "Ответственные за риски назначены"
            ]
        
        elif template_type == "coordination":
            deliverables = [
                "Проведена координационная встреча",
                "Достигнуты agreements по точкам интеграции",
                "Создан план совместных действий",
                "Ответственные назначены",
                "Результаты задокументированы"
            ]
        
        elif template_type == "documentation":
            deliverables = [
                "Документ создан/обновлён",
                "Проведено ревью документа",
                "Внесены правки по результатам ревью",
                "Документ опубликован в agreed location",
                "Команда проинформирована"
            ]
        
        return deliverables
    
    def generate_success_criteria(self, template_type: str, info: Dict) -> List[str]:
        """Генерирует критерии успеха"""
        criteria = []
        
        if template_type == "sprint_planning":
            criteria = [
                "Бэклог спринта готов и все задачи имеют оценки",
                "Каждый участник команды понимает свои задачи",
                "Sprint Goals ясны и достижимы",
                "План спринта реалистичен с учётом capacity команды"
            ]
        
        elif template_type == "daily_standup":
            criteria = [
                "Стендап уложился в 15 минут",
                "Все участники поделились прогрессом и планами",
                "Блокеры выявлены и назначены ответственные",
                "Статусы задач актуальны"
            ]
        
        else:
            criteria = [
                "Все деливераблы выполнены",
                "Участники удовлетворены процессом и результатом",
                "Результаты задокументированы и доступны",
                "Следующие шаги определены"
            ]
        
        return criteria
    
    def create_manager_issue(self, template_type: str, title: str, body: str, 
                           labels: List[str], assignee: Optional[str] = None) -> tuple:
        """Создает задачу менеджера"""
        cmd = [
            "issue", "create",
            "--title", title,
            "--body", body,
            "--template", "manager_task.yml"
        ]
        
        # Добавляем лейблы
        for label in labels:
            cmd.extend(["--label", label])
        
        # Добавляем назначение
        if assignee:
            cmd.extend(["--assignee", assignee])
        
        # Добавляем в проект
        cmd.extend(["--project", "CELL-EVOLUTION"])
        
        # Выполняем команду
        return self.run_gh_command(cmd)
    
    def create_weekly_standup_series(self, sprint_info: Dict):
        """Создает серию задач на ежедневные стендапы"""
        print(f"\n📅 Создаю задачи на стендапы для {sprint_info['display']}")
        
        start_date = datetime.strptime(sprint_info["start"], "%d.%m.%Y")
        end_date = datetime.strptime(sprint_info["end"], "%d.%m.%Y")
        
        current_date = start_date
        standup_count = 0
        
        while current_date <= end_date:
            # Только рабочие дни (понедельник-пятница)
            if current_date.weekday() < 5:
                date_str = current_date.strftime("%d.%m.%Y")
                title = f"🔄 Ежедневный стендап {date_str} ({sprint_info['display']})"
                
                body = f"""## 🎯 Организационная задача
*Тип: Ежедневный стендап*

### Дата стендапа
{date_str}

### Время
9:00

### Продолжительность
15 минут

### Формат
Онлайн, Discord

### Фасилитатор
Тимлид

### 📋 Ожидаемые результаты / Деливераблы
- [ ] Проведён ежедневный стендап (15 минут максимум)
- [ ] Обновлены статусы задач в GitHub Projects
- [ ] Выявленные блокеры зафиксированы
- [ ] Команда синхронизирована по текущему прогрессу

### ✅ Критерии успеха
- Стендап уложился в 15 минут
- Все участники поделились прогрессом и планами
- Блокеры выявлены и назначены ответственные
- Статусы задач актуальны
"""
                
                labels = ["type: management", "component: infrastructure", 
                         "priority: high", "status: backlog"]
                
                success, output = self.create_manager_issue(
                    "daily_standup",
                    title,
                    body,
                    labels,
                    "тимлид"  # Назначаем на тимлида
                )
                
                if success:
                    standup_count += 1
                    print(f"  ✅ Создана задача на стендап {date_str}")
                else:
                    print(f"  ❌ Ошибка: {output}")
            
            current_date += timedelta(days=1)
        
        print(f"\n🎉 Создано {standup_count} задач на стендапы")
    
    def interactive_mode(self):
        """Интерактивный режим создания задач"""
        print("\n" + "="*60)
        print("   🚀 СОЗДАНИЕ МЕНЕДЖЕРСКИХ ЗАДАЧ CELL-EVOLUTION")
        print("="*60)
        
        # Проверяем аутентификацию
        if not self.check_auth():
            print("\n❌ GitHub CLI не аутентифицирован.")
            print("💡 Выполните: gh auth login")
            return
        
        # Показываем доступные типы задач
        print("\n📋 Доступные типы менеджерских задач:")
        for i, (key, template) in enumerate(self.task_templates.items(), 1):
            print(f"  {i}. {template['name']} ({key})")
        
        print(f"  {len(self.task_templates) + 1}. Создать серию стендапов на спринт")
        print(f"  {len(self.task_templates) + 2}. Отмена")
        
        try:
            choice = int(input(f"\n👉 Выберите тип (1-{len(self.task_templates) + 2}): ").strip())
            
            if choice == len(self.task_templates) + 1:
                # Создание серии стендапов
                sprint_info = self.get_current_sprint()
                print(f"\n📅 Текущий спринт: {sprint_info['display']}")
                confirm = input(f"\nСоздать задачи на стендапы для этого спринта? (y/N): ").strip().lower()
                
                if confirm == 'y':
                    self.create_weekly_standup_series(sprint_info)
                return
                
            elif choice == len(self.task_templates) + 2:
                print("Отменено")
                return
                
            elif 1 <= choice <= len(self.task_templates):
                template_key = list(self.task_templates.keys())[choice - 1]
                
                # Собираем информацию
                info = self.gather_template_info(template_key)
                
                # Генерируем заголовок
                title_prefix = self.task_templates[template_key]["name"].split(" ")[0]  # Берем эмодзи
                title = f"{title_prefix} {info.get('sprint_info', info.get('date', ''))}"
                
                # Генерируем тело
                body = self.generate_issue_body(template_key, info)
                
                # Собираем лейблы
                labels = self.task_templates[template_key]["default_labels"].copy()
                if "extra_labels" in info:
                    labels.extend(info["extra_labels"])
                
                # Создаем задачу
                print(f"\n🔄 Создаю задачу: {title}")
                
                success, output = self.create_manager_issue(
                    template_key,
                    title,
                    body,
                    labels,
                    info.get("assignee")
                )
                
                if success:
                    print(f"✅ Менеджерская задача успешно создана!")
                    if output:
                        print(f"   {output}")
                else:
                    print(f"❌ Ошибка при создании задачи: {output}")
                    
            else:
                print("❌ Неверный выбор")
                
        except ValueError:
            print("❌ Введите число")
        except Exception as e:
            print(f"❌ Ошибка: {e}")
    
    def quick_create(self, task_type: str, sprint_info: str = None):
        """Быстрое создание задачи"""
        if task_type not in self.task_templates:
            print(f"❌ Неизвестный тип задачи: {task_type}")
            print(f"   Доступные: {', '.join(self.task_templates.keys())}")
            return
        
        template = self.task_templates[task_type]
        
        # Используем текущий спринт, если не указан
        if not sprint_info:
            sprint = self.get_current_sprint()
            sprint_info = sprint["display"]
        
        # Генерируем стандартную задачу
        title = f"{template['name'].split(' ')[0]} {sprint_info}"
        
        # Простое тело
        body = f"""## 🎯 Организационная задача
*Тип: {template['name']}*

### Спринт / Этап
{sprint_info}

### Категория задачи
{template['category']}

### 📋 Ожидаемые результаты / Деливераблы
- [ ] Задача выполнена
- [ ] Результаты задокументированы
- [ ] Команда проинформирована

### ✅ Критерии успеха
- Все деливераблы выполнены
- Участники удовлетворены процессом
- Следующие шаги определены
"""
        
        success, output = self.create_manager_issue(
            task_type,
            title,
            body,
            template["default_labels"],
            "тимлид"  # По умолчанию на тимлида
        )
        
        if success:
            print(f"✅ Создана задача: {title}")
        else:
            print(f"❌ Ошибка: {output}")

def main():
    """Основная функция"""
    parser = argparse.ArgumentParser(
        description="CELL-EVOLUTION Manager Task Creator",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Примеры использования:
  %(prog)s                            # Интерактивный режим
  %(prog)s --quick sprint_planning    # Быстрое создание задачи планирования
  %(prog)s --quick daily_standup      # Задача на стендап
  %(prog)s --quick retrospective      # Задача на ретроспективу
  %(prog)s --standup-series           # Серия стендапов на спринт
        """
    )
    
    parser.add_argument(
        "--quick", "-q",
        choices=["sprint_planning", "daily_standup", "retrospective", 
                "progress_report", "risk_management", "coordination", "documentation"],
        help="Быстрое создание задачи указанного типа"
    )
    
    parser.add_argument(
        "--sprint", "-s",
        type=str,
        help="Информация о спринте (для --quick)"
    )
    
    parser.add_argument(
        "--standup-series",
        action="store_true",
        help="Создать серию задач на стендапы для текущего спринта"
    )
    
    parser.add_argument(
        "--list-templates",
        action="store_true",
        help="Показать доступные шаблоны"
    )
    
    args = parser.parse_args()
    creator = ManagerTaskCreator()
    
    # Проверяем аутентификацию
    if not creator.check_auth():
        print("❌ GitHub CLI не аутентифицирован.")
        print("💡 Выполните: gh auth login")
        sys.exit(1)
    
    # Обрабатываем аргументы
    if args.list_templates:
        print("\n📋 Доступные шаблоны менеджерских задач:")
        for key, template in creator.task_templates.items():
            print(f"  {key:20} - {template['name']}")
        print()
    
    elif args.quick:
        creator.quick_create(args.quick, args.sprint)
    
    elif args.standup_series:
        sprint_info = creator.get_current_sprint()
        creator.create_weekly_standup_series(sprint_info)
    
    else:
        # Интерактивный режим
        creator.interactive_mode()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 Выход...")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Ошибка: {e}")
        sys.exit(1)
