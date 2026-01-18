"""
Состояние игры и статистика
"""

from dataclasses import dataclass, field
import math
from typing import Dict, List, Optional, Tuple
import numpy as np

@dataclass
class DetectedObject:
    """Обнаруженный объект на экране"""
    x: int
    y: int
    width: int
    height: int
    object_type: str  # 'creep', 'jungle', 'enemy', 'tower', 'base', 'objective'
    confidence: float
    health: float = 100.0
    distance: float = 0.0
    
    @property
    def position(self):
        """Центр объекта"""
        return (self.x + self.width // 2, self.y + self.height // 2)
    
    @property
    def center(self):
        """Центр объекта (альтернативное свойство)"""
        return self.position
    
    @property
    def area(self):
        """Площадь объекта"""
        return self.width * self.height

@dataclass
class BotStats:
    """Статистика бота"""
    # Основные счетчики
    cycles: int = 0
    enemies_killed: int = 0
    creeps_killed: int = 0
    jungle_camps_cleared: int = 0
    successful_ganks: int = 0
    failed_ganks: int = 0
    gank_attempts: int = 0
    combos_executed: int = 0
    vision_detections: int = 0
    total_gold: int = 300  # Начальное золото
    errors: int = 0
    
    # Дополнительная статистика
    successful_actions: int = 0
    failed_actions: int = 0
    total_actions: int = 0
    total_damage: int = 0
    damage_taken: int = 0
    time_alive: float = 0.0
    objectives_completed: int = 0
    towers_destroyed: int = 0
    assists: int = 0
    deaths: int = 0
    
    # Время
    game_start_time: float = 0.0
    last_update_time: float = 0.0
    
    def increment(self, stat_name: str, value: int = 1):
        """Увеличить статистику"""
        if hasattr(self, stat_name):
            current = getattr(self, stat_name)
            setattr(self, stat_name, current + value)
        else:
            print(f"⚠️ Статистика '{stat_name}' не существует")
    
    def get_success_rate(self) -> float:
        """Получить общий процент успешности"""
        if self.total_actions == 0:
            return 0.0
        return self.successful_actions / self.total_actions
    
    def get_kda(self) -> str:
        """Получить KDA"""
        deaths = max(self.deaths, 1)  # Чтобы избежать деления на 0
        return f"{self.enemies_killed}/{self.deaths}/{self.assists}"
    
    def to_dict(self) -> Dict:
        """Преобразовать в словарь"""
        return {
            'cycles': self.cycles,
            'enemies_killed': self.enemies_killed,
            'creeps_killed': self.creeps_killed,
            'jungle_camps_cleared': self.jungle_camps_cleared,
            'successful_ganks': self.successful_ganks,
            'gank_attempts': self.gank_attempts,
            'combos_executed': self.combos_executed,
            'total_gold': self.total_gold,
            'successful_actions': self.successful_actions,
            'failed_actions': self.failed_actions,
            'total_actions': self.total_actions,
            'errors': self.errors,
            'success_rate': self.get_success_rate(),
            'kda': self.get_kda()
        }
    
    def reset(self):
        """Сбросить статистику"""
        self.__init__()

@dataclass
class GameState:
    """Текущее состояние игры"""
    # Статистика героя
    my_health: float = 100.0
    my_mana: float = 100.0
    my_level: int = 1
    my_gold: int = 300
    my_experience: float = 0.0
    
    # Обнаруженные объекты
    visible_objects: List[DetectedObject] = field(default_factory=list)
    
    # Счетчики
    enemies_nearby: int = 0
    creeps_nearby: int = 0
    jungle_creeps_nearby: int = 0
    allies_nearby: int = 0
    towers_nearby: int = 0
    
    # Позиция и карта
    map_position: str = "ally_territory"  # 'ally_territory', 'jungle', 'enemy_territory', 'base', 'river'
    safety_score: float = 1.0
    
    # Фаза игры
    phase: str = "early"  # 'early', 'mid', 'late', 'endgame'
    
    # Готовность скиллов
    skills_ready: Dict[str, bool] = field(default_factory=lambda: {
        's1': True,
        's2': True,
        's3': True,
        'ult': True
    })
    
    # Время игры
    game_time: float = 0.0
    
    # Дополнительная информация
    enemy_composition: List[str] = field(default_factory=list)
    objective_status: Dict[str, bool] = field(default_factory=dict)
    
    def update_counts(self, screen_center: tuple):
        """Обновить счетчики объектов на основе расстояния"""
        self.enemies_nearby = 0
        self.creeps_nearby = 0
        self.jungle_creeps_nearby = 0
        
        if not screen_center:
            return
            
        center_x, center_y = screen_center
        
        for obj in self.visible_objects:
            # Рассчитываем расстояние до центра экрана
            obj_x, obj_y = obj.position
            distance = np.sqrt((obj_x - center_x) ** 2 + (obj_y - center_y) ** 2)
            obj.distance = distance
            
            # Считаем объекты вблизи (в пределах 300 пикселей)
            if distance < 300:
                if obj.object_type == 'enemy':
                    self.enemies_nearby += 1
                elif obj.object_type == 'creep':
                    self.creeps_nearby += 1
                elif obj.object_type == 'jungle':
                    self.jungle_creeps_nearby += 1
    
    def get_nearest_enemy(self, screen_center: tuple) -> Optional[DetectedObject]:
        """Получить ближайшего врага"""
        if not self.visible_objects or not screen_center:
            return None
            
        center_x, center_y = screen_center
        enemies = [obj for obj in self.visible_objects if obj.object_type == 'enemy']
        
        if not enemies:
            return None
            
        # Находим ближайшего врага
        nearest = min(enemies, key=lambda obj: np.sqrt(
            (obj.position[0] - center_x) ** 2 + (obj.position[1] - center_y) ** 2
        ))
        return nearest
    
    def get_nearest_creep(self, screen_center: tuple) -> Optional[DetectedObject]:
        """Получить ближайшего крипа"""
        if not self.visible_objects or not screen_center:
            return None
            
        center_x, center_y = screen_center
        creeps = [obj for obj in self.visible_objects 
                 if obj.object_type in ['creep', 'jungle']]
        
        if not creeps:
            return None
            
        # Находим ближайшего крипа
        nearest = min(creeps, key=lambda obj: np.sqrt(
            (obj.position[0] - center_x) ** 2 + (obj.position[1] - center_y) ** 2
        ))
        return nearest
    
    def is_safe_to_gank(self) -> bool:
        """Безопасно ли совершать ганг"""
        return (
            self.enemies_nearby <= 2 and
            self.my_health > 50 and
            self.safety_score > 0.4
        )
    
    def get_state_snapshot(self) -> Dict:
        """Получить снимок состояния для обучения"""
        return {
            'health': self.my_health,
            'level': self.my_level,
            'gold': self.my_gold,
            'position': self.map_position,
            'enemies_nearby': self.enemies_nearby,
            'creeps_nearby': self.creeps_nearby,
            'jungle_creeps_nearby': self.jungle_creeps_nearby,
            'phase': self.phase,
            'safety_score': self.safety_score,
            'game_time': self.game_time,
            'skills_ready': self.skills_ready.copy()
        }
    
    def update_from_analysis(self, analysis: Dict):
        """Обновить состояние из анализа"""
        if 'interface' in analysis:
            interface = analysis['interface']
            self.my_health = interface.get('health', self.my_health)
            self.my_mana = interface.get('mana', self.my_mana)
            self.my_level = interface.get('level', self.my_level)
            self.my_gold = interface.get('gold', self.my_gold)
            self.skills_ready = interface.get('skills_ready', self.skills_ready)
        
        if 'minimap' in analysis:
            self.map_position = analysis['minimap'].get('position', self.map_position)
        
        if 'objects' in analysis:
            self.visible_objects = analysis['objects']
            
@dataclass
class GameObject:
    """Объект в игре"""
    type: str  # 'creep', 'jungle', 'hero', 'tower'
    position: Tuple[int, int]
    confidence: float
    timestamp: float
    health: float = 100.0
    is_enemy: bool = False
    distance: float = 0.0
    
    def calculate_distance(self, from_pos: Tuple[int, int]) -> float:
        """Вычисление расстояния до точки"""
        return math.sqrt((self.position[0] - from_pos[0])**2 + 
                        (self.position[1] - from_pos[1])**2)

@dataclass
class GameState:
    """Состояние игры"""
    my_health: float = 100.0
    my_mana: float = 100.0
    my_level: int = 1
    my_gold: int = 300
    map_position: str = "base"
    game_time: int = 0
    phase: str = "early"
    visible_objects: List[GameObject] = field(default_factory=list)
    enemies_nearby: int = 0
    creeps_nearby: int = 0
    jungle_creeps_nearby: int = 0
    in_combat: bool = False
    ult_ready: bool = False
    skills_ready: Dict[str, bool] = field(default_factory=lambda: {
        's1': True, 's2': True, 's3': True, 'ult': False
    })
    safety_score: float = 1.0  # 1.0 = безопасно, 0.0 = опасно
    
    def update_counts(self, screen_center: Optional[Tuple[int, int]] = None):
        """Обновление счетчиков объектов"""
        self.enemies_nearby = 0
        self.creeps_nearby = 0
        self.jungle_creeps_nearby = 0
        
        for obj in self.visible_objects:
            # Вычисляем расстояние если передан центр экрана
            if screen_center:
                obj.distance = obj.calculate_distance(screen_center)
            
            if obj.type == 'hero' and obj.is_enemy:
                self.enemies_nearby += 1
            elif obj.type == 'creep':
                self.creeps_nearby += 1
            elif obj.type == 'jungle':
                self.jungle_creeps_nearby += 1
    
    def get_nearest_creep(self, screen_center: Tuple[int, int]) -> Optional[GameObject]:
        """Получение ближайшего крипа"""
        creeps = [obj for obj in self.visible_objects 
                 if obj.type in ['creep', 'jungle']]
        
        if not creeps:
            return None
        
        # Вычисляем расстояния
        for creep in creeps:
            creep.distance = creep.calculate_distance(screen_center)
        
        # Выбираем ближайшего
        return min(creeps, key=lambda x: x.distance)
    
    def get_nearest_enemy(self, screen_center: Tuple[int, int]) -> Optional[GameObject]:
        """Получение ближайшего врага"""
        enemies = [obj for obj in self.visible_objects 
                  if obj.type == 'hero' and obj.is_enemy]
        
        if not enemies:
            return None
        
        # Вычисляем расстояния
        for enemy in enemies:
            enemy.distance = enemy.calculate_distance(screen_center)
        
        # Выбираем ближайшего с низким ХП
        return min(enemies, key=lambda x: (x.distance, x.health))
    
    def get_state_snapshot(self) -> Dict:
        """Снимок состояния для обучения"""
        return {
            'health': self.my_health,
            'level': self.my_level,
            'gold': self.my_gold,
            'position': self.map_position,
            'enemies_nearby': self.enemies_nearby,
            'creeps_nearby': self.creeps_nearby,
            'jungle_creeps_nearby': self.jungle_creeps_nearby,
            'phase': self.phase,
            'safety_score': self.safety_score,
            'timestamp': time.time()
        }
    
    def is_safe_to_farm(self) -> bool:
        """Безопасно ли фармить"""
        return (
            self.safety_score > 0.5 and
            self.enemies_nearby == 0 and
            self.my_health > 30
        )
    
    def is_safe_to_gank(self) -> bool:
        """Безопасно ли гангать"""
        return (
            self.safety_score > 0.3 and
            self.enemies_nearby <= 2 and
            self.my_health > 60 and
            self.my_level >= 4
        )