# Mars Cave AI — MVP Demonstration

---

## Сценарий демонстрации MVP

### Цель демонстрации

Показать работу прототипа системы автономной навигации робота-спелеолога на основе искусственного интеллекта.

Во время демонстрации система:

- получает видеопоток с робота
- анализирует окружающую среду нейросетью
- определяет безопасный маршрут
- управляет движением робота

---

## ⚙️ Оборудование

### Роботическая платформа

- LEGO SPIKE Prime
- Мотор A — движение
- Мотор C — поворот

---

### Камера

ESP32-CAM:

- передаёт видеопоток по Wi-Fi
- формат — MJPEG stream

---

### Вычислительный модуль

Ноутбук с:

- Python
- PyTorch
- обученной нейросетью UNet

---

## Искусственный интеллект

Используется модель сегментации:

**UNet + ResNet18 encoder**

Задача модели:

Классификация сцены на:

- SAFE — безопасная поверхность
- OBSTACLE — препятствия

---

## Pipeline работы системы

### 1. Захват видео

ESP32-CAM передаёт поток в реальном времени на ноутбук.

---

### 2. Обработка нейросетью

Каждый кадр:

- масштабируется
- подаётся в модель
- сегментируется

---

### 3. Анализ безопасного маршрута

Нижняя часть изображения:

делится на 3 зоны:

- Left
- Center
- Right

Система вычисляет процент препятствий.

---

### 4. Принятие решения

Алгоритм автопилота:

- Если центр свободен → движение вперёд
- Если центр заблокирован → поворот в безопасную сторону
- Если всё заблокировано → остановка

---

### 5. Управление роботом

Команды передаются через BLE:

- `fwd` — движение вперёд
- `rev` — назад
- `stp` — стоп
- `lft` — поворот влево
- `rgt` — вправо
- `ctr` — центр
- `bye` — завершение работы

---

## Интерфейс демонстрации

На экране отображается:

- видеопоток с робота
- сегментация сцены
- статистика безопасной зоны
- режим управления

---

## Режимы работы

### MANUAL

Ручное управление с клавиатуры.

---

### AUTO

Система автоматически:

- анализирует среду
- выбирает безопасное направление
- управляет движением робота

---

## Результат демонстрации

Система успешно показывает:

- работу нейросети в реальном времени
- анализ безопасного маршрута
- управление роботической платформой
- возможность автономной навигации

---

## Космическое применение

Данная технология может использоваться для:

- исследования марсианских пещер
- миссий на Луне
- автономных космических роботов

---

---

## MVP Demonstration Scenario

### Goal

To demonstrate an AI-powered robotic navigation system operating in cave environments.

The system performs:

- real-time video acquisition
- neural network segmentation
- safe path detection
- robot control

---

## Hardware

Robot:

- LEGO SPIKE Prime

Camera:

- ESP32-CAM Wi-Fi video stream

Processing:

- Laptop with PyTorch AI model

---

## AI Model

UNet segmentation network classifies:

SAFE vs OBSTACLE areas.

---

## Pipeline

1. Video stream from ESP32-CAM  
2. Neural network segmentation  
3. Safe path analysis  
4. Autonomous decision making  
5. BLE robot control  

---

## Modes

Manual mode — keyboard control  
Auto mode — AI navigation  

---

## Result

The MVP demonstrates:

- real-time AI navigation
- robotic cave exploration
- autonomous movement capability

---

## Space Application

The system can be adapted for:

- Mars lava tubes exploration
- lunar cave missions
- underground planetary robotics