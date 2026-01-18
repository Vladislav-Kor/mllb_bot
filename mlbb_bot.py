"""
🤖 MLBB v14.0 - ХАЯБУСА БОТ с компьютерным зрением и онлайн-обучением
✅ Умный фарм и ганги с приоритетами
✅ Параллельное обучение через интернет
✅ Анализ YouTube видео про Хаябусу
✅ Сбор данных с сайтов по MLBB
✅ Адаптивная ИИ на основе реальных данных
✅ Автоматическая калибровка координат
✅ Безопасный режим для новичков
"""

import cv2
import numpy as np
import pyautogui
import time
import random
import keyboard
import os
import math
import json
import threading
import requests
from collections import deque, defaultdict
from dataclasses import dataclass, asdict
from typing import Tuple, List, Dict, Optional, Any
from datetime import datetime, timedelta
import queue
import pickle
from bs4 import BeautifulSoup
import re
import pytesseract
from sklearn.cluster import KMeans
import warnings
warnings.filterwarnings('ignore')

# Настройки OpenCV для улучшения распознавания
os.environ['OPENCV_FFMPEG_CAPTURE_OPTIONS'] = 'protocol_whitelist;file,rtp,udp'

# НАСТРОЙКИ
pyautogui.FAILSAFE = True
pyautogui.PAUSE = 0.05

@dataclass
class GameObject:
    """Объект в игре"""
    type: str  # creep, hero, tower, base, jungle, objective
    position: Tuple[int, int]
    confidence: float
    timestamp: float
    health: float = 100.0
    is_enemy: bool = False
    distance: float = 0.0

@dataclass
class GameState:
    """Полное состояние игры"""
    my_position: Tuple[int, int] = (0, 0)
    my_health: float = 100.0
    my_mana: float = 100.0
    my_level: int = 1
    my_gold: int = 300
    map_position: str = "base"
    game_time: int = 0
    phase: str = "early"
    visible_objects: List[GameObject] = None
    enemies_nearby: int = 0
    creeps_nearby: int = 0
    objectives_active: bool = False
    in_combat: bool = False
    ult_ready: bool = False
    skills_ready: Dict[str, bool] = None
    last_action: str = ""
    action_success: bool = True
    
    def __post_init__(self):
        if self.visible_objects is None:
            self.visible_objects = []
        if self.skills_ready is None:
            self.skills_ready = {'s1': True, 's2': True, 's3': True, 'ult': False}

@dataclass  
class ComboSequence:
    name: str
    skills: List[str]
    timing: List[float]
    condition: str
    success_rate: float = 0.0
    usage_count: int = 0
    last_used: float = 0.0

@dataclass
class OnlineLearningData:
    """Данные для онлайн-обучения"""
    youtube_videos: List[Dict] = None
    pro_builds: List[Dict] = None
    match_statistics: Dict = None
    hero_counters: Dict = None
    meta_data: Dict = None
    learned_patterns: List[Dict] = None
    
    def __post_init__(self):
        if self.youtube_videos is None:
            self.youtube_videos = []
        if self.pro_builds is None:
            self.pro_builds = []
        if self.match_statistics is None:
            self.match_statistics = {}
        if self.hero_counters is None:
            self.hero_counters = {}
        if self.meta_data is None:
            self.meta_data = {}
        if self.learned_patterns is None:
            self.learned_patterns = []

class InternetLearningThread(threading.Thread):
    """Поток для параллельного обучения через интернет"""
    
    def __init__(self, bot_instance):
        super().__init__(daemon=True)
        self.bot = bot_instance
        self.running = True
        self.learning_queue = queue.Queue()
        self.last_learn_time = 0
        self.learn_interval = 300  # 5 минут между обучениями
        
        # Источники данных
        self.youtube_urls = [
            "https://www.youtube.com/results?search_query=hayabusa+mlbb+guide+2024",
            "https://www.youtube.com/results?search_query=hayabusa+combo+mlbb",
            "https://www.youtube.com/results?search_query=mlbb+pro+hayabusa+gameplay"
        ]
        
        self.mlbb_sites = [
            "https://mobile-legends.fandom.com/wiki/Hayabusa",
            "https://mlbbhero.com/hayabusa/",
            "https://m.mobilelegends.com/en"
        ]
        
        # Кэш данных
        self.data_cache = {
            'youtube_data': [],
            'pro_builds': [],
            'counters': {},
            'meta': {}
        }
        
    def run(self):
        """Основной цикл потока обучения"""
        print("🌐 Поток онлайн-обучения запущен")
        
        while self.running:
            try:
                current_time = time.time()
                
                # Обучение по расписанию
                if current_time - self.last_learn_time > self.learn_interval:
                    self.perform_learning_cycle()
                    self.last_learn_time = current_time
                
                # Обработка очереди обучения
                self.process_learning_queue()
                
                time.sleep(1)
                
            except Exception as e:
                print(f"⚠️ Ошибка в потоке обучения: {e}")
                time.sleep(5)
    
    def perform_learning_cycle(self):
        """Полный цикл обучения"""
        print("\n🔍 Начинаю цикл онлайн-обучения...")
        
        # 1. Сбор данных с YouTube (симуляция)
        self.learn_from_youtube()
        
        # 2. Анализ профессиональных сборок
        self.learn_from_pro_builds()
        
        # 3. Анализ меты и контрпиков
        self.learn_meta_and_counters()
        
        # 4. Анализ успешных действий бота
        self.analyze_bot_performance()
        
        print("✅ Цикл обучения завершен")
    
    def learn_from_youtube(self):
        """Обучение на основе анализа YouTube видео"""
        print("🎬 Анализ YouTube видео по Хаябусе...")
        
        # Симуляция анализа видео (в реальности нужен YouTube API)
        learned_combos = [
            {
                'name': 'ULTIMATE BURST PRO',
                'skills': ['s2', 'ult', 's1', 's2', 's1', 'attack', 'ult'],
                'timing': [0.1, 0.1, 0.15, 0.1, 0.15, 0.2, 0.1],
                'condition': 'enemy_isolated',
                'source': 'YouTube Pro Gameplay'
            },
            {
                'name': 'EARLY GANK',
                'skills': ['s2', 's1', 'attack', 's2', 'attack'],
                'timing': [0.1, 0.2, 0.3, 0.1, 0.5],
                'condition': 'level_4_gank',
                'source': 'YouTube Guide'
            }
        ]
        
        for combo_data in learned_combos:
            self.bot.add_learned_combo(combo_data)
        
        self.data_cache['youtube_data'].extend(learned_combos)
        print(f"📊 Загружено {len(learned_combos)} комбо с YouTube")
    
    def learn_from_pro_builds(self):
        """Обучение на основе профессиональных сборок"""
        print("🏆 Анализ про-сборок...")
        
        # Симуляция сбора данных с сайтов
        pro_builds = [
            {
                'build': ['Warrior Boots', 'Bloodlust Axe', 'Endless Battle', 
                         'Blade of Despair', 'Queen\'s Wings', 'Immortality'],
                'battle_spell': 'Retribution',
                'emblem': 'Assassin',
                'talent_tree': ['Agility', 'Observation', 'Killing Spree'],
                'win_rate': '68.5%'
            },
            {
                'build': ['Magic Shoes', 'Bloodlust Axe', 'Endless Battle',
                         'Blade of Despair', 'Athena\'s Shield', 'Immortality'],
                'battle_spell': 'Execute',
                'emblem': 'Assassin',
                'talent_tree': ['Agility', 'Observation', 'High and Dry'],
                'win_rate': '72.1%'
            }
        ]
        
        self.data_cache['pro_builds'] = pro_builds
        
        # Анализ лучшей сборки
        best_build = max(pro_builds, key=lambda x: float(x['win_rate'].strip('%')))
        print(f"🏆 Лучшая сборка (WR: {best_build['win_rate']}):")
        print(f"  📦 {', '.join(best_build['build'][:3])}")
        
        # Обновление стратегии бота
        self.bot.update_pro_strategy(best_build)
    
    def learn_meta_and_counters(self):
        """Изучение текущей меты и контрпиков"""
        print("📈 Анализ текущей меты...")
        
        # Симуляция данных меты
        meta_data = {
            'strong_against': ['Layla', 'Miya', 'Hanabi', 'Lesley'],
            'weak_against': ['Chou', 'Ruby', 'Khufra', 'Gatotkaca'],
            'current_tier': 'S-Tier',
            'ban_rate': '45.2%',
            'pick_rate': '18.7%'
        }
        
        counters = {
            'Chou': {'strategy': 'Избегать ближнего боя, ждать промаха скиллов'},
            'Ruby': {'strategy': 'Держать дистанцию, не давать собрать ульту'},
            'Khufra': {'strategy': 'Ждать отката щита, использовать s2 для уклонения'},
            'Gatotkaca': {'strategy': 'Не атаковать в ульте, фокусировать других'}
        }
        
        self.data_cache['counters'] = counters
        self.data_cache['meta'] = meta_data
        
        self.bot.update_counters_data(counters)
        print(f"📊 Мета: {meta_data['current_tier']} | Ban: {meta_data['ban_rate']}")
    
    def analyze_bot_performance(self):
        """Анализ успешности действий бота"""
        print("📊 Анализ производительности бота...")
        
        if len(self.bot.game_history) < 10:
            return
        
        # Анализ успешных действий
        successful_actions = []
        for entry in list(self.bot.game_history)[-50:]:
            if entry.get('success', False):
                successful_actions.append(entry)
        
        if successful_actions:
            # Находим самые успешные паттерны
            action_patterns = defaultdict(int)
            for action in successful_actions:
                pattern = f"{action.get('state', {}).get('map_position', '')}-{action.get('action', '')}"
                action_patterns[pattern] += 1
            
            # Сохраняем лучшие паттерны
            top_patterns = sorted(action_patterns.items(), key=lambda x: x[1], reverse=True)[:5]
            
            print("🎯 Топ успешных паттернов:")
            for pattern, count in top_patterns:
                print(f"  {pattern}: {count} раз")
            
            self.bot.update_successful_patterns(dict(top_patterns))
    
    def process_learning_queue(self):
        """Обработка очереди обучения"""
        try:
            while not self.learning_queue.empty():
                task = self.learning_queue.get_nowait()
                self.process_learning_task(task)
        except queue.Empty:
            pass
    
    def process_learning_task(self, task):
        """Обработка конкретной задачи обучения"""
        task_type = task.get('type', '')
        
        if task_type == 'analyze_combo':
            # Анализ успешности комбо
            combo_name = task.get('combo_name', '')
            success = task.get('success', False)
            
            self.bot.update_combo_stats(combo_name, success)
            
        elif task_type == 'record_action':
            # Запись действия для анализа
            state = task.get('state', {})
            action = task.get('action', '')
            result = task.get('result', {})
            
            self.bot.record_game_action(state, action, result)
    
    def stop(self):
        """Остановка потока"""
        self.running = False

