import datetime
import os
import tarfile
import chardet


def ls(current_dir, tar_path):
    with tarfile.open(tar_path, "r") as tar:
        contents = []
        if current_dir:
            current_dir = current_dir.rstrip("/") + "/"

        for member in tar.getmembers():
            if member.name.startswith(current_dir):
                stripped_name = member.name[len(current_dir):]
                if "/" not in stripped_name.rstrip("/"):
                    is_dir = member.isdir()
                    contents.append((stripped_name.rstrip("/"), is_dir))

        if not contents:
            return "Directory path is empty."

        contents = sorted(contents, key=lambda x: x[0].lower())
        return "\n".join(colorize(name, is_dir) for name, is_dir in contents)


def cd(current_dir, target_dir, tar_path):
    try:
        with tarfile.open(tar_path, "r") as tar:
            if target_dir == "..":
                # Если текущая директория пуста, остаемся в корне
                if not current_dir:
                    return ""
                # Переход на уровень вверх: убираем последний компонент пути
                return "/".join(current_dir.rstrip("/").split("/")[:-1])

            elif target_dir == "/":
                # Возврат в корневую директорию
                return ""

            else:
                # Переход в указанную директорию
                if current_dir:
                    target_path = f"{current_dir.rstrip('/')}/{target_dir}".lstrip("/")
                else:
                    target_path = target_dir

                # Проверяем, существует ли указанная директория
                for member in tar.getmembers():
                    if member.isdir() and member.name.rstrip("/") == target_path.rstrip("/"):
                        return target_path
                return current_dir  # Если директория не найдена, остаемся в текущей
    except Exception as e:
        return current_dir




def uniq(file_path, tar_path, current_dir=""):
    with tarfile.open(tar_path, "r") as tar:
        if current_dir:
            file_path = os.path.join(current_dir, file_path).lstrip(os.sep)

        try:
            file = tar.extractfile(file_path)
            file_content = file.read()
            encoding = chardet.detect(file_content).get('encoding', 'utf-8')
            lines = file_content.decode(encoding).splitlines()
            unique_lines = sorted(set(line.strip() for line in lines))
            return "\n".join(unique_lines)

        except KeyError:
            return f"Error: File '{file_path}' not found inside the archive."



def date():
    return str(datetime.datetime.now())

def exit_command(is_gui_running=True, root=None):
    """
    :param is_gui_running: Флаг, указывает, используется ли GUI.
    :param root: Объект корневого окна tkinter, если приложение работает с GUI.
    :return: Сообщение о завершении работы.
    """
    if is_gui_running and root:
        root.destroy()
    print("Exiting application...")
    os._exit(0)


def normalize_path(path):
    return path.lstrip("./")


def colorize(name, is_dir):
    return f"[DIR] {name}" if is_dir else f"[FILE] {name}"
