#!/usr/bin/env python3
"""
CELL-EVOLUTION Manager Task Creator
Автоматическое создание типовых менеджерских задач через GitHub CLI.
"""
import subprocess
import sys
import json
from datetime import datetime, timedelta
from pathlib import Path

def run_gh_command(args, capture_output=True):
    """Выполняет команду GitHub CLI."""
    try:
        result = subprocess.run(['gh'] + args, 
                              capture_output=capture_output, 
                              text=True, 
                              check=True)
        if capture_output:
            return result.stdout.strip()
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Ошибка GitHub CLI: {e.stderr}")
        return None
    except FileNotFoundError:
        print("❌ GitHub CLI не установлен. Установите: https://cli.github.com/")
        return None

def create_manager_task(task_type, title, sprint_info, **kwargs):
    """Создаёт менеджерскую задачу по шаблону."""
    
    # Шаблоны для типовых менеджерских задач
    templates = {
        'sprint_planning': {
            'category': 'Планирование и оценка (Planning)',
            'description': f'''**Цель:** Провести планирование {sprint_info}, определить цели, оценить и распределить задачи.
**Контекст:** Старт нового итерационного цикла разработки.
**Ожидаемый результат:** Чёткий план спринта с приоритизированным бэклогом и назначенными ответственными.''',
            'deliverables': '''- [ ] Проведена встреча планирования спринта (Sprint Planning)
- [ ] Сформирован и приоритизирован бэклог спринта в GitHub Projects
- [ ] Все задачи спринта оценены (story points) и назначены на исполнителей
- [ ] Цели спринта (Sprint Goals) сформулированы и понятны команде
- [ ] Обновлён roadmap проекта (если требуется)''',
            'participants': 'Вся команда (11 разработчиков + 4 дизайнера), техлид, продакт',
            'metrics': '- Все задачи спринта созданы в Issues с корректными лейблами и оценками.\n- Каждый участник команды понимает свои задачи на спринт.\n- Sprint Goals задокументированы в описании спринта.',
            'labels': ['type: management', 'component: infrastructure', 'priority: critical', 'status: backlog']
        },
        
        'daily_standup': {
            'category': 'Координация команды (Coordination)',
            'description': f'''**Цель:** Ежедневная синхронизация команды {sprint_info} для отслеживания прогресса и выявления блокеров.
**Контекст:** Регулярная рутина по методологии Scrum/Agile.
**Ожидаемый результат:** Команда синхронизирована, блокеры выявлены и эскалированы.''',
            'deliverables': '''- [ ] Проведён ежедневный стендап (15 минут)
- [ ] Обновлены статусы задач в GitHub Projects
- [ ] Блокеры зафиксированы и назначены ответственные для их решения''',
            'participants': 'Вся команда разработки и дизайна, техлид',
            'metrics': '- Каждый участник озвучил прогресс, планы и блокеры.\n- Статусы задач актуализированы.\n- Новые блокеры зафиксированы в Issues при необходимости.',
            'labels': ['type: management', 'component: infrastructure', 'priority: high', 'status: backlog']
        },
        
        'retrospective': {
            'category': 'Процессы и улучшения (Process Improvement)',
            'description': f'''**Цель:** Провести ретроспективу {sprint_info}, проанализировать процессы и выявить точки улучшения.
**Контекст:** Завершение итерационного цикла разработки.
**Ожидаемый результат:** Список конкретных action items по улучшению рабочих процессов.''',
            'deliverables': '''- [ ] Проведена встреча ретроспективы (Sprint Retrospective)
- [ ] Собраны feedbacks от всех участников команды
- [ ] Сформирован список улучшений (What went well/What to improve)
- [ ] Определены конкретные action items с ответственными и сроками''',
            'participants': 'Вся команда (11 разработчиков + 4 дизайнера), техлид, фасилитатор',
            'metrics': '- Каждый участник высказался.\n- Созданы Issues для action items по улучшению процессов.\n- Команда договорилась об изменениях в следующем спринте.',
            'labels': ['type: management', 'component: infrastructure', 'priority: high', 'status: backlog']
        },
        
        'progress_report': {
            'category': 'Анализ и отчётность (Analytics)',
            'description': f'''**Цель:** Подготовить отчёт о прогрессе {sprint_info} для стейкхолдеров.
**Контекст:** Необходимость прозрачности и информирования заинтересованных сторон.
**Ожидаемый результат:** Профессиональный отчёт, демонстрирующий прогресс, риски и планы.''',
            'deliverables': '''- [ ] Собраны метрики спринта (velocity, completion rate, burndown)
- [ ] Подготовлен презентационный материал/отчёт
- [ ] Проведена демонстрация результатов (Sprint Review)
- [ ] Получен feedback от стейкхолдеров''',
            'participants': 'Тимлид, продакт, стейкхолдеры (преподаватель/заказчик)',
            'metrics': '- Отчёт создан и представлен.\n- Стейкхолдеры информированы о прогрессе и планах.\n- Feedback учтён в планировании следующего спринта.',
            'labels': ['type: management', 'component: infrastructure', 'priority: medium', 'status: backlog']
        },
        
        'risk_management': {
            'category': 'Риск-менеджмент (Risk Management)',
            'description': f'''**Цель:** Выявить и проанализировать риски {sprint_info}, разработать mitigation plan.
**Контекст:** Проактивное управление потенциальными проблемами проекта.
**Ожидаемый результат:** Документ с идентифицированными рисками, их оценкой и планами минимизации.''',
            'deliverables': '''- [ ] Проведён мозговой штурм по идентификации рисков
- [ ] Риски оценены по вероятности и влиянию (риск-матрица)
- [ ] Разработаны mitigation strategies для ключевых рисков
- [ ] Назначены ответственные за мониторинг рисков''',
            'participants': 'Тимлид, техлид, продакт, старшие разработчики',
            'metrics': '- Риски задокументированы и отслеживаются.\n- Для high-priority рисков есть чёткие планы действий.\n- Команда осведомлена о ключевых рисках.',
            'labels': ['type: management', 'component: infrastructure', 'priority: high', 'status: backlog']
        }
    }
    
    if task_type not in templates:
        print(f"❌ Неизвестный тип задачи. Доступные: {', '.join(templates.keys())}")
        return False
    
    template = templates[task_type]
    
    # Формируем тело задачи
    body_lines = []
    
    # Спринт/Этап
    body_lines.append(f"### Спринт / Этап / Веха")
    body_lines.append(sprint_info)
    body_lines.append("")
    
    # Категория задачи
    body_lines.append(f"### Категория задачи")
    body_lines.append(template['category'])
    body_lines.append("")
    
    # Описание
    body_lines.append(f"### Описание задачи и контекст")
    body_lines.append(template['description'])
    body_lines.append("")
    
    # Ожидаемые результаты
    body_lines.append(f"### Ожидаемые результаты / Деливераблы")
    body_lines.append(template['deliverables'])
    body_lines.append("")
    
    # Участники
    body_lines.append(f"### Участники / Заинтересованные стороны")
    body_lines.append(template['participants'])
    body_lines.append("")
    
    # Метрики успеха
    body_lines.append(f"### Метрики успеха / Критерии завершения")
    body_lines.append(template['metrics'])
    body_lines.append("")
    
    # Дедлайн (если указан)
    if 'deadline' in kwargs:
        body_lines.append(f"### Дедлайн")
        body_lines.append(kwargs['deadline'])
        body_lines.append("")
    
    # Дополнительные поля
    if 'additional_info' in kwargs:
        body_lines.append(f"### Дополнительная информация")
        body_lines.append(kwargs['additional_info'])
        body_lines.append("")
    
    body = "\n".join(body_lines)
    
    # Собираем команду gh
    cmd = [
        'issue', 'create',
        '--title', f"[MANAGER] {title}",
        '--body', body,
        '--template', 'manager_task.yml'
    ]
    
    # Добавляем лейблы
    for label in template['labels']:
        cmd.extend(['--label', label])
    
    # Добавляем дополнительные лейблы из kwargs
    if 'extra_labels' in kwargs:
        for label in kwargs['extra_labels']:
            cmd.extend(['--label', label])
    
    # Назначение (если указано)
    if 'assignee' in kwargs:
        cmd.extend(['--assignee', kwargs['assignee']])
    
    print(f"📝 Создаю задачу: {title}")
    print(f"   Тип: {task_type}")
    print(f"   Спринт: {sprint_info}")
    
    # Выполняем команду
    success = run_gh_command(cmd, capture_output=False)
    
    if success:
        print(f"✅ Менеджерская задача успешно создана!")
        return True
    else:
        print(f"❌ Не удалось создать задачу")
        return False

def calculate_sprint_dates(sprint_number=1):
    """Рассчитывает даты спринта (пример)."""
    # Настройте под ваш график спринтов
    start_date = datetime.now()
    end_date = start_date + timedelta(days=13)  # 2-недельный спринт
    return {
        'number': sprint_number,
        'start': start_date.strftime('%d.%m.%Y'),
        'end': end_date.strftime('%d.%m.%Y'),
        'display': f'Спринт #{sprint_number} ({start_date.strftime("%d.%m")}-{end_date.strftime("%d.%m.%Y")})'
    }

def main():
    """Основная функция."""
    print("\n" + "="*60)
    print("   🚀 АВТОМАТИЗАЦИЯ МЕНЕДЖЕРСКИХ ЗАДАЧ CELL-EVOLUTION")
    print("="*60)
    
    # Проверяем аутентификацию GitHub CLI
    auth_check = run_gh_command(['auth', 'status'])
    if not auth_check:
        print("\n❌ Требуется аутентификация в GitHub CLI.")
        print("   Выполните: gh auth login")
        return
    
    sprint_info = calculate_sprint_dates(1)
    
    print(f"\n📅 Текущий спринт: {sprint_info['display']}")
    print("\n📋 Доступные типы менеджерских задач:")
    print("   1. Планирование спринта (sprint_planning)")
    print("   2. Ежедневный стендап (daily_standup)")
    print("   3. Ретроспектива (retrospective)")
    print("   4. Отчёт о прогрессе (progress_report)")
    print("   5. Управление рисками (risk_management)")
    print("   6. Произвольная задача (custom)")
    
    choice = input("\n🎯 Выберите тип задачи (1-6 или название): ").strip()
    
    task_types = {
        '1': 'sprint_planning',
        '2': 'daily_standup',
        '3': 'retrospective',
        '4': 'progress_report',
        '5': 'risk_management',
        '6': 'custom'
    }
    
    task_type = task_types.get(choice, choice)
    
    if task_type == 'custom':
        title = input("Введите заголовок задачи: ").strip()
        sprint = input(f"Спринт/Этап [{sprint_info['display']}]: ").strip() or sprint_info['display']
        category = input("Категория задачи: ").strip()
        
        print("\n✏️  Введите описание задачи (Ctrl+D для завершения):")
        description_lines = []
        while True:
            try:
                line = input()
                description_lines.append(line)
            except EOFError:
                break
        description = "\n".join(description_lines)
        
        # Создаём кастомную задачу через прямой вызов gh
        cmd = [
            'issue', 'create',
            '--title', f"[MANAGER] {title}",
            '--body', f"### Спринт / Этап / Веха\n{sprint}\n\n### Категория задачи\n{category}\n\n### Описание задачи и контекст\n{description}",
            '--template', 'manager_task.yml',
            '--label', 'type: management',
            '--label', 'component: infrastructure',
            '--label', 'status: backlog'
        ]
        
        assignee = input("Назначить на (логин GitHub, Enter чтобы пропустить): ").strip()
        if assignee:
            cmd.extend(['--assignee', assignee])
        
        run_gh_command(cmd, capture_output=False)
        
    else:
        # Используем шаблон
        if task_type not in ['sprint_planning', 'daily_standup', 'retrospective', 'progress_report', 'risk_management']:
            print("❌ Неверный тип задачи")
            return
        
        # Автогенерация заголовков
        titles = {
            'sprint_planning': f'Планирование {sprint_info["display"]}',
            'daily_standup': f'Ежедневный стендап {sprint_info["display"]}',
            'retrospective': f'Ретроспектива {sprint_info["display"]}',
            'progress_report': f'Отчёт о прогрессе {sprint_info["display"]}',
            'risk_management': f'Анализ рисков {sprint_info["display"]}'
        }
        
        title = titles[task_type]
        
        # Дополнительные параметры
        assignee = input(f"Назначить на (логин GitHub, Enter для {task_type}): ").strip()
        extra_labels = []
        
        if task_type == 'sprint_planning':
            deadline = input(f"Дедлайн планирования [{sprint_info['start']}]: ").strip() or sprint_info['start']
            create_manager_task(
                task_type=task_type,
                title=title,
                sprint_info=sprint_info['display'],
                assignee=assignee or 'тимлид',
                deadline=deadline
            )
        else:
            create_manager_task(
                task_type=task_type,
                title=title,
                sprint_info=sprint_info['display'],
                assignee=assignee
            )

if __name__ == "__main__":
    main()
