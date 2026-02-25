
"""
ESP32 MJPEG Cave AI Monitor with Autopilot - GUI Interface
===========================================================

Графический интерфейс с tkinter для управления роботом через BLE
с видеопотоком, сегментацией и автопилотом.

Требования:
  pip install bleak opencv-python numpy torch segmentation-models-pytorch pillow
"""

from __future__ import annotations

import time
import threading
import queue
from dataclasses import dataclass
from pathlib import Path
from typing import Tuple, Optional
import tkinter as tk
from tkinter import ttk, messagebox
from PIL import Image, ImageTk

import cv2
import numpy as np
import torch
import segmentation_models_pytorch as smp

import asyncio
import sys
from bleak import BleakClient, BleakScanner

# ═══════════════════════════════════════════════════════════════════════════
#   КОНФИГУРАЦИЯ
# ═══════════════════════════════════════════════════════════════════════════

STREAM_URL = "/stream"
HUB_NAME = "Pybricks Hub"
PYBRICKS_CHAR_UUID = "CHAR UUID"
MODEL_PATH = Path(r"\mars_cave_ai\models\unet_safe_obstacle1.pth")
IMG_SIZE = 320
INFER_EVERY_N_FRAMES = 2
ALPHA = 0.35

# Команды 
CMD_FWD = b"rev"
CMD_REV = b"fwd"
CMD_STOP = b"stp"
CMD_LEFT = b"lft"
CMD_RIGHT = b"rgt"
CMD_CENTER = b"ctr"
CMD_BYE = b"bye"

# Автопилот
ROI_Y1 = 0.55
ROI_Y2 = 0.95
CENTER_CLEAR_MAX_OBS = 0.20
STOP_IF_ALL_BAD = 0.60
TURN_HOLD_SEC = 0.35
AUTO_DRIVE_INTERVAL = 0.22
AUTO_STEER_INTERVAL = 0.28
MANUAL_OVERRIDE_SEC = 1.0


# ═══════════════════════════════════════════════════════════════════════════
#   BLE КОНТРОЛЛЕР
# ═══════════════════════════════════════════════════════════════════════════

@dataclass
class HubStatus:
    connected: bool = False
    last_reply: bytes = b""
    last_ready_ts: float = 0.0
    last_send_ts: float = 0.0
    err: str = ""


class SpikeBLEController:
    def __init__(self, hub_name: str):
        self.hub_name = hub_name
        self.status = HubStatus()
        self._cmd_q: queue.Queue[bytes] = queue.Queue()
        self._stop = threading.Event()
        self._ready_event: Optional[asyncio.Event] = None
        self._thread = threading.Thread(target=self._run_thread, daemon=True)

    def start(self):
        self._thread.start()

    def stop(self):
        self._stop.set()
        try:
            self._cmd_q.put_nowait(CMD_BYE)
        except Exception:
            pass

    def send(self, cmd3: bytes):
        if not isinstance(cmd3, (bytes, bytearray)) or len(cmd3) != 3:
            return
        self._cmd_q.put(cmd3)

    def _handle_rx(self, _, data: bytearray):
        if not data:
            return
        if data[0] == 0x01:
            payload = bytes(data[1:])
            if payload == b"rdy":
                self.status.last_ready_ts = time.time()
                if self._ready_event is not None:
                    self._ready_event.set()
            else:
                self.status.last_reply = payload

    async def _ble_loop(self):
        if sys.platform.startswith("win"):
            asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

        self._ready_event = asyncio.Event()

        while not self._stop.is_set():
            try:
                self.status.err = ""
                self.status.connected = False

                dev = await BleakScanner.find_device_by_name(self.hub_name, timeout=12.0)
                if dev is None:
                    self.status.err = "Hub not found"
                    await asyncio.sleep(1.0)
                    continue

                async with BleakClient(dev) as client:
                    self.status.connected = True
                    await client.start_notify(PYBRICKS_CHAR_UUID, self._handle_rx)

                    while not self._stop.is_set() and client.is_connected:
                        try:
                            cmd = self._cmd_q.get(timeout=0.2)
                        except queue.Empty:
                            continue

                        try:
                            await asyncio.wait_for(self._ready_event.wait(), timeout=2.5)
                        except asyncio.TimeoutError:
                            self.status.err = "No 'rdy' from hub"
                            self._ready_event.clear()
                            continue

                        self._ready_event.clear()

                        try:
                            await client.write_gatt_char(
                                PYBRICKS_CHAR_UUID,
                                b"\x06" + cmd,
                                response=True
                            )
                            self.status.last_send_ts = time.time()
                        except Exception as e:
                            self.status.err = f"Send error: {type(e).__name__}"
                            break

                    try:
                        await client.stop_notify(PYBRICKS_CHAR_UUID)
                    except Exception:
                        pass

            except Exception as e:
                self.status.err = f"BLE error: {type(e).__name__}"
                await asyncio.sleep(1.0)

    def _run_thread(self):
        asyncio.run(self._ble_loop())


