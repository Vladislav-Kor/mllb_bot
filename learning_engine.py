"""
УЛЬТРА-ОБУЧАЮЩАЯ СИСТЕМА ДЛЯ MLBB БОТА
Интегрирует Deep Reinforcement Learning, адаптивное поведение и прогрессивное улучшение
"""

import json
import time
import threading
import pickle
import numpy as np
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, field, asdict
from collections import defaultdict, deque
import random
from pathlib import Path
import torch
import torch.nn as nn
import torch.optim as optim

@dataclass
class NeuralNetworkModel:
    """Простая нейросеть для оценки состояний"""
    def __init__(self, input_size: int, hidden_size: int, output_size: int):
        self.net = nn.Sequential(
            nn.Linear(input_size, hidden_size),
            nn.ReLU(),
            nn.Dropout(0.2),
            nn.Linear(hidden_size, hidden_size // 2),
            nn.ReLU(),
            nn.Linear(hidden_size // 2, output_size)
        )
        self.optimizer = optim.Adam(self.net.parameters(), lr=0.001)
        self.loss_fn = nn.MSELoss()
    
    def predict(self, state: np.ndarray) -> np.ndarray:
        """Предсказание Q-значений для состояний"""
        with torch.no_grad():
            tensor_state = torch.FloatTensor(state)
            return self.net(tensor_state).numpy()
    
    def train(self, states: np.ndarray, targets: np.ndarray, epochs: int = 5):
        """Обучение нейросети"""
        states_tensor = torch.FloatTensor(states)
        targets_tensor = torch.FloatTensor(targets)
        
        for epoch in range(epochs):
            self.optimizer.zero_grad()
            predictions = self.net(states_tensor)
            loss = self.loss_fn(predictions, targets_tensor)
            loss.backward()
            self.optimizer.step()
        
        return loss.item()

@dataclass
class UltraLearningData:
    """Сверх-данные для ультра-обучения"""
    experiences: List[Dict] = field(default_factory=list)
    trajectories: List[List[Dict]] = field(default_factory=list)
    q_table: Dict[str, Dict[str, float]] = field(default_factory=dict)
    success_patterns: Dict[str, Dict] = field(default_factory=dict)
    failure_patterns: Dict[str, Dict] = field(default_factory=dict)
    
    # Метрики обучения
    learning_metrics: Dict[str, List[float]] = field(default_factory=lambda: {
        'rewards': [],
        'success_rate': [],
        'exploration_rate': [],
        'loss': []
    })
    
    def add_experience(self, experience: Dict):
        """Добавление опыта"""
        self.experiences.append(experience)
        if len(self.experiences) > 100000:  # Ограничение памяти
            self.experiences = self.experiences[-50000:]
    
    def add_trajectory(self, trajectory: List[Dict]):
        """Добавление траектории (последовательность действий)"""
        self.trajectories.append(trajectory)
        if len(self.trajectories) > 1000:
            self.trajectories = self.trajectories[-500:]
    
    def update_q_value(self, state: str, action: str, value: float, alpha: float = 0.1):
        """Обновление Q-значения с учетом скорости обучения"""
        if state not in self.q_table:
            self.q_table[state] = {}
        
        old_value = self.q_table[state].get(action, 0.0)
        self.q_table[state][action] = old_value + alpha * (value - old_value)
    
    def get_best_action(self, state: str) -> Optional[str]:
        """Получение лучшего действия для состояния"""
        if state not in self.q_table or not self.q_table[state]:
            return None
        
        return max(self.q_table[state].items(), key=lambda x: x[1])[0]
    
    def get_action_value(self, state: str, action: str) -> float:
        """Получение значения действия для состояния"""
        return self.q_table.get(state, {}).get(action, 0.0)

class UltraLearningEngine:
    """Ультра-продвинутый движок обучения с реинфорсмент лернингом"""
    
    def __init__(self, data_dir: str = "ultra_data", use_neural: bool = True):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(exist_ok=True)
        
        self.data = UltraLearningData()
        self.use_neural = use_neural
        
        # Параметры RL
        self.gamma = 0.95  # Коэффициент дисконтирования
        self.alpha = 0.2   # Скорость обучения
        self.epsilon = 0.3  # Начальная вероятность исследования
        self.epsilon_decay = 0.995
        self.epsilon_min = 0.05
        self.batch_size = 32
        
        # Нейросеть для Deep Q-Learning
        if use_neural and torch.cuda.is_available():
            print("🎮 Используется CUDA для нейросетевого обучения")
            self.device = torch.device("cuda")
        elif use_neural:
            print("💻 Используется CPU для нейросетевого обучения")
            self.device = torch.device("cpu")
        else:
            print("📊 Используется табличный Q-Learning")
            self.device = None
        
        if use_neural:
            self.dqn = NeuralNetworkModel(input_size=15, hidden_size=128, output_size=9)
            self.target_net = NeuralNetworkModel(input_size=15, hidden_size=128, output_size=9)
            self.update_target_net()
            self.replay_buffer = deque(maxlen=10000)
        
        # Маппинг действий к индексам
        self.action_map = {
            'farm': 0, 'gank': 1, 'jungle': 2, 'retreat': 3,
            'patrol': 4, 'teamfight': 5, 'objective': 6, 
            'defend': 7, 'push': 8
        }
        self.reverse_action_map = {v: k for k, v in self.action_map.items()}
        
        # Трекеры для адаптивного обучения
        self.recent_rewards = deque(maxlen=100)
        self.success_history = deque(maxlen=50)
        self.exploration_history = []
        
        # Загрузка предыдущих данных
        self.load_ultra_data()
        
        # Автосохранение
        self.auto_save_thread(300)
        
        print(f"🚀 УЛЬТРА-СИСТЕМА ОБУЧЕНИЯ АКТИВИРОВАНА")
        print(f"🧠 Используется {'нейросеть' if use_neural else 'Q-таблица'}")
        print(f"📊 Загружено {len(self.data.experiences)} опытов и {len(self.data.trajectories)} траекторий")
    
    def state_to_vector(self, state: Dict) -> np.ndarray:
        """Преобразование состояния в вектор для нейросети"""
        vector = np.zeros(15, dtype=np.float32)
        
        # Нормализованные признаки
        vector[0] = state.get('health', 100) / 100.0
        vector[1] = state.get('level', 1) / 15.0
        vector[2] = state.get('gold', 300) / 10000.0
        vector[3] = min(state.get('enemies_nearby', 0) / 5.0, 1.0)
        vector[4] = min(state.get('creeps_nearby', 0) / 10.0, 1.0)
        vector[5] = min(state.get('jungle_creeps_nearby', 0) / 5.0, 1.0)
        vector[6] = state.get('safety_score', 1.0)
        
        # One-hot кодирование фазы
        phases = ['early', 'mid', 'late', 'endgame']
        phase = state.get('phase', 'early')
        phase_idx = phases.index(phase) if phase in phases else 0
        vector[7 + phase_idx] = 1.0
        
        # One-hot кодирование позиции
        positions = ['base', 'ally_territory', 'jungle', 'enemy_territory']
        position = state.get('position', 'ally_territory')
        pos_idx = positions.index(position) if position in positions else 0
        vector[11 + pos_idx] = 1.0
        
        return vector
    
    def calculate_reward(self, state: Dict, action: str, result: Dict, next_state: Dict) -> float:
        """Расчет вознаграждения с учетом множества факторов"""
        reward = 0.0
        
        # Базовое вознаграждение за успех
        if result.get('success', False):
            reward += 5.0
        
        # Вознаграждение за урон
        damage_reward = result.get('damage_dealt', 0) / 100.0
        reward += damage_reward
        
        # Вознаграждение за золото
        gold_reward = result.get('gold_earned', 0) / 50.0
        reward += gold_reward
        
        # Вознаграждение за убийства
        kill_reward = result.get('kills', 0) * 10.0
        reward += kill_reward
        
        # Штраф за полученный урон
        damage_taken_penalty = result.get('damage_taken', 0) / 50.0
        reward -= damage_taken_penalty
        
        # Вознаграждение за выживание
        if next_state.get('health', 100) > 30:
            reward += 1.0
        
        # Вознаграждение за эффективное использование времени
        time_penalty = result.get('time_taken', 0) / 10.0
        reward -= time_penalty
        
        # Вознаграждение за достижение целей
        if result.get('objective_completed', False):
            reward += 20.0
        
        # Вознаграждение за командную игру
        if result.get('team_assist', False):
            reward += 3.0
        
        return reward
    
    def record_ultra_experience(self, state: Dict, action: str, result: Dict, 
                               next_state: Dict, context: Dict = None):
        """Запись ультра-опыта с реинфорсмент лернингом"""
        try:
            if context is None:
                context = {}
            
            # Расчет вознаграждения
            reward = self.calculate_reward(state, action, result, next_state)
            self.recent_rewards.append(reward)
            
            # Создание опыта для RL
            experience = {
                'state': state,
                'action': action,
                'reward': reward,
                'next_state': next_state,
                'done': next_state.get('health', 100) <= 0,
                'timestamp': time.time(),
                'context': context
            }
            
            self.data.add_experience(experience)
            
            # Обучение на этом опыте
            self.learn_from_experience(experience)
            
            # Обновление паттернов успеха/неудачи
            self.update_success_patterns(state, action, result, reward)
            
            # Адаптивное обновление epsilon (исследование/использование)
            self.adapt_exploration_rate(reward)
            
            # Логирование успешных действий
            if reward > 10.0:
                print(f"🏆 УЛЬТРА-УСПЕХ: {action.upper()} награда: {reward:.1f}")
            
            # Периодическое глубокое обучение
            if len(self.data.experiences) % 100 == 0:
                self.deep_train()
            
            return reward
            
        except Exception as e:
            print(f"⚠️ Ошибка записи ультра-опыта: {e}")
            return 0.0
    
    def learn_from_experience(self, experience: Dict):
        """Обучение на одном опыте с Q-learning"""
        state = experience['state']
        action = experience['action']
        reward = experience['reward']
        next_state = experience['next_state']
        done = experience['done']
        
        # Получаем ключи состояний
        state_key = self._create_state_key(state)
        next_state_key = self._create_state_key(next_state)
        
        # Получаем текущее Q-значение
        current_q = self.data.get_action_value(state_key, action)
        
        if done:
            # Если эпизод закончен, Q-значение равно награде
            target_q = reward
        else:
            # Иначе учитываем будущие награды
            next_best_q = 0.0
            best_next_action = self.data.get_best_action(next_state_key)
            if best_next_action:
                next_best_q = self.data.get_action_value(next_state_key, best_next_action)
            
            target_q = reward + self.gamma * next_best_q
        
        # Обновляем Q-таблицу
        self.data.update_q_value(state_key, action, target_q, self.alpha)
        
        # Для нейросетевого обучения добавляем в буфер воспроизведения
        if self.use_neural:
            state_vector = self.state_to_vector(state)
            next_state_vector = self.state_to_vector(next_state)
            action_idx = self.action_map.get(action, 0)
            
            replay_experience = (
                state_vector,
                action_idx,
                reward,
                next_state_vector,
                done
            )
            self.replay_buffer.append(replay_experience)
    
    def update_success_patterns(self, state: Dict, action: str, result: Dict, reward: float):
        """Обновление паттернов успеха и неудачи"""
        state_key = self._create_state_key(state)
        pattern_key = f"{state_key}_{action}"
        
        if reward > 5.0:  # Успешный паттерн
            if pattern_key not in self.data.success_patterns:
                self.data.success_patterns[pattern_key] = {
                    'count': 0,
                    'total_reward': 0.0,
                    'avg_reward': 0.0,
                    'last_success': time.time()
                }
            
            pattern = self.data.success_patterns[pattern_key]
            pattern['count'] += 1
            pattern['total_reward'] += reward
            pattern['avg_reward'] = pattern['total_reward'] / pattern['count']
            pattern['last_success'] = time.time()
            
        elif reward < -5.0:  # Неудачный паттерн
            if pattern_key not in self.data.failure_patterns:
                self.data.failure_patterns[pattern_key] = {
                    'count': 0,
                    'total_reward': 0.0,
                    'avg_reward': 0.0,
                    'last_failure': time.time()
                }
            
            pattern = self.data.failure_patterns[pattern_key]
            pattern['count'] += 1
            pattern['total_reward'] += reward
            pattern['avg_reward'] = pattern['total_reward'] / pattern['count']
            pattern['last_failure'] = time.time()
    
    def adapt_exploration_rate(self, reward: float):
        """Адаптивное обновление вероятности исследования"""
        self.success_history.append(reward > 0)
        
        # Если успешность растет, уменьшаем исследование
        if len(self.success_history) > 20:
            success_rate = sum(self.success_history) / len(self.success_history)
            if success_rate > 0.7:
                self.epsilon *= 0.99
            elif success_rate < 0.3:
                self.epsilon *= 1.01
        
        # Гарантируем границы epsilon
        self.epsilon = max(self.epsilon_min, min(self.epsilon, 1.0))
        
        # Запись истории исследования
        self.exploration_history.append(self.epsilon)
        if len(self.exploration_history) > 1000:
            self.exploration_history = self.exploration_history[-1000:]
    
    def select_ultra_action(self, state: Dict, possible_actions: List[str]) -> Tuple[str, float]:
        """Выбор ультра-оптимального действия с балансом исследования/использования"""
        try:
            # Epsilon-greedy стратегия
            if random.random() < self.epsilon:
                # Исследование: случайное действие
                action = random.choice(possible_actions)
                confidence = self.epsilon
                return action, confidence
            
            # Использование: выбираем лучшее действие
            state_key = self._create_state_key(state)
            
            if self.use_neural and len(self.replay_buffer) >= self.batch_size:
                # Используем нейросеть для оценки
                state_vector = self.state_to_vector(state)
                with torch.no_grad():
                    q_values = self.dqn.predict(state_vector.reshape(1, -1))[0]
                
                # Фильтруем только возможные действия
                action_scores = {}
                for action in possible_actions:
                    action_idx = self.action_map.get(action)
                    if action_idx is not None:
                        action_scores[action] = q_values[action_idx]
                
                if action_scores:
                    best_action = max(action_scores.items(), key=lambda x: x[1])[0]
                    best_score = action_scores[best_action]
                    confidence = min(1.0, best_score / 10.0)  # Нормализуем уверенность
                    return best_action, confidence
            
            # Используем Q-таблицу
            best_action = None
            best_q = -float('inf')
            
            for action in possible_actions:
                q_value = self.data.get_action_value(state_key, action)
                if q_value > best_q:
                    best_q = q_value
                    best_action = action
            
            if best_action is None:
                best_action = random.choice(possible_actions)
                confidence = 0.3
            else:
                confidence = min(1.0, (best_q + 10) / 20.0)  # Нормализуем уверенность
            
            return best_action, confidence
            
        except Exception as e:
            print(f"⚠️ Ошибка выбора ультра-действия: {e}")
            return random.choice(possible_actions), 0.3
    
    def deep_train(self):
        """Глубокое обучение нейросети на буфере воспроизведения"""
        if not self.use_neural or len(self.replay_buffer) < self.batch_size:
            return
        
        try:
            # Выборка из буфера воспроизведения
            batch = random.sample(self.replay_buffer, self.batch_size)
            
            states = np.zeros((self.batch_size, 15))
            actions = np.zeros(self.batch_size, dtype=np.int64)
            rewards = np.zeros(self.batch_size)
            next_states = np.zeros((self.batch_size, 15))
            dones = np.zeros(self.batch_size, dtype=np.bool_)
            
            for i, (state, action, reward, next_state, done) in enumerate(batch):
                states[i] = state
                actions[i] = action
                rewards[i] = reward
                next_states[i] = next_state
                dones[i] = done
            
            # Вычисляем целевые Q-значения
            with torch.no_grad():
                next_q_values = self.target_net.predict(next_states)
                max_next_q = np.max(next_q_values, axis=1)
            
            target_q = rewards + self.gamma * max_next_q * (~dones)
            
            # Предсказания текущей сети
            current_q_values = self.dqn.predict(states)
            
            # Обновляем только Q-значения для выбранных действий
            for i in range(self.batch_size):
                current_q_values[i, actions[i]] = target_q[i]
            
            # Обучение сети
            loss = self.dqn.train(states, current_q_values, epochs=3)
            
            # Обновляем метрики
            self.data.learning_metrics['loss'].append(loss)
            
            # Периодическое обновление целевой сети
            if len(self.data.experiences) % 1000 == 0:
                self.update_target_net()
                print(f"🔄 Целевая нейросеть обновлена, loss: {loss:.4f}")
            
        except Exception as e:
            print(f"⚠️ Ошибка глубокого обучения: {e}")
    
    def update_target_net(self):
        """Обновление целевой нейросети (soft update)"""
        if not self.use_neural:
            return
        
        # Soft update: обновляем целевую сеть медленно
        target_params = self.target_net.net.state_dict()
        source_params = self.dqn.net.state_dict()
        
        tau = 0.001  # Коэффициент мягкого обновления
        for key in source_params:
            target_params[key] = target_params[key] * (1 - tau) + source_params[key] * tau
        
        self.target_net.net.load_state_dict(target_params)
    
    def record_trajectory(self, trajectory: List[Dict]):
        """Запись полной траектории (последовательности состояний-действий)"""
        self.data.add_trajectory(trajectory)
        
        # Обучение на траектории
        self.learn_from_trajectory(trajectory)
    
    def learn_from_trajectory(self, trajectory: List[Dict]):
        """Обучение на полной траектории (Monte Carlo)"""
        if len(trajectory) < 2:
            return
        
        # Вычисляем возвраты (returns) с конца траектории
        returns = 0
        for i in range(len(trajectory) - 1, -1, -1):
            experience = trajectory[i]
            reward = experience.get('reward', 0)
            returns = reward + self.gamma * returns
            
            # Обновляем Q-значение с учетом общего возврата
            state = experience.get('state', {})
            action = experience.get('action', '')
            state_key = self._create_state_key(state)
            self.data.update_q_value(state_key, action, returns, self.alpha * 0.5)
    
    def get_ultra_recommendations(self, state: Dict, top_n: int = 3) -> List[Dict]:
        """Получение ультра-рекомендаций с обоснованием"""
        recommendations = []
        state_key = self._create_state_key(state)
        
        # Анализируем успешные паттерны для похожих состояний
        similar_patterns = self.find_similar_patterns(state_key)
        
        for pattern_key, pattern_data in similar_patterns[:top_n]:
            parts = pattern_key.split('_')
            if len(parts) >= 2:
                action = parts[-1]  # Последняя часть - действие
                state_part = '_'.join(parts[:-1])
                
                recommendations.append({
                    'action': action,
                    'confidence': pattern_data.get('avg_reward', 0) / 10.0,
                    'success_rate': pattern_data.get('count', 0) / max(pattern_data.get('count', 1), 1),
                    'reason': f"Успешный паттерн: {pattern_data.get('count', 0)} успехов",
                    'avg_reward': pattern_data.get('avg_reward', 0)
                })
        
        return sorted(recommendations, key=lambda x: x['confidence'], reverse=True)
    
    def find_similar_patterns(self, state_key: str, threshold: float = 0.7) -> List[Tuple[str, Dict]]:
        """Поиск похожих паттернов"""
        similar = []
        state_parts = state_key.split('_')
        
        for pattern_key, pattern_data in self.data.success_patterns.items():
            pattern_parts = pattern_key.split('_')
            
            # Простая метрика схожести
            common_parts = len(set(state_parts) & set(pattern_parts[:-1]))
            similarity = common_parts / max(len(set(state_parts)), len(set(pattern_parts[:-1])))
            
            if similarity >= threshold:
                similar.append((pattern_key, pattern_data))
        
        # Сортируем по успешности
        similar.sort(key=lambda x: x[1].get('avg_reward', 0), reverse=True)
        return similar
    
    def save_ultra_data(self, filename: str = None):
        """Сохранение ультра-данных обучения"""
        if filename is None:
            timestamp = time.strftime("%Y%m%d_%H%M%S")
            filename = self.data_dir / f"ultra_learning_{timestamp}.pkl"
        
        try:
            # Сохраняем данные
            data_to_save = {
                'data': self.data,
                'epsilon': self.epsilon,
                'recent_rewards': list(self.recent_rewards),
                'exploration_history': self.exploration_history,
                'timestamp': time.time()
            }
            
            with open(filename, 'wb') as f:
                pickle.dump(data_to_save, f)
            
            # Сохраняем нейросети
            if self.use_neural:
                torch.save(self.dqn.net.state_dict(), self.data_dir / "dqn_model.pth")
                torch.save(self.target_net.net.state_dict(), self.data_dir / "target_model.pth")
            
            print(f"💾 Ультра-данные сохранены в {filename}")
            
        except Exception as e:
            print(f"⚠️ Ошибка сохранения ультра-данных: {e}")
    
    def load_ultra_data(self):
        """Загрузка ультра-данных обучения"""
        try:
            # Ищем последний файл
            ultra_files = list(self.data_dir.glob("ultra_learning_*.pkl"))
            if not ultra_files:
                print("📂 Ультра-данные не найдены, начинаем с нуля")
                return
            
            latest_file = max(ultra_files, key=lambda x: x.stat().st_mtime)
            
            with open(latest_file, 'rb') as f:
                loaded_data = pickle.load(f)
            
            self.data = loaded_data.get('data', UltraLearningData())
            self.epsilon = loaded_data.get('epsilon', 0.3)
            self.recent_rewards = deque(loaded_data.get('recent_rewards', []), maxlen=100)
            self.exploration_history = loaded_data.get('exploration_history', [])
            
            # Загружаем нейросети
            if self.use_neural:
                dqn_path = self.data_dir / "dqn_model.pth"
                target_path = self.data_dir / "target_model.pth"
                
                if dqn_path.exists():
                    self.dqn.net.load_state_dict(torch.load(dqn_path))
                    print("🧠 DQN нейросеть загружена")
                
                if target_path.exists():
                    self.target_net.net.load_state_dict(torch.load(target_path))
                    print("🎯 Целевая нейросеть загружена")
            
            print(f"📂 Загружены ультра-данные из {latest_file.name}")
            print(f"📊 Опытов: {len(self.data.experiences)}, "
                  f"Траекторий: {len(self.data.trajectories)}, "
                  f"Успешных паттернов: {len(self.data.success_patterns)}")
            
        except Exception as e:
            print(f"⚠️ Ошибка загрузки ультра-данных: {e}")
            print("🔄 Начинаем с нуля")
            self.data = UltraLearningData()
    
    def auto_save_thread(self, interval: int = 300):
        """Автосохранение данных"""
        def save_loop():
            while True:
                time.sleep(interval)
                self.save_ultra_data()
                self.print_progress()
        
        thread = threading.Thread(target=save_loop, daemon=True)
        thread.start()
        print(f"⏱️ Автосохранение ультра-данных каждые {interval} секунд")
    
    def print_progress(self):
        """Вывод прогресса обучения"""
        if not self.recent_rewards:
            return
        
        avg_reward = np.mean(list(self.recent_rewards))
        success_rate = len([r for r in self.recent_rewards if r > 0]) / len(self.recent_rewards)
        
        print(f"\n📈 ПРОГРЕСС УЛЬТРА-ОБУЧЕНИЯ:")
        print(f"   Средняя награда: {avg_reward:.2f}")
        print(f"   Успешность: {success_rate:.1%}")
        print(f"   Исследование (epsilon): {self.epsilon:.3f}")
        print(f"   Опытов: {len(self.data.experiences)}")
        print(f"   Успешных паттернов: {len(self.data.success_patterns)}")
        print(f"   Q-записей: {sum(len(v) for v in self.data.q_table.values())}")
        
        if self.data.learning_metrics.get('loss'):
            avg_loss = np.mean(self.data.learning_metrics['loss'][-10:])
            print(f"   Потеря нейросети: {avg_loss:.4f}")
        
        # Рекомендации для текущего состояния
        if self.data.success_patterns:
            top_patterns = sorted(
                self.data.success_patterns.items(),
                key=lambda x: x[1].get('avg_reward', 0),
                reverse=True
            )[:3]
            
            print(f"\n🏆 ТОП-3 паттерна:")
            for i, (pattern, data) in enumerate(top_patterns, 1):
                print(f"   {i}. {pattern}: награда={data.get('avg_reward', 0):.1f}, "
                      f"попыток={data.get('count', 0)}")
    
    def _create_state_key(self, state: Dict) -> str:
        """Создание ключа состояния"""
        key_parts = [
            f"h{int(state.get('health', 0))}",
            f"l{state.get('level', 1)}",
            f"e{state.get('enemies_nearby', 0)}",
            f"c{state.get('creeps_nearby', 0)}",
            f"j{state.get('jungle_creeps_nearby', 0)}",
            f"s{int(state.get('safety_score', 1.0) * 10)}",
            f"g{int(state.get('gold', 0) / 100)}",
            f"p{state.get('phase', 'early')[:1]}",
            f"pos{state.get('position', 'unknown')[:3]}"
        ]
        return "_".join(key_parts)
    
    def get_learning_insights(self) -> Dict:
        """Получение инсайтов обучения"""
        if not self.data.experiences:
            return {}
        
        # Анализ последних опытов
        recent_experiences = self.data.experiences[-100:]
        recent_rewards = [exp.get('reward', 0) for exp in recent_experiences]
        
        # Анализ успешности по действиям
        action_success = defaultdict(list)
        for exp in recent_experiences:
            action = exp.get('action', '')
            reward = exp.get('reward', 0)
            action_success[action].append(reward > 0)
        
        action_stats = {}
        for action, successes in action_success.items():
            if successes:
                action_stats[action] = {
                    'success_rate': sum(successes) / len(successes),
                    'count': len(successes),
                    'avg_reward': np.mean([exp.get('reward', 0) 
                                         for exp in recent_experiences 
                                         if exp.get('action') == action])
                }
        
        # Тренды
        if len(self.data.learning_metrics.get('success_rate', [])) > 10:
            recent_success = self.data.learning_metrics['success_rate'][-10:]
            success_trend = np.polyfit(range(len(recent_success)), recent_success, 1)[0]
        else:
            success_trend = 0
        
        return {
            'avg_reward': np.mean(recent_rewards) if recent_rewards else 0,
            'reward_std': np.std(recent_rewards) if recent_rewards else 0,
            'action_stats': dict(action_stats),
            'exploration_rate': self.epsilon,
            'success_trend': success_trend,
            'total_experiences': len(self.data.experiences),
            'unique_patterns': len(self.data.success_patterns),
            'learning_progress': min(100, len(self.data.experiences) / 1000 * 100)  # Процент обучения
        }

# Интеграция с существующей системой
def integrate_ultra_learning(bot_core_instance):
    """Интеграция ультра-обучения с основным ботом"""
    
    # Инициализация ультра-движка
    ultra_engine = UltraLearningEngine(data_dir="ultra_learning_data", use_neural=True)
    
    # Модификация метода game_cycle
    original_game_cycle = bot_core_instance.game_cycle
    
    def ultra_game_cycle():
        # Сохраняем исходное состояние
        initial_state = bot_core_instance.state.__dict__.copy()
        
        # Выполняем обычный цикл
        result = original_game_cycle()
        
        # Получаем новое состояние
        new_state = bot_core_instance.state.__dict__.copy()
        
        # Записываем ультра-опыт
        if hasattr(bot_core_instance, 'last_action'):
            reward = ultra_engine.record_ultra_experience(
                state=initial_state,
                action=bot_core_instance.last_action,
                result=result,
                next_state=new_state,
                context={
                    'phase': bot_core_instance.state.phase,
                    'position': bot_core_instance.state.map_position
                }
            )
            
            # Адаптивный выбор действий на основе обучения
            if random.random() < 0.3:  # 30% chance to use ultra learning
                possible_actions = ['farm', 'gank', 'jungle', 'retreat', 'patrol']
                ultra_action, confidence = ultra_engine.select_ultra_action(
                    state=initial_state,
                    possible_actions=possible_actions
                )
                
                if confidence > 0.6:
                    bot_core_instance.last_action = ultra_action
                    print(f"🎯 УЛЬТРА-ВЫБОР: {ultra_action} (уверенность: {confidence:.1%})")
        
        return result
    
    # Заменяем метод
    bot_core_instance.game_cycle = ultra_game_cycle
    
    # Добавляем ультра-движок в экземпляр
    bot_core_instance.ultra_engine = ultra_engine
    
    print("🚀 УЛЬТРА-ОБУЧЕНИЕ ИНТЕГРИРОВАНО В БОТА")
    return bot_core_instance