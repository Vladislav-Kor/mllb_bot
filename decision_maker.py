"""
ИИ принятия решений для бота Хаябуса
"""

import time
import random
import json
from typing import Dict, List, Tuple, Optional, Any
from collections import defaultdict
from game_state import GameState
from config import BOT_CONFIG, JUNGLE_ROUTES
from utils import calculate_safety_score, weighted_choice

class DecisionMaker:
    """Система принятия решений на основе ИИ"""
    
    def __init__(self, config: Dict):
        self.config = config
        self.action_stats = {}
        self.learned_patterns = {}
        self.last_action_time = {}
        self.last_action = None
        self.last_action_details = {}
        
        # Приоритеты действий по фазам игры
        self.phase_strategies = {
            'early': self.early_game_strategy,
            'mid': self.mid_game_strategy,
            'late': self.late_game_strategy,
            'endgame': self.endgame_strategy
        }
        
        # Временные ограничения
        self.action_cooldowns = {
            'farm': 2.0,
            'gank': 8.0,
            'jungle': 3.0,
            'retreat': 1.0,
            'patrol': 1.0,
            'teamfight': 5.0,
            'objective': 10.0,
            'defend': 3.0,
            'push': 2.0
        }
        
        # Настройки агрессивности
        self.aggressiveness = config.get('aggressiveness', 0.4)
        
        # Настройки фарма
        self.farm_priority = config.get('farm_priority', 0.8)
        
        print("🧠 Инициализирован модуль принятия решений")
    
    def _get_action_key(self, action: Any) -> str:
        """Преобразует действие в строковый ключ для использования в словаре"""
        return str(action)
    
    def select_action(self, state: GameState) -> Tuple[str, Dict]:
        """Выбор действия на основе текущего состояния"""
        current_time = time.time()
        
        # Обновляем безопасность
        self.update_safety_score(state)
        
        # 1. Проверка критических условий (всегда приоритет)
        critical_action = self.check_critical_conditions(state)
        if critical_action:
            action, details = critical_action
            self.last_action = action
            self.last_action_details = details
            return action, details
        
        # 2. Выбор стратегии по фазе игры
        strategy_func = self.phase_strategies.get(state.phase, self.early_game_strategy)
        action, details = strategy_func(state, current_time)
        
        # 3. Проверка кулдауна
        if action in self.last_action_time:
            time_since_last = current_time - self.last_action_time[action]
            cooldown = self.action_cooldowns.get(action, 0)
            
            if time_since_last < cooldown:
                # Пробуем альтернативное действие
                backup_action, backup_details = self.get_backup_action(state, action)
                action, details = backup_action, {'reason': f'cooldown_{action}', 'original': action, **backup_details}
        
        # 4. Проверяем, не застряли ли мы на одном действии
        if self.last_action == action:
            action_time = current_time - self.last_action_time.get(action, 0)
            if action_time > 10.0:  # 10 секунд на одном действии - слишком долго
                random_action = random.choice(['patrol', 'jungle', 'farm'])
                action, details = random_action, {'reason': 'stuck', 'original': action}
        
        # 5. Обновляем время последнего действия
        self.last_action_time[action] = current_time
        self.last_action = action
        self.last_action_details = details
        
        return action, details
    
    def check_critical_conditions(self, state: GameState) -> Optional[Tuple[str, Dict]]:
        """Проверка критических условий"""
        # Критическое здоровье
        if state.my_health < 20:
            return ('retreat', {'reason': 'low_health', 'health': state.my_health})

        # Слишком много врагов
        if state.enemies_nearby >= 3 and state.my_health < 60:
            return ('retreat', {'reason': 'too_many_enemies', 'count': state.enemies_nearby})

        # Опасная позиция
        if state.safety_score < 0.2:
            return ('retreat', {'reason': 'dangerous_position', 'safety': state.safety_score})

        return None
    
    def early_game_strategy(self, state: GameState, current_time: float) -> Tuple[str, Dict]:
        """Стратегия ранней игры (уровни 1-5)"""
        # Ранняя игра: фарм > лес > патруль
        
        # Если рядом есть крипы на линии - фармим
        if state.creeps_nearby > 0:
            return 'farm', {'priority': 'high', 'target': 'lane_creeps', 'count': state.creeps_nearby}
        
        # Если есть лесные крипы - фармим лес
        if state.jungle_creeps_nearby > 0:
            return 'jungle', {'priority': 'medium', 'target': 'jungle_creeps', 'count': state.jungle_creeps_nearby}
        
        # Если нет крипов - идем патрулировать лес
        return 'patrol', {'priority': 'low', 'route': 'jungle_patrol'}
    
    def mid_game_strategy(self, state: GameState, current_time: float) -> Tuple[str, Dict]:
        """Стратегия средней игры (уровни 6-12)"""
        # Средняя игра: безопасный фарм > ганг > лес
        
        # Если безопасно и есть крипы - фармим
        if state.creeps_nearby > 0 and state.safety_score > 0.5:
            return 'farm', {'priority': 'high', 'target': 'lane_creeps', 'count': state.creeps_nearby}
        
        # Если есть лесные крипы и безопасно - фармим лес
        if state.jungle_creeps_nearby > 0 and state.safety_score > 0.4:
            return 'jungle', {'priority': 'medium', 'target': 'jungle_creeps', 'count': state.jungle_creeps_nearby}
        
        # Если есть враги и условия для ганга
        if self.should_gank(state):
            return 'gank', {'priority': 'medium', 'target': 'enemy_hero', 'count': state.enemies_nearby}
        
        # Если ничего нет - патрулируем
        return 'patrol', {'priority': 'low', 'area': 'jungle'}
    
    def late_game_strategy(self, state: GameState, current_time: float) -> Tuple[str, Dict]:
        """Стратегия поздней игры (уровни 13-15)"""
        # Поздняя игра: командные бои > объективы > фарм
        
        # Если много врагов - командный бой
        if state.enemies_nearby >= 2 and state.my_health > 50:
            return 'teamfight', {'priority': 'high', 'enemies': state.enemies_nearby}
        
        # Если безопасно и есть крипы - фармим
        if state.creeps_nearby > 0 and state.safety_score > 0.7:
            return 'farm', {'priority': 'medium', 'target': 'lane', 'count': state.creeps_nearby}
        
        # Если есть лесные крипы - фармим лес
        if state.jungle_creeps_nearby > 0 and state.safety_score > 0.5:
            return 'jungle', {'priority': 'medium', 'target': 'jungle_creeps', 'count': state.jungle_creeps_nearby}
        
        # По умолчанию патрулируем безопасные зоны
        return 'patrol', {'priority': 'low', 'area': 'safe_zone'}
    
    def endgame_strategy(self, state: GameState, current_time: float) -> Tuple[str, Dict]:
        """Стратегия эндгейма"""
        # Эндгейм: база > объективы > пуши
        
        # Если враги у нашей базы - защищаем
        if state.enemies_nearby >= 3 and state.map_position == 'base':
            return 'defend', {'priority': 'high', 'target': 'base', 'enemies': state.enemies_nearby}
        
        # Если безопасно - пушим линии
        if state.creeps_nearby > 0 and state.safety_score > 0.8:
            return 'push', {'priority': 'medium', 'target': 'lanes', 'count': state.creeps_nearby}
        
        # Если много золота и безопасно - ищем объективы
        if state.gold > 2000 and state.safety_score > 0.6:
            return 'objective', {'priority': 'medium', 'target': 'lord/turtle'}
        
        # По умолчанию защищаем
        return 'defend', {'priority': 'low', 'target': 'base'}
    
    def get_backup_action(self, state: GameState, unavailable_action: str) -> Tuple[str, Dict]:
        """Получение альтернативного действия"""
        backup_actions = {
            'farm': ['jungle', 'patrol', 'retreat'],
            'gank': ['farm', 'jungle', 'patrol'],
            'jungle': ['farm', 'patrol', 'retreat'],
            'retreat': ['patrol', 'jungle'],
            'teamfight': ['retreat', 'defend'],
            'objective': ['farm', 'patrol'],
            'defend': ['retreat', 'patrol'],
            'push': ['farm', 'patrol'],
            'patrol': ['farm', 'jungle']
        }
        
        alternatives = backup_actions.get(unavailable_action, ['patrol'])
        
        # Выбираем первое доступное действие
        for action in alternatives:
            if self.is_action_available(state, action):
                return action, {'reason': 'backup', 'original': unavailable_action}
        
        # Если ничего не доступно - патрулируем
        return 'patrol', {'reason': 'default'}
    
    def is_action_available(self, state: GameState, action: str) -> bool:
        """Проверка доступности действия"""
        if action == 'farm':
            return (state.creeps_nearby > 0 or state.jungle_creeps_nearby > 0) and state.safety_score > 0.3
        
        if action == 'gank':
            return self.should_gank(state)
        
        if action == 'jungle':
            return state.jungle_creeps_nearby > 0 or state.map_position == 'jungle'
        
        if action == 'retreat':
            return state.my_health < 50 or state.safety_score < 0.2
        
        if action == 'teamfight':
            return state.enemies_nearby >= 2 and state.my_health > 50
        
        if action == 'objective':
            return state.my_health > 60 and state.safety_score > 0.5
        
        if action == 'defend':
            return state.enemies_nearby >= 2
        
        if action == 'push':
            return state.creeps_nearby > 0 and state.safety_score > 0.6
        
        return True  # patrol всегда доступен
    
    def should_gank(self, state: GameState) -> bool:
        """Следует ли совершать ганг"""
        # Базовые условия для ганга
        base_conditions = (
            state.enemies_nearby > 0 and
            state.enemies_nearby <= 2 and
            state.my_health > 60 and
            state.safety_score > 0.5
        )
        
        if not base_conditions:
            return False
        
        # Проверяем статистику успешности гангов
        gank_success_rate = self.get_action_success_rate('gank')
        
        # Чем выше агрессивность, тем чаще пробуем ганковать
        return gank_success_rate > (0.5 - self.aggressiveness * 0.2)
    
    def get_action_success_rate(self, action: str) -> float:
        """Получение статистики успешности действия"""
        action_key = self._get_action_key(action)
        
        if action_key in self.action_stats:
            stats = self.action_stats[action_key]
            if stats['total'] > 0:
                return stats['success'] / stats['total']
        return 0.5  # Дефолтное значение
    
    def record_action_result(self, action: str, success: bool, details: Dict = None):
        """Запись результата действия"""
        if details is None:
            details = {}
        
        action_key = self._get_action_key(action)
        
        # Инициализируем статистику для действия, если ее еще нет
        if action_key not in self.action_stats:
            self.action_stats[action_key] = {
                'action': action,  # Сохраняем оригинальное действие
                'total': 0,
                'success': 0,
                'last_success': success
            }
        
        # Обновляем статистику
        self.action_stats[action_key]['total'] += 1
        if success:
            self.action_stats[action_key]['success'] += 1
        self.action_stats[action_key]['last_success'] = success
        
        # Сохранение паттерна
        if details:
            pattern_key = f"{action}_{'success' if success else 'fail'}_{int(time.time())}"
            if pattern_key not in self.learned_patterns:
                self.learned_patterns[pattern_key] = 0
            self.learned_patterns[pattern_key] += 1
        
        # Логируем успешные действия
        if success and action in ['farm', 'gank']:
            print(f"✅ {action.upper()}: Успешно! Детали: {details}")
    
    def get_jungle_route(self, route_name: str = 'blue_side_start') -> List[Tuple[int, int]]:
        """Получение маршрута по лесу"""
        return JUNGLE_ROUTES.get(route_name, JUNGLE_ROUTES['jungle_patrol'])
    
    def get_best_patterns(self, min_count: int = 3) -> Dict:
        """Получение лучших паттернов"""
        best_patterns = {}
        for pattern, count in self.learned_patterns.items():
            if count >= min_count:
                # Извлекаем действие из паттерна
                parts = pattern.split('_')
                if len(parts) >= 1:
                    action = parts[0]
                    success_rate = self.get_action_success_rate(action)
                    
                    if success_rate >= 0.4:  # Более низкий порог для обучения
                        best_patterns[pattern] = {
                            'count': count,
                            'success_rate': success_rate,
                            'action': action
                        }
        
        return dict(sorted(best_patterns.items(), 
                          key=lambda x: x[1]['count'], 
                          reverse=True))
    
    def should_retreat(self, state: GameState) -> bool:
        """Следует ли отступать"""
        return (
            state.my_health < 30 or
            (state.enemies_nearby >= 3 and state.my_health < 70) or
            state.safety_score < 0.15
        )
    
    def update_safety_score(self, state: GameState):
        """Обновление показателя безопасности"""
        try:
            state.safety_score = calculate_safety_score(
                enemies_nearby=state.enemies_nearby,
                health=state.my_health,
                position=state.map_position
            )
        except Exception as e:
            print(f"⚠️ Ошибка расчета безопасности: {e}")
            # Значение по умолчанию
            state.safety_score = 0.5
    
    def get_statistics(self) -> Dict:
        """Получение статистики принятия решений"""
        total_actions = sum(stats['total'] for stats in self.action_stats.values())
        successful_actions = sum(stats['success'] for stats in self.action_stats.values())
        
        # Статистика по типам действий
        action_stats_summary = {}
        for action_key, stats in self.action_stats.items():
            action = stats.get('action', action_key)
            if stats['total'] > 0:
                action_stats_summary[action] = {
                    'total': stats['total'],
                    'success': stats['success'],
                    'rate': stats['success'] / stats['total']
                }
        
        return {
            'total_actions': total_actions,
            'successful_actions': successful_actions,
            'success_rate': successful_actions / total_actions if total_actions > 0 else 0,
            'unique_patterns': len(self.learned_patterns),
            'best_patterns': self.get_best_patterns(min_count=1),
            'action_stats': action_stats_summary
        }
    
    def save_learning_data(self, filename: str):
        """Сохранение данных обучения"""
        data = {
            'action_stats': self.action_stats,
            'learned_patterns': self.learned_patterns,
            'last_action_time': self.last_action_time,
            'config': self.config
        }
        
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, default=str)
            print(f"💾 Данные обучения сохранены в {filename}")
        except Exception as e:
            print(f"❌ Ошибка сохранения данных обучения: {e}")
    
    def load_learning_data(self, filename: str):
        """Загрузка данных обучения"""
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            self.action_stats = data.get('action_stats', {})
            self.learned_patterns = data.get('learned_patterns', {})
            self.last_action_time = data.get('last_action_time', {})
            print(f"📚 Загружено {len(self.learned_patterns)} паттернов и {len(self.action_stats)} статистик действий")
        except FileNotFoundError:
            print("📂 Файл с данными обучения не найден, начинаем с нуля")
        except Exception as e:
            print(f"❌ Ошибка загрузки данных обучения: {e}")