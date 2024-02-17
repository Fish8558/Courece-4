import json
import os
from abc import ABC, abstractmethod

from config import JSON_PATH_ALL_VACANCY, PATH_FOLDER


class BaseSaver(ABC):
    """Абстрактный класс сохранения"""

    @abstractmethod
    def add_vacancy(self, vacancy) -> None:
        """
        Абстрактный метод добавления вакансии
        :param vacancy: вакансия
        :return: None
        """
        pass

    def del_vacancy(self, vacancy) -> None:
        """
        Абстрактный метод удаления вакансии
        :param vacancy: вакансия
        :return: None
        """
        pass


class JSONSaver(BaseSaver):
    """Класс сохранения в json файл"""

    def __init__(self):
        """Инициализация параметров"""
        self.file_path = JSON_PATH_ALL_VACANCY

    def add_vacancy(self, vacancy: dict) -> None:
        """
        Метод добавления вакансии в json файл
        :param vacancy: вакансия для добавления
        :return: None
        """
        if not os.path.exists(PATH_FOLDER):
            os.mkdir(PATH_FOLDER)
        with open(self.file_path, "a", encoding='UTF-8') as f:
            if os.stat(self.file_path).st_size == 0:
                json.dump([vacancy], f, indent=2, ensure_ascii=False)
            else:
                with open(self.file_path, encoding='UTF-8') as file:
                    data_vacancy = json.load(file)
                data_vacancy.append(vacancy)
                with open(self.file_path, "w", encoding='UTF-8') as outfile:
                    json.dump(data_vacancy, outfile, indent=2, ensure_ascii=False)

    def del_vacancy(self, vacancy) -> None:
        """
        Метод удаления вакансии из json файла
        :param vacancy: вакансия для удаления
        :return: None
        """
        if os.path.exists(self.file_path):
            with open(self.file_path, encoding='UTF-8') as file:
                data_vacancy = json.load(file)
            if vacancy in data_vacancy:
                for item in data_vacancy:
                    if item == vacancy:
                        index = data_vacancy.index(item)
                        del data_vacancy[index]
                        print("Вакансия найдена. Удаляем...")
                        break
                with open(self.file_path, "w", encoding='UTF-8') as outfile:
                    json.dump(data_vacancy, outfile, indent=2, ensure_ascii=False)

            else:
                print("Такой вакансии нет")
        else:
            print("Несуществующий путь.")