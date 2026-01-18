# mllb_bot

# 1. Установка зависимостей
pip install opencv-python numpy pyautogui keyboard

# 2. Запуск scrcpy (телефон по USB)
scrcpy --video-codec=h265 --max-size=1920

# 3. Создай шаблоны (СОВЕРШЕННО ОБЯЗАТЕЛЬНО):
#   - Запусти MLBB в тренировке
#   - Сделай скриншоты:
#     skill1.png  - кнопка 1-го навыка (120x120px)
#     skill2.png  - кнопка 2-го навыка  
#     enemy_dot.png - красная точка врага на миникарте (30x30px)
#     creep.png   - желтый крип на миникарте (30x30px)
#     recall.png  - кнопка рекара (80x80px)
#     shop.png    - иконка магазина (60x60px)

# 4. Запуск бота
python mlbb_bot.py
