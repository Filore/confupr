## Задача 1

Написать программу на Питоне, которая транслирует граф зависимостей civgraph в makefile в духе примера выше. Для мало знакомых с Питоном используется упрощенный вариант civgraph: civgraph.json.

```
import json

def parse_civgraph(civgraph_file):
    with open(civgraph_file, 'r') as file:
        data = json.load(file)
    return data

def generate_makefile(data, output_file):
    with open(output_file, 'w') as file:
        for target, dependencies in data.items():
            dep_str = " ".join(dependencies) if dependencies else ""
            file.write(f"{target}: {dep_str}\n")
            file.write(f"\t@echo {target}\n\n")

def main():
    output_file = "Makefile"
    civgraph_file = "civgraph.json"

    data = parse_civgraph(civgraph_file)

    generate_makefile(data, output_file)
    print(f"Makefile был сгенерирован в {output_file}")

if __name__ == "__main__":
    main()
```

Команды для запуска:

python main.py 

make mathematics


<img width="633" alt="image" src="https://github.com/user-attachments/assets/665aeb29-ea43-4b6d-8a85-77fce3b51f1a" />


## Задача 2

```
import json
import os

TASKS_FILE = "tasks.txt"


def load_tasks():
    if os.path.exists(TASKS_FILE):
        with open(TASKS_FILE, 'r') as f:
            return set(f.read().splitlines())
    return set()


def save_tasks(tasks):
    with open(TASKS_FILE, 'w') as f:
        f.write('\n'.join(tasks))


def load_dependency_graph(filename):
    try:
        with open(filename, 'r') as f:
            return json.load(f)
    except Exception as e:
        print(f"Ошибка при загрузке файла {filename}: {e}")
        return {}


def generate_makefile(dependency_graph, target_task):
    visited_tasks = set()
    tasks_to_process = []
    completed_tasks = load_tasks()

    def process_task(task):
        if task in visited_tasks or task in completed_tasks:
            return
        visited_tasks.add(task)
        for dependency in dependency_graph.get(task, []):
            process_task(dependency)
        tasks_to_process.append(task)

    process_task(target_task)

    if not tasks_to_process:
        print("Все задачи уже были выполнены.")
    else:
        for task in tasks_to_process:
            if task not in completed_tasks:
                print(f"{task}")
                completed_tasks.add(task)

        save_tasks(completed_tasks)


if __name__ == '__main__':
    # Загружаем граф зависимостей из файла
    dependency_graph = load_dependency_graph('civgraph.json')

    if not dependency_graph:
        print("Не удалось загрузить граф зависимостей. Программа завершена.")
    else:
        target_task = input('>make ')
        generate_makefile(dependency_graph, target_task)

```

Команды для запуска:

python main.py 

>make mathematics

<img width="547" alt="image" src="https://github.com/user-attachments/assets/bc73dc1a-fd5b-4d90-ac32-9ce014fededa" />


## Задача 3

```
import json
import os

TASKS_FILE = "completed_tasks.txt"


def load_tasks():
    if os.path.exists(TASKS_FILE):
        with open(TASKS_FILE, 'r') as f:
            return set(f.read().splitlines())
    return set()


def save_tasks(tasks):
    with open(TASKS_FILE, 'w') as f:
        f.write('\n'.join(tasks))


def load_dependency_graph(filename):
    try:
        with open(filename, 'r') as f:
            return json.load(f)
    except Exception as e:
        print(f"Ошибка при загрузке {filename}: {e}")
        return {}


def generate_makefile(dependency_graph, target_task):
    visited_tasks = set()
    tasks_to_process = []
    completed_tasks = load_tasks()

    def process_task(task):
        if task in visited_tasks or task in completed_tasks:
            return
        visited_tasks.add(task)
        for dependency in dependency_graph.get(task, []):
            process_task(dependency)
        tasks_to_process.append(task)

    process_task(target_task)

    if not tasks_to_process:
        print("Все задачи уже были выполнены.")
    else:
        for task in tasks_to_process:
            if task not in completed_tasks:
                print(f"{task}")
                completed_tasks.add(task)

        save_tasks(completed_tasks)


def clean():
    if os.path.exists(TASKS_FILE):
        os.remove(TASKS_FILE)
        print(f"Файл с завершенными задачами {TASKS_FILE} удален.")
    else:
        print("Файл с завершенными задачами не найден. Нечего очищать.")


if __name__ == '__main__':
    dependency_graph = load_dependency_graph('civgraph.json')

    if not dependency_graph:
        print("Не удалось загрузить граф зависимостей. Программа завершена.")
    else:
        action = input('Выберите действие make/clean: ')

        if action == 'make':
            target_task = input('>make ')
            generate_makefile(dependency_graph, target_task)
        elif action == 'clean':
            clean()
        else:
            print("Неизвестное действие. Пожалуйста, введите 'build' или 'clean'.")
```

Команды для запуска:

python main.py

make clean

make mathematics

<img width="547" alt="image" src="https://github.com/user-attachments/assets/eac57322-b78a-43b3-a1f2-2fb82e5b089e" />



## Задача 4

```
# Компилятор и флаги
CC = gcc
CFLAGS = -Wall -g

# Исходные файлы
SRCS = prog.c data.c

# Выходной исполняемый файл
TARGET = prog

# Имя архива
ARCHIVE = distr.zip

# Файл со списком файлов
LISTFILE = files.lst

# Цель по умолчанию
all: $(ARCHIVE)

# Сборка исполняемого файла
$(TARGET): $(SRCS)
	$(CC) $(CFLAGS) $(SRCS) -o $(TARGET)

# Генерация files.lst
$(LISTFILE): $(TARGET)
	ls > $(LISTFILE)

# Создание архива
$(ARCHIVE): $(TARGET) $(LISTFILE)
	7z a $(ARCHIVE) $(TARGET) $(LISTFILE)

# Очистка сгенерированных файлов
clean:
	rm -f $(TARGET) $(LISTFILE) $(ARCHIVE)

# Цель для создания архива отдельно
archive: $(ARCHIVE)

# Объявление .PHONY целей
.PHONY: all clean archive

```