# ═══════════════════════════════════════════════════════════════════════════
#   МОДЕЛЬ СЕГМЕНТАЦИИ
# ═══════════════════════════════════════════════════════════════════════════

def load_model(model_path: Path):
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model = smp.Unet("resnet18", encoder_weights=None, in_channels=3, classes=2).to(device)
    model.load_state_dict(torch.load(model_path, map_location=device))
    model.eval()
    return model, device


@torch.no_grad()
def predict_mask(model, device, frame_bgr: np.ndarray, img_size: int) -> np.ndarray:
    h, w = frame_bgr.shape[:2]
    rgb = cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2RGB)
    inp = cv2.resize(rgb, (img_size, img_size), interpolation=cv2.INTER_AREA)
    x = (inp.astype(np.float32) / 255.0).transpose(2, 0, 1)[None, ...]
    x = torch.tensor(x, device=device)
    logits = model(x)
    pred = torch.argmax(logits, dim=1).detach().cpu().numpy()[0].astype(np.uint8)
    return cv2.resize(pred, (w, h), interpolation=cv2.INTER_NEAREST)


def zone_ratios(mask01: np.ndarray):
    h, w = mask01.shape[:2]
    y1 = int(h * ROI_Y1)
    y2 = int(h * ROI_Y2)
    roi = mask01[y1:y2, :]
    third = w // 3
    L = roi[:, :third]
    C = roi[:, third:2 * third]
    R = roi[:, 2 * third:]
    oL = float(np.mean(L == 1))
    oC = float(np.mean(C == 1))
    oR = float(np.mean(R == 1))
    return oL, oC, oR, (y1, y2)


def autopilot(oL, oC, oR):
    if min(oL, oC, oR) > STOP_IF_ALL_BAD:
        return CMD_STOP, CMD_CENTER
    if oC <= CENTER_CLEAR_MAX_OBS:
        return CMD_FWD, CMD_CENTER
    if oL < oR:
        return CMD_FWD, CMD_LEFT
    else:
        return CMD_FWD, CMD_RIGHT


# ═══════════════════════════════════════════════════════════════════════════
#   GUI ПРИЛОЖЕНИЕ
# ═══════════════════════════════════════════════════════════════════════════

class CaveAIApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Cave AI Monitor - Autopilot Control")
        self.root.geometry("1400x900")
        self.root.configure(bg="#1a1a1a")

        # Состояние
        self.auto_on = False
        self.running = True
        self.last_mask = None
        self.frame_id = 0
        self.fps = 0.0
        self.safe_ratio = 0.0
        self.obst_ratio = 0.0
        self.oL = self.oC = self.oR = 0.0

        # Таймеры автопилота
        self.last_drive_ts = 0.0
        self.last_steer_ts = 0.0
        self.last_turn_ts = 0.0
        self.last_manual_ts = 0.0

        # Инициализация
        self.setup_ui()
        self.load_resources()
        self.start_threads()

        # Привязка клавиш
        self.root.bind('<KeyPress>', self.on_key_press)
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

        # Обновление UI
        self.update_ui()

    def setup_ui(self):
        """Создание интерфейса"""

        # ═══════════════════════════════════════════════════════════════════
        # ВЕРХНЯЯ ПАНЕЛЬ - СТАТУС И УПРАВЛЕНИЕ
        # ═══════════════════════════════════════════════════════════════════

        top_frame = tk.Frame(self.root, bg="#2a2a2a", height=100)
        top_frame.pack(side=tk.TOP, fill=tk.X, padx=10, pady=10)
        top_frame.pack_propagate(False)

        # Левая часть - статус
        status_frame = tk.Frame(top_frame, bg="#2a2a2a")
        status_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10, pady=10)

        self.status_label = tk.Label(
            status_frame,
            text="🔴 Disconnected",
            font=("Arial", 16, "bold"),
            fg="#ff4444",
            bg="#2a2a2a"
        )
        self.status_label.pack(anchor=tk.W)

        self.mode_label = tk.Label(
            status_frame,
            text="MODE: MANUAL",
            font=("Arial", 14),
            fg="#ffffff",
            bg="#2a2a2a"
        )
        self.mode_label.pack(anchor=tk.W, pady=5)

        self.error_label = tk.Label(
            status_frame,
            text="",
            font=("Arial", 10),
            fg="#ffaa00",
            bg="#2a2a2a"
        )
        self.error_label.pack(anchor=tk.W)

        # Правая часть - кнопки управления
        control_frame = tk.Frame(top_frame, bg="#2a2a2a")
        control_frame.pack( side=tk.RIGHT, padx=10, pady=10)

        self.arm_button = tk.Button(
            control_frame,
            text="ARM AUTO",
            command=self.toggle_auto,
            font=("Arial", 14, "bold"),
            bg="#4a4a4a",
            fg="#ffffff",
            activebackground="#5a5a5a",
            width=15,
            height=2,
            relief=tk.RAISED,
            bd=3
        )
        self.arm_button.pack(pady=5)

        emergency_button = tk.Button(
            control_frame,
            text="⚠ EMERGENCY STOP",
            command=self.emergency_stop,
            font=("Arial", 12, "bold"),
            bg="#aa2222",
            fg="#ffffff",
            activebackground="#cc3333",
            width=15,
            height=1
        )
        emergency_button.pack(pady=5)

        # ═══════════════════════════════════════════════════════════════════
        # ЦЕНТРАЛЬНАЯ ПАНЕЛЬ - ВИДЕО
        # ═══════════════════════════════════════════════════════════════════

        video_frame = tk.Frame(self.root, bg="#1a1a1a")
        video_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True, padx=10, pady=5)

        # Левое видео - оригинал
        left_panel = tk.Frame(video_frame, bg="#2a2a2a", relief=tk.RIDGE, bd=2)
        left_panel.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5)

        tk.Label(
            left_panel,
            text="VIDEO STREAM",
            font=("Arial", 12, "bold"),
            fg="#ffffff",
            bg="#2a2a2a"
        ).pack(pady=5)

        self.video_label = tk.Label(left_panel, bg="#000000")
        self.video_label.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Правое видео - сегментация
        right_panel = tk.Frame(video_frame, bg="#2a2a2a", relief=tk.RIDGE, bd=2)
        right_panel.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=5)

        tk.Label(
            right_panel,
            text="SEGMENTATION",
            font=("Arial", 12, "bold"),
            fg="#ffffff",
            bg="#2a2a2a"
        ).pack(pady=5)

        self.seg_label = tk.Label(right_panel, bg="#000000")
        self.seg_label.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # ═══════════════════════════════════════════════════════════════════
        # НИЖНЯЯ ПАНЕЛЬ - МЕТРИКИ И УПРАВЛЕНИЕ
        # ═══════════════════════════════════════════════════════════════════

        bottom_frame = tk.Frame(self.root, bg="#2a2a2a", height=200)
        bottom_frame.pack(side=tk.BOTTOM, fill=tk.X, padx=10, pady=10)
        bottom_frame.pack_propagate(False)

        # Метрики
        metrics_frame = tk.Frame(bottom_frame, bg="#2a2a2a")
        metrics_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10)

        tk.Label(
            metrics_frame,
            text="METRICS",
            font=("Arial", 14, "bold"),
            fg="#ffffff",
            bg="#2a2a2a"
        ).pack(anchor=tk.W, pady=5)

        self.metrics_text = tk.Text(
            metrics_frame,
            font=("Courier", 11),
            bg="#1a1a1a",
            fg="#00ff00",
            height=8,
            width=50,
            relief=tk.FLAT,
            state=tk.DISABLED
        )
        self.metrics_text.pack(fill=tk.BOTH, expand=True)

        # Управление клавишами
        keys_frame = tk.Frame(bottom_frame, bg="#2a2a2a")
        keys_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=10)

        tk.Label(
            keys_frame,
            text="KEYBOARD CONTROLS",
            font=("Arial", 14, "bold"),
            fg="#ffffff",
            bg="#2a2a2a"
        ).pack(anchor=tk.W, pady=5)

        keys_text = """
        M          - ARM/DISARM Autopilot
        W          - Forward
        S          - Reverse
        A          - Turn Left
        D          - Turn Right
        E          - Center
        SPACE      - Emergency Stop
        Q / ESC    - Quit
        """

        tk.Label(
            keys_frame,
            text=keys_text,
            font=("Courier", 10),
            fg="#cccccc",
            bg="#2a2a2a",
            justify=tk.LEFT
        ).pack(anchor=tk.W, padx=10)

    def load_resources(self):
        """Загрузка модели и инициализация BLE"""
        if not MODEL_PATH.exists():
            messagebox.showerror("Error", f"Model not found:\n{MODEL_PATH}")
            self.root.quit()
            return

        self.model, self.device = load_model(MODEL_PATH)
        self.ble = SpikeBLEController(HUB_NAME)
        self.ble.start()

    def start_threads(self):
        """Запуск фоновых потоков"""
        # Поток видео
        self.video_thread = threading.Thread(target=self.video_loop, daemon=True)
        self.video_thread.start()

        # Поток автопилота
        self.auto_thread = threading.Thread(target=self.autopilot_loop, daemon=True)
        self.auto_thread.start()

    def video_loop(self):
        """Фоновый поток захвата видео"""
        cap = cv2.VideoCapture(STREAM_URL)
        t0 = time.time()
        nframes = 0

        while self.running:
            ret, frame = cap.read()
            if not ret or frame is None:
                time.sleep(0.1)
                continue

            self.frame_id += 1
            nframes += 1
            self.fps = nframes / max(1e-6, (time.time() - t0))

            # Инференс
            if self.frame_id % INFER_EVERY_N_FRAMES == 0:
                try:
                    self.last_mask = predict_mask(self.model, self.device, frame, IMG_SIZE)
                except Exception:
                    self.last_mask = None

            # Обработка маски
            if self.last_mask is not None:
                mask = self.last_mask
                self.safe_ratio = float(np.mean(mask == 0))
                self.obst_ratio = 1.0 - self.safe_ratio
                self.oL, self.oC, self.oR, roi_y = zone_ratios(mask)

                # Сегментация с оверлеем
                overlay = frame.copy()
                overlay[mask == 0] = (0, 255, 0)
                overlay[mask == 1] = (0, 0, 255)
                seg = cv2.addWeighted(frame, 1 - ALPHA, overlay, ALPHA, 0)

                # Рисуем ROI линии
                h, w = frame.shape[:2]
                y1, y2 = roi_y
                cv2.line(seg, (0, y1), (w, y1), (255, 255, 255), 2)
                cv2.line(seg, (0, y2), (w, y2), (255, 255, 255), 2)
                t1 = w // 3
                t2 = 2 * w // 3
                cv2.line(seg, (t1, y1), (t1, y2), (255, 255, 255), 2)
                cv2.line(seg, (t2, y1), (t2, y2), (255, 255, 255), 2)
            else:
                seg = frame.copy()

            # Конвертация для tkinter
            self.current_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            self.current_seg = cv2.cvtColor(seg, cv2.COLOR_BGR2RGB)

        cap.release()

    def autopilot_loop(self):
        """Фоновый поток автопилота"""
        while self.running:
            time.sleep(0.05)

            if not self.auto_on or not self.ble.status.connected or self.last_mask is None:
                continue

            now = time.time()
            if (now - self.last_manual_ts) < MANUAL_OVERRIDE_SEC:
                continue

            # Решение автопилота
            drive_cmd, steer_cmd = autopilot(self.oL, self.oC, self.oR)

            # Рулежка
            if steer_cmd in (CMD_LEFT, CMD_RIGHT):
                if now - self.last_steer_ts >= AUTO_STEER_INTERVAL:
                    self.ble.send(steer_cmd)
                    self.last_steer_ts = now
                    self.last_turn_ts = now
            else:
                if (now - self.last_turn_ts) > TURN_HOLD_SEC and (now - self.last_steer_ts) >= AUTO_STEER_INTERVAL:
                    self.ble.send(CMD_CENTER)
                    self.last_steer_ts = now

            # Привод
            if now - self.last_drive_ts >= AUTO_DRIVE_INTERVAL:
                self.ble.send(drive_cmd)
                self.last_drive_ts = now

    def update_ui(self):
        """Обновление UI (главный поток)"""
        if not self.running:
            return

        # Обновление статуса
        if self.ble.status.connected:
            self.status_label.config(text="🟢 Connected", fg="#44ff44")
        else:
            self.status_label.config(text="🔴 Disconnected", fg="#ff4444")

        mode = "AUTO" if self.auto_on else "MANUAL"
        self.mode_label.config(text=f"MODE: {mode}")

        if self.ble.status.err:
            self.error_label.config(text=f"Error: {self.ble.status.err}")
        else:
            self.error_label.config(text="")

        # Обновление кнопки ARM
        if self.auto_on:
            self.arm_button.config(text="DISARM AUTO", bg="#22aa22")
        else:
            self.arm_button.config(text="ARM AUTO", bg="#4a4a4a")

        # Обновление видео
        if hasattr(self, 'current_frame'):
            try:
                # Оригинальное видео
                img = Image.fromarray(self.current_frame)
                img = img.resize((640, 480), Image.Resampling.LANCZOS)
                photo = ImageTk.PhotoImage(img)
                self.video_label.config(image=photo)
                self.video_label.image = photo

                # Сегментация
                seg_img = Image.fromarray(self.current_seg)
                seg_img = seg_img.resize((640, 480), Image.Resampling.LANCZOS)
                seg_photo = ImageTk.PhotoImage(seg_img)
                self.seg_label.config(image=seg_photo)
                self.seg_label.image = seg_photo
            except Exception:
                pass

        # Обновление метрик
        metrics = f"""
FPS:           {self.fps:6.1f}
SAFE:          {self.safe_ratio * 100:6.1f}%
OBSTACLES:     {self.obst_ratio * 100:6.1f}%

ZONES (Obstacle %):
  Left:        {self.oL * 100:6.1f}%
  Center:      {self.oC * 100:6.1f}%
  Right:       {self.oR * 100:6.1f}%
        """

        self.metrics_text.config(state=tk.NORMAL)
        self.metrics_text.delete(1.0, tk.END)
        self.metrics_text.insert(1.0, metrics.strip())
        self.metrics_text.config(state=tk.DISABLED)

        # Следующий кадр
        self.root.after(50, self.update_ui)

    def toggle_auto(self):
        """Переключение автопилота"""
        self.auto_on = not self.auto_on
        if not self.auto_on:
            self.ble.send(CMD_STOP)
            self.ble.send(CMD_CENTER)

    def emergency_stop(self):
        """Экстренная остановка"""
        self.auto_on = False
        self.ble.send(CMD_STOP)
        self.ble.send(CMD_CENTER)
        self.last_manual_ts = time.time()

    def on_key_press(self, event):
        """Обработка нажатий клавиш"""
        key = event.char.lower()

        if key == 'm':
            self.toggle_auto()

        elif key == 'w':
            self.last_manual_ts = time.time()
            self.ble.send(CMD_FWD)

        elif key == 's':
            self.last_manual_ts = time.time()
            self.ble.send(CMD_REV)

        elif key == 'a':
            self.last_manual_ts = time.time()
            self.ble.send(CMD_LEFT)

        elif key == 'd':
            self.last_manual_ts = time.time()
            self.ble.send(CMD_RIGHT)

        elif key == 'e':
            self.last_manual_ts = time.time()
            self.ble.send(CMD_CENTER)

        elif key == ' ':
            self.last_manual_ts = time.time()
            self.ble.send(CMD_STOP)

        elif key in ('q', '\x1b'):  # Q или ESC
            self.on_closing()

    def on_closing(self):
        """Закрытие приложения"""
        self.running = False
        self.ble.send(CMD_BYE)
        time.sleep(0.5)
        self.ble.stop()
        self.root.quit()
        self.root.destroy()


# ═══════════════════════════════════════════════════════════════════════════
#   ГЛАВНАЯ ФУНКЦИЯ
# ═══════════════════════════════════════════════════════════════════════════

def main():
    root = tk.Tk()
    app = CaveAIApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
