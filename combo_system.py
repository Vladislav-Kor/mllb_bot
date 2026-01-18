"""
Система комбо для Хаябуса
"""

import json
import time
from dataclasses import dataclass, field
from typing import List, Dict, Optional
from pathlib import Path

@dataclass
class ComboSequence:
    """Последовательность комбо"""
    name: str
    description: str
    skills: List[str]  # Последовательность скиллов
    timing: List[float]  # Тайминги между скиллами
    condition: Optional[str] = None  # Условие применения
    priority: int = 5  # Приоритет (1-10)
    
    # Статистика
    successes: int = 0
    failures: int = 0
    total_executions: int = 0
    avg_execution_time: float = 0.0
    last_used: float = 0.0
    
    @property
    def success_rate(self) -> float:
        """Процент успешных выполнений"""
        if self.total_executions == 0:
            return 0.0
        return self.successes / self.total_executions
    
    def update_success(self, success: bool, execution_time: float = 0.0):
        """Обновить статистику после выполнения"""
        self.total_executions += 1
        
        if success:
            self.successes += 1
        else:
            self.failures += 1
        
        # Обновляем среднее время выполнения
        if execution_time > 0:
            if self.avg_execution_time == 0:
                self.avg_execution_time = execution_time
            else:
                # Скользящее среднее
                self.avg_execution_time = (self.avg_execution_time * (self.total_executions - 1) + execution_time) / self.total_executions
        
        self.last_used = time.time()
    
    def to_dict(self) -> Dict:
        """Преобразовать в словарь"""
        return {
            'name': self.name,
            'description': self.description,
            'skills': self.skills,
            'timing': self.timing,
            'condition': self.condition,
            'priority': self.priority,
            'successes': self.successes,
            'failures': self.failures,
            'total_executions': self.total_executions,
            'success_rate': self.success_rate,
            'avg_execution_time': self.avg_execution_time,
            'last_used': self.last_used
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'ComboSequence':
        """Создать из словаря"""
        combo = cls(
            name=data['name'],
            description=data['description'],
            skills=data['skills'],
            timing=data['timing'],
            condition=data.get('condition'),
            priority=data.get('priority', 5)
        )
        
        # Восстанавливаем статистику
        combo.successes = data.get('successes', 0)
        combo.failures = data.get('failures', 0)
        combo.total_executions = data.get('total_executions', 0)
        combo.avg_execution_time = data.get('avg_execution_time', 0.0)
        combo.last_used = data.get('last_used', 0.0)
        
        return combo

class ComboSystem:
    """Система управления комбо"""
    
    def __init__(self, data_dir: str = "data"):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(exist_ok=True)
        
        self.combos: Dict[str, ComboSequence] = {}
        
        # Загружаем стандартные комбо
        self.load_default_combos()
        
        # Загружаем сохраненные комбо
        self.load_combos()
        
        print(f"💫 Система комбо инициализирована: {len(self.combos)} комбо")
    
    def load_default_combos(self):
        """Загрузить стандартные комбо"""
        default_combos = [
            ComboSequence(
                name="QUICK GANK",
                description="Быстрый ганг на ослабленного врага",
                skills=['s2', 's1', 's3', 'attack'],
                timing=[0.1, 0.2, 0.3, 0.1],
                priority=8
            ),
            ComboSequence(
                name="ULTIMATE BURST",
                description="Полное комбо с ультимейтом для убийства",
                skills=['s2', 's1', 'ult', 's3', 'attack'],
                timing=[0.1, 0.2, 0.3, 0.2, 0.1],
                priority=9
            ),
            ComboSequence(
                name="ESCAPE COMBO",
                description="Комбо для побега из опасной ситуации",
                skills=['s2', 's2', 's2'],  # Многократное использование теней для побега
                timing=[0.1, 0.1, 0.2],
                priority=10
            ),
            ComboSequence(
                name="LANE FARM",
                description="Эффективная очистка линии миньонов",
                skills=['s1', 's2', 'attack', 'attack'],
                timing=[0.2, 0.1, 0.1, 0.1],
                priority=7
            ),
            ComboSequence(
                name="JUNGLE CLEAR",
                description="Быстрая очистка лагеря леса",
                skills=['s1', 's2', 'attack', 's3', 'attack'],
                timing=[0.2, 0.1, 0.2, 0.1, 0.1],
                priority=6
            ),
            ComboSequence(
                name="OBJECTIVE STEAL",
                description="Попытка украсть лорда/черепаху",
                skills=['s2', 'ult', 's1', 's3', 'attack'],
                timing=[0.1, 0.3, 0.1, 0.1, 0.1],
                priority=8
            ),
        ]
        
        for combo in default_combos:
            self.combos[combo.name] = combo
    
    def get_combo(self, name: str) -> Optional[ComboSequence]:
        """Получить комбо по имени"""
        return self.combos.get(name)
    
    def get_best_combo_for_situation(self, situation: str) -> Optional[ComboSequence]:
        """Получить лучшее комбо для ситуации"""
        situation_map = {
            'gank': ['QUICK GANK', 'ULTIMATE BURST'],
            'farm': ['LANE FARM', 'JUNGLE CLEAR'],
            'escape': ['ESCAPE COMBO'],
            'objective': ['OBJECTIVE STEAL', 'ULTIMATE BURST'],
            'teamfight': ['ULTIMATE BURST']
        }
        
        if situation not in situation_map:
            return None
        
        # Выбираем комбо с наивысшим приоритетом и успешностью
        available_combos = []
        for combo_name in situation_map[situation]:
            combo = self.combos.get(combo_name)
            if combo:
                # Скор = приоритет * успешность
                score = combo.priority * combo.success_rate if combo.total_executions > 0 else combo.priority
                available_combos.append((score, combo))
        
        if not available_combos:
            return None
        
        # Сортируем по скору
        available_combos.sort(key=lambda x: x[0], reverse=True)
        return available_combos[0][1]
    
    def add_combo(self, combo: ComboSequence):
        """Добавить новое комбо"""
        self.combos[combo.name] = combo
        print(f"➕ Добавлено комбо: {combo.name}")
    
    def remove_combo(self, name: str):
        """Удалить комбо"""
        if name in self.combos:
            del self.combos[name]
            print(f"➖ Удалено комбо: {name}")
    
    def get_all_combos(self) -> List[ComboSequence]:
        """Получить все комбо"""
        return list(self.combos.values())
    
    def get_combo_stats(self) -> Dict:
        """Получить статистику комбо"""
        stats = {}
        for name, combo in self.combos.items():
            stats[name] = {
                'success_rate': combo.success_rate,
                'total_executions': combo.total_executions,
                'avg_time': combo.avg_execution_time,
                'priority': combo.priority,
                'last_used': combo.last_used
            }
        
        return stats
    
    def save_combos(self, filename: str = None):
        """Сохранить комбо в файл"""
        if filename is None:
            filename = self.data_dir / "combos.json"
        
        try:
            data = {}
            for name, combo in self.combos.items():
                data[name] = combo.to_dict()
            
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            
            print(f"💾 Комбо сохранены в {filename}")
            return True
            
        except Exception as e:
            print(f"❌ Ошибка сохранения комбо: {e}")
            return False
    
    def load_combos(self, filename: str = None) -> int:
        """Загрузить комбо из файла"""
        if filename is None:
            filename = self.data_dir / "combos.json"
        
        try:
            if not filename.exists():
                print(f"📂 Файл комбо не найден: {filename}")
                return 0
            
            with open(filename, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            loaded_count = 0
            for name, combo_data in data.items():
                try:
                    combo = ComboSequence.from_dict(combo_data)
                    self.combos[name] = combo
                    loaded_count += 1
                except Exception as e:
                    print(f"⚠️ Ошибка загрузки комбо {name}: {e}")
            
            print(f"📂 Загружено {loaded_count} комбо из {filename}")
            return loaded_count
            
        except Exception as e:
            print(f"❌ Ошибка загрузки комбо: {e}")
            return 0
    
    def reset_stats(self):
        """Сбросить статистику комбо"""
        for combo in self.combos.values():
            combo.successes = 0
            combo.failures = 0
            combo.total_executions = 0
            combo.avg_execution_time = 0.0
        
        print("🔄 Статистика комбо сброшена")
    
    def print_stats(self):
        """Вывести статистику комбо"""
        print("\n📊 СТАТИСТИКА КОМБО:")
        print("=" * 50)
        
        for name, combo in sorted(self.combos.items(), 
                                 key=lambda x: x[1].success_rate, 
                                 reverse=True):
            if combo.total_executions > 0:
                print(f"{name}:")
                print(f"  Успешность: {combo.success_rate:.1%} ({combo.successes}/{combo.total_executions})")
                print(f"  Среднее время: {combo.avg_execution_time:.2f}с")
                print(f"  Приоритет: {combo.priority}/10")
                print(f"  Последнее использование: {time.strftime('%H:%M:%S', time.localtime(combo.last_used)) if combo.last_used > 0 else 'никогда'}")
                print()