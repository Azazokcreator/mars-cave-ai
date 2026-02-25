
"""
SPIKE Prime / Pybricks BLE Server для управления роботом-танком
Протокол: получает 3-байтные команды через stdin, отправляет "rdy" через stdout

Команды:
  fwd - вперёд (tank_drive с положительной мощностью)
  rev - назад (tank_drive с отрицательной мощностью)
  stp - стоп
  lft - поворот налево на месте
  rgt - поворот направо на месте
  ctr - ехать прямо (центр)
  bye - завершение работы


from pybricks.pupdevices import Motor, UltrasonicSensor
from pybricks.parameters import Port, Stop, Direction
from pybricks.tools import wait
from usys import stdin, stdout
from uselect import poll

# ═══════════════════════════════════════════════════════════════
#   КОНФИГУРАЦИЯ МОТОРОВ
# ═══════════════════════════════════════════════════════════════

# Порты подключения моторов
FLASHLIGHT = UltrasonicSensor(Port.A)
LEFT_MOTOR_PORT = Port.C
RIGHT_MOTOR_PORT = Port.D

# Направление вращения моторов
# Если робот едёт назад когда должен ехать вперёд - поменяйте на COUNTERCLOCKWISE
LEFT_MOTOR_DIRECTION = Direction.COUNTERCLOCKWISE
RIGHT_MOTOR_DIRECTION = Direction.CLOCKWISE

left_motor = Motor(LEFT_MOTOR_PORT, LEFT_MOTOR_DIRECTION)
right_motor = Motor(RIGHT_MOTOR_PORT, RIGHT_MOTOR_DIRECTION)

# ═══════════════════════════════════════════════════════════════
#   ПАРАМЕТРЫ ДВИЖЕНИЯ
# ═══════════════════════════════════════════════════════════════

DRIVE_DC = 55           # Мощность движения вперёд/назад (-100 до 100)
TURN_STRENGTH = 55      # Мощность при повороте на месте (0 до 100)

# Константы направлений
CENTER = 0
LEFT = -1
RIGHT = +1

# ═══════════════════════════════════════════════════════════════
#   ФУНКЦИИ УПРАВЛЕНИЯ
# ═══════════════════════════════════════════════════════════════

def tank_drive(left_power, right_power):
    """
    Установить мощность для обоих моторов
    
    Args:
        left_power: мощность левого мотора (-100 до 100)
        right_power: мощность правого мотора (-100 до 100)
    """
    left_motor.dc(left_power)
    right_motor.dc(right_power)


def drive_forward():
    """Ехать вперёд"""
    tank_drive(DRIVE_DC, DRIVE_DC)


def drive_backward():
    """Ехать назад"""
    tank_drive(-DRIVE_DC, -DRIVE_DC)


def turn_left():
    """Поворот налево на месте"""
    tank_drive(-TURN_STRENGTH, TURN_STRENGTH)


def turn_right():
    """Поворот направо на месте"""
    tank_drive(TURN_STRENGTH, -TURN_STRENGTH)


def drive_straight():
    """Ехать прямо (то же что forward)"""
    tank_drive(DRIVE_DC, DRIVE_DC)


def stop_motors():
    """Остановить все моторы"""
    left_motor.stop()
    right_motor.stop()


# ═══════════════════════════════════════════════════════════════
#   ИНИЦИАЛИЗАЦИЯ
# ═══════════════════════════════════════════════════════════════

# Настройка опроса stdin
keyboard = poll()
keyboard.register(stdin)

# Остановить моторы при старте
stop_motors()

# ═══════════════════════════════════════════════════════════════
#   ОСНОВНОЙ ЦИКЛ СЕРВЕРА
# ═══════════════════════════════════════════════════════════════

# Отправляем первый сигнал готовности при запуске
stdout.buffer.write(b"rdy")
wait(50)  # Небольшая задержка для стабильности BLE

while True:
    # Ожидаем поступления данных от клиента (Python PC)
    FLASHLIGHT.lights.on(100)
    while not keyboard.poll(0):
        wait(10)
    
    # Читаем команду (всегда 3 байта)
    cmd = stdin.buffer.read(3)
    
    # Проверка: команда должна быть ровно 3 байта
    if not cmd or len(cmd) != 3:
        stop_motors()
        stdout.buffer.write(b"ERR")
        stdout.buffer.write(b"rdy")
        continue
    
    # ─────────────────────────────────────────────────────────
    # ОБРАБОТКА КОМАНД
    # ─────────────────────────────────────────────────────────
    
    if cmd == b"fwd":
        # Команда: ехать вперёд
        drive_forward()
        stdout.buffer.write(b"OK ")
    
    elif cmd == b"rev":
        # Команда: ехать назад
        drive_backward()
        stdout.buffer.write(b"OK ")
    
    elif cmd == b"stp":
        # Команда: стоп
        stop_motors()
        stdout.buffer.write(b"OK ")
    
    elif cmd == b"lft":
        # Команда: поворот налево на месте
        turn_left()
        stdout.buffer.write(b"OK ")
    
    elif cmd == b"rgt":
        # Команда: поворот направо на месте
        turn_right()
        stdout.buffer.write(b"OK ")
    
    elif cmd == b"ctr":
        # Команда: ехать прямо (центр)
        drive_straight()
        stdout.buffer.write(b"OK ")
    
    elif cmd == b"bye":
        # Команда: завершить работу
        stop_motors()
        stdout.buffer.write(b"BYE")
        FLASHLIGHT.lights.off()
        wait(300)  # Задержка перед выходом
        break
    
    else:
        # Неизвестная команда
        stop_motors()
        stdout.buffer.write(b"???")
    
    stdout.buffer.write(b"rdy")

# ═══════════════════════════════════════════════════════════════
#   ЗАВЕРШЕНИЕ РАБОТЫ
# ═══════════════════════════════════════════════════════════════
FLASHLIGHT.lights.off()
stop_motors()
