"""
Вспомогательные функции для бота
"""

import math
import time
import random
from typing import Tuple, List, Dict, Any
import json
import os
from datetime import datetime

def calculate_distance(pos1: Tuple[int, int], pos2: Tuple[int, int]) -> float:
    """Расстояние между двумя точками"""
    return math.sqrt((pos1[0] - pos2[0])**2 + (pos1[1] - pos2[1])**2)

def calculate_angle(from_pos: Tuple[int, int], to_pos: Tuple[int, int]) -> float:
    """Угол от точки from_pos к точке to_pos"""
    dx = to_pos[0] - from_pos[0]
    dy = to_pos[1] - from_pos[1]
    return math.degrees(math.atan2(dy, dx)) % 360

def get_screen_center() -> Tuple[int, int]:
    """Получение центра экрана"""
    import pyautogui
    screen_width, screen_height = pyautogui.size()
    return (screen_width // 2, screen_height // 2)

def get_screen_size() -> Tuple[int, int]:
    """Получение размера экрана"""
    import pyautogui
    return pyautogui.size()

def format_time(seconds: int) -> str:
    """Форматирование времени"""
    minutes = seconds // 60
    secs = seconds % 60
    return f"{minutes:02d}:{secs:02d}"

def print_banner(text: str, width: int = 60):
    """Печать красивого баннера"""
    border = "=" * width
    print(f"\n{border}")
    print(f"{text.center(width)}")
    print(f"{border}")

def print_status(phase: str, level: int, gold: int, 
                health: int, kills: int, creeps: int, jungle: int = 0):
    """Печать статуса игры"""
    icons = {'early': '🌅', 'mid': '🌞', 'late': '🌙', 'endgame': '🏁'}
    icon = icons.get(phase, '❓')
    jungle_icon = '🌲' if jungle > 0 else '  '
    print(f"[{icon} Ур.{level} 💰{gold} ❤️{health}% ⚔️{kills} 👾{creeps} {jungle_icon}]")

def save_to_json(data: Any, filename: str) -> bool:
    """Сохранение данных в JSON файл"""
    try:
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False, default=str)
        return True
    except Exception as e:
        print(f"⚠️ Ошибка сохранения в {filename}: {e}")
        return False

def load_from_json(filename: str) -> Any:
    """Загрузка данных из JSON файла"""
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        return None
    except Exception as e:
        print(f"⚠️ Ошибка загрузки из {filename}: {e}")
        return None

def create_directory(directory: str):
    """Создание директории"""
    if not os.path.exists(directory):
        os.makedirs(directory)
        print(f"📁 Создана директория: {directory}")

def get_timestamp() -> str:
    """Получение временной метки"""
    return datetime.now().strftime("%Y%m%d_%H%M%S")

def clamp(value: float, min_val: float, max_val: float) -> float:
    """Ограничение значения в диапазоне"""
    return max(min_val, min(max_val, value))

def weighted_choice(choices: List[Any], weights: List[float]) -> Any:
    """Взвешенный случайный выбор"""
    total = sum(weights)
    r = random.uniform(0, total)
    upto = 0
    
    for choice, weight in zip(choices, weights):
        if upto + weight >= r:
            return choice
        upto += weight
    
    return choices[-1]

def calculate_safety_score(enemies_nearby: int, health: float, 
                          position: str) -> float:
    """Расчет показателя безопасности"""
    score = 1.0
    
    # Влияние врагов
    if enemies_nearby >= 3:
        score *= 0.3
    elif enemies_nearby == 2:
        score *= 0.6
    elif enemies_nearby == 1:
        score *= 0.8
    
    # Влияние здоровья
    if health < 30:
        score *= 0.4
    elif health < 50:
        score *= 0.7
    elif health < 70:
        score *= 0.9
    
    # Влияние позиции
    if position == "enemy_territory":
        score *= 0.5
    elif position == "jungle":
        score *= 0.8
    
    return clamp(score, 0.0, 1.0)

def debug_vision(objects: List[Any], message: str = ""):
    """Отладочный вывод для зрения"""
    if message:
        print(f"👁️ {message}")
    
    creep_count = sum(1 for obj in objects if getattr(obj, 'type', '') in ['creep', 'jungle'])
    enemy_count = sum(1 for obj in objects if getattr(obj, 'type', '') == 'hero' and getattr(obj, 'is_enemy', False))
    
    if creep_count > 0 or enemy_count > 0:
        print(f"   👾 Крипы: {creep_count} | ⚔️ Враги: {enemy_count}")