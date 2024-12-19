## Задание 1

```
\textbf{ФИО студента: Топорков МА}
\int_x^\infty \frac{dt}{t(t^2 - 1) \log t} = \int_x^\infty \frac{1}{t \log t}\left( \sum_m t^{-2m} \right) dt = \sum_m \int_x^\infty \frac{t^{-2m}}{t \log t} dt \overset{u = t^{-2m}}{=} -\sum_m \mathrm{li}(x^{-2m})
```

<img width="1195" alt="image" src="https://github.com/user-attachments/assets/a2f6b9f9-e03d-4a1a-b88e-0b11a05987a1" />

## Задание 2

```
@startuml
skinparam lifelineStrategy nosolid
actor "Студент Топорков МА" as S
database Piazza as P
actor Преподаватель as T

T -> P : Публикация задачи
activate P
P --> T : Задача опубликована
deactivate P
...
S -> P : Поиск задач
activate P
P --> S : Получение задачи
deactivate P
...
S -> P : Публикация решения
activate P
P --> S : Решение опубликовано
deactivate P
...
T -> P : Поиск решений
activate P
P --> T : Решение найдено
T -> P : Публикация оценки
P --> T : Оценка опубликована
deactivate P
...
S -> P : Проверка оценки
activate P
P --> S : Оценка получена
deactivate P
@enduml
```

<img width="473" alt="image" src="https://github.com/user-attachments/assets/f62fa290-11c2-4626-a3b2-c6eebb9614c7" />



