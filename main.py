"""
Главный запускной файл бота Хаябуса
"""

import os
import sys

def check_dependencies():
    """Проверка зависимостей"""
    required_packages = [
        'opencv-python',
        'numpy',
        'pyautogui',
        'keyboard',
    ]
    
    missing_packages = []
    for package in required_packages:
        try:
            __import__(package.replace('-', '_'))
        except ImportError:
            missing_packages.append(package)
    
    return missing_packages

def install_dependencies(missing_packages):
    """Установка зависимостей"""
    import subprocess
    
    print(f"\n❌ Отсутствуют пакеты: {', '.join(missing_packages)}")
    print("Устанавливаю автоматически...")
    
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install"] + missing_packages)
        print("✅ Пакеты установлены!")
        return True
    except Exception as e:
        print(f"❌ Ошибка установки: {e}")
        print("\nУстановите вручную:")
        print(f"pip install {' '.join(missing_packages)}")
        return False

def disclaimer():
    """Вывод предупреждения"""
    from utils import print_banner
    
    print_banner("ВАЖНОЕ ПРЕДУПРЕЖДЕНИЕ", 80)
    print("🚨 ЭТОТ БОТ ПРЕДНАЗНАЧЕН ИСКЛЮЧИТЕЛЬНО ДЛЯ:")
    print("   1. ОБРАЗОВАТЕЛЬНЫХ ЦЕЛЕЙ И ИССЛЕДОВАНИЙ")
    print("   2. ТРЕНИРОВОЧНОГО РЕЖИМА MLBB")
    print("   3. ИЗУЧЕНИЯ КОМПЬЮТЕРНОГО ЗРЕНИЯ И ИИ")
    print("")
    print("⚠️ ЗАПРЕЩЕНО ИСПОЛЬЗОВАТЬ В РАНГОВЫХ ИГРАХ!")
    print("⚠️ ИСПОЛЬЗОВАНИЕ МОЖЕТ ПРИВЕСТИ К БАНУ АККАУНТА!")
    print("⚠️ АВТОР НЕ НЕСЕТ ОТВЕТСТВЕННОСТИ ЗА ВАШИ ДЕЙСТВИЯ!")
    print("=" * 80)
    
    confirm = input("\nЯ понимаю и согласен (y/n): ")
    return confirm.lower() == 'y'

def check_files():
    """Проверка наличия всех файлов"""
    required_files = [
        'config.py',
        'game_state.py',
        'utils.py',
        'vision_engine.py',
        'input_controller.py',
        'combo_system.py',
        'decision_maker.py',
        'learning_engine.py',
        'bot_core.py'
    ]
    
    missing_files = []
    for file in required_files:
        if not os.path.exists(file):
            missing_files.append(file)
    
    return missing_files

def create_missing_files(missing_files):
    """Создание недостающих файлов"""
    print(f"\n📄 Создаю недостающие файлы ({len(missing_files)}):")
    
    # Базовые заглушки для быстрого создания
    file_templates = {
        'config.py': "# Конфигурация будет создана автоматически\n",
        'game_state.py': "# Классы состояния будут созданы автоматически\n",
        'utils.py': "# Утилиты будут созданы автоматически\n",
    }
    
    for file in missing_files:
        content = file_templates.get(file, "# Файл создан автоматически\n")
        
        try:
            with open(file, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"  ✓ {file}")
        except Exception as e:
            print(f"  ✗ {file}: {e}")
    
    print("\n⚠️ Файлы созданы как заглушки. Запустите программу снова.")
    return len(missing_files) == 0

def main():
    """Главная функция"""
    print("🤖 MLBB ХАЯБУСА БОТ v2.0")
    print("=" * 60)
    
    # Проверка зависимостей
    missing_packages = check_dependencies()
    if missing_packages:
        if not install_dependencies(missing_packages):
            input("\nНажмите Enter для выхода...")
            return
    
    # Проверка файлов
    missing_files = check_files()
    if missing_files:
        if not create_missing_files(missing_files):
            input("\nНажмите Enter для выхода...")
            return
        return  # Перезапустите программу после создания файлов
    
    # Предупреждение
    if not disclaimer():
        print("\nВыход...")
        return
    
    # Запуск бота
    try:
        from bot_core import HayabusaBot
        
        print("\n" + "="*60)
        print("🎮 ПОДГОТОВКА К ЗАПУСКУ")
        print("="*60)
        print("1. Откройте MLBB в оконном режиме")
        print("2. Зайдите в тренировочный режим")
        print("3. Выберите Хаябусу")
        print("4. Убедитесь что игра активна")
        print("="*60)
        
        input("\nНажмите Enter когда будете готовы...")
        
        # Создаем и запускаем бота
        bot = HayabusaBot()
        bot.main_loop()
        
    except ImportError as e:
        print(f"\n❌ Ошибка импорта: {e}")
        print("Проверьте наличие всех файлов бота.")
        input("\nНажмите Enter для выхода...")
    except Exception as e:
        print(f"\n❌ Критическая ошибка: {e}")
        import traceback
        traceback.print_exc()
        input("\nНажмите Enter для выхода...")

if __name__ == "__main__":
    main()