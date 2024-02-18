import json
import os
from config import JSON_PATH_FILTER_VACANCY, JSON_PATH_ALL_VACANCY
from src.hh_api import HeadHunterAPI
from src.vacancy import Vacancy
from src.vacancy_saver import JSONSaver


def search_vacancies_in_json():
    """
    Функция взаимодействия с пользователем,
    фильтрация json файла с вакансиями по выбранным параметрам
    """
    while True:
        filter_user = input("\nПо каким критериям вы хотите получить вакансии:\n"
                            "1 - по совпадению слова в названии вакансии\n"
                            "2 - по совпадению города\n"
                            "3 - по названию компании\n"
                            "4 - по зарплате\n"
                            "0 - выход\n").strip()

        if not (filter_user in ["0", "1", "2", "3", "4"]):
            print("\nВы ввели неверное значение попробуйте снова\n")
            continue

        with open(JSON_PATH_ALL_VACANCY, encoding='utf-8') as file:
            json_data = json.load(file)

        list_vacancy = [Vacancy(**item) for item in json_data]
        sorted_vacancies = Vacancy.sort_vacancies(list_vacancy)

        if filter_user == "0":
            print("Всего доброго! Выход.")
            exit()
        if filter_user == "1":
            user_answer = input("Введите ключевое слово для поиска в названии вакансии: ").strip().lower()
            Vacancy.filter_name_vacancy(sorted_vacancies, user_answer)

        elif filter_user == "2":
            user_answer = input("Введите название города: ").strip().lower()
            Vacancy.filter_name_city(sorted_vacancies, user_answer)

        elif filter_user == "3":
            user_answer = input("Введите название компании: ").strip().lower()
            Vacancy.filter_name_company(sorted_vacancies, user_answer)

        elif filter_user == "4":
            user_from, user_to = list(map(int, input("Введите диапазон зарплаты"
                                                     "(пример 100000-150000): ").strip().split('-')))
            Vacancy.filter_user_salary(sorted_vacancies, user_from, user_to)
        else:
            print("Несуществующий параметр запроса")


def get_vacancy_in_platform():
    """Функция взаимодействие с пользователем, обращение к API по заданным параметрам"""
    search_query = input("\nВведите поисковый запрос: ").strip()
    with_experience = input('\nВведите опыт работы(число лет)\n'
                            '(Нажмите Enter если искать вакансии с любым опытом): ').strip()

    user_query = {'search_query': search_query,
                  'experience': with_experience}

    hh = HeadHunterAPI()
    list_vacancy = hh.get_vacancies(**user_query)
    total = len(list_vacancy)
    save = JSONSaver()

    for i, vacancy in enumerate(list_vacancy, 1):
        save.add_vacancy(vacancy)
        if i % 100 == 0:
            print(f"Сохранено вакансий {i} из {total}")

    vacancies_all_obj = []
    for vac in list_vacancy:
        vacancies_all_obj.append(Vacancy(**vac))

    filter_words = input("\nВведите ключевые слова(через пробел) для фильтрации вакансий\n"
                         "(Нажмите Enter чтобы искать без фильтра): ").lower().split()

    filtered_vacancies = Vacancy.filter_vacancies(vacancies_all_obj, filter_words)

    if not filtered_vacancies:
        print("\nНет вакансий, соответствующих заданным критериям.")
        exit()

    top_n = input("\nВведите количество вакансий которое вы хотите получить\n"
                  "(Нажмите Enter чтобы получить все): ").strip()

    sorted_vacancies = Vacancy.sort_vacancies(filtered_vacancies)
    top_vacancies = Vacancy.get_top_vacancies(sorted_vacancies, top_n)
    Vacancy.print_vacancies(top_vacancies)
    total = len(top_vacancies)

    print(f"Всего вакансий получено: {total}")

    save_list_vacancy = input("\nХотите ли сохранить вакансии:\n"
                              "1 - да\n"
                              "2 - нет\n").strip()
    if save_list_vacancy == "1":
        save = JSONSaver()
        save.file_path = JSON_PATH_FILTER_VACANCY
        for i, vacancy in enumerate(top_vacancies, 1):
            save.add_vacancy(vacancy.__dict__)
            print(f"Сохранение вакансий {i} из {total}")
        print("Данные сохранены. Выход.")
    else:
        print("Выход")
        exit()


def user_interaction():
    """Стартовое взаимодействие"""
    while True:
        user_answer = input("Здравствуйте! Введите число и нажмите Enter:\n"
                            "1 - для получения вакансий от API\n"
                            "2 - для работы с существующим json файлом вакансий\n").strip()
        if user_answer in ["1", "2"]:
            break
    if user_answer == "1":
        get_vacancy_in_platform()
    elif user_answer == "2":
        if not os.path.exists(JSON_PATH_ALL_VACANCY):
            print("Файла json не существует сначала получите вакансии от API\n")
            user_interaction()
        else:
            search_vacancies_in_json()
