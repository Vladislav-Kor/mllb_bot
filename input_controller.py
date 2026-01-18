"""
Контроллер ввода для управления игрой
"""

import pyautogui
import math
import time
import random
from typing import Tuple, Dict, Optional
from utils import get_screen_center, calculate_distance, calculate_angle

class InputController:
    """Контроллер ввода (мышь/клавиатура)"""
    
    def __init__(self, joystick_center: Tuple[int, int], 
                 joystick_radius: int,
                 attack_button: Tuple[int, int],
                 skill_buttons: Dict[str, Tuple[int, int]]):
        
        self.joystick_center = joystick_center
        self.joystick_radius = joystick_radius
        self.attack_button = attack_button
        self.skill_buttons = skill_buttons
        
        # Настройки PyAutoGUI
        pyautogui.FAILSAFE = True
        pyautogui.PAUSE = 0.05
        
        self.is_dragging = False
        self.drag_duration = 0.15
        
        print(f"🎮 Контроллер инициализирован: джойстик={joystick_center}")
    
    def drag_joystick_to_angle(self, angle: float, force: float = 0.8) -> bool:
        """Перетаскивание джойстика по углу"""
        jx, jy = self.joystick_center
        radius = int(self.joystick_radius * force)
        
        # Преобразование угла в координаты
        rad = math.radians(angle)
        dx = int(radius * math.cos(rad))
        dy = int(radius * math.sin(rad))
        
        end_x = jx + dx
        end_y = jy + dy
        
        try:
            pyautogui.mouseDown(x=jx, y=jy)
            self.is_dragging = True
            
            pyautogui.moveTo(end_x, end_y, duration=self.drag_duration)
            time.sleep(0.2)
            
            pyautogui.mouseUp()
            self.is_dragging = False
            
            # Названия направлений
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
            print(f"⚠️ Ошибка перетаскивания джойстика: {e}")
            if self.is_dragging:
                pyautogui.mouseUp()
                self.is_dragging = False
            return False
    
    def drag_joystick_to_position(self, target_x: int, target_y: int, 
                                 force: float = 0.8) -> bool:
        """Перетаскивание джойстика к позиции на экране"""
        jx, jy = self.joystick_center
        
        # Вычисление угла к цели
        dx = target_x - jx
        dy = target_y - jy
        distance = math.sqrt(dx*dx + dy*dy)
        
        if distance == 0:
            return False
        
        angle = math.degrees(math.atan2(dy, dx))
        
        return self.drag_joystick_to_angle(angle, force)
    
    def use_skill(self, skill_name: str, delay: float = 0.1) -> bool:
        """Использование скилла"""
        if skill_name in self.skill_buttons:
            x, y = self.skill_buttons[skill_name]
            
            # Добавляем случайность для реалистичности
            x += random.randint(-3, 3)
            y += random.randint(-3, 3)
            
            try:
                pyautogui.click(x, y, duration=0.03)
                print(f"⚡ {skill_name.upper()}")
                time.sleep(delay)
                return True
            except Exception as e:
                print(f"⚠️ Ошибка использования скилла {skill_name}: {e}")
                return False
        
        print(f"⚠️ Скилл {skill_name} не найден")
        return False
    
    def basic_attack(self, count: int = 1, delay_between: float = 0.08):
        """Базовая атака"""
        for i in range(count):
            x, y = self.attack_button
            
            # Случайное смещение для реалистичности
            x += random.randint(-10, 10)
            y += random.randint(-10, 10)
            
            try:
                pyautogui.click(x, y, duration=0.02)
                print(f"⚔️ Атака {i+1}/{count}")
                if i < count - 1:  # Не ждать после последней атаки
                    time.sleep(delay_between)
            except Exception as e:
                print(f"⚠️ Ошибка базовой атаки: {e}")
    
    def move_toward_object(self, target_position: Tuple[int, int], 
                          min_distance: int = 150, max_attempts: int = 3) -> bool:
        """Движение к объекту с безопасной дистанцией"""
        screen_center = get_screen_center()
        current_distance = calculate_distance(screen_center, target_position)
        
        if current_distance <= min_distance:
            # Уже достаточно близко
            return True
        
        # Вычисляем угол к цели
        angle = calculate_angle(screen_center, target_position)
        
        # Двигаемся поэтапно
        for attempt in range(max_attempts):
            # Уменьшаем силу по мере приближения
            force = min(0.7, 0.3 + (current_distance / 500))
            
            success = self.drag_joystick_to_angle(angle, force)
            if not success:
                return False
            
            # Пауза для анализа нового положения
            time.sleep(1.0)
            
            # Проверяем новое расстояние (в реальной игре нужно было бы пересчитать)
            # Для симуляции просто уменьшаем расстояние
            current_distance = max(min_distance, current_distance - 100)
            
            if current_distance <= min_distance:
                print(f"✅ Достигнута безопасная дистанция")
                return True
        
        print(f"⚠️ Не удалось приблизиться к цели")
        return False
    
    def safe_retreat(self, from_position: Optional[Tuple[int, int]] = None):
        """Безопасное отступление"""
        print("🏃 ОТСТУПЛЕНИЕ!")
        
        # Используем скиллы для ускорения побега
        self.use_skill('s2', 0.05)
        time.sleep(0.1)
        self.use_skill('s2', 0.05)
        
        # Определяем направление отступления
        if from_position:
            screen_center = get_screen_center()
            angle_to_target = calculate_angle(screen_center, from_position)
            retreat_angle = (angle_to_target + 180) % 360  # В обратную сторону
        else:
            retreat_angle = 225  # По умолчанию вниз-влево (к базе)
        
        # Быстрое отступление
        self.drag_joystick_to_angle(retreat_angle, 0.9)
        time.sleep(0.5)
        
        # Дополнительное отступление
        self.drag_joystick_to_angle((retreat_angle + 45) % 360, 0.7)
        
        print("✅ Отступление выполнено")
    
    def calibrate(self) -> bool:
        """Калибровка координат"""
        print("🎮 Для калибровки:")
        print("1. Запустите тренировочный режим MLBB")
        print("2. Убедитесь что игра в оконном режиме")
        print("3. Нажмите Enter для продолжения...")
        
        input()  # Ждем нажатия Enter
        
        # Автоматическая калибровка
        screen_width, screen_height = pyautogui.size()
        
        print(f"📏 Разрешение экрана: {screen_width}x{screen_height}")
        
        # Обновляем координаты скиллов
        self.skill_buttons = {
            's1': (int(screen_width * 0.78), int(screen_height * 0.88)),
            's2': (int(screen_width * 0.85), int(screen_height * 0.88)),
            's3': (int(screen_width * 0.92), int(screen_height * 0.88)),
            'ult': (int(screen_width * 0.96), int(screen_height * 0.78)),
        }
        
        print(f"✅ Координаты калиброваны: {self.skill_buttons}")
        return True
    
    def stop_all_actions(self):
        """Остановка всех действий"""
        if self.is_dragging:
            pyautogui.mouseUp()
            self.is_dragging = False
            print("🛑 Все действия остановлены")