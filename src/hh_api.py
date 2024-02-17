import random
import time
from abc import ABC, abstractmethod
import requests


class JobVacancyAPI(ABC):
    """Абстрактный класс пря поиска вакансий через API"""

    @abstractmethod
    def get_vacancies(self, **kwargs: dict) -> None:
        """
        Абстрактный метод получения вакансий
        :param kwargs: полученные от пользователя параметры в виде словаря для запроса
        :return: None
        """
        pass

    @staticmethod
    def correct_query(user_params: dict) -> dict:
        """
        Статический метод корректировки запроса пользователя
        :param user_params: словарь пользователя с параметрами запроса
        :return: корректный словарь для запроса к API
        """
        pass

    @staticmethod
    def get_params_vacancy(job_item: dict) -> dict:
        """
        Метод возвращающий словарь с параметрами вакансии
        :param job_item: словарь полученный от API с параметрами вакансии
        :return: возвращаем словарь с нужными нам параметрами
        """
        pass


class HeadHunterAPI(JobVacancyAPI):
    """Класс для рабы с API HeadHunter"""

    url = 'https://api.hh.ru/vacancies/'

    def __init__(self) -> None:
        """Инициализация параметров для запроса к API"""
        self.vacancies = []
        self.params = {
            'text': None,
            'only_with_salary': True,
            'area': 113,
            'per_page': 100,
            'page': 0,
        }

        self.headers = {
            "User-Agent": "Mozilla/5.0 (Linux; arm_64; Android 11; SM-G780F) "
                          "AppleWebKit/537.36 (KHTML, like Gecko) "
                          "Chrome/86.0.4240.198 "
                          "YaBrowser/20.11.2.69.00 SA/3 "
                          "Mobile Safari/537.36"
        }

    def get_vacancies(self, **kwargs: dict) -> list:
        """
        Метод для получения вакансий с API HeadHunter
        :param kwargs: словарь полученный от пользователя с параметрами для запроса
        :return: None
        """
        data = self.correct_query(kwargs)
        self.params['text'] = data['search_query']
        if data.get('experience'):
            self.params['experience'] = data['experience']
        while True:
            try:
                response = requests.get(self.url, params=self.params, headers=self.headers)
                if response.status_code == 200:
                    get_data = response.json()
                    items = get_data['items']
                    found = get_data['found']
                    page = get_data['page']
                    pages = get_data['pages']
                    for item in items:
                        job_vacancy = self.get_params_vacancy(item)
                        self.vacancies.append(job_vacancy)
                    print(f'Загружены вакансии. Страница {page + 1} из {pages}')
                    if page == pages - 1:
                        break
                    self.params['page'] = self.params.get('page') + 1
                    random_time = random.uniform(0.2, 0.4)
                    time.sleep(random_time)
            except requests.HTTPError:
                continue
        print(f'Всего вакансий на hh {found} из них получено: {len(self.vacancies)}')
        return self.vacancies

    @staticmethod
    def correct_query(user_params: dict) -> dict:
        """
        Метод обработки полученных от пользователя данных для обращения к API
        :param user_params: словарь с параметрами полученный от пользователя
        :return: откорректированный словарь параметров для запроса к API
        """
        experience_dict = {
            range(0, 1): {'id': 'noExperience', 'name': "без опыта"},
            range(1, 3): {'id': 'between1And3', 'name': "от 1 до 3 лет"},
            range(3, 6): {'id': 'between3And6', 'name': "от 3 до 6 лет"},
            range(6, 30): {'id': 'moreThan6', 'name': "более 6 лет"}
        }

        experience = user_params['experience']
        if experience.isdigit():
            for key in experience_dict.keys():
                if int(experience) in key:
                    user_params['experience'] = experience_dict[key]['id']
        else:
            del user_params['experience']

        return user_params

    @staticmethod
    def get_params_vacancy(item_vacancy: dict) -> dict:
        """
        Метод получающий параметры вакансии и возвращающий словарь
        :param item_vacancy: json словарь полученный от API с вакансией
        :return: возвращает словарь с вакансией
        """
        id_vacancy = int(item_vacancy['id'])
        name = item_vacancy['name']
        if item_vacancy['salary']:
            salary = {'from': item_vacancy['salary']['from'],
                      'to': item_vacancy['salary']['to'],
                      'currency': item_vacancy['salary']['currency']}
        else:
            salary = None
        experience = item_vacancy['experience']['name']
        requirement = item_vacancy.get('snippet').get('requirement')
        responsibility = item_vacancy.get('snippet').get('responsibility')
        description = f"{requirement if requirement else ''} {responsibility if responsibility else ''}"
        area = item_vacancy.get('area').get('name')
        employer = item_vacancy.get('employer').get('name')
        url_vacancy = item_vacancy.get('alternate_url')

        data = {'id': id_vacancy,
                'name': name,
                'salary': salary,
                'experience': experience,
                'description': description,
                'area': area,
                'employer': employer,
                'url_vacancy': url_vacancy}

        return data