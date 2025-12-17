#!/usr/bin/env python3
"""
Визуальный редактор баланса игры
"""
import json
import tkinter as tk
from tkinter import ttk, messagebox
from pathlib import Path

class BalanceEditor:
    def __init__(self, root):
        self.root = root
        self.root.title("Cell Genesis - Balance Editor")
        self.root.geometry("1200x800")
        
        self.config_file = Path("assets/data/balance.json")
        self.data = self.load_data()
        
        self.setup_ui()
        self.load_values()
    
    def load_data(self):
        """Загрузить данные баланса"""
        if self.config_file.exists():
            with open(self.config_file, 'r') as f:
                return json.load(f)
        
        # Дефолтные значения
        return {
            "cell": {
                "base_energy": 100,
                "energy_consumption": {"movement": 0.1, "metabolism": 0.05},
                "size_multiplier": 1.0
            },
            "evolution": {
                "mutation_chance": 0.3,
                "max_traits": 5,
                "upgrade_costs": {"speed": 10, "vision": 15, "size": 20}
            },
            "environment": {
                "food_spawn_rate": 0.1,
                "toxin_spawn_rate": 0.01,
                "current_strength": 0.5
            }
        }
    
    def setup_ui(self):
        """Настроить интерфейс"""
        # Панель навигации
        nav_frame = ttk.Frame(self.root, padding=10)
        nav_frame.grid(row=0, column=0, sticky="nsw")
        
        categories = ["Клетка", "Эволюция", "Среда", "Питание", "Враги"]
        for i, category in enumerate(categories):
            btn = ttk.Button(nav_frame, text=category, 
                           command=lambda c=category: self.show_category(c))
            btn.grid(row=i, column=0, pady=5, sticky="ew")
        
        # Основная область
        self.main_frame = ttk.Frame(self.root, padding=20)
        self.main_frame.grid(row=0, column=1, sticky="nsew")
        
        # Панель управления
        control_frame = ttk.Frame(self.root, padding=10)
        control_frame.grid(row=1, column=0, columnspan=2, sticky="ew")
        
        ttk.Button(control_frame, text="💾 Сохранить", 
                  command=self.save_data).pack(side=tk.LEFT, padx=5)
        ttk.Button(control_frame, text="🔄 Сбросить", 
                  command=self.reset_data).pack(side=tk.LEFT, padx=5)
        ttk.Button(control_frame, text="📊 Экспорт", 
                  command=self.export_data).pack(side=tk.LEFT, padx=5)
        
        # Настройка сетки
        self.root.grid_columnconfigure(1, weight=1)
        self.root.grid_rowconfigure(0, weight=1)
    
    def show_category(self, category):
        """Показать выбранную категорию"""
        # Очистить основную область
        for widget in self.main_frame.winfo_children():
            widget.destroy()
        
        ttk.Label(self.main_frame, text=category, 
                 font=("Arial", 16, "bold")).pack(anchor="w", pady=10)
        
        # Создать поля для категории
        category_key = self.get_category_key(category)
        if category_key in self.data:
            self.create_editors(self.data[category_key], category_key)
    
    def create_editors(self, data, prefix="", row=1):
        """Рекурсивно создать редакторы"""
        for key, value in data.items():
            full_key = f"{prefix}.{key}" if prefix else key
            
            frame = ttk.Frame(self.main_frame)
            frame.pack(fill="x", pady=2)
            
            ttk.Label(frame, text=key, width=30, anchor="w").pack(side=tk.LEFT)
            
            if isinstance(value, (int, float)):
                var = tk.DoubleVar(value=value)
                scale = ttk.Scale(frame, from_=0, to=value*3 if value > 0 else 10, 
                                variable=var, orient=tk.HORIZONTAL)
                scale.pack(side=tk.LEFT, fill="x", expand=True, padx=10)
                
                entry = ttk.Entry(frame, textvariable=var, width=10)
                entry.pack(side=tk.LEFT)
                
                self.vars[full_key] = var
            elif isinstance(value, dict):
                # Рекурсивно для вложенных словарей
                self.create_editors(value, full_key, row)
            row += 1
    
    def load_values(self):
        """Загрузить значения в переменные"""
        self.vars = {}
        self.show_category("Клетка")
    
    def save_data(self):
        """Сохранить изменения"""
        for key, var in self.vars.items():
            keys = key.split(".")
            data = self.data
            for k in keys[:-1]:
                data = data[k]
            data[keys[-1]] = var.get()
        
        # Сохранить в файл
        with open(self.config_file, 'w') as f:
            json.dump(self.data, f, indent=2)
        
        messagebox.showinfo("Сохранено", "Баланс успешно сохранен!")
    
    def reset_data(self):
        """Сбросить к значениям по умолчанию"""
        if messagebox.askyesno("Сброс", "Сбросить все значения?"):
            self.data = self.load_data()
            self.load_values()
    
    def export_data(self):
        """Экспортировать в Python модуль"""
        py_file = Path("src/cell_genesis/utils/balance_config.py")
        
        with open(py_file, 'w') as f:
            f.write("# Auto-generated balance config\n\n")
            f.write("BALANCE = ")
            f.write(json.dumps(self.data, indent=4))
        
        messagebox.showinfo("Экспорт", f"Конфиг экспортирован в {py_file}")
    
    def get_category_key(self, category):
        """Преобразовать русское название в ключ"""
        mapping = {
            "Клетка": "cell",
            "Эволюция": "evolution",
            "Среда": "environment",
            "Питание": "food",
            "Враги": "enemies"
        }
        return mapping.get(category, category.lower())

if __name__ == "__main__":
    root = tk.Tk()
    editor = BalanceEditor(root)
    root.mainloop()
