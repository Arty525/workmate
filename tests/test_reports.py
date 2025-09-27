import pytest
import csv
import os
from src.reports import CSVReader, PerformanceReporter


@pytest.fixture
def sample_csv_data():
    """Фикстура с небольшим набором тестовых данных"""
    return [
        {"student_name": "Иванов Иван", "subject": "Математика", "grade": "5"},
        {"student_name": "Петров Петр", "subject": "Физика", "grade": "4"},
        {"student_name": "Иванов Иван", "subject": "Физика", "grade": "3"},
        {"student_name": "Сидорова Мария", "subject": "Математика", "grade": "5"},
        {"student_name": "Петров Петр", "subject": "Математика", "grade": "4"},
    ]


@pytest.fixture
def sample_student_data():
    """Фикстура с данными для тестирования PerformanceReporter"""
    return [
        {"student_name": "Иванов Иван", "grade": "5"},
        {"student_name": "Петров Петр", "grade": "4"},
        {"student_name": "Иванов Иван", "grade": "3"},
        {"student_name": "Сидорова Мария", "grade": "5"},
        {"student_name": "Петров Петр", "grade": "4"},
        {"student_name": "Новый Студент", "grade": "5"},
    ]


@pytest.fixture
def create_test_csv(tmp_path):
    """Фикстура для создания временного CSV файла"""

    def _create_test_csv(filename, data):
        file_path = tmp_path / "data"
        file_path.mkdir()
        full_path = file_path / filename

        with open(full_path, 'w', encoding='utf-8', newline='') as f:
            if data:
                writer = csv.DictWriter(f, fieldnames=data[0].keys())
                writer.writeheader()
                writer.writerows(data)

        return str(tmp_path)

    return _create_test_csv


class TestCSVReader:
    def test_read_valid_file(self, create_test_csv, sample_csv_data):
        """Тест чтения корректного CSV файла"""
        tmp_dir = create_test_csv("test.csv", sample_csv_data)

        original_cwd = os.getcwd()
        os.chdir(tmp_dir)

        try:
            reader = CSVReader()
            result = reader.read(["test.csv"])

            assert len(result) == len(sample_csv_data)
            assert result[0]["student_name"] == sample_csv_data[0]["student_name"]
            assert result[1]["grade"] == sample_csv_data[1]["grade"]
        finally:
            os.chdir(original_cwd)

    def test_read_nonexistent_file(self):
        """Тест чтения несуществующего файла"""
        reader = CSVReader()

        with pytest.raises(FileNotFoundError, match="Файл 'nonexistent.csv' не найден"):
            reader.read(["nonexistent.csv"])

    def test_read_empty_file(self, create_test_csv):
        """Тест чтения пустого CSV файла"""
        tmp_dir = create_test_csv("empty.csv", [])

        original_cwd = os.getcwd()
        os.chdir(tmp_dir)

        try:
            reader = CSVReader()
            result = reader.read(["empty.csv"])

            assert len(result) == 0
        finally:
            os.chdir(original_cwd)


# Тесты для PerformanceReporter
class TestPerformanceReporter:
    @pytest.mark.parametrize("input_data,expected_results", [
        # Тест 1: базовый случай
        ([
             {"student_name": "Иванов", "grade": "5"},
             {"student_name": "Петров", "grade": "4"},
             {"student_name": "Иванов", "grade": "3"},
         ], {
             "Иванов": 4.0,  # (5+3)/2 = 4.0
             "Петров": 4.0  # 4/1 = 4.0
         }),
        # Тест 2: один студент с одной оценкой
        ([
             {"student_name": "Сидорова", "grade": "5"},
         ], {
             "Сидорова": 5.0
         }),
        # Тест 3: студенты без оценок (должны обработаться как 0)
        ([
             {"student_name": "Иванов", "grade": ""},
             {"student_name": "Петров", "grade": "4"},
         ], {
             "Петров": 4.0,
             "Иванов": 0.0
         }),
    ])
    def test_report_calculations(self, input_data, expected_results):
        """Тест корректности расчетов средних оценок"""
        reporter = PerformanceReporter()
        result = reporter.report(input_data)

        for student, expected_grade in expected_results.items():
            assert student in result
            assert result[student] == expected_results[student]

    def test_report_sorting(self, sample_student_data):
        """Тест корректности сортировки результатов"""
        reporter = PerformanceReporter()
        result = reporter.report(sample_student_data)

        grades = list(result.values())
        assert grades == sorted(grades, reverse=True)

    def test_tabulate_view_empty_data(self):
        """Тест отображения пустых данных"""
        reporter = PerformanceReporter()

        reporter.tabulate_view({})

    def test_tabulate_view_normal_data(self):
        """Тест отображения нормальных данных"""
        reporter = PerformanceReporter()
        test_data = {"Иванов": 4.5, "Петров": 3.8, "Сидорова": 5.0}

        reporter.tabulate_view(test_data)

    def test_invalid_grade_handling(self):
        """Тест обработки некорректных оценок"""
        reporter = PerformanceReporter()

        invalid_data = [
            {"student_name": "Иванов", "grade": "5"},
            {"student_name": "Петров", "grade": "не число"},
        ]

        result = reporter.report(invalid_data)

        # Проверяем, что некорректная оценка обработана как 0
        assert result["Петров"] == 0.0
        assert result["Иванов"] == 5.0


def test_integration(create_test_csv, sample_csv_data):
    """Интеграционный тест: чтение + обработка + вывод"""
    tmp_dir = create_test_csv("integration_test.csv", sample_csv_data)

    original_cwd = os.getcwd()
    os.chdir(tmp_dir)

    try:
        reader = CSVReader()
        data = reader.read(["integration_test.csv"])

        reporter = PerformanceReporter()
        result = reporter.report(data)

        assert len(result) > 0
        assert all(isinstance(grade, float) for grade in result.values())

        reporter.tabulate_view(result)

    finally:
        os.chdir(original_cwd)
