from pathlib import Path
import shutil

FILE_TYPES = {
    "Images": [".jpg", ".jpeg", ".png", ".gif", ".bmp"],
    "Documents": [".pdf", ".docx", ".txt", ".xlsx", ".pptx"],
    "Videos": [".mp4", ".mov", ".avi", ".mkv", ".webm"],
    "Music": [".mp3", ".wav", ".flac"],
    "Archives": [".zip", ".rar", ".7z", ".tar", ".gz"],
    "Executable": [".exe", ".jar"],
    "Others": []
}


def organize_folder(folder_path: str) -> None:
    """
    Рекурсивно обходит все файлы внутри folder_path (и его подпапок),
    перемещает их в соответствующие категории, и удаляет пустые подпапки.
    В итоге в корне будут только папки категорий (Images, Documents и т.д.)
    без дополнительных уровней вложенности.
    """

    folder = Path(folder_path)

    # Проверяем, что folder_path — существующая папка
    if not folder.exists():
        print(f"Папка {folder} не существует.")
        return
    if not folder.is_dir():
        print(f"Путь {folder} не является папкой.")
        return

    # Сразу «создадим» все папки-категории (если каких-то нет, они появятся)
    category_folders = []
    for cat_name in FILE_TYPES:
        cat_path = folder / cat_name
        cat_path.mkdir(exist_ok=True)  # Не будет ошибки, если папка уже существует
        category_folders.append(cat_path)

    # Рекурсивно обходим все содержимое папки
    for item in folder.rglob('*'):
        # Если это директория — пока пропускаем (файлы обрабатываем)
        if item.is_dir():
            continue

        # Определяем расширение и категорию
        ext = item.suffix.lower()
        category = "Others"
        for cat_name, extensions in FILE_TYPES.items():
            if ext in extensions:
                category = cat_name
                break

        # Папка, куда мы хотим переместить файл
        category_folder = folder / category

        # Если файл уже лежит в нужной категории — пропускаем
        if item.parent == category_folder:
            continue

        # Формируем итоговый путь
        new_path = category_folder / item.name

        # Если файл с таким именем уже существует, переименуем (new_file_copy, new_file_copy2, ...)
        counter = 1
        while new_path.exists():
            new_filename = f"{item.stem}_copy{counter}{item.suffix}"
            new_path = category_folder / new_filename
            counter += 1

        # Перемещаем файл
        try:
            shutil.move(str(item), str(new_path))
            print(f"Файл {item.name} -> \"{category}\"")
        except Exception as e:
            print(f"Ошибка при перемещении {item} -> {new_path}: {e}")

    # Удаляем все пустые директории (кроме папок категорий).
    # Сортируем в обратном порядке, чтобы сначала обрабатывать самые глубокие папки
    for dirpath in sorted(folder.rglob('*'), reverse=True):
        if dirpath.is_dir() and dirpath not in category_folders:
            # Если в папке ничего нет, удаляем
            if not any(dirpath.iterdir()):
                try:
                    dirpath.rmdir()
                except OSError as e:
                    print(f"Не удалось удалить папку {dirpath}: {e}")

    print("Сортировка завершена!")


if __name__ == "__main__":
    folder_to_organize = input("Введите путь к папке для сортировки: ")
    organize_folder(folder_to_organize)
