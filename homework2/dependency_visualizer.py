import os
import sys
import subprocess
import tempfile
import tarfile
import requests
from typing import Dict, List, Set
import xml.etree.ElementTree as ET
import shutil


def download_apkindex(repo_url: str, temp_dir: str) -> str:
    """
    Загружает APKINDEX.tar.gz из указанного репозитория и извлекает файл APKINDEX.
    Возвращает путь к извлеченному APKINDEX файлу с уникальным именем.
    """
    apkindex_url = f"{repo_url}/x86_64/APKINDEX.tar.gz"
    response = requests.get(apkindex_url, stream=True)
    if response.status_code != 200:
        raise ConnectionError(f"Не удалось скачать APKINDEX из {apkindex_url}")

    repo_name = repo_url.rstrip('/').split('/')[-1]
    tar_path = os.path.join(temp_dir, f"APKINDEX-{repo_name}.tar.gz")
    with open(tar_path, 'wb') as f:
        for chunk in response.iter_content(chunk_size=8192):
            f.write(chunk)
    print(f"Скачивание завершено: {tar_path}")

    # Извлекаем APKINDEX из архива с использованием фильтра для безопасности
    try:
        with tarfile.open(tar_path, 'r:gz') as tar:
            def is_safe(tarinfo):
                # Разрешаем только файлы без вложенных директорий
                if '/' in tarinfo.name or tarinfo.name.startswith('..'):
                    return None
                return tarinfo

            tar.extractall(path=temp_dir, members=(m for m in tar if is_safe(m)))
        os.remove(tar_path)
    except tarfile.TarError as e:
        raise RuntimeError(f"Ошибка при распаковке {tar_path}: {e}")

    # Найти извлеченный APKINDEX и переименовать его
    extracted_apkindex = os.path.join(temp_dir, 'APKINDEX')
    renamed_apkindex = os.path.join(temp_dir, f'APKINDEX-{repo_name}')
    if os.path.exists(extracted_apkindex):
        os.rename(extracted_apkindex, renamed_apkindex)
        return renamed_apkindex
    else:
        raise FileNotFoundError(f"Файл APKINDEX не найден в {tar_path}")


def parse_apkindex(apkindex_path: str) -> Dict[str, List[str]]:

    #Парсит файл APKINDEX и возвращает словарь пакетов с их зависимостями.

    if not os.path.exists(apkindex_path):
        raise FileNotFoundError(f"Файл APKINDEX не найден: {apkindex_path}")

    packages_db = {}
    current_package = None
    dependencies = []

    try:
        with open(apkindex_path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue  # Пропускаем пустые строки
                if line.startswith('P:'):
                    if current_package:
                        packages_db[current_package] = dependencies
                    current_package = line[2:].strip()
                    dependencies = []
                elif line.startswith('D:'):
                    dep_line = line[2:].strip()
                    if dep_line:
                        deps = dep_line.split()
                        dependencies.extend(deps)
            if current_package:
                packages_db[current_package] = dependencies
    except Exception as e:
        raise IOError(f"Ошибка чтения файла APKINDEX: {e}")

    return packages_db


def build_dependency_graph(package_name: str, packages_db: Dict[str, List[str]]) -> Dict[str, List[str]]:

    #Строит граф зависимостей для заданного пакета, включая транзитивные зависимости.

    if package_name not in packages_db:
        raise ValueError(f"Пакет '{package_name}' не найден в APKINDEX.")

    dependency_graph = {}
    visited: Set[str] = set()

    def visit(pkg: str):
        if pkg not in visited:
            visited.add(pkg)
            deps = packages_db.get(pkg, [])
            dependency_graph[pkg] = deps
            for dep in deps:
                visit(dep)

    visit(package_name)
    return dependency_graph


def generate_graphviz(dependency_graph: Dict[str, List[str]]) -> str:

    #Генерирует код DOT для Graphviz на основе графа зависимостей.

    lines = ['digraph G {']
    lines.append('    node [shape=box];')  # Опционально: установка формы узлов
    for pkg, deps in dependency_graph.items():
        for dep in deps:
            lines.append(f'    "{pkg}" -> "{dep}";')
    lines.append('}')
    return '\n'.join(lines)


def generate_image(dot_code: str, graphviz_path: str, output_image_path: str) -> None:

    #Использует Graphviz для генерации PNG-изображения графа зависимостей.

    with tempfile.NamedTemporaryFile('w', delete=False, suffix='.dot') as tmp:
        tmp.write(dot_code)
        tmp_path = tmp.name
        print(f"Временный файл DOT создан: {tmp_path}")

    try:
        # Команда для запуска Graphviz (dot)
        command = [graphviz_path, '-Tpng', tmp_path, '-o', output_image_path]
        result = subprocess.run(command, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        if not os.path.exists(output_image_path):
            raise FileNotFoundError("Graphviz не сгенерировал изображение.")
    except subprocess.CalledProcessError as e:
        stderr = e.stderr.decode().strip()
        raise RuntimeError(f"Ошибка при выполнении Graphviz: {stderr}")
    finally:
        if os.path.exists(tmp_path):
            os.remove(tmp_path)


def display_image(image_path: str) -> None:
    """
    Открывает сгенерированное изображение с помощью стандартного просмотрщика изображений ОС.
    """
    if sys.platform.startswith('darwin'):
        subprocess.run(['open', image_path])
    elif os.name == 'nt':
        os.startfile(image_path)
    elif os.name == 'posix':
        subprocess.run(['xdg-open', image_path])
    else:
        print(f"Невозможно автоматически открыть изображение. Оно сохранено по пути: {image_path}")


def main():
    if len(sys.argv) != 2:
        print("Usage: python dependency_visualizer.py <package_name>")
        sys.exit(1)

    package_name = sys.argv[1]
    graphviz_path = r"/opt/homebrew/bin/dot"

    if not os.path.isfile(graphviz_path):
        print(f"Graphviz не найден по пути: {graphviz_path}")
        sys.exit(1)

    # URLs репозиториев Alpine Linux
    repositories = [
        "https://dl-cdn.alpinelinux.org/alpine/latest-stable/main",
        "https://dl-cdn.alpinelinux.org/alpine/latest-stable/community"
    ]

    with tempfile.TemporaryDirectory() as temp_dir:
        print("Начало загрузки APKINDEX файлов...")
        apkindex_files = []
        for repo in repositories:
            try:
                apkindex_path = download_apkindex(repo, temp_dir)
                apkindex_files.append(apkindex_path)
                print(f"Файл APKINDEX извлечён и доступен: {apkindex_path}")
            except Exception as e:
                print(f"Ошибка при загрузке APKINDEX из {repo}: {e}")
                sys.exit(1)

        print("Парсинг APKINDEX файлов...")
        packages_db = {}
        for apkindex in apkindex_files:
            try:
                parsed = parse_apkindex(apkindex)
                packages_db.update(parsed)
                print(f"Парсинг файла: {apkindex} завершён. Найдено пакетов: {len(parsed)}")
            except Exception as e:
                print(f"Ошибка при парсинге {apkindex}: {e}")
                sys.exit(1)

        print(f"Всего найдено пакетов: {len(packages_db)}")

        # Проверка наличия искомого пакета
        if package_name not in packages_db:
            print(f"Пакет '{package_name}' не найден в APKINDEX.")
            print("Возможные причины:")
            print("- Неверное имя пакета (проверьте регистр и точность имени).")
            print("- Пакет отсутствует в репозиториях 'main' и 'community'.")
            sys.exit(1)

        try:
            dependency_graph = build_dependency_graph(package_name, packages_db)
            print(f"Граф зависимостей для '{package_name}' успешно построен.")
        except Exception as e:
            print(f"Ошибка: {e}")
            sys.exit(1)

        dot_code = generate_graphviz(dependency_graph)
        print("Сгенерирован код DOT:")
        print(dot_code)

        output_image_path = os.path.join(os.getcwd(), f"{package_name}_dependencies.png")
        try:
            generate_image(dot_code, graphviz_path, output_image_path)
            print(f"Граф зависимостей успешно сохранен в {output_image_path}")
            display_image(output_image_path)
        except Exception as e:
            print(f"Ошибка при генерации изображения: {e}")
            sys.exit(1)


if __name__ == "__main__":
    main()