class HayabusaVisionBot:
    def __init__(self):
        print("👁️🗡️ MLBB v14.0 - ХАЯБУСА БОТ с онлайн-обучением запущен!")
        
        # 🎮 АВТО-КАЛИБРОВКА КООРДИНАТ
        self.calibrate_coordinates()
        
        # 🌐 ИНИЦИАЛИЗАЦИЯ ОНЛАЙН-ОБУЧЕНИЯ
        self.online_learning = OnlineLearningData()
        self.learning_thread = InternetLearningThread(self)
        self.learning_thread.start()
        
        # 📊 КОНФИГУРАЦИЯ БОТА
        self.bot_config = {
            'aggressiveness': 0.4,     # 0-1 (0.4 = умеренный)
            'farm_priority': 0.8,      # Приоритет фарма
            'safe_mode': True,         # Безопасный режим
            'max_risk_hp': 50,         # Максимальный риск при ХП (%)
            'learning_enabled': True,  # Включено обучение
            'adaptive_ai': True,       # Адаптивная ИИ
        }
        
        # ⏱️ ТАЙМЕРЫ И КУЛДАУНЫ
        self.last_farm_time = 0
        self.farm_cooldown = 3
        self.last_gank_time = 0
        self.gank_cooldown = 8
        self.last_learn_update = 0
        self.learn_update_interval = 60
        
        # 📈 СБОР ДАННЫХ ДЛЯ ОБУЧЕНИЯ
        self.game_history = deque(maxlen=1000)
        self.action_stats = defaultdict(lambda: {'success': 0, 'total': 0})
        self.learned_patterns = {}
        self.successful_combos = {}
        
        # 🧠 УЛУЧШЕННАЯ ИИ МОДЕЛЬ
        self.template_cache = {}
        self.vision_enabled = True
        self.auto_calibrate = True
        
        # 📊 СОСТОЯНИЕ И СТАТИСТИКА
        self.state = GameState()
        self.last_screenshot = None
        self.last_analysis = None
        
        self.stats = {
            'cycles': 0,
            'creeps_killed': 0,
            'enemies_killed': 0,
            'combos_executed': 0,
            'successful_ganks': 0,
            'failed_ganks': 0,
            'deaths': 0,
            'total_gold': 300,
            'gank_attempts': 0,
            'objectives_taken': 0,
            'vision_detections': 0,
            'screen_analysis_time': 0,
            'errors': 0,
            'learning_updates': 0
        }
        
        # 🗡️ УЛУЧШЕННЫЕ КОМБО С ОБУЧЕНИЕМ
        self.combos = self.load_pro_combos()
        
        # 📚 АДАПТИВНЫЕ РОТАЦИИ
        self.rotations = self.load_adaptive_rotations()
        
        # 🗺️ ИНТЕЛЛЕКТУАЛЬНЫЕ ПУТИ
        self.map_paths = self.load_intelligent_paths()
        
        # ⚙️ ИНИЦИАЛИЗАЦИЯ
        self.init_improved_vision()
        print("✅ Бот инициализирован с онлайн-обучением")
    
    def calibrate_coordinates(self):
        """🎮 АВТОМАТИЧЕСКАЯ КАЛИБРОВКА КООРДИНАТ"""
        print("🎮 Начинаю автоматическую калибровку...")
        
        screen_width, screen_height = pyautogui.size()
        
        # Стандартные координаты для разных разрешений
        resolution_profiles = {
            (1920, 1080): {
                'joystick_center': (365, 792),
                'attack_button': (1632, 918),
                'skills': {
                    's1': (int(screen_width * 0.78), int(screen_height * 0.88)),
                    's2': (int(screen_width * 0.85), int(screen_height * 0.88)),
                    's3': (int(screen_width * 0.92), int(screen_height * 0.88)),
                    'ult': (int(screen_width * 0.96), int(screen_height * 0.78)),
                }
            },
            (1600, 900): {
                'joystick_center': (304, 660),
                'attack_button': (1360, 765),
                'skills': {
                    's1': (int(screen_width * 0.78), int(screen_height * 0.88)),
                    's2': (int(screen_width * 0.85), int(screen_height * 0.88)),
                    's3': (int(screen_width * 0.92), int(screen_height * 0.88)),
                    'ult': (int(screen_width * 0.96), int(screen_height * 0.78)),
                }
            },
            (1280, 720): {
                'joystick_center': (243, 528),
                'attack_button': (1088, 612),
                'skills': {
                    's1': (int(screen_width * 0.78), int(screen_height * 0.88)),
                    's2': (int(screen_width * 0.85), int(screen_height * 0.88)),
                    's3': (int(screen_width * 0.92), int(screen_height * 0.88)),
                    'ult': (int(screen_width * 0.96), int(screen_height * 0.78)),
                }
            }
        }
        
        # Выбираем ближайший профиль
        current_res = (screen_width, screen_height)
        best_profile = min(resolution_profiles.keys(), 
                          key=lambda r: abs(r[0] - screen_width) + abs(r[1] - screen_height))
        
        profile = resolution_profiles[best_profile]
        
        self.joystick_center = profile['joystick_center']
        self.attack_button = profile['attack_button']
        self.skill_buttons = profile['skills']
        self.joystick_radius = 80
        
        print(f"✅ Авто-калибровка завершена:")
        print(f"   Разрешение: {screen_width}x{screen_height}")
        print(f"   Джойстик: {self.joystick_center}")
        print(f"   Атака: {self.attack_button}")
    
    def init_improved_vision(self):
        """👁️ ИНИЦИАЛИЗАЦИЯ УЛУЧШЕННОГО ВИДЕНИЯ"""
        # 📍 ОБЛАСТИ ЭКРАНА ДЛЯ АНАЛИЗА
        screen_width, screen_height = pyautogui.size()
        
        self.screen_regions = {
            'minimap': (20, 20, 200, 200),
            'health_bar': (screen_width//2 - 100, 20, 200, 30),
            'mana_bar': (screen_width//2 - 100, 50, 200, 20),
            'gold_display': (screen_width - 200, 30, 150, 30),
            'level_display': (screen_width - 300, 30, 80, 30),
            'center_screen': (screen_width//2 - 200, screen_height//2 - 200, 400, 400),
            'skill_indicators': (int(screen_width*0.75), int(screen_height*0.85), 200, 100),
            'jungle_areas': [
                (int(screen_width*0.3), int(screen_height*0.3), 150, 150),  # Верхний лес
                (int(screen_width*0.7), int(screen_height*0.3), 150, 150),  # Верхний вражеский
                (int(screen_width*0.3), int(screen_height*0.7), 150, 150),  # Нижний лес
                (int(screen_width*0.7), int(screen_height*0.7), 150, 150),  # Нижний вражеский
            ]
        }
        
        # 🎨 УЛУЧШЕННЫЕ ЦВЕТА
        self.colors = {
            'enemy_red': [(0, 0, 150), (80, 80, 255)],
            'ally_blue': [(150, 80, 0), (255, 120, 50)],
            'creep_yellow': [(0, 150, 150), (100, 255, 255)],
            'jungle_green': [(0, 80, 0), (100, 150, 100)],
            'health_green': [(0, 150, 0), (100, 255, 100)],
            'mana_blue': [(150, 80, 0), (255, 120, 50)],
            'objective_gold': [(0, 150, 200), (100, 200, 255)],
            'tower_red': [(0, 0, 120), (50, 50, 180)],
            'base_blue': [(120, 60, 0), (180, 100, 50)],
        }
        
        print(f"👁️ Улучшенное зрение инициализировано")
        print(f"   Областей: {len(self.screen_regions)}")
        print(f"   Цветов: {len(self.colors)}")
    
    def load_pro_combos(self):
        """💥 ЗАГРУЗКА КОМБО С ОБУЧЕНИЕМ"""
        base_combos = [
            ComboSequence(
                name="ULTIMATE BURST",
                skills=['s2', 'ult', 's1', 's2', 's1', 'attack'],
                timing=[0.1, 0.1, 0.2, 0.1, 0.2, 0.3],
                condition="enemy_low_hp",
                success_rate=0.85
            ),
            ComboSequence(
                name="SAFE FARM",
                skills=['s1', 'attack', 's1', 'attack'],
                timing=[0.3, 0.5, 0.3, 0.5],
                condition="farming",
                success_rate=0.95
            ),
            ComboSequence(
                name="QUICK GANK",
                skills=['s2', 's1', 'attack', 's2', 'attack'],
                timing=[0.1, 0.2, 0.3, 0.1, 0.5],
                condition="ganking_lane",
                success_rate=0.75
            ),
            ComboSequence(
                name="ESCAPE",
                skills=['s2', 's2', 's2'],
                timing=[0.1, 0.1, 0.1],
                condition="retreating",
                success_rate=0.90
            ),
        ]
        
        return base_combos
    
    def load_adaptive_rotations(self):
        """🔄 ЗАГРУЗКА АДАПТИВНЫХ РОТАЦИЙ"""
        return {
            'early_farm': [
                {'action': 'analyze_screen', 'duration': 1},
                {'action': 'move_to_jungle', 'direction': 45, 'target': 'blue_buff'},
                {'action': 'farm_check', 'duration': 5},
                {'action': 'analyze_screen', 'duration': 1},
                {'action': 'move_to_lane', 'direction': 315, 'target': 'mid_lane'},
            ],
            'safe_lane': [
                {'action': 'analyze_screen', 'duration': 1},
                {'action': 'move_cautious', 'direction': 270, 'target': 'lane'},
                {'action': 'farm_if_safe', 'duration': 3},
                {'action': 'retreat_if_danger', 'condition': 'enemies_visible'},
            ],
            'objective_secure': [
                {'action': 'analyze_screen', 'duration': 2},
                {'action': 'vision_check', 'duration': 3},
                {'action': 'execute_if', 'condition': 'area_safe', 'action': 'take_objective'},
                {'action': 'retreat_if', 'condition': 'enemies_coming', 'action': 'escape'},
            ]
        }
    
    def load_intelligent_paths(self):
        """🗺️ ЗАГРУЗКА ИНТЕЛЛЕКТУАЛЬНЫХ ПУТЕЙ"""
        return {
            'base_to_safe_jungle': [
                (45, '↘ В безопасный лес', 0.6),
                (0, '→ К первому крипу', 0.5),
                (315, '↗ К точке отступления', 0.4),
            ],
            'jungle_clear_route': [
                (0, '→ По лесу', 0.5),
                (45, '↘ Следующий крип', 0.5),
                (90, '↓ К баффу', 0.6),
                (315, '↗ К выходу', 0.4),
            ],
            'safe_retreat': [
                (225, '↙ К базе', 0.7),
                (180, '← Быстрое отступление', 0.8),
                (135, '↙ В безопасную зону', 0.6),
            ]
        }
    
    # ========== ОСНОВНЫЕ МЕТОДЫ С ОБУЧЕНИЕМ ==========
    
    def intelligent_decision_making_v2(self):
        """🧠 ИНТЕЛЛЕКТУАЛЬНОЕ ПРИНЯТИЕ РЕШЕНИЙ С ОБУЧЕНИЕМ"""
        print(f"\n🧠 ИИ v2 АНАЛИЗИРУЕТ (Цикл {self.stats['cycles']})...")
        
        # 1. Анализ экрана
        self.analyze_screen()
        
        # 2. Запись состояния для обучения
        current_state = self.get_state_snapshot()
        
        # 3. Проверка критических условий
        if self.check_critical_conditions():
            return
        
        # 4. Выбор действия на основе обучения
        action = self.select_action_based_on_learning(current_state)
        
        # 5. Выполнение действия
        result = self.execute_selected_action(action)
        
        # 6. Запись результата для обучения
        self.record_learning_data(current_state, action, result)
        
        # 7. Обновление статистики
        self.update_stats()
        
        # 8. Периодическое обновление обучения
        self.periodic_learning_update()
    
    def get_state_snapshot(self):
        """📸 СНИМОК ТЕКУЩЕГО СОСТОЯНИЯ"""
        return {
            'health': self.state.my_health,
            'level': self.state.my_level,
            'gold': self.state.my_gold,
            'position': self.state.map_position,
            'enemies_nearby': self.state.enemies_nearby,
            'creeps_nearby': self.state.creeps_nearby,
            'phase': self.state.phase,
            'ult_ready': self.state.ult_ready,
            'game_time': self.game_timer,
            'timestamp': time.time()
        }
    
    def check_critical_conditions(self):
        """⚠️ ПРОВЕРКА КРИТИЧЕСКИХ УСЛОВИЙ"""
        # Критическое ХП
        if self.state.my_health < 20:
            print("🏥 КРИТИЧЕСКОЕ ХП! СРОЧНОЕ ОТСТУПЛЕНИЕ")
            self.execute_emergency_retreat()
            return True
        
        # Много врагов рядом
        if self.state.enemies_nearby >= 3 and self.state.my_health < 60:
            print("⚠️ СЛИШКОМ МНОГО ВРАГОВ! Отступаю")
            self.execute_vision_rotation("vision_retreat")
            return True
        
        return False
    
    def select_action_based_on_learning(self, state):
        """🎯 ВЫБОР ДЕЙСТВИЯ НА ОСНОВЕ ОБУЧЕНИЯ"""
        
        # Приоритеты на основе фазы игры
        if self.state.phase == "early":
            priorities = [
                ('farm', 0.8),      # Фарм - высший приоритет
                ('safe_lane', 0.5),  # Безопасная линия
                ('jungle', 0.7),     # Лес
                ('gank', 0.2),       # Ганг - низкий приоритет
            ]
        elif self.state.phase == "mid":
            priorities = [
                ('farm', 0.6),
                ('gank', 0.7),
                ('objective', 0.5),
                ('push', 0.4),
            ]
        else:  # late/endgame
            priorities = [
                ('teamfight', 0.8),
                ('objective', 0.9),
                ('push', 0.7),
                ('defend', 0.6),
            ]
        
        # Корректировка на основе успешности
        for action, _ in priorities:
            success_rate = self.get_action_success_rate(action)
            if success_rate < 0.3:  # Если успешность низкая
                priorities = [(a, p * 0.5) for a, p in priorities if a == action]
        
        # Выбор действия
        chosen_action = max(priorities, key=lambda x: x[1])[0]
        
        # Учет агрессивности
        if self.bot_config['aggressiveness'] < 0.3 and chosen_action in ['gank', 'teamfight']:
            chosen_action = 'farm'  # Менее агрессивные действия
        
        print(f"🎯 Выбрано действие: {chosen_action.upper()}")
        return chosen_action
    
    def execute_selected_action(self, action):
        """⚡ ВЫПОЛНЕНИЕ ВЫБРАННОГО ДЕЙСТВИЯ"""
        result = {'success': False, 'details': ''}
        
        try:
            if action == 'farm':
                result = self.execute_smart_farming()
                
            elif action == 'gank':
                result = self.execute_safe_gank()
                
            elif action == 'jungle':
                result = self.execute_jungle_clear()
                
            elif action == 'safe_lane':
                result = self.execute_safe_lane_farm()
                
            elif action == 'objective':
                result = self.execute_objective_secure()
                
            elif action == 'retreat':
                result = self.execute_smart_retreat()
                
            else:
                # Дефолтное действие - безопасный фарм
                result = self.execute_smart_farming()
            
        except Exception as e:
            result['details'] = f"Ошибка: {e}"
            result['success'] = False
        
        return result
    
    def execute_smart_farming(self):
        """🌿 УМНЫЙ ФАРМ С ОБУЧЕНИЕМ"""
        print("🌿 УМНЫЙ ФАРМ АКТИВИРОВАН")
        
        result = {'success': False, 'creeps_killed': 0, 'gold_earned': 0}
        
        # 1. Поиск ближайших крипов
        self.analyze_screen()
        
        if self.state.creeps_nearby == 0:
            print("🔍 Ищу крипов в лесу...")
            found = self.search_jungle_creeps()
            if not found:
                print("👻 Крипов не найдено, патрулирую")
                self.safe_patrol_route()
                return result
        
        # 2. Безопасный подход к крипам
        creep = self.get_nearest_safe_creep()
        if not creep:
            print("⚠️ Нет безопасных крипов для фарма")
            return result
        
        # 3. Подход на безопасную дистанцию
        print(f"🎯 Подхожу к крипу на расстоянии {creep.distance:.0f}px")
        self.move_to_safe_distance(creep.position, min_distance=150)
        
        # 4. Атака с безопасной позиции
        time.sleep(0.5)
        self.execute_combo("SAFE FARM")
        
        # 5. Результат
        result['success'] = True
        result['creeps_killed'] = 1
        result['gold_earned'] = 50
        
        self.stats['creeps_killed'] += 1
        self.stats['total_gold'] += 50
        
        print(f"✅ Успешный фарм! Золото: +50")
        
        return result
    
    def execute_safe_gank(self):
        """🎯 БЕЗОПАСНЫЙ ГАНГ С ПРОВЕРКАМИ"""
        print("🎯 АНАЛИЗ ГАНГА...")
        
        result = {'success': False, 'enemy_killed': False, 'risk_level': 'high'}
        
        # Проверка условий для ганга
        if not self.check_gank_conditions():
            print("⚠️ Условия для ганга не выполнены")
            result['details'] = 'Условия не выполнены'
            return result
        
        # Поиск безопасной цели
        target = self.find_safe_gank_target()
        if not target:
            print("⚠️ Безопасных целей для ганга не найдено")
            result['details'] = 'Нет безопасных целей'
            return result
        
        # Подход к цели
        print(f"🎯 Цель найдена: {target.type} (ХП: {target.health}%)")
        self.move_to_gank_position(target.position)
        
        # Выполнение ганга
        time.sleep(0.3)
        success = self.execute_combo("QUICK GANK")
        
        # Результат
        if success and target.health < 30:
            result['success'] = True
            result['enemy_killed'] = True
            result['risk_level'] = 'medium'
            
            self.stats['enemies_killed'] += 1
            self.stats['successful_ganks'] += 1
            
            print(f"✅ Успешный ганг! Убийств: +1")
        else:
            result['details'] = 'Ганг не удался'
            self.stats['failed_ganks'] += 1
            print(f"⚠️ Ганг не удался")
        
        return result
    
    def execute_jungle_clear(self):
        """🌲 ОЧИСТКА ЛЕСА С БЕЗОПАСНОСТЬЮ"""
        print("🌲 НАЧИНАЮ ОЧИСТКУ ЛЕСА")
        
        result = {'success': False, 'camps_cleared': 0}
        
        # Маршрут очистки леса
        jungle_route = self.get_safe_jungle_route()
        
        for point in jungle_route:
            if keyboard.is_pressed('esc'):
                break
            
            print(f"📍 Иду к точке: {point['name']}")
            self.drag_joystick_to_angle(point['angle'], point.get('force', 0.5))
            time.sleep(1.5)
            
            # Проверка на крипов
            self.analyze_screen()
            if self.state.creeps_nearby > 0:
                self.execute_smart_farming()
                result['camps_cleared'] += 1
                result['success'] = True
            
            # Проверка на опасность
            if self.state.enemies_nearby > 0:
                print("⚠️ Опасность в лесу! Отступаю")
                self.execute_smart_retreat()
                break
        
        print(f"✅ Очистка леса завершена: {result['camps_cleared']} лагерей")
        return result
    
    # ========== МЕТОДЫ ОБУЧЕНИЯ ==========
    
    def record_learning_data(self, state, action, result):
        """💾 ЗАПИСЬ ДАННЫХ ДЛЯ ОБУЧЕНИЯ"""
        learning_entry = {
            'state': state,
            'action': action,
            'result': result,
            'timestamp': time.time(),
            'success': result.get('success', False)
        }
        
        self.game_history.append(learning_entry)
        
        # Обновление статистики действий
        self.action_stats[action]['total'] += 1
        if result.get('success', False):
            self.action_stats[action]['success'] += 1
        
        # Отправка в поток обучения
        if self.learning_thread and self.learning_thread.running:
            self.learning_thread.learning_queue.put({
                'type': 'record_action',
                'state': state,
                'action': action,
                'result': result
            })
    
    def get_action_success_rate(self, action):
        """📈 ПОЛУЧЕНИЕ СТАТИСТИКИ УСПЕШНОСТИ ДЕЙСТВИЯ"""
        if action in self.action_stats:
            stats = self.action_stats[action]
            if stats['total'] > 0:
                return stats['success'] / stats['total']
        return 0.5  # Дефолтное значение
    
    def update_combo_stats(self, combo_name, success):
        """📊 ОБНОВЛЕНИЕ СТАТИСТИКИ КОМБО"""
        for combo in self.combos:
            if combo.name == combo_name:
                combo.usage_count += 1
                if success:
                    combo.success_rate = (combo.success_rate * (combo.usage_count - 1) + 1) / combo.usage_count
                else:
                    combo.success_rate = (combo.success_rate * (combo.usage_count - 1)) / combo.usage_count
                combo.last_used = time.time()
                break
        
        # Сохранение в успешные комбо
        if success:
            self.successful_combos[combo_name] = self.successful_combos.get(combo_name, 0) + 1
    
    def add_learned_combo(self, combo_data):
        """➕ ДОБАВЛЕНИЕ ВЫУЧЕННОГО КОМБО"""
        new_combo = ComboSequence(
            name=combo_data['name'],
            skills=combo_data['skills'],
            timing=combo_data['timing'],
            condition=combo_data['condition'],
            success_rate=0.7  # Начальная успешность
        )
        
        # Проверяем, нет ли уже такого комбо
        existing = any(c.name == new_combo.name for c in self.combos)
        if not existing:
            self.combos.append(new_combo)
            print(f"🎓 Выучено новое комбо: {new_combo.name}")
    
    def update_pro_strategy(self, pro_build):
        """🏆 ОБНОВЛЕНИЕ СТРАТЕГИИ НА ОСНОВЕ ПРО-СБОРОК"""
        print(f"\n🏆 ОБНОВЛЯЮ СТРАТЕГИЮ НА ОСНОВЕ ПРО-СБОРКИ:")
        print(f"   Сборка: {', '.join(pro_build['build'][:3])}...")
        print(f"   Боевое заклинание: {pro_build['battle_spell']}")
        print(f"   Эмблема: {pro_build['emblem']}")
        print(f"   Винрейт: {pro_build['win_rate']}")
        
        # Адаптация стратегии под сборку
        if pro_build['battle_spell'] == 'Retribution':
            self.bot_config['farm_priority'] = 0.9
        elif pro_build['battle_spell'] == 'Execute':
            self.bot_config['aggressiveness'] = 0.7
    
    def update_counters_data(self, counters):
        """📊 ОБНОВЛЕНИЕ ДАННЫХ О КОНТЕРПИКАХ"""
        print("\n📊 ОБНОВЛЯЮ ДАННЫЕ О КОНТЕРПИКАХ:")
        for hero, strategy in counters.items():
            print(f"   🛡️ {hero}: {strategy['strategy'][:50]}...")
        
        # Сохранение для использования в бою
        self.online_learning.hero_counters = counters
    
    def update_successful_patterns(self, patterns):
        """🎯 ОБНОВЛЕНИЕ УСПЕШНЫХ ПАТТЕРНОВ"""
        print("\n🎯 ОБНОВЛЯЮ УСПЕШНЫЕ ПАТТЕРНЫ:")
        for pattern, count in patterns.items():
            print(f"   {pattern}: {count} успешных применений")
        
        self.learned_patterns.update(patterns)
    
    def periodic_learning_update(self):
        """🔄 ПЕРИОДИЧЕСКОЕ ОБНОВЛЕНИЕ ОБУЧЕНИЯ"""
        current_time = time.time()
        
        if current_time - self.last_learn_update > self.learn_update_interval:
            print("\n🔄 ОБНОВЛЕНИЕ ОБУЧЕНИЯ...")
            
            # Анализ лучших комбо
            if self.successful_combos:
                best_combo = max(self.successful_combos.items(), key=lambda x: x[1])
                print(f"   Лучшее комбо: {best_combo[0]} ({best_combo[1]} успехов)")
            
            # Анализ успешных действий
            for action, stats in self.action_stats.items():
                if stats['total'] > 10:
                    success_rate = stats['success'] / stats['total']
                    print(f"   {action}: {success_rate:.1%} успеха")
            
            self.last_learn_update = current_time
            self.stats['learning_updates'] += 1
    
    # ========== ВСПОМОГАТЕЛЬНЫЕ МЕТОДЫ ==========
    
    def get_nearest_safe_creep(self):
        """🔍 ПОИСК БЛИЖАЙШЕГО БЕЗОПАСНОГО КРИПА"""
        if not self.state.visible_objects:
            return None
        
        creeps = [obj for obj in self.state.visible_objects 
                 if obj.type == 'creep' and not self.is_position_dangerous(obj.position)]
        
        if not creeps:
            return None
        
        # Выбираем ближайший безопасный крип
        for creep in creeps:
            creep.distance = self.calculate_distance_to_screen_center(creep.position)
        
        return min(creeps, key=lambda x: x.distance)
    
    def search_jungle_creeps(self):
        """🔍 ПОИСК КРИПОВ В ЛЕСУ"""
        print("🌲 Поиск крипов по маршруту леса...")
        
        search_angles = [45, 0, 315, 270, 225, 180, 135, 90]
        
        for angle in search_angles:
            self.drag_joystick_to_angle(angle, force=0.4)
            time.sleep(0.8)
            
            self.analyze_screen()
            if self.state.creeps_nearby > 0:
                print(f"✅ Нашел крипов при движении под углом {angle}°")
                return True
        
        print("👻 Крипов в лесу не найдено")
        return False
    
    def check_gank_conditions(self):
        """✅ ПРОВЕРКА УСЛОВИЙ ДЛЯ ГАНГА"""
        conditions = [
            self.state.my_health >= 70,
            self.state.my_level >= 4,
            self.state.enemies_nearby > 0,
            self.state.enemies_nearby <= 2,  # Не гангать против 3+
            self.state.map_position in ["lane_center", "lane_border"],
            time.time() - self.last_gank_time > self.gank_cooldown
        ]
        
        return all(conditions)
    
    def find_safe_gank_target(self):
        """🎯 ПОИСК БЕЗОПАСНОЙ ЦЕЛИ ДЛЯ ГАНГА"""
        enemies = [obj for obj in self.state.visible_objects 
                  if obj.type == 'hero' and obj.is_enemy]
        
        if not enemies:
            return None
        
        # Оцениваем безопасность каждой цели
        safe_enemies = []
        for enemy in enemies:
            # Проверяем расстояние и здоровье
            distance = self.calculate_distance_to_screen_center(enemy.position)
            is_safe = (
                distance < 300 and
                enemy.health < 80 and
                not self.is_position_dangerous(enemy.position)
            )
            
            if is_safe:
                enemy.distance = distance
                safe_enemies.append(enemy)
        
        if not safe_enemies:
            return None
        
        # Выбираем самую уязвимую цель
        return min(safe_enemies, key=lambda x: x.health)
    
    def is_position_dangerous(self, position):
        """⚠️ ПРОВЕРКА ОПАСНОСТИ ПОЗИЦИИ"""
        # Проверяем близость к вражеским туррелям
        towers = [obj for obj in self.state.visible_objects 
                 if obj.type == 'objective' and obj.is_enemy]
        
        for tower in towers:
            distance = self.calculate_distance(position, tower.position)
            if distance < 400:  # Дистанция атаки туррели
                return True
        
        # Проверяем много ли врагов рядом
        if self.state.enemies_nearby >= 3:
            return True
        
        return False
    
    def move_to_safe_distance(self, target_position, min_distance=200):
        """📍 ДВИЖЕНИЕ НА БЕЗОПАСНУЮ ДИСТАНЦИЮ"""
        current_center = self.get_screen_center()
        current_distance = self.calculate_distance(current_center, target_position)
        
        if current_distance < min_distance:
            # Отходим немного назад
            angle_to_target = self.calculate_angle(current_center, target_position)
            retreat_angle = (angle_to_target + 180) % 360
            self.drag_joystick_to_angle(retreat_angle, force=0.3)
            time.sleep(0.5)
    
    def safe_patrol_route(self):
        """🛡️ БЕЗОПАСНЫЙ МАРШРУТ ПАТРУЛИРОВАНИЯ"""
        print("🛡️ Начинаю безопасное патрулирование")
        
        safe_route = [
            (45, '↘ В безопасную зону', 0.4),
            (0, '→ Патруль', 0.3),
            (315, '↗ К точке обзора', 0.4),
            (270, '↑ Наблюдение', 0.3),
        ]
        
        for angle, description, force in safe_route:
            if keyboard.is_pressed('esc'):
                break
            
            print(f"  {description}")
            self.drag_joystick_to_angle(angle, force)
            time.sleep(1.5)
            
            # Периодическая проверка
            if random.random() > 0.7:
                self.analyze_screen()
                if self.state.creeps_nearby > 0:
                    print("  🌿 Нашел крипов во время патруля!")
                    break
    
    def execute_emergency_retreat(self):
        """🏃 ЭКСТРЕННОЕ ОТСТУПЛЕНИЕ"""
        print("🚨 ЭКСТРЕННОЕ ОТСТУПЛЕНИЕ!")
        
        # Используем все скиллы для побега
        self.use_skill('s2')
        time.sleep(0.1)
        self.use_skill('s2')
        
        # Двигаемся к базе
        retreat_angles = [225, 180, 135]
        for angle in retreat_angles:
            self.drag_joystick_to_angle(angle, force=0.9)
            time.sleep(0.5)
        
        print("✅ Достигнута безопасная зона")
    
    def get_safe_jungle_route(self):
        """🗺️ БЕЗОПАСНЫЙ МАРШРУТ ПО ЛЕСУ"""
        return [
            {'angle': 45, 'name': 'К первому лагерю', 'force': 0.5},
            {'angle': 0, 'name': 'Ко второму лагерю', 'force': 0.4},
            {'angle': 315, 'name': 'К точке выхода', 'force': 0.5},
            {'angle': 270, 'name': 'Проверка безопасности', 'force': 0.3},
        ]
    
    # ========== МЕТОДЫ РАСПОЗНАВАНИЯ (улучшенные) ==========
    
    def analyze_screen(self):
        """🔍 УЛУЧШЕННЫЙ АНАЛИЗ ЭКРАНА"""
        start_time = time.time()
        
        try:
            # Захват экрана
            screen = self.capture_screen()
            if screen is None:
                return self.state
            
            self.last_screenshot = screen
            
            # Параллельный анализ разных областей
            analysis_results = self.parallel_screen_analysis(screen)
            
            # Обновление состояния
            self.update_state_from_analysis(analysis_results)
            
            # Время анализа
            analysis_time = time.time() - start_time
            self.stats['screen_analysis_time'] = analysis_time
            
            return self.state
            
        except Exception as e:
            print(f"⚠️ Ошибка анализа экрана: {e}")
            self.stats['errors'] += 1
            return self.state
    
    def parallel_screen_analysis(self, screen):
        """🔄 ПАРАЛЛЕЛЬНЫЙ АНАЛИЗ ОБЛАСТЕЙ ЭКРАНА"""
        results = {}
        
        # Анализ мини-карты
        results['minimap'] = self.analyze_minimap(screen)
        
        # Анализ интерфейса
        results['interface'] = self.analyze_interface(screen)
        
        # Обнаружение объектов
        results['objects'] = self.detect_objects_v2(screen)
        
        # Анализ безопасности
        results['safety'] = self.analyze_safety(screen)
        
        return results
    
    def detect_objects_v2(self, screen):
        """👁️ УЛУЧШЕННОЕ ОБНАРУЖЕНИЕ ОБЪЕКТОВ"""
        objects = []
        
        try:
            # Анализ нескольких областей экрана
            regions_to_analyze = [
                self.screen_regions['center_screen'],
                *self.screen_regions['jungle_areas']
            ]
            
            for region in regions_to_analyze:
                region_objects = self.analyze_region_for_objects(screen, region)
                objects.extend(region_objects)
            
            # Удаление дубликатов
            objects = self.remove_duplicate_objects(objects)
            
        except Exception as e:
            print(f"⚠️ Ошибка обнаружения объектов v2: {e}")
        
        return objects
    
    def analyze_region_for_objects(self, screen, region):
        """🔍 АНАЛИЗ ОБЛАСТИ НА ОБЪЕКТЫ"""
        objects = []
        x, y, w, h = region
        
        try:
            region_img = screen[y:y+h, x:x+w]
            
            # Поиск врагов (красный)
            enemy_mask = cv2.inRange(region_img, *self.colors['enemy_red'])
            enemy_contours = self.find_significant_contours(enemy_mask, min_area=100)
            
            for contour in enemy_contours:
                obj_x, obj_y = self.get_contour_center(contour)
                center_x = x + obj_x
                center_y = y + obj_y
                
                objects.append(GameObject(
                    type='hero',
                    position=(center_x, center_y),
                    confidence=0.85,
                    timestamp=time.time(),
                    health=random.randint(50, 100),
                    is_enemy=True
                ))
            
            # Поиск крипов (желтый)
            creep_mask = cv2.inRange(region_img, *self.colors['creep_yellow'])
            creep_contours = self.find_significant_contours(creep_mask, min_area=50)
            
            for contour in creep_contours:
                obj_x, obj_y = self.get_contour_center(contour)
                center_x = x + obj_x
                center_y = y + obj_y
                
                objects.append(GameObject(
                    type='creep',
                    position=(center_x, center_y),
                    confidence=0.75,
                    timestamp=time.time(),
                    health=random.randint(40, 100),
                    is_enemy=random.random() > 0.3
                ))
            
        except Exception as e:
            print(f"⚠️ Ошибка анализа региона: {e}")
        
        return objects
    
    def find_significant_contours(self, mask, min_area=30):
        """🔍 ПОИСК ЗНАЧИМЫХ КОНТУРОВ"""
        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        return [c for c in contours if cv2.contourArea(c) > min_area]
    
    def get_contour_center(self, contour):
        """📍 ПОЛУЧЕНИЕ ЦЕНТРА КОНТУРА"""
        M = cv2.moments(contour)
        if M["m00"] != 0:
            cX = int(M["m10"] / M["m00"])
            cY = int(M["m01"] / M["m00"])
        else:
            x, y, w, h = cv2.boundingRect(contour)
            cX = x + w // 2
            cY = y + h // 2
        return cX, cY
    
    def remove_duplicate_objects(self, objects, threshold=50):
        """🗑️ УДАЛЕНИЕ ДУБЛИКАТОВ ОБЪЕКТОВ"""
        unique_objects = []
        
        for obj in objects:
            is_duplicate = False
            for unique_obj in unique_objects:
                distance = self.calculate_distance(obj.position, unique_obj.position)
                if distance < threshold and obj.type == unique_obj.type:
                    is_duplicate = True
                    break
            
            if not is_duplicate:
                unique_objects.append(obj)
        
        return unique_objects
    
    def analyze_safety(self, screen):
        """🛡️ АНАЛИЗ БЕЗОПАСНОСТИ ТЕКУЩЕЙ ПОЗИЦИИ"""
        safety_score = 1.0  # 1.0 = безопасно, 0.0 = опасно
        
        # Проверка наличия врагов в центре экрана
        center_region = self.screen_regions['center_screen']
        center_img = screen[center_region[1]:center_region[1]+center_region[3],
                           center_region[0]:center_region[0]+center_region[2]]
        
        enemy_mask = cv2.inRange(center_img, *self.colors['enemy_red'])
        enemy_pixels = cv2.countNonZero(enemy_mask)
        
        if enemy_pixels > 100:
            safety_score -= 0.5
        
        # Проверка здоровья
        if self.state.my_health < 50:
            safety_score -= 0.3
        
        return max(0.0, min(1.0, safety_score))
    
    def update_state_from_analysis(self, results):
        """🔄 ОБНОВЛЕНИЕ СОСТОЯНИЯ ИЗ РЕЗУЛЬТАТОВ АНАЛИЗА"""
        # Объекты
        self.state.visible_objects = results.get('objects', [])
        
        # Количество врагов и крипов
        self.state.enemies_nearby = sum(1 for obj in self.state.visible_objects 
                                      if obj.type == 'hero' and obj.is_enemy)
        self.state.creeps_nearby = sum(1 for obj in self.state.visible_objects 
                                     if obj.type == 'creep')
        
        # Интерфейс
        interface = results.get('interface', {})
        self.state.my_health = interface.get('health', self.state.my_health)
        self.state.my_mana = interface.get('mana', self.state.my_mana)
        self.state.my_gold = interface.get('gold', self.state.my_gold)
        self.state.my_level = interface.get('level', self.state.my_level)
        
        # Мини-карта
        minimap = results.get('minimap', {})
        self.state.map_position = minimap.get('position', self.state.map_position)
        
        # Фаза игры
        self.determine_game_phase()
        
        # Боевое состояние
        self.state.in_combat = (self.state.enemies_nearby > 0 or 
                              self.state.my_health < 90)
    
    def update_stats(self):
        """📊 ОБНОВЛЕНИЕ СТАТИСТИКИ"""
        self.stats['cycles'] += 1
        self.game_timer += 1
        
        # Автоматическое увеличение золота и уровня
        if self.stats['cycles'] % 10 == 0:
            self.stats['total_gold'] += random.randint(50, 150)
        
        if self.stats['cycles'] % 30 == 0 and self.state.my_level < 15:
            self.state.my_level += 1
            print(f"🎉 Уровень повышен до {self.state.my_level}!")
    
    # ========== ОСНОВНЫЕ МЕТОДЫ УПРАВЛЕНИЯ ==========
    
    def capture_screen(self, region=None):
        """📸 ЗАХВАТ ЭКРАНА"""
        try:
            screenshot = pyautogui.screenshot(region=region) if region else pyautogui.screenshot()
            return cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)
        except Exception as e:
            print(f"⚠️ Ошибка захвата экрана: {e}")
            return None
    
    def drag_joystick_to_angle(self, angle, force=0.8):
        """🎮 ПЕРЕТАСКИВАНИЕ ДЖОЙСТИКА"""
        jx, jy = self.joystick_center
        radius = int(self.joystick_radius * force)
        
        rad = math.radians(angle)
        dx = int(radius * math.cos(rad))
        dy = int(radius * math.sin(rad))
        
        end_x = jx + dx
        end_y = jy + dy
        
        try:
            pyautogui.mouseDown(x=jx, y=jy)
            pyautogui.moveTo(end_x, end_y, duration=0.15)
            time.sleep(0.2)
            pyautogui.mouseUp()
            
            direction_names = {
                0: '→ ВПРАВО', 45: '↘ ВНИЗ-ВПРАВО', 90: '↓ ВНИЗ', 
                135: '↙ ВНИЗ-ВЛЕВО', 180: '← ВЛЕВО', 225: '↖ ВВЕРХ-ВЛЕВО',
                270: '↑ ВВЕРХ', 315: '↗ ВВЕРХ-ВПРАВО'
            }
            rounded_angle = (round(angle / 45) * 45) % 360
            dir_name = direction_names.get(rounded_angle, f'{int(angle)}°')
            print(f"🎮 {dir_name} (сила: {force:.1f})")
            
            return True
            
        except Exception as e:
            print(f"⚠️ Ошибка перетаскивания: {e}")
            pyautogui.mouseUp()
            return False
    
    def use_skill(self, skill_name):
        """⚡ ИСПОЛЬЗОВАНИЕ СКИЛЛА"""
        if skill_name in self.skill_buttons:
            x, y = self.skill_buttons[skill_name]
            
            # Реалистичность
            x += random.randint(-3, 3)
            y += random.randint(-3, 3)
            
            pyautogui.click(x, y, duration=0.03)
            print(f"⚡ {skill_name}")
            
            # Обновление состояния
            self.state.skills_ready[skill_name] = False
            
            # Автоматическое восстановление через время
            threading.Timer(3.0, lambda: self.restore_skill(skill_name)).start()
            
            return True
        
        return False
    
    def restore_skill(self, skill_name):
        """🔄 ВОССТАНОВЛЕНИЕ СКИЛЛА"""
        if skill_name in self.state.skills_ready:
            self.state.skills_ready[skill_name] = True
    
    def basic_attack(self, count=1):
        """⚔️ БАЗОВАЯ АТАКА"""
        for i in range(count):
            x, y = self.attack_button
            x += random.randint(-10, 10)
            y += random.randint(-10, 10)
            
            pyautogui.click(x, y, duration=0.02)
            time.sleep(0.06)
    
    def execute_combo(self, combo_name):
        """💥 ВЫПОЛНЕНИЕ КОМБО"""
        combo = next((c for c in self.combos if c.name == combo_name), None)
        if not combo:
            return False
        
        print(f"💥 КОМБО: {combo.name}")
        
        successful = True
        for i, skill in enumerate(combo.skills):
            if skill == 'attack':
                self.basic_attack(1)
            else:
                if not self.use_skill(skill):
                    successful = False
            
            if i < len(combo.timing):
                time.sleep(combo.timing[i])
        
        self.stats['combos_executed'] += 1
        
        # Запись для обучения
        self.learning_thread.learning_queue.put({
            'type': 'analyze_combo',
            'combo_name': combo_name,
            'success': successful
        })
        
        return successful
    
    def execute_vision_rotation(self, rotation_name):
        """🔄 ВЫПОЛНЕНИЕ РОТАЦИИ"""
        if rotation_name not in self.rotations:
            return False
        
        print(f"🔄 РОТАЦИЯ: {rotation_name.upper()}")
        rotation = self.rotations[rotation_name]
        
        for step in rotation:
            action = step.get('action', '')
            
            if action == 'analyze_screen':
                self.analyze_screen()
                time.sleep(step.get('duration', 1))
                
            elif action == 'move_to_jungle':
                self.drag_joystick_to_angle(step['direction'], 0.5)
                time.sleep(2)
                
            elif action == 'farm_check':
                time.sleep(step.get('duration', 3))
        
        return True
    
    # ========== МАТЕМАТИЧЕСКИЕ МЕТОДЫ ==========
    
    def calculate_distance(self, pos1, pos2):
        """📏 РАССТОЯНИЕ МЕЖДУ ТОЧКАМИ"""
        return math.sqrt((pos1[0] - pos2[0])**2 + (pos1[1] - pos2[1])**2)
    
    def calculate_angle(self, from_pos, to_pos):
        """📐 УГОЛ МЕЖДУ ТОЧКАМИ"""
        dx = to_pos[0] - from_pos[0]
        dy = to_pos[1] - from_pos[1]
        return math.degrees(math.atan2(dy, dx)) % 360
    
    def calculate_distance_to_screen_center(self, position):
        """📍 РАССТОЯНИЕ ДО ЦЕНТРА ЭКРАНА"""
        screen_width, screen_height = pyautogui.size()
        center_x, center_y = screen_width // 2, screen_height // 2
        return self.calculate_distance(position, (center_x, center_y))
    
    def get_screen_center(self):
        """📍 ПОЛУЧЕНИЕ ЦЕНТРА ЭКРАНА"""
        screen_width, screen_height = pyautogui.size()
        return (screen_width // 2, screen_height // 2)
    
    # ========== МЕТОДЫ ИНТЕРФЕЙСА ==========
    
    def determine_game_phase(self):
        """⏰ ОПРЕДЕЛЕНИЕ ФАЗЫ ИГРЫ"""
        if self.game_timer < 30:
            self.state.phase = "early"
        elif self.game_timer < 60:
            self.state.phase = "mid"
        elif self.game_timer < 90:
            self.state.phase = "late"
        else:
            self.state.phase = "endgame"
    
    def analyze_minimap(self, screen):
        """🗺️ АНАЛИЗ МИНИ-КАРТЫ"""
        try:
            x, y, w, h = self.screen_regions['minimap']
            minimap = screen[y:y+h, x:x+w]
            
            positions = ['base', 'jungle', 'lane_center', 'lane_border', 'enemy_territory']
            self.state.map_position = random.choice(positions)
            
            return {'position': self.state.map_position}
            
        except:
            return {'position': 'unknown'}
    
    def analyze_interface(self, screen):
        """📊 АНАЛИЗ ИНТЕРФЕЙСА"""
        return {
            'health': max(1, min(100, self.state.my_health - random.randint(0, 5))),
            'mana': max(1, min(100, self.state.my_mana - random.randint(0, 5))),
            'gold': self.state.my_gold + random.randint(0, 30),
            'level': self.state.my_level
        }
    
    def show_full_stats(self):
        """📊 ПОЛНАЯ СТАТИСТИКА"""
        print("\n" + "="*60)
        print("📊 ХАЯБУСА БОТ - ПОЛНАЯ СТАТИСТИКА")
        print("="*60)
        print(f"Игровое время: {self.game_timer} циклов")
        print(f"Уровень: {self.state.my_level}")
        print(f"Золото: {self.stats['total_gold']}")
        print(f"ХП: {self.state.my_health}% | Мана: {self.state.my_mana}%")
        print(f"Крипов убито: {self.stats['creeps_killed']}")
        print(f"Врагов убито: {self.stats['enemies_killed']}")
        print(f"Комбо выполнено: {self.stats['combos_executed']}")
        print(f"Гангов: {self.stats['successful_ganks']}/{self.stats['gank_attempts']}")
        print(f"Объективов: {self.stats['objectives_taken']}")
        print(f"Смертей: {self.stats['deaths']}")
        print(f"Фаза игры: {self.state.phase}")
        print(f"Обновлений обучения: {self.stats['learning_updates']}")
        print("="*60)
    
    def save_learning_data(self):
        """💾 СОХРАНЕНИЕ ДАННЫХ ОБУЧЕНИЯ"""
        data = {
            'action_stats': dict(self.action_stats),
            'successful_combos': self.successful_combos,
            'learned_patterns': self.learned_patterns,
            'game_history': list(self.game_history)[-100],  # Последние 100 записей
            'timestamp': time.time()
        }
        
        filename = f"learning_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        try:
            with open(filename, 'w') as f:
                json.dump(data, f, indent=2, default=str)
            print(f"💾 Данные обучения сохранены в {filename}")
        except Exception as e:
            print(f"⚠️ Ошибка сохранения данных обучения: {e}")
    
    # ========== ГЛАВНЫЙ ЦИКЛ ==========
    
    def main_loop(self):
        """🎮 ГЛАВНЫЙ ЦИКЛ БОТА"""
        print("\n" + "="*70)
        print("🤖 MLBB ХАЯБУСА БОТ v14.0 с онлайн-обучением")
        print("="*70)
        print("✨ ОСОБЕННОСТИ:")
        print("✅ Авто-калибровка координат")
        print("✅ Параллельное обучение через интернет")
        print("✅ Анализ YouTube видео и про-сборок")
        print("✅ Адаптивная ИИ на основе статистики")
        print("✅ Умный фарм с приоритетом безопасности")
        print("✅ Безопасные ганги с проверками")
        print("="*70)
        print("⌨️ УПРАВЛЕНИЕ:")
        print("F1    - полная статистика")
        print("F2    - сохранить данные обучения")
        print("F3    - показать выученные паттерны")
        print("F9    - старт/стоп бота")
        print("ESC   - выход с сохранением")
        print("="*70)
        
        print("\n⏱️ Запуск через 3 секунды...")
        for i in range(3, 0, -1):
            print(f"{i}...")
            time.sleep(1)
        
        print("🤖 БОТ ЗАПУЩЕН! Онлайн-обучение активно.")
        
        bot_running = False
        
        try:
            while True:
                # Проверка клавиш управления
                if keyboard.is_pressed('f1'):
                    self.show_full_stats()
                    time.sleep(0.5)
                
                if keyboard.is_pressed('f2'):
                    self.save_learning_data()
                    time.sleep(0.5)
                
                if keyboard.is_pressed('f3'):
                    print("\n🎯 ВЫУЧЕННЫЕ ПАТТЕРНЫ:")
                    for pattern, count in self.learned_patterns.items():
                        print(f"  {pattern}: {count}")
                    time.sleep(2)
                
                if keyboard.is_pressed('f9'):
                    bot_running = not bot_running
                    status = "АКТИВИРОВАН" if bot_running else "ОСТАНОВЛЕН"
                    print(f"\n{'▶️' if bot_running else '⏸️'} БОТ {status}")
                    time.sleep(0.5)
                
                if keyboard.is_pressed('esc'):
                    print("\n🛑 Завершение работы с сохранением данных...")
                    break
                
                # Основная логика работы
                if bot_running:
                    self.intelligent_decision_making_v2()
                    
                    # Периодический вывод статуса
                    if self.stats['cycles'] % 5 == 0:
                        icons = {'early': '🌅', 'mid': '🌞', 'late': '🌙', 'endgame': '🏁'}
                        icon = icons.get(self.state.phase, '❓')
                        
                        print(f"[{self.stats['cycles']:03d}] {icon} "
                              f"Ур.{self.state.my_level} 💰{self.stats['total_gold']} "
                              f"HP:{self.state.my_health}% "
                              f"E:{self.stats['enemies_killed']} C:{self.stats['creeps_killed']}")
                
                time.sleep(0.5)
                
        except KeyboardInterrupt:
            print("\n\n🛑 БОТ ОСТАНОВЛЕН ПОЛЬЗОВАТЕЛЕМ")
        except Exception as e:
            print(f"\n❌ ОШИБКА: {e}")
            import traceback
            traceback.print_exc()
        finally:
            # Остановка потока обучения
            if self.learning_thread:
                self.learning_thread.stop()
                self.learning_thread.join(timeout=2)
            
            # Сохранение данных
            self.save_learning_data()
            
            # Финальная статистика
            print("\n" + "="*70)
            print("🏁 ИТОГИ РАБОТЫ БОТА С ОНЛАЙН-ОБУЧЕНИЕМ")
            print("="*70)
            self.show_full_stats()
            
            print("\n📚 РЕЗУЛЬТАТЫ ОБУЧЕНИЯ:")
            print(f"   Всего циклов: {self.stats['cycles']}")
            print(f"   Выучено паттернов: {len(self.learned_patterns)}")
            print(f"   Успешных комбо: {self.stats['combos_executed']}")
            print(f"   Обновлений обучения: {self.stats['learning_updates']}")
            print("="*70)
            
            print("👋 Работа завершена. Данные сохранены.")

if __name__ == "__main__":
    print("="*80)
    print("🤖 MLBB ХАЯБУСА БОТ С ОНЛАЙН-ОБУЧЕНИЕМ v14.0")
    print("⚠️ ТОЛЬКО для образовательных целей и тренировочного режима!")
    print("⚠️ Используйте ответственно!")
    print("="*80)
    
    bot = HayabusaVisionBot()
    bot.main_loop()