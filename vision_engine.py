"""
Улучшенный движок компьютерного зрения для MLBB
"""

import cv2
import numpy as np
import pyautogui
import time
import random
from typing import Tuple, List, Dict
from game_state import GameObject
from config import COLORS
from utils import get_screen_center, debug_vision

class VisionEngine:
    """Движок компьютерного зрения с реальным распознаванием"""
    
    def __init__(self, screen_regions: Dict, debug: bool = False):
        self.screen_regions = screen_regions
        self.debug = debug
        self.last_screenshot = None
        self.last_analysis_time = 0
        
        # Цветовые диапазоны в HSV
        self.hsv_ranges = {
            'creep': ([20, 100, 100], [30, 255, 255]),    # Желтый минионы
            'jungle': ([10, 50, 50], [20, 255, 255]),     # Оранжевый крипы
            'enemy': ([0, 100, 100], [10, 255, 255]),     # Красный враги
            'health': ([40, 40, 40], [80, 255, 255]),     # Зеленый здоровье
            'tower': ([0, 50, 50], [5, 255, 255]),        # Красный туррели
        }
        
        print("👁️ Движок зрения инициализирован")
    
    def capture_screen(self, region=None):
        """Захват экрана"""
        try:
            if region:
                screenshot = pyautogui.screenshot(region=region)
            else:
                screenshot = pyautogui.screenshot()
            
            screenshot = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)
            
            if self.debug and random.random() < 0.1:  # 10% шанс сохранить скриншот для отладки
                timestamp = int(time.time())
                cv2.imwrite(f"debug_screen_{timestamp}.png", screenshot)
            
            return screenshot
        except Exception as e:
            print(f"⚠️ Ошибка захвата экрана: {e}")
            return None
    
    def analyze_screen(self) -> Dict:
        """Полный анализ экрана"""
        start_time = time.time()
        results = {'objects': [], 'minimap': {}, 'interface': {}}
        
        try:
            # Захватываем весь экран
            screen = self.capture_screen()
            if screen is None:
                return results
            
            self.last_screenshot = screen
            
            # 1. Обнаружение объектов в центре экрана
            center_objects = self.detect_objects_in_center(screen)
            results['objects'] = center_objects
            
            # 2. Поиск крипов в зонах леса
            jungle_objects = self.search_jungle_areas(screen)
            results['objects'].extend(jungle_objects)
            
            # 3. Анализ мини-карты
            results['minimap'] = self.analyze_minimap(screen)
            
            # 4. Анализ интерфейса
            results['interface'] = self.analyze_interface(screen)
            
            # 5. Время анализа
            results['analysis_time'] = time.time() - start_time
            self.last_analysis_time = time.time()
            
            # Отладочный вывод
            if self.debug:
                total_objects = len(results['objects'])
                creeps = sum(1 for obj in results['objects'] if obj.type in ['creep', 'jungle'])
                enemies = sum(1 for obj in results['objects'] if obj.type == 'hero' and obj.is_enemy)
                print(f"👁️ Анализ: {total_objects} объектов ({creeps} крипов, {enemies} врагов)")
            
        except Exception as e:
            print(f"⚠️ Ошибка анализа экрана: {e}")
            import traceback
            traceback.print_exc()
        
        return results
    
    def detect_objects_in_center(self, screen: np.ndarray) -> List[GameObject]:
        """Обнаружение объектов в центральной области"""
        objects = []
        
        try:
            # Определяем центральную область
            center_region = self.screen_regions['center_screen']
            x, y, w, h = center_region
            
            # Вырезаем центральную область
            center_area = screen[y:y+h, x:x+w]
            
            # Преобразуем в HSV для лучшего распознавания цветов
            hsv = cv2.cvtColor(center_area, cv2.COLOR_BGR2HSV)
            
            # 1. Поиск крипов (минионов и крипов леса)
            creep_objects = self.detect_by_color(hsv, 'creep', center_region, 'creep', False)
            jungle_objects = self.detect_by_color(hsv, 'jungle', center_region, 'jungle', True)
            
            objects.extend(creep_objects)
            objects.extend(jungle_objects)
            
            # 2. Поиск вражеских героев
            enemy_objects = self.detect_by_color(hsv, 'enemy', center_region, 'hero', True)
            objects.extend(enemy_objects)
            
            # 3. Поиск туррелей
            tower_objects = self.detect_by_color(hsv, 'tower', center_region, 'tower', True)
            objects.extend(tower_objects)
            
            # Отладочный вывод
            if self.debug and objects:
                debug_vision(objects, "Центр экрана")
            
        except Exception as e:
            print(f"⚠️ Ошибка детектирования в центре: {e}")
        
        return objects
    
    def detect_by_color(self, hsv_image: np.ndarray, color_type: str, 
                       offset: Tuple, obj_type: str, is_enemy: bool) -> List[GameObject]:
        """Обнаружение объектов по цвету"""
        objects = []
        
        try:
            lower, upper = self.hsv_ranges[color_type]
            lower_np = np.array(lower)
            upper_np = np.array(upper)
            
            # Создаем маску
            mask = cv2.inRange(hsv_image, lower_np, upper_np)
            
            # Улучшаем маску
            kernel = np.ones((3, 3), np.uint8)
            mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)
            mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
            
            # Находим контуры
            contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            for contour in contours:
                area = cv2.contourArea(contour)
                
                # Фильтр по размеру в зависимости от типа объекта
                min_area = 20 if obj_type in ['creep', 'jungle'] else 50
                max_area = 500 if obj_type in ['creep', 'jungle'] else 1000
                
                if min_area < area < max_area:
                    x, y, w, h = cv2.boundingRect(contour)
                    
                    # Вычисляем центр объекта с учетом смещения
                    center_x = offset[0] + x + w // 2
                    center_y = offset[1] + y + h // 2
                    
                    # Вычисляем уверенность на основе размера и четкости контура
                    contour_solidity = area / (w * h) if w * h > 0 else 0
                    confidence = min(0.95, 0.5 + contour_solidity * 0.5)
                    
                    # Определяем здоровье (случайно для симуляции)
                    health = random.randint(30, 100) if obj_type == 'hero' else 100.0
                    
                    objects.append(GameObject(
                        type=obj_type,
                        position=(center_x, center_y),
                        confidence=confidence,
                        timestamp=time.time(),
                        health=health,
                        is_enemy=is_enemy
                    ))
            
        except Exception as e:
            print(f"⚠️ Ошибка детектирования цвета {color_type}: {e}")
        
        return objects
    
    def search_jungle_areas(self, screen: np.ndarray) -> List[GameObject]:
        """Поиск крипов в зонах леса"""
        objects = []
        
        try:
            # Координаты основных зон леса для 1920x1080
            jungle_zones = [
                (600, 300, 150, 150),   # Верхний лес (синий бафф)
                (1150, 300, 150, 150),  # Верхний вражеский лес
                (600, 600, 150, 150),   # Нижний лес (красный бафф)
                (1150, 600, 150, 150),  # Нижний вражеский лес
                (850, 450, 150, 150),   # Центральный лес (скакун/черепаха)
            ]
            
            for zone in jungle_zones:
                x, y, w, h = zone
                jungle_area = screen[y:y+h, x:x+w]
                
                # Преобразуем в HSV
                hsv = cv2.cvtColor(jungle_area, cv2.COLOR_BGR2HSV)
                
                # Ищем крипов леса
                jungle_objects = self.detect_by_color(hsv, 'jungle', (x, y), 'jungle', True)
                objects.extend(jungle_objects)
                
                # Также ищем обычных крипов
                creep_objects = self.detect_by_color(hsv, 'creep', (x, y), 'creep', True)
                objects.extend(creep_objects)
            
            if self.debug and objects:
                jungle_count = sum(1 for obj in objects if obj.type == 'jungle')
                creep_count = sum(1 for obj in objects if obj.type == 'creep')
                print(f"🌲 Лес: найдено {jungle_count} крипов леса, {creep_count} крипов")
            
        except Exception as e:
            print(f"⚠️ Ошибка поиска в лесу: {e}")
        
        return objects
    
    def analyze_minimap(self, screen: np.ndarray) -> Dict:
        """Анализ мини-карты"""
        try:
            x, y, w, h = self.screen_regions['minimap']
            minimap = screen[y:y+h, x:x+w]
            
            # Преобразуем в HSV
            hsv = cv2.cvtColor(minimap, cv2.COLOR_BGR2HSV)
            
            # Ищем зеленые зоны (лес)
            jungle_lower = np.array([35, 40, 40])
            jungle_upper = np.array([85, 255, 255])
            jungle_mask = cv2.inRange(hsv, jungle_lower, jungle_upper)
            
            jungle_pixels = cv2.countNonZero(jungle_mask)
            total_pixels = w * h
            
            if total_pixels == 0:
                return {'position': 'unknown'}
            
            jungle_ratio = jungle_pixels / total_pixels
            
            # Определяем позицию
            if jungle_ratio > 0.4:
                position = "jungle"
            elif jungle_ratio > 0.15:
                position = "lane_border"
            else:
                # Проверяем наличие врагов (красные точки)
                enemy_lower = np.array([0, 100, 100])
                enemy_upper = np.array([10, 255, 255])
                enemy_mask = cv2.inRange(hsv, enemy_lower, enemy_upper)
                enemy_pixels = cv2.countNonZero(enemy_mask)
                
                if enemy_pixels > 50:
                    position = "enemy_territory"
                else:
                    position = "lane_center"
            
            return {'position': position}
            
        except Exception as e:
            print(f"⚠️ Ошибка анализа мини-карты: {e}")
            return {'position': 'unknown'}
    
    def analyze_interface(self, screen: np.ndarray) -> Dict:
        """Анализ интерфейса"""
        results = {
            'health': 100,
            'mana': 100,
            'gold': 300,
            'level': 1,
            'skills_ready': {
                's1': True, 's2': True, 's3': True, 'ult': False
            }
        }
        
        try:
            # Анализ полоски здоровья
            health_region = self.screen_regions['health_bar']
            x, y, w, h = health_region
            
            if y + h <= screen.shape[0] and x + w <= screen.shape[1]:
                health_area = screen[y:y+h, x:x+w]
                
                # Ищем зеленый цвет
                hsv = cv2.cvtColor(health_area, cv2.COLOR_BGR2HSV)
                health_lower = np.array([40, 40, 40])
                health_upper = np.array([80, 255, 255])
                health_mask = cv2.inRange(hsv, health_lower, health_upper)
                
                health_pixels = cv2.countNonZero(health_mask)
                total_pixels = w * h
                
                if total_pixels > 0:
                    health_percent = (health_pixels / total_pixels) * 100
                    results['health'] = min(100, max(1, int(health_percent)))
            
            # Симуляция скиллов (в реальной игре нужно распознавать иконки)
            if random.random() > 0.1:  # 90% шанс что скиллы готовы
                results['skills_ready']['s1'] = True
                results['skills_ready']['s2'] = True
                results['skills_ready']['s3'] = True
            
            if random.random() > 0.7:  # 30% шанс что ульта готова
                results['skills_ready']['ult'] = True
            
            # Симуляция роста
            if random.random() > 0.8:
                results['level'] = min(15, results['level'] + 1)
                results['gold'] += random.randint(50, 200)
            
        except Exception as e:
            print(f"⚠️ Ошибка анализа интерфейса: {e}")
        
        return results
    
    def save_debug_screenshot(self, objects: List[GameObject], filename: str = None):
        """Сохранение скриншота с отладочной информацией"""
        if self.last_screenshot is None:
            return
        
        try:
            debug_img = self.last_screenshot.copy()
            
            # Рисуем обнаруженные объекты
            for obj in objects:
                x, y = obj.position
                color = (0, 255, 0) if not obj.is_enemy else (0, 0, 255)  # Зеленый для союзников, красный для врагов
                cv2.circle(debug_img, (x, y), 10, color, 2)
                
                # Подпись
                label = f"{obj.type} {int(obj.health)}%"
                cv2.putText(debug_img, label, (x-20, y-15), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 1)
            
            if filename is None:
                timestamp = int(time.time())
                filename = f"debug_vision_{timestamp}.png"
            
            cv2.imwrite(filename, debug_img)
            print(f"📸 Отладочный скриншот сохранен: {filename}")
            
        except Exception as e:
            print(f"⚠️ Ошибка сохранения скриншота: {e}")