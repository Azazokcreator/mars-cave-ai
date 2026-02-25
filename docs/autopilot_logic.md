# Логика автопилота



--- 



## Анализ ROI



Используется нижняя часть кадра.



Причина:



именно там находится поверхность движения



Деление на зоны



Кадр делится на 3 области:



* Left
* Center
* Right



Оценка безопасности



В каждой зоне рассчитывается:



процент пикселей препятствий.



---



## Алгоритм принятия решений



Если центр свободен:



→ движение прямо



Если центр заблокирован:



→ поворот в сторону меньшего препятствия



Если все зоны опасны:



→ остановка



---





# Autopilot Logic



The system analyzes the lower ROI of the frame.



The ROI is split into three zones:



Left / Center / Right.



Decision rules:



Clear center → move forward



Blocked center → turn to safer side



All blocked → stop


