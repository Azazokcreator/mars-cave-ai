# Архитектура системы Mars Cave AI

---

## Общая концепция



Mars Cave AI — это программно-аппаратная система автономной навигации робота в сложной подземной среде на основе компьютерного зрения и искусственного интеллекта.



Система предназначена для:



* исследования пещер
* обнаружения безопасных маршрутов
* управления мобильным роботом в реальном времени



---

## Общий pipeline системы



---



1\. Захват изображения



Источник:

ESP32-CAM

Функция:



* передача видеопотока MJPEG по Wi-Fi
* поток поступает на ноутбук в реальном времени



---



2\. Предобработка



Изображение:



* масштабируется до 320×320
* нормализуется
* преобразуется в формат tensor



---



3\. Нейросетевая обработка



Используется модель:

UNet + ResNet18 encoder



Задача:

Сегментация сцены на два класса:



SAFE — безопасная поверхность

OBSTACLE — препятствия



---



4\. Анализ безопасного маршрута



Алгоритм:



выделяется нижняя часть кадра (ROI)



ROI делится на 3 зоны:



* Left
* Center
* Right



вычисляется доля препятствий в каждой зоне



---



5\. Модуль принятия решений



На основе анализа зон:



* определяется безопасное направление движения
* формируются команды управления роботом



6\. Управление роботом



Команды передаются через:



BLE (Bluetooth Low Energy)



В SPIKE Prime Hub.



Поток данных



ESP32-CAM → WiFi → Laptop → Neural Network → Decision Logic → BLE → Robot Motors



---


## Преимущества архитектуры



* модульность
* реальное время работы
* возможность автономного управления
* масштабируемость для космических миссий



---





# System Architecture — Mars Cave AI



---



## Overview



Mars Cave AI is an AI-powered robotic navigation system designed for operation in underground and planetary cave environments.



Pipeline



* Video capture via ESP32-CAM
* Image preprocessing
* AI segmentation using UNet
* Safe path analysis
* Decision-making module
* Robot control via BLE
* Data Flow



ESP32-CAM → WiFi → Laptop → Neural Network → Decision Logic → BLE → Robot


