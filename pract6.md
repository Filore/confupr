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

def parse_civgraph(civgraph_file):
    with open(civgraph_file, 'r') as file:
        data = json.load(file)
    return data

def generate_makefile(data, output_file):
    with open(output_file, 'w') as file:
        all_targets = " ".join([f"{target}.stamp" for target in data.keys()])
        file.write(f"all: {all_targets}\n\n")
        
        for target, dependencies in data.items():
            dep_str = " ".join([f"{dep}.stamp" for dep in dependencies]) if dependencies else ""
            file.write(f"{target}.stamp: {dep_str}\n")
            file.write(f"\t@echo Выполняю задачу: {target}\n")
            file.write(f"\t@touch {target}.stamp\n\n")
        
        
        file.write(".PHONY: all\n")

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

<img width="647" alt="image" src="https://github.com/user-attachments/assets/47d46922-0af3-4fe7-b464-1aa3231f5b4e" />

## Задача 3

```
import json


def parse_civgraph(civgraph_file):
    with open(civgraph_file, 'r') as file:
        data = json.load(file)
    return data


def generate_makefile(data, output_file):
    with open(output_file, 'w') as file:
        # Добавляем цель по умолчанию
        all_targets = " ".join(data.keys())
        file.write(f"all: {all_targets}\n\n")

        for target, dependencies in data.items():
            dep_str = " ".join(dependencies) if dependencies else ""
            file.write(f"{target}: {dep_str}\n")
            file.write(f"\t@echo {target}\n")
            file.write(f"\t@touch {target}\n\n")

        # Опционально можно добавить очистку
        file.write("clean:\n")
        file.write(f"\t@rm -f {' '.join(data.keys())}\n")


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

make clean

make mathematics

![image](https://github.com/user-attachments/assets/24918853-7c9f-493b-8870-039cba3a4a55)


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

