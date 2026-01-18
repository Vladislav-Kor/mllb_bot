"""
Основной класс бота Хаябуса с продвинутым обучением
"""

import time
import random
import threading
from typing import Dict, Any, Optional
import keyboard
from game_state import GameState, BotStats
from vision_engine import VisionEngine
from decision_maker import DecisionMaker
from input_controller import InputController
from combo_system import ComboSystem
from config import SCREEN_PROFILES, BOT_CONFIG, CONTROL_KEYS, JUNGLE_ROUTES
from utils import print_banner, print_status, get_screen_center, get_screen_size

# Импорт ультра-обучения (опционально)
try:
    from ultra_learning import UltraLearningEngine, integrate_ultra_learning
    ULTRA_LEARNING_AVAILABLE = True
except ImportError:
    ULTRA_LEARNING_AVAILABLE = False
    print("⚠️ Ультра-обучение не доступно, используем стандартное")

class HayabusaBot:
    """Главный класс бота Хаябуса с AI обучением"""
    
    def __init__(self):
        print_banner("🤖 MLBB ХАЯБУСА БОТ v3.0 AI EDITION", 70)
        
        # Инициализация состояния
        self.state = GameState()
        self.stats = BotStats()
        self.config = BOT_CONFIG.copy()
        
        # Счетчики циклов
        self.cycle_count = 0
        self.game_timer = 0
        self.running = False
        self.paused = False
        self.last_action = None
        
        # Таймеры действий
        self.last_action_time = {
            'farm': 0,
            'gank': 0,
            'jungle': 0,
            'retreat': 0,
            'patrol': 0
        }
        
        # Настройка экрана и координат
        self.init_screen_components()
        
        # Инициализация систем
        self.combo_system = ComboSystem()
        self.vision_engine = VisionEngine(
            self.screen_regions, 
            self.config.get('vision_debug', False)
        )
        self.input_controller = InputController(
            self.joystick_center,
            self.joystick_radius,
            self.attack_button,
            self.skill_buttons
        )
        self.decision_maker = DecisionMaker(self.config)
        
        # Инициализация системы обучения
        self.init_learning_system()
        
        # Загружаем сохраненные данные
        self.load_saved_data()
        
        print("\n✅ Бот инициализирован и готов к работе")
        print(f"🧠 Используется: {self.learning_type}")
    
    def init_learning_system(self):
        """Инициализация системы обучения"""
        self.learning_type = "стандартное"
        
        if ULTRA_LEARNING_AVAILABLE and self.config.get('use_ultra_learning', True):
            try:
                self.learning_engine = UltraLearningEngine(
                    data_dir="ultra_learning_data",
                    use_neural=True
                )
                self.learning_type = "УЛЬТРА-обучение с нейросетью"
                
                # Интеграция ультра-обучения в логику бота
                self = integrate_ultra_learning(self)
                
            except Exception as e:
                print(f"⚠️ Ошибка ультра-обучения: {e}")
                self.init_standard_learning()
        else:
            self.init_standard_learning()
    
    def init_standard_learning(self):
        """Инициализация стандартного обучения"""
        try:
            from learning_engine import EnhancedLearningEngine
            self.learning_engine = EnhancedLearningEngine(
                data_dir="data", 
                model_dir="models"
            )
        except ImportError:
            print("⚠️ EnhancedLearningEngine не найден, используем базовую систему")
            # Создаем простую систему обучения
            self.learning_engine = SimpleLearningEngine()
    
    def init_screen_components(self):
        """Инициализация компонентов экрана"""
        screen_width, screen_height = get_screen_size()
        
        # Выбор профиля разрешения
        best_res = min(SCREEN_PROFILES.keys(), 
                      key=lambda r: abs(r[0] - screen_width) + abs(r[1] - screen_height))
        profile = SCREEN_PROFILES[best_res]
        
        self.joystick_center = profile['joystick_center']
        self.attack_button = profile['attack_button']
        self.joystick_radius = profile['joystick_radius']
        
        # Кнопки скиллов
        self.skill_buttons = {
            's1': (int(screen_width * 0.78), int(screen_height * 0.88)),
            's2': (int(screen_width * 0.85), int(screen_height * 0.88)),
            's3': (int(screen_width * 0.92), int(screen_height * 0.88)),
            'ult': (int(screen_width * 0.96), int(screen_height * 0.78)),
        }
        
        # Области экрана для анализа
        self.screen_regions = {
            'minimap': (20, 20, 200, 200),
            'health_bar': (screen_width//2 - 100, 20, 200, 30),
            'mana_bar': (screen_width//2 - 100, 50, 200, 20),
            'center_screen': (screen_width//2 - 200, screen_height//2 - 200, 400, 400),
            'skill_indicators': (int(screen_width*0.75), int(screen_height*0.85), 200, 100),
            'gold_area': (screen_width - 200, 30, 180, 40),
            'level_area': (screen_width//2 - 50, screen_height - 100, 100, 30),
        }
        
        print(f"📺 Разрешение: {screen_width}x{screen_height}")
        print(f"🎮 Джойстик: {self.joystick_center}")
        print(f"⚔️ Атака: {self.attack_button}")
        print(f"💫 Навыки: {len(self.skill_buttons)} кнопок")
    
    def load_saved_data(self):
        """Загрузка сохраненных данных"""
        try:
            # Загружаем комбо
            combos_loaded = self.combo_system.load_combos()
            if combos_loaded:
                print(f"📂 Загружено {combos_loaded} комбо")
            
            # Загружаем данные обучения
            if hasattr(self.learning_engine, 'load_saved_data'):
                self.learning_engine.load_saved_data()
            elif hasattr(self.learning_engine, 'load_ultra_data'):
                self.learning_engine.load_ultra_data()
            
        except Exception as e:
            print(f"⚠️ Ошибка загрузки данных: {e}")
    
    def main_loop(self):
        """Главный цикл бота"""
        print_banner("УПРАВЛЕНИЕ БОТОМ", 70)
        print("F1    - Статистика")
        print("F2    - Сохранить данные")
        print("F3    - Переключить отладку зрения")
        print("F4    - Показать обученные паттерны")
        print("F9    - Старт/Стоп бота")
        print("F10   - Пауза/Продолжить")
        print("ESC   - Выход")
        print("=" * 70)
        
        print("\n⏱️ Запуск через 3 секунды...")
        for i in range(3, 0, -1):
            print(f"{i}...")
            time.sleep(1)
        
        print("🤖 БОТ ЗАПУЩЕН! Используйте F9 для старта.")
        
        # Запускаем поток автосохранения
        self.start_auto_save()
        
        try:
            while True:
                # Обработка управления
                self.handle_controls()
                
                # Основная логика работы
                if self.running and not self.paused:
                    self.game_cycle()
                
                # Небольшая пауза для снижения нагрузки
                time.sleep(0.05)
                
        except KeyboardInterrupt:
            print("\n\n🛑 Бот остановлен пользователем")
        except Exception as e:
            print(f"\n❌ Критическая ошибка: {e}")
            import traceback
            traceback.print_exc()
        finally:
            self.cleanup()
    
    def handle_controls(self):
        """Обработка клавиш управления"""
        # Старт/Стоп бота
        if keyboard.is_pressed(CONTROL_KEYS['toggle_bot']):
            self.running = not self.running
            status = "АКТИВИРОВАН" if self.running else "ОСТАНОВЛЕН"
            print(f"\n{'▶️' if self.running else '⏸️'} БОТ {status}")
            time.sleep(0.3)
        
        # Пауза/Продолжить
        if keyboard.is_pressed('F10'):
            self.paused = not self.paused
            status = "ПАУЗА" if self.paused else "ПРОДОЛЖЕНИЕ"
            print(f"\n⏯️ {status}")
            time.sleep(0.3)
        
        # Статистика
        if keyboard.is_pressed(CONTROL_KEYS['stats']):
            self.show_stats()
            time.sleep(0.3)
        
        # Сохранение данных
        if keyboard.is_pressed(CONTROL_KEYS['save_learning']):
            self.save_learning_data()
            time.sleep(0.3)
        
        # Отладка зрения
        if keyboard.is_pressed(CONTROL_KEYS['toggle_vision_debug']):
            self.config['vision_debug'] = not self.config.get('vision_debug', False)
            self.vision_engine.debug_mode = self.config['vision_debug']
            status = "ВКЛ" if self.config['vision_debug'] else "ВЫКЛ"
            print(f"\n👁️ Отладка зрения: {status}")
            time.sleep(0.3)
        
        # Показать паттерны
        if keyboard.is_pressed('F4'):
            self.show_learned_patterns()
            time.sleep(0.3)
        
        # Выход
        if keyboard.is_pressed(CONTROL_KEYS['exit']):
            print("\n🛑 Завершение работы...")
            raise KeyboardInterrupt
    
    def game_cycle(self):
        """Один цикл игры"""
        cycle_start = time.time()
        self.cycle_count += 1

        try:
             # 1. Анализ экрана (с оптимизацией частоты)
            analysis = self.vision_engine.analyze_screen()
            print(f"DEBUG: Анализ экрана: {analysis}")

            # 2. Обновление состояния
            self.update_state(analysis)

            # Отладочный вывод состояния
            print(f"DEBUG: Здоровье: {self.state.my_health}, Безопасность: {self.state.safety_score}, Враги: {self.state.enemies_nearby}")

            # 3. Выбор действия (с использованием AI обучения)
            action, action_details = self.select_action_with_ai()
            self.last_action = action
            
            # 4. Выполнение действия
            result = self.execute_action(action, action_details)
            
            # 5. Запись результата для обучения
            self.record_learning_data(action, result)
            
            # 6. Обновление статистики игры
            self.update_game_stats()
            
            # 7. Периодический вывод статуса
            if self.cycle_count % 5 == 0:  # Каждые 5 циклов
                self.print_game_status()
            
            # 8. Периодическое обучение
            if self.cycle_count % 25 == 0:
                self.perform_learning()
            
            # 9. Контроль времени цикла
            cycle_time = time.time() - cycle_start
            if cycle_time > 0.5:
                print(f"⚠️ Длинный цикл: {cycle_time:.2f}с")
            
        except Exception as e:
            print(f"❌ Ошибка в цикле игры: {e}")
            self.stats.errors += 1
    
    def select_action_with_ai(self):
        """Выбор действия с использованием AI обучения"""
        try:
            # Если есть ультра-обучение, используем его
            if hasattr(self, 'ultra_engine'):
                possible_actions = ['farm', 'gank', 'jungle', 'retreat', 'patrol']
                action, confidence = self.ultra_engine.select_ultra_action(
                    state=self.state.__dict__,
                    possible_actions=possible_actions
                )
                
                if confidence > 0.4:  # Доверяем если уверенность > 40%
                    details = {'confidence': confidence, 'source': 'ultra_ai'}
                    print(f"🎯 AI выбрал: {action} (уверенность: {confidence:.1%})")
                    return action, details
            
            # Используем стандартный DecisionMaker
            action, details = self.decision_maker.select_action(self.state)
            details['source'] = 'decision_maker'
            
            return action, details
            
        except Exception as e:
            print(f"⚠️ Ошибка AI выбора: {e}")
            # Возвращаем безопасное действие
            return 'patrol', {'reason': 'fallback'}
    
    def update_state(self, analysis: Dict):
        """Обновление состояния игры"""
        if not analysis:
            return
        
        # Обновление объектов
        if 'objects' in analysis:
            self.state.visible_objects = analysis['objects']
            screen_center = get_screen_center()
            self.state.update_counts(screen_center)
        
        # Обновление интерфейса
        if 'interface' in analysis:
            interface = analysis['interface']
            self.state.my_health = interface.get('health', self.state.my_health)
            self.state.my_mana = interface.get('mana', self.state.my_mana)
            self.state.my_level = interface.get('level', self.state.my_level)
            self.state.my_gold = interface.get('gold', self.state.my_gold)
            self.state.skills_ready = interface.get('skills_ready', self.state.skills_ready)
        
        # Обновление мини-карты
        if 'minimap' in analysis:
            self.state.map_position = analysis['minimap'].get('position', 'unknown')
        
        # Обновляем фазу игры
        self.update_game_phase()
        
        # Обновляем показатель безопасности
        if hasattr(self.decision_maker, 'update_safety_score'):
            self.decision_maker.update_safety_score(self.state)
        
        # Обновляем статистику зрения
        if 'objects' in analysis:
            self.stats.vision_detections += len(analysis['objects'])
    
    def update_game_phase(self):
        """Обновление фазы игры"""
        # В реальной игре это должно основываться на времени
        # Сейчас используем уровень как прокси
        if self.state.my_level < 5:
            self.state.phase = "early"
        elif self.state.my_level < 10:
            self.state.phase = "mid"
        elif self.state.my_level < 15:
            self.state.phase = "late"
        else:
            self.state.phase = "endgame"
    
    def execute_action(self, action: str, details: Dict) -> Dict:
        """Выполнение выбранного действия"""
        result = {
            'success': False,
            'action': action,
            'details': details,
            'damage_dealt': 0,
            'damage_taken': 0,
            'kills': 0,
            'gold_earned': 0,
            'creeps_killed': 0,
            'time_taken': 0,
            'health_change': 0,
            'error': None
        }
        
        start_time = time.time()
        initial_health = self.state.my_health
        
        try:
            # Проверяем время с последнего выполнения этого действия
            current_time = time.time()
            if action in self.last_action_time:
                time_since_last = current_time - self.last_action_time[action]
                if time_since_last < 2.0:  # 2 секунды минимальный интервал
                    print(f"⏳ Действие {action} на кулдауне")
                    return result
            
            # Выполняем действие
            if action == 'farm':
                result = self.execute_farming()
            
            elif action == 'jungle':
                result = self.execute_jungle_clear()
            
            elif action == 'gank':
                result = self.execute_ganking()
            
            elif action == 'patrol':
                result = self.execute_patrol()
            
            elif action == 'retreat':
                result = self.execute_retreat()
            
            elif action == 'teamfight':
                result = self.execute_teamfight()
            
            else:
                result = self.execute_default_action()
            
            # Обновляем время последнего выполнения
            self.last_action_time[action] = current_time
            
        except Exception as e:
            result['error'] = str(e)
            result['success'] = False
            self.stats.errors += 1
            print(f"❌ Ошибка выполнения {action}: {e}")
        
        finally:
            # Рассчитываем изменение здоровья
            result['health_change'] = initial_health - self.state.my_health
            result['time_taken'] = time.time() - start_time
            
            # Если действие успешно, обновляем статистику
            if result['success']:
                self.stats.successful_actions += 1
            else:
                self.stats.failed_actions += 1
        
        return result
    
    def execute_farming(self) -> Dict:
        """Выполнение фарма"""
        print("🌿 УМНЫЙ ФАРМ...")
        
        result = {
            'success': False,
            'creeps_killed': 0,
            'gold_earned': 0,
            'damage_dealt': random.randint(300, 800),
            'details': {}
        }
        
        # Проверяем наличие крипов
        if self.state.creeps_nearby == 0 and self.state.jungle_creeps_nearby == 0:
            print("👻 Крипов нет, ищу...")
            found = self.search_for_creeps()
            if not found:
                print("⚠️ Крипов не нашел")
                return result
        
        # Выбираем ближайшего крипа
        screen_center = get_screen_center()
        target = self.state.get_nearest_creep(screen_center)
        
        if not target:
            print("⚠️ Не могу найти цель для фарма")
            return result
        
        print(f"🎯 Цель: {target.type} (расстояние: {int(target.distance)}px)")
        
        # Подход к цели
        if target.distance > 150:
            print(f"📍 Подхожу к цели...")
            self.input_controller.move_toward_object(target.position, min_distance=100)
            time.sleep(0.3)
        
        # Выбор комбо в зависимости от типа крипа
        if target.type == 'jungle':
            combo_name = "JUNGLE CLEAR"
            gold_reward = 80
        else:
            combo_name = "LANE FARM"
            gold_reward = 60
        
        # Выполнение комбо
        print(f"💥 Использую {combo_name}...")
        success = self.execute_combo(combo_name)
        
        if success:
            result['success'] = True
            result['creeps_killed'] = 1
            result['gold_earned'] = gold_reward
            
            # Обновление статистики
            if target.type == 'jungle':
                self.stats.jungle_camps_cleared += 1
                print(f"✅ Очищен лагерь! +{gold_reward} золота")
            else:
                self.stats.creeps_killed += 1
                print(f"✅ Крип убит! +{gold_reward} золота")
            
            self.stats.total_gold += gold_reward
            self.last_action_time['farm'] = time.time()
        else:
            print("⚠️ Фарм не удался")
        
        return result
    
    def execute_jungle_clear(self) -> Dict:
        """Очистка леса"""
        print("🌲 ОЧИСТКА ЛЕСА...")
        
        result = {
            'success': False,
            'camps_cleared': 0,
            'gold_earned': 0,
            'damage_dealt': random.randint(500, 1200),
            'details': {}
        }
        
        # Если есть крипы в лесу - фармим их
        if self.state.jungle_creeps_nearby > 0:
            print(f"✅ Нашел {self.state.jungle_creeps_nearby} крипов в лесу")
            return self.execute_farming()
        
        # Если нет - идем по маршруту
        print("🔍 Ищу крипов по маршруту леса...")
        
        # Выбираем маршрут в зависимости от фазы игры
        route_name = 'blue_side_start' if self.state.phase == 'early' else 'jungle_patrol'
        route = JUNGLE_ROUTES.get(route_name, JUNGLE_ROUTES['jungle_patrol'])
        
        camps_cleared = 0
        gold_earned = 0
        
        for angle, description, force, duration in route[:3]:  # Только первые 3 точки
            if not self.running:
                break
            
            print(f"  {description}")
            self.input_controller.drag_joystick_to_angle(angle, force)
            time.sleep(duration / 2)  # Двигаемся половину времени
            
            # Анализируем после движения
            analysis = self.vision_engine.analyze_screen()
            self.update_state(analysis)
            
            # Если нашли крипов - фармим
            if self.state.jungle_creeps_nearby > 0:
                print(f"  ✅ Нашел крипов!")
                farm_result = self.execute_farming()
                if farm_result['success']:
                    camps_cleared += 1
                    gold_earned += farm_result['gold_earned']
            
            # Оставшаяся половина времени для завершения движения
            time.sleep(duration / 2)
        
        if camps_cleared > 0:
            result['success'] = True
            result['camps_cleared'] = camps_cleared
            result['gold_earned'] = gold_earned
            self.last_action_time['jungle'] = time.time()
            print(f"✅ Очищено {camps_cleared} лагерей, +{gold_earned} золота")
        else:
            print("⚠️ Крипов в лесу не найдено")
        
        return result
    
    def execute_ganking(self) -> Dict:
        """Выполнение ганга"""
        print("🎯 АНАЛИЗ ГАНГА...")
        
        result = {
            'success': False,
            'enemy_killed': False,
            'gold_earned': 0,
            'damage_dealt': 0,
            'details': {}
        }
        
        # Проверка условий
        current_time = time.time()
        
        if not self.state.is_safe_to_gank():
            print("⚠️ Небезопасно для ганга")
            return result
        
        if self.state.enemies_nearby == 0:
            print("⚠️ Врагов не видно")
            return result
        
        # Поиск цели
        screen_center = get_screen_center()
        target = self.state.get_nearest_enemy(screen_center)
        
        if not target:
            print("⚠️ Не могу найти цель для ганга")
            return result
        
        print(f"🎯 Цель: вражеский герой (расстояние: {int(target.distance)}px)")
        
        # Подход к цели
        if target.distance > 200:
            print("📍 Подхожу к цели...")
            self.input_controller.move_toward_object(target.position, min_distance=150)
            time.sleep(0.3)
        
        # Выполнение комбо ганга
        print("💥 АТАКА!")
        success = self.execute_combo("QUICK GANK")
        
        if success:
            # Имитация результата (в реальной игре нужно детектить смерть врага)
            kill_chance = 0.6  # 60% шанс убийства
            
            if random.random() < kill_chance:
                result['success'] = True
                result['enemy_killed'] = True
                result['gold_earned'] = 300
                result['damage_dealt'] = random.randint(800, 1500)
                
                self.stats.enemies_killed += 1
                self.stats.successful_ganks += 1
                self.stats.total_gold += 300
                self.last_action_time['gank'] = current_time
                
                print("✅ Успешный ганг! Враг убит! +300 золота")
            else:
                result['success'] = False
                result['damage_dealt'] = random.randint(300, 700)
                self.stats.failed_ganks += 1
                print("⚠️ Ганг не удался, враг выжил")
        else:
            self.stats.failed_ganks += 1
            print("⚠️ Ошибка выполнения комбо")
        
        self.stats.gank_attempts += 1
        return result
    
    def execute_patrol(self) -> Dict:
        """Патрулирование"""
        print("🛡️ ПАТРУЛИРОВАНИЕ...")
        
        # Выбираем направление патруля
        directions = [
            (315, "↖ Вверх-влево"),
            (0, "↑ Вверх"),
            (45, "↗ Вверх-вправо"),
            (270, "← Влево"),
            (90, "→ Вправо"),
            (225, "↙ Вниз-влево"),
            (180, "↓ Вниз"),
            (135, "↘ Вниз-вправо")
        ]
        
        angle, description = random.choice(directions)
        force = random.uniform(0.3, 0.7)
        
        print(f"  {description} (сила: {force:.1f})")
        self.input_controller.drag_joystick_to_angle(angle, force)
        time.sleep(1.0)
        
        return {
            'success': True,
            'details': {'direction': angle, 'force': force}
        }
    
    def execute_retreat(self) -> Dict:
        """Отступление"""
        print("🏃 ОТСТУПЛЕНИЕ!")

        # Определяем направление отступления (к базе)
        retreat_angle = 225  # Влево-вниз как пример

        # Используем комбо для побега
        escape_success = self.execute_combo("ESCAPE COMBO")

        # Отступаем
        self.input_controller.drag_joystick_to_angle(retreat_angle, 0.8)
        time.sleep(0.8)  # Уменьшим время отступления

        return {
            'success': escape_success,
            'details': {'reason': 'low_health' if self.state.my_health < 30 else 'danger'}
        }
    
    def execute_teamfight(self) -> Dict:
        """Командный бой"""
        print("⚔️ КОМАНДНЫЙ БОЙ!")
        
        # Используем ультимейт комбо
        success = self.execute_combo("ULTIMATE BURST")
        
        # Отступаем после боя
        time.sleep(0.5)
        self.input_controller.safe_retreat()
        
        return {
            'success': success,
            'damage_dealt': random.randint(1000, 2500) if success else random.randint(300, 800),
            'details': {'enemies': self.state.enemies_nearby}
        }
    
    def execute_default_action(self) -> Dict:
        """Действие по умолчанию"""
        print("🗺️ ИССЛЕДОВАНИЕ...")
        
        # Случайное движение
        angle = random.randint(0, 360)
        force = random.uniform(0.3, 0.6)
        self.input_controller.drag_joystick_to_angle(angle, force)
        time.sleep(1.5)
        
        return {
            'success': True,
            'details': {'exploration': True, 'angle': angle}
        }
    
    def search_for_creeps(self) -> bool:
        """Поиск крипов"""
        print("🔍 ПОИСК КРИПОВ...")
        
        # Быстрый поиск по 4 направлениям
        search_angles = [0, 90, 180, 270]
        
        for angle in search_angles:
            self.input_controller.drag_joystick_to_angle(angle, 0.4)
            time.sleep(0.5)
            
            # Анализируем после движения
            analysis = self.vision_engine.analyze_screen()
            self.update_state(analysis)
            
            if self.state.creeps_nearby > 0 or self.state.jungle_creeps_nearby > 0:
                print(f"✅ Нашел крипов под углом {angle}°")
                return True
        
        print("👻 Крипов не найдено")
        return False
    
    def execute_combo(self, combo_name: str) -> bool:
        """Выполнение комбо"""
        combo = self.combo_system.get_combo(combo_name)
        if not combo:
            print(f"⚠️ Комбо '{combo_name}' не найдено")
            return False
        
        print(f"💥 КОМБО: {combo.name}")
        
        start_time = time.time()
        successful_steps = 0
        total_steps = len(combo.skills)
        
        for i, skill in enumerate(combo.skills):
            if not self.running:
                break
            
            if skill == 'attack':
                self.input_controller.basic_attack(1)
                successful_steps += 1
            else:
                # Проверяем готовность скилла
                if self.state.skills_ready.get(skill, True):  # По умолчанию True для симуляции
                    if self.input_controller.use_skill(skill):
                        successful_steps += 1
                else:
                    print(f"⏳ Скилл {skill} не готов, пропускаю")
            
            # Пауза между шагами
            if i < len(combo.timing):
                time.sleep(combo.timing[i])
            else:
                time.sleep(0.2)  # Дефолтная пауза
        
        # Определяем успешность
        success_rate = successful_steps / total_steps if total_steps > 0 else 0
        success = success_rate >= 0.6  # 60% успешных шагов
        
        # Обновление статистики комбо
        combo.update_success(success)
        self.stats.combos_executed += 1
        
        # Запись в обучение
        execution_time = time.time() - start_time
        
        if hasattr(self.learning_engine, 'record_combo'):
            self.learning_engine.record_combo(combo_name, success, execution_time)
        
        if success:
            print(f"✅ Комбо успешно выполнено ({successful_steps}/{total_steps} шагов)")
        else:
            print(f"⚠️ Комбо выполнено частично ({successful_steps}/{total_steps} шагов)")
        
        return success
    
    def record_learning_data(self, action: str, result: Dict):
        """Запись данных для обучения"""
        try:
            # Запись в систему принятия решений
            self.decision_maker.record_action_result(
                action, 
                result.get('success', False), 
                result.get('details', {})
            )
            
            # Запись в движок обучения
            if hasattr(self.learning_engine, 'record_action'):
                # Подготовка контекста
                context = {
                    'phase': self.state.phase,
                    'region': self.state.map_position,
                    'health': self.state.my_health,
                    'level': self.state.my_level,
                    'gold': self.state.my_gold
                }
                
                self.learning_engine.record_action(
                    state=self.state.__dict__,
                    action=action,
                    result=result,
                    context=context
                )
            
            # Для ультра-обучения нужна дополнительная информация
            if hasattr(self, 'ultra_engine'):
                # Запись уже происходит в game_cycle через integrate_ultra_learning
                pass
            
            # Обновление статистики
            stats_update = {
                'cycles': 1,
                'enemies_killed': result.get('kills', 0),
                'creeps_killed': result.get('creeps_killed', 0),
                'gold_earned': result.get('gold_earned', 0),
            }
            
            if hasattr(self.learning_engine, 'update_stats'):
                self.learning_engine.update_stats(stats_update)
            
        except Exception as e:
            print(f"⚠️ Ошибка записи данных обучения: {e}")
    
    def perform_learning(self):
        """Выполнение цикла обучения"""
        try:
            if hasattr(self.learning_engine, 'train_from_experience'):
                self.learning_engine.train_from_experience()
            
            # Для ультра-обучения
            if hasattr(self, 'ultra_engine') and hasattr(self.ultra_engine, 'deep_train'):
                self.ultra_engine.deep_train()
                
        except Exception as e:
            print(f"⚠️ Ошибка обучения: {e}")
    
    def update_game_stats(self):
        """Обновление статистики игры"""
        self.stats.cycles += 1
        self.game_timer += 1
        
        # Автоматическое увеличение золота и уровня (симуляция)
        if self.stats.cycles % 20 == 0:
            gold_increment = random.randint(30, 100)
            self.stats.total_gold += gold_increment
            self.state.my_gold = self.stats.total_gold
        
        if self.stats.cycles % 50 == 0 and self.state.my_level < 15:
            self.state.my_level += 1
            print(f"🎉 Уровень повышен до {self.state.my_level}!")
    
    def print_game_status(self):
        """Вывод статуса игры"""
        print_status(
            self.state.phase,
            self.state.my_level,
            self.stats.total_gold,
            int(self.state.my_health),
            self.stats.enemies_killed,
            self.stats.creeps_killed,
            self.state.jungle_creeps_nearby
        )
    
    def show_stats(self):
        """Показать статистику"""
        from utils import print_banner
        
        print_banner("ПОЛНАЯ СТАТИСТИКА", 60)
        print(f"Циклов игры: {self.stats.cycles}")
        print(f"Игровое время: {self.game_timer}")
        print(f"Уровень: {self.state.my_level}")
        print(f"Золото: {self.stats.total_gold}")
        print(f"ХП: {self.state.my_health}% | Мана: {self.state.my_mana}%")
        print(f"Убийств: {self.stats.enemies_killed}")
        print(f"Крипов: {self.stats.creeps_killed}")
        print(f"Гангов: {self.stats.successful_ganks}/{self.stats.gank_attempts}")
        print(f"Лагерий: {self.stats.jungle_camps_cleared}")
        print(f"Комбо: {self.stats.combos_executed}")
        print(f"Фаза: {self.state.phase}")
        print(f"Позиция: {self.state.map_position}")
        print(f"Безопасность: {self.state.safety_score:.2f}")
        print(f"Успешных действий: {self.stats.successful_actions}")
        print(f"Ошибок: {self.stats.errors}")
        print("=" * 60)
        
        # Статистика обучения
        if hasattr(self.learning_engine, 'get_summary'):
            learning_summary = self.learning_engine.get_summary()
            print(f"Выучено паттернов: {learning_summary.get('successful_patterns', 0)}")
            print(f"Лучшее комбо: {learning_summary.get('best_combo', 'N/A')} "
                  f"({learning_summary.get('best_combo_success_rate', 0):.1%})")
            print(f"Всего циклов: {learning_summary.get('total_cycles', 0)}")
            print(f"Общая успешность: {learning_summary.get('success_rate', 0):.1%}")
    
    def show_learned_patterns(self):
        """Показать выученные паттерны"""
        if not hasattr(self.learning_engine, 'get_successful_patterns'):
            print("⚠️ Система обучения не поддерживает просмотр паттернов")
            return
        
        patterns = self.learning_engine.get_successful_patterns(min_success_rate=0.5)
        
        print_banner("ВЫУЧЕННЫЕ ПАТТЕРНЫ", 60)
        if not patterns:
            print("🤷 Паттернов еще не выучено")
            return
        
        print(f"Найдено {len(patterns)} успешных паттернов:")
        for i, pattern in enumerate(patterns[:5], 1):  # Показываем топ-5
            action = pattern.get('pattern', {}).get('action', 'unknown')
            success_rate = pattern.get('success_rate', 0)
            count = pattern.get('count', 0)
            print(f"{i}. {action}: успешность {success_rate:.1%} ({count} попыток)")
    
    def save_learning_data(self):
        """Сохранение данных обучения"""
        print("💾 Сохраняю данные обучения...")
        
        try:
            # Сохраняем комбо
            self.combo_system.save_combos()
            
            # Сохраняем данные обучения
            if hasattr(self.learning_engine, 'save_data'):
                self.learning_engine.save_data()
            elif hasattr(self.learning_engine, 'save_ultra_data'):
                self.learning_engine.save_ultra_data()
            
            print("✅ Данные успешно сохранены")
            
        except Exception as e:
            print(f"❌ Ошибка сохранения данных: {e}")
    
    def start_auto_save(self):
        """Запуск автоматического сохранения"""
        def auto_save_loop():
            save_interval = 300  # 5 минут
            while True:
                time.sleep(save_interval)
                if self.running:
                    self.save_learning_data()
        
        # Запускаем в отдельном потоке
        auto_save_thread = threading.Thread(target=auto_save_loop, daemon=True)
        auto_save_thread.start()
        print("⏱️ Автосохранение включено (каждые 5 минут)")
    
    def cleanup(self):
        """Очистка ресурсов"""
        print("\n🧹 Очистка ресурсов...")
        
        # Остановка всех действий
        self.input_controller.stop_all_actions()
        
        # Сохранение данных
        self.save_learning_data()
        
        # Финальная статистика
        self.show_stats()
        
        print("\n" + "="*60)
        print("🏁 РАБОТА БОТА ЗАВЕРШЕНА")
        print("="*60)
        print(f"Итоги:")
        print(f"  Всего циклов: {self.stats.cycles}")
        print(f"  Убийств: {self.stats.enemies_killed}")
        print(f"  Крипов: {self.stats.creeps_killed}")
        print(f"  Золото: {self.stats.total_gold}")
        print(f"  Успешных гангов: {self.stats.successful_ganks}")
        print(f"  Ошибок: {self.stats.errors}")
        print(f"  Тип обучения: {self.learning_type}")
        print("="*60)
        print("👋 До свидания!")


class SimpleLearningEngine:
    """Простая система обучения на случай отсутствия основной"""
    
    def __init__(self):
        self.patterns = []
        self.combos = []
        
    def record_action(self, state, action, result, context=None):
        """Запись действия"""
        self.patterns.append({
            'state': state,
            'action': action,
            'result': result,
            'timestamp': time.time()
        })
    
    def record_combo(self, combo_name, success, execution_time):
        """Запись комбо"""
        self.combos.append({
            'name': combo_name,
            'success': success,
            'time': execution_time
        })
    
    def get_summary(self):
        """Получение сводки"""
        return {
            'total_patterns': len(self.patterns),
            'total_combos': len(self.combos),
            'successful_patterns': 0,
            'best_combo': 'N/A',
            'best_combo_success_rate': 0,
            'total_cycles': 0,
            'success_rate': 0
        }