"""
Terminal To-Do List Manager
Управление задачами в терминале с сохранением данных
"""

import os
import json
import sys
import datetime
from enum import Enum
from typing import List, Dict, Optional
import getpass
from dataclasses import dataclass, asdict
from pathlib import Path

class Priority(Enum):
    LOW = "Низкий"
    MEDIUM = "Средний"
    HIGH = "Высокий"
    URGENT = "Срочный"

class Status(Enum):
    TODO = "К выполнению"
    IN_PROGRESS = "В процессе"
    DONE = "Выполнено"
    CANCELLED = "Отменено"

@dataclass
class Task:
    id: int
    title: str
    description: str
    priority: Priority
    status: Status
    created_at: str
    due_date: Optional[str] = None
    tags: List[str] = None
    
    def __post_init__(self):
        if self.tags is None:
            self.tags = []
    
    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'priority': self.priority.value,
            'status': self.status.value,
            'created_at': self.created_at,
            'due_date': self.due_date,
            'tags': self.tags
        }

class TodoApp:
    def __init__(self, data_file: str = "tasks.json"):
        self.data_file = data_file
        self.tasks: List[Task] = []
        self.current_id = 1
        self.load_tasks()
        
        # Цвета для терминала
        self.colors = {
            'header': '\033[95m',
            'blue': '\033[94m',
            'cyan': '\033[96m',
            'green': '\033[92m',
            'yellow': '\033[93m',
            'red': '\033[91m',
            'bold': '\033[1m',
            'underline': '\033[4m',
            'end': '\033[0m'
        }
        
        # Символы для прогресс-бара
        self.progress_chars = ['░', '▒', '▓', '█']
    
    def load_tasks(self):
        """Загрузка задач из файла"""
        if Path(self.data_file).exists():
            try:
                with open(self.data_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    for task_data in data:
                        task = Task(
                            id=task_data['id'],
                            title=task_data['title'],
                            description=task_data['description'],
                            priority=Priority(task_data['priority']),
                            status=Status(task_data['status']),
                            created_at=task_data['created_at'],
                            due_date=task_data.get('due_date'),
                            tags=task_data.get('tags', [])
                        )
                        self.tasks.append(task)
                        if task.id >= self.current_id:
                            self.current_id = task.id + 1
            except Exception as e:
                print(f"Ошибка загрузки задач: {e}")
    
    def save_tasks(self):
        """Сохранение задач в файл"""
        try:
            with open(self.data_file, 'w', encoding='utf-8') as f:
                json.dump([task.to_dict() for task in self.tasks], f, 
                         ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"Ошибка сохранения задач: {e}")
    
    def clear_screen(self):
        """Очистка экрана терминала"""
        os.system('cls' if os.name == 'nt' else 'clear')
    
    def print_header(self):
        """Отображение заголовка"""
        self.clear_screen()
        header = """
╔══════════════════════════════════════════════════════════╗
║                🚀 TERMINAL TASK MANAGER 🚀               ║
║                Управление задачами v1.0                  ║
╚══════════════════════════════════════════════════════════╝
        """
        print(f"{self.colors['cyan']}{header}{self.colors['end']}")
    
    def print_menu(self):
        """Отображение меню"""
        menu = f"""
{self.colors['bold']}МЕНЮ:{self.colors['end']}

{self.colors['green']}[1]{self.colors['end']} 📋 Показать все задачи
{self.colors['green']}[2]{self.colors['end']} ➕ Добавить задачу
{self.colors['green']}[3]{self.colors['end']} ✏️  Редактировать задачу
{self.colors['green']}[4]{self.colors['end']} ✅ Завершить задачу
{self.colors['green']}[5]{self.colors['end']} ❌ Удалить задачу
{self.colors['green']}[6]{self.colors['end']} 🔍 Поиск задач
{self.colors['green']}[7]{self.colors['end']} 📊 Статистика
{self.colors['green']}[8]{self.colors['end']} 🏷️  Управление тегами
{self.colors['green']}[9]{self.colors['end']} 💾 Сохранить и выйти
{self.colors['green']}[0]{self.colors['end']} 🚪 Выйти без сохранения

{self.colors['yellow']}Выберите действие:{self.colors['end']} """
        return input(menu)
    
    def add_task(self):
        """Добавление новой задачи"""
        self.print_header()
        print(f"{self.colors['bold']}➕ ДОБАВЛЕНИЕ НОВОЙ ЗАДАЧИ{self.colors['end']}\n")
        
        title = input(f"{self.colors['blue']}Название задачи: {self.colors['end']}").strip()
        if not title:
            print(f"{self.colors['red']}Название не может быть пустым!{self.colors['end']}")
            input("Нажмите Enter для продолжения...")
            return
        
        description = input(f"{self.colors['blue']}Описание: {self.colors['end']}").strip()
        
        print(f"\n{self.colors['blue']}Приоритет:{self.colors['end']}")
        for i, priority in enumerate(Priority, 1):
            print(f"  [{i}] {priority.value}")
        
        try:
            priority_choice = int(input(f"\nВыберите приоритет (1-{len(Priority)}): "))
            priority = list(Priority)[priority_choice - 1]
        except:
            priority = Priority.MEDIUM
        
        due_date = input(f"\n{self.colors['blue']}Срок выполнения (ДД.ММ.ГГГГ или Enter): {self.colors['end']}").strip()
        
        tags_input = input(f"{self.colors['blue']}Теги (через запятую): {self.colors['end']}").strip()
        tags = [tag.strip() for tag in tags_input.split(',') if tag.strip()]
        
        task = Task(
            id=self.current_id,
            title=title,
            description=description,
            priority=priority,
            status=Status.TODO,
            created_at=datetime.datetime.now().strftime("%d.%m.%Y %H:%M"),
            due_date=due_date if due_date else None,
            tags=tags
        )
        
        self.tasks.append(task)
        self.current_id += 1
        
        print(f"\n{self.colors['green']}✅ Задача успешно добавлена!{self.colors['end']}")
        input("Нажмите Enter для продолжения...")
    
    def show_tasks(self, tasks_to_show=None):
        """Отображение списка задач"""
        tasks = tasks_to_show if tasks_to_show else self.tasks
        
        if not tasks:
            print(f"{self.colors['yellow']}📭 Список задач пуст{self.colors['end']}")
            input("Нажмите Enter для продолжения...")
            return
        
        print(f"\n{self.colors['bold']}📋 СПИСОК ЗАДАЧ ({len(tasks)}):{self.colors['end']}\n")
        
        for task in tasks:
            # Цвет статуса
            status_color = self.colors['green'] if task.status == Status.DONE else \
                          self.colors['yellow'] if task.status == Status.IN_PROGRESS else \
                          self.colors['red'] if task.status == Status.CANCELLED else \
                          self.colors['blue']
            
            # Цвет приоритета
            priority_color = self.colors['red'] if task.priority == Priority.URGENT else \
                            self.colors['yellow'] if task.priority == Priority.HIGH else \
                            self.colors['green'] if task.priority == Priority.MEDIUM else \
                            self.colors['blue']
            
            print(f"{self.colors['bold']}┌─ ЗАДАЧА #{task.id}{self.colors['end']}")
            print(f"│ {self.colors['bold']}Название:{self.colors['end']} {task.title}")
            print(f"│ {self.colors['bold']}Описание:{self.colors['end']} {task.description}")
            print(f"│ {self.colors['bold']}Статус:{self.colors['end']} {status_color}{task.status.value}{self.colors['end']}")
            print(f"│ {self.colors['bold']}Приоритет:{self.colors['end']} {priority_color}{task.priority.value}{self.colors['end']}")
            print(f"│ {self.colors['bold']}Создана:{self.colors['end']} {task.created_at}")
            if task.due_date:
                print(f"│ {self.colors['bold']}Срок:{self.colors['end']} {task.due_date}")
            if task.tags:
                print(f"│ {self.colors['bold']}Теги:{self.colors['end']} {', '.join(task.tags)}")
            print(f"└{'─' * 40}\n")
    
    def edit_task(self):
        """Редактирование задачи"""
        if not self.tasks:
            print(f"{self.colors['yellow']}Нет задач для редактирования{self.colors['end']}")
            input("Нажмите Enter для продолжения...")
            return
        
        self.show_tasks()
        try:
            task_id = int(input(f"\n{self.colors['yellow']}Введите ID задачи для редактирования: {self.colors['end']}"))
            task = next((t for t in self.tasks if t.id == task_id), None)
            
            if not task:
                print(f"{self.colors['red']}Задача не найдена!{self.colors['end']}")
                input("Нажмите Enter для продолжения...")
                return
            
            print(f"\n{self.colors['bold']}Редактирование задачи #{task.id}{self.colors['end']}")
            print("(Оставьте поле пустым, чтобы не изменять)\n")
            
            new_title = input(f"Название [{task.title}]: ").strip()
            if new_title:
                task.title = new_title
            
            new_desc = input(f"Описание [{task.description}]: ").strip()
            if new_desc:
                task.description = new_desc
            
            print(f"\nТекущий статус: {task.status.value}")
            print("Выберите новый статус:")
            for i, status in enumerate(Status, 1):
                print(f"  [{i}] {status.value}")
            
            status_input = input(f"\nНовый статус (1-{len(Status)}): ").strip()
            if status_input:
                try:
                    task.status = list(Status)[int(status_input) - 1]
                except:
                    pass
            
            print(f"{self.colors['green']}✅ Задача обновлена!{self.colors['end']}")
            
        except ValueError:
            print(f"{self.colors['red']}Неверный ID!{self.colors['end']}")
        
        input("Нажмите Enter для продолжения...")
    
    def delete_task(self):
        """Удаление задачи"""
        if not self.tasks:
            print(f"{self.colors['yellow']}Нет задач для удаления{self.colors['end']}")
            input("Нажмите Enter для продолжения...")
            return
        
        self.show_tasks()
        try:
            task_id = int(input(f"\n{self.colors['red']}Введите ID задачи для удаления: {self.colors['end']}"))
            task = next((t for t in self.tasks if t.id == task_id), None)
            
            if task:
                confirm = input(f"{self.colors['red']}Удалить задачу '{task.title}'? (y/N): {self.colors['end']}")
                if confirm.lower() == 'y':
                    self.tasks.remove(task)
                    print(f"{self.colors['green']}✅ Задача удалена!{self.colors['end']}")
            else:
                print(f"{self.colors['red']}Задача не найдена!{self.colors['end']}")
        except ValueError:
            print(f"{self.colors['red']}Неверный ID!{self.colors['end']}")
        
        input("Нажмите Enter для продолжения...")
    
    def search_tasks(self):
        """Поиск задач"""
        if not self.tasks:
            print(f"{self.colors['yellow']}Нет задач для поиска{self.colors['end']}")
            input("Нажмите Enter для продолжения...")
            return
        
        print(f"\n{self.colors['bold']}🔍 ПОИСК ЗАДАЧ{self.colors['end']}\n")
        print("[1] По названию")
        print("[2] По тегу")
        print("[3] По статусу")
        print("[4] По приоритету")
        
        choice = input(f"\n{self.colors['yellow']}Выберите тип поиска: {self.colors['end']}").strip()
        
        results = []
        if choice == '1':
            keyword = input("Введите ключевое слово: ").lower()
            results = [t for t in self.tasks if keyword in t.title.lower()]
        elif choice == '2':
            tag = input("Введите тег: ").lower()
            results = [t for t in self.tasks if tag in [tg.lower() for tg in t.tags]]
        elif choice == '3':
            for i, status in enumerate(Status, 1):
                print(f"  [{i}] {status.value}")
            try:
                status_idx = int(input(f"\nВыберите статус (1-{len(Status)}): ")) - 1
                status = list(Status)[status_idx]
                results = [t for t in self.tasks if t.status == status]
            except:
                pass
        elif choice == '4':
            for i, priority in enumerate(Priority, 1):
                print(f"  [{i}] {priority.value}")
            try:
                priority_idx = int(input(f"\nВыберите приоритет (1-{len(Priority)}): ")) - 1
                priority = list(Priority)[priority_idx]
                results = [t for t in self.tasks if t.priority == priority]
            except:
                pass
        
        if results:
            self.show_tasks(results)
        else:
            print(f"{self.colors['yellow']}Задачи не найдены{self.colors['end']}")
        
        input("Нажмите Enter для продолжения...")
    
    def show_stats(self):
        """Показать статистику"""
        total = len(self.tasks)
        if total == 0:
            print(f"{self.colors['yellow']}Нет данных для статистики{self.colors['end']}")
            input("Нажмите Enter для продолжения...")
            return
        
        done = len([t for t in self.tasks if t.status == Status.DONE])
        in_progress = len([t for t in self.tasks if t.status == Status.IN_PROGRESS])
        todo = len([t for t in self.tasks if t.status == Status.TODO])
        
        print(f"\n{self.colors['bold']}📊 СТАТИСТИКА{self.colors['end']}\n")
        print(f"Всего задач: {total}")
        print(f"Выполнено: {done} ({done/total*100:.1f}%)")
        print(f"В процессе: {in_progress} ({in_progress/total*100:.1f}%)")
        print(f"К выполнению: {todo} ({todo/total*100:.1f}%)")
        
        # Прогресс-бар
        progress = done / total if total > 0 else 0
        bar_length = 30
        filled = int(bar_length * progress)
        bar = '█' * filled + '░' * (bar_length - filled)
        
        print(f"\n{self.colors['bold']}Общий прогресс:{self.colors['end']}")
        print(f"[{bar}] {progress*100:.1f}%")
        
        input("\nНажмите Enter для продолжения...")
    
    def manage_tags(self):
        """Управление тегами"""
        all_tags = set()
        for task in self.tasks:
            all_tags.update(task.tags)
        
        if not all_tags:
            print(f"{self.colors['yellow']}Теги не найдены{self.colors['end']}")
            input("Нажмите Enter для продолжения...")
            return
        
        print(f"\n{self.colors['bold']}🏷️  ВСЕ ТЕГИ ({len(all_tags)}):{self.colors['end']}\n")
        for tag in sorted(all_tags):
            count = sum(1 for t in self.tasks if tag in t.tags)
            print(f"  #{tag}: {count} задач")
        
        input("\nНажмите Enter для продолжения...")
    
    def complete_task(self):
        """Завершение задачи"""
        if not self.tasks:
            print(f"{self.colors['yellow']}Нет задач для завершения{self.colors['end']}")
            input("Нажмите Enter для продолжения...")
            return
        
        # Показать только незавершенные задачи
        active_tasks = [t for t in self.tasks if t.status != Status.DONE]
        if not active_tasks:
            print(f"{self.colors['yellow']}Все задачи уже выполнены!{self.colors['end']}")
            input("Нажмите Enter для продолжения...")
            return
        
        self.show_tasks(active_tasks)
        
        try:
            task_id = int(input(f"\n{self.colors['yellow']}Введите ID задачи для завершения: {self.colors['end']}"))
            task = next((t for t in self.tasks if t.id == task_id), None)
            
            if task:
                task.status = Status.DONE
                print(f"{self.colors['green']}✅ Задача '{task.title}' выполнена!{self.colors['end']}")
            else:
                print(f"{self.colors['red']}Задача не найдена!{self.colors['end']}")
        except ValueError:
            print(f"{self.colors['red']}Неверный ID!{self.colors['end']}")
        
        input("Нажмите Enter для продолжения...")
    
    def run(self):
        """Запуск основного цикла приложения"""
        while True:
            self.print_header()
            choice = self.print_menu()
            
            if choice == '1':
                self.print_header()
                self.show_tasks()
                input("Нажмите Enter для продолжения...")
            elif choice == '2':
                self.add_task()
            elif choice == '3':
                self.print_header()
                self.edit_task()
            elif choice == '4':
                self.print_header()
                self.complete_task()
            elif choice == '5':
                self.print_header()
                self.delete_task()
            elif choice == '6':
                self.print_header()
                self.search_tasks()
            elif choice == '7':
                self.print_header()
                self.show_stats()
            elif choice == '8':
                self.print_header()
                self.manage_tags()
            elif choice == '9':
                self.save_tasks()
                print(f"\n{self.colors['green']}✅ Данные сохранены. До свидания!{self.colors['end']}")
                break
            elif choice == '0':
                print(f"\n{self.colors['yellow']}⚠️  Изменения не сохранены. Выход...{self.colors['end']}")
                break
            else:
                print(f"{self.colors['red']}Неверный выбор!{self.colors['end']}")
                input("Нажмите Enter для продолжения...")

def main():
    """Точка входа в приложение"""
    app = TodoApp()
    
    # Проверка на первый запуск
    if not Path(app.data_file).exists():
        app.print_header()
        print(f"{app.colors['cyan']}👋 Добро пожаловать в Task Manager!{app.colors['end']}")
        print("Это ваш первый запуск. Начните с добавления задач.\n")
        input("Нажмите Enter для продолжения...")
    
    try:
        app.run()
    except KeyboardInterrupt:
        print(f"\n\n{app.colors['yellow']}⚠️  Приложение прервано пользователем{app.colors['end']}")
        save = input(f"{app.colors['yellow']}Сохранить изменения перед выходом? (y/N): {app.colors['end']}")
        if save.lower() == 'y':
            app.save_tasks()
            print(f"{app.colors['green']}✅ Данные сохранены{app.colors['end']}")
    except Exception as e:
        print(f"{app.colors['red']}⚠️  Произошла ошибка: {e}{app.colors['end']}")
        input("Нажмите Enter для выхода...")

if __name__ == "__main__":
    main()