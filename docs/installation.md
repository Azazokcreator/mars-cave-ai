
# Mars Cave AI — Installation & Setup Guide

---

# 🇷🇺 Инструкция по установке и запуску

## 1️⃣ Требования

### Операционная система
- Windows 10/11 (рекомендуется)
- macOS / Linux (возможна адаптация)

### Python
- Python 3.10 – 3.11

Проверка версии:
```bash
python --version
````

---

## 2️⃣ Клонирование репозитория

```bash
git clone https://github.com/your-username/mars-cave-ai.git
cd mars-cave-ai
```

---

## 3️⃣ Создание виртуального окружения

```bash
python -m venv venv
```

Активировать:

Windows:

```bash
venv\Scripts\activate
```

macOS/Linux:

```bash
source venv/bin/activate
```

---

## 4️⃣ Установка зависимостей

```bash
pip install -r requirements.txt
```

Если используется GPU (CUDA), PyTorch необходимо установить отдельно согласно инструкции:
[https://pytorch.org](https://pytorch.org)

---

## 5️⃣ Загрузка весов модели

Веса модели не хранятся в репозитории.

Скачать файл:

```
unet_safe_obstacle1.pth
```

Поместить в папку:

```
models/
```

Структура:

```
mars-cave-ai/
  models/
    unet_safe_obstacle1.pth
```

---

## 6️⃣ Настройка ESP32-CAM

1. Загрузить прошивку для MJPEG-stream.
2. Подключить ESP32 к Wi-Fi.
3. Узнать IP-адрес устройства.
4. Проверить в браузере:

```
http://<ESP_IP>/stream
```

Если видео отображается — камера работает корректно.

---

## 7️⃣ Подключение SPIKE Prime

1. Установить Pybricks firmware.
2. Загрузить скрипт сервера:

```
src/spike/spike_server.py
```

3. Убедиться, что BLE-соединение доступно.
4. Закрыть LEGO приложение (если запущено).

---

## 8️⃣ Запуск AI-монитора

```bash
python src/pc/cave_ai_monitor.py
```

После запуска:

* откроется окно видеопотока
* будет отображаться сегментация
* можно управлять роботом

---

## 🎮 Управление

W — вперед
S — назад
A — поворот влево
D — поворот вправо
SPACE — стоп
M — включить автопилот
Q — выход

---

## ⚠️ Возможные ошибки

### BLE не подключается

* закрыть LEGO / Pybricks Code
* перезапустить хаб
* проверить имя устройства

---

### Нет видеопотока

* проверить IP ESP32
* убедиться, что устройство в одной сети
* проверить /stream в браузере

---

# 🇬🇧 Installation Guide

---

## 1️⃣ Requirements

### OS

* Windows 10/11 (recommended)
* macOS / Linux (adaptable)

### Python

* Python 3.10 – 3.11

Check version:

```bash
python --version
```

---

## 2️⃣ Clone Repository

```bash
git clone https://github.com/your-username/mars-cave-ai.git
cd mars-cave-ai
```

---

## 3️⃣ Create Virtual Environment

```bash
python -m venv venv
```

Activate:

Windows:

```bash
venv\Scripts\activate
```

macOS/Linux:

```bash
source venv/bin/activate
```

---

## 4️⃣ Install Dependencies

```bash
pip install -r requirements.txt
```

If GPU is required, install PyTorch separately from:
[https://pytorch.org](https://pytorch.org)

---

## 5️⃣ Download Model Weights

Download:

```
unet_safe_obstacle1.pth
```

Place into:

```
models/
```

---

## 6️⃣ ESP32 Setup

1. Flash MJPEG streaming firmware.
2. Connect ESP32 to Wi-Fi.
3. Find its IP address.
4. Test stream:

```
http://<ESP_IP>/stream
```

---

## 7️⃣ SPIKE Setup

1. Install Pybricks firmware.
2. Upload spike_server.py.
3. Ensure BLE availability.
4. Close LEGO official app.

---

## 8️⃣ Run AI Monitor

```bash
python src/pc/cave_ai_monitor.py
```

---

## 🎮 Controls

W — forward
S — backward
A — left
D — right
SPACE — stop
M — toggle autopilot
Q — quit

---

# ✅ System Ready

If everything is configured correctly, the system should:

* display real-time segmentation
* respond to manual commands
* operate in autopilot mode




