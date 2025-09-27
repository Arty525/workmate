import argparse
import sys
from src.reports import CSVReader, PerformanceReporter


if __name__ == "__main__":
    try:
        parser = argparse.ArgumentParser()
        parser.add_argument("--files", nargs='+', help="Файлы для обработки")
        parser.add_argument("--report", help="Тип отчета")

        args = parser.parse_args()

        reports = [
            "student-performance",
        ]

        if args.report not in reports:
            print(f"Отчета с именем {args.report} не существует")
            sys.exit(1)

        if args.report == "student-performance":
            students_data = CSVReader().read(args.files)
            report_data = PerformanceReporter().report(students_data)
            print(PerformanceReporter().tabulate_view(report_data))

    except FileNotFoundError:
        print(f"Файл с именем {args.files} не найден")
