import csv
import os
from abc import ABC, abstractmethod
from typing import Any
from tabulate import tabulate


class Reader(ABC):
    @abstractmethod
    def read(self, filename: str) -> list[dict[str, Any]]:
        """
        Считывает данные из файла и возвращает их в виде списка словарей.
        :argument filename (str): Имя файла
        :return List[Dict[str, Any]]: Список словарей, где ключи - названия колонок,
        значения - данные из соответствующих ячеек
        :raises FileNotFoundError: Если файл не существует, Exception: При ошибках чтения файла
        """
        pass


class Reporter(ABC):
    @abstractmethod
    def report(self, data: list) -> list:
        """
        Функция получает список словарей и возвращает отсортированный словарь
        :argument data (list[dict[str, Any]]): Данные о студентах
        :return dict[str, float]: отсортированный словарь со средними оценками студентов
        """
        pass

    @abstractmethod
    def tabulate_view(self, report_data: dict[str, float]) -> None:
        """Функция выводит отчет в виде таблицы в консоль"""
        pass


class CSVReader(Reader):
    def read(self, files: list[str]) -> list[dict[str, Any]]:
        data = []

        try:
            for filename in files:
                with open(
                    os.path.join("data", filename), "r", encoding="utf-8", newline=""
                ) as csvfile:
                    # Создаем объект для чтения CSV
                    reader = csv.DictReader(csvfile)

                    # Читаем каждую строку и добавляем в список
                    for row in reader:
                        data.append(dict(row))

        except FileNotFoundError:
            raise FileNotFoundError(f"Файл '{filename}' не найден")
        except Exception as e:
            raise Exception(f"Ошибка при чтении CSV файла: {e}")

        return data


class PerformanceReporter(Reporter):
    def report(self, data: list[dict[str, Any]]) -> dict[str, float]:
        result = {}

        for student in data:
            try:
                grade = int(student.get("grade", 0))
            except (ValueError, TypeError):
                grade = 0

            if result.get(student["student_name"]):
                result[student["student_name"]].append(grade)
            else:
                result[student["student_name"]] = [grade]

        for student in result:
            result[student] = round(sum(result[student]) / len(result[student]), 3)

        return dict(sorted(result.items(), key=lambda grade: grade[1], reverse=True))

    def tabulate_view(self, report_data: dict[str, float]) -> str | None:
        if not report_data:
            print("Нет данных для отображения")
            return None

        table_data = [[key, float(value)] for key, value in report_data.items()]

        return tabulate(
            table_data,
            headers=["Key", "Value"],
            showindex=range(1, len(table_data) + 1),
            floatfmt=".1f",
            tablefmt="grid"
        )
