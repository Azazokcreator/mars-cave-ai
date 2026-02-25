# 🚀 Mars Cave AI
## AI Navigation for Underground Space Missions

---

## 🇷🇺 Описание проекта

Mars Cave AI — это система автономной навигации для роботов, предназначенных для исследования подземных объектов на Луне и Марсе: лавовых трубок, пещер и туннелей.

Система демонстрирует полный цикл работы:

📷 видеопоток → 🧠 нейросеть → 🗺 карта проходимости → 🤖 управление роботом

---

## 🇬🇧 Project Overview

Mars Cave AI is an autonomous navigation system designed for robots exploring underground environments on the Moon and Mars, such as lava tubes, caves, and tunnels.

The system demonstrates a full AI pipeline:

📷 video stream → 🧠 neural network → 🗺 safety map → 🤖 robot control

---

# 🌌 Проблема / Problem

## 🇷🇺

Подземные пространства — ключевые объекты будущих космических миссий:

- потенциальные места размещения баз
- защита от радиации
- возможные источники воды

Основные трудности:

- отсутствие GPS
- слабая связь
- высокий риск потери роботов
- оператор не видит реальную проходимость среды

---

## 🇬🇧

Underground environments are critical for future space missions:

- potential locations for human bases
- natural radiation protection
- possible water resources

Challenges:

- no GPS
- limited communication
- high risk of robot loss
- operators cannot assess terrain safety

---

# 💡 Решение / Solution

## 🇷🇺

Mars Cave AI — AI-модуль автономной навигации, который:

✔ анализирует видео в реальном времени  
✔ строит карту безопасного движения  
✔ помогает оператору управлять роботом  
✔ обеспечивает полуавтономное движение  

---

## 🇬🇧

Mars Cave AI is an AI navigation module that:

✔ processes live video  
✔ generates a safety map  
✔ assists operator navigation  
✔ enables semi-autonomous robot movement  

---

# ⚙️ MVP Возможности / MVP Features

## 🇷🇺

- Live video с ESP32-CAM
- Сегментация среды в реальном времени (U-Net)
- Определение SAFE / OBSTACLE зон
- HUD интерфейс мониторинга
- Управление роботом через BLE (Pybricks)
- MANUAL режим управления
- AUTO режим автопилота

---

## 🇬🇧

- Live video from ESP32-CAM
- Real-time environment segmentation (U-Net)
- SAFE / OBSTACLE detection
- Monitoring HUD interface
- BLE robot control (Pybricks)
- Manual driving mode
- AI autopilot mode

---

# 🧠 Как работает система / System Workflow


ESP32 Camera → PC → AI Segmentation → Safety Map → Decision → BLE → Robot


---

# 🎮 Команды управления / Control Commands

| Command | Action |
|--------|--------|
| fwd | move forward |
| rev | move backward |
| stp | stop |
| lft | turn left |
| rgt | turn right |
| ctr | center / go straight |
| bye | terminate program |

---

# 🤖 Автопилот / Autopilot Logic

## 🇷🇺

Алгоритм:

1. Анализ нижней части кадра (ROI)
2. Деление на зоны: Left / Center / Right
3. Оценка безопасной области
4. Выбор направления движения

---

## 🇬🇧

Algorithm:

1. Analyze lower frame region (ROI)
2. Split into Left / Center / Right zones
3. Calculate safe area ratio
4. Select safest direction

---

# 🛰️ Космическое применение / Space Applications

## 🇷🇺

- разведка лавовых трубок
- исследование марсианских пещер
- автономная навигация подземных роботов
- снижение риска потери аппаратов

---

## 🇬🇧

- lava tube exploration
- Martian cave scouting
- autonomous underground navigation
- reducing mission risk

---

# 🛠️ Технологический стек / Technology Stack

- Python
- PyTorch
- U-Net segmentation
- OpenCV
- ESP32-CAM streaming
- BLE (Bleak)
- Pybricks SPIKE

---

# ▶️ Запуск / Getting Started

## Installation

```bash
pip install -r requirements.txt
Run AI Monitor
python cave_ai_monitor.py