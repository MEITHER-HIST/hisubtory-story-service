import csv
from pathlib import Path
from django.core.management.base import BaseCommand
from subway.models import Line, Station

class Command(BaseCommand):
    help = "Seed subway lines and stations from CSV and link them (MySQL)"

    def handle(self, *args, **options):
        base_path = Path("subway/management/seed_data")
        lines_file = base_path / "lines.csv"
        stations_file = base_path / "stations.csv"

        if not lines_file.exists() or not stations_file.exists():
            self.stderr.write(self.style.ERROR("CSV files not found!"))
            return

        # 1. Seed Lines
        self.stdout.write("Seeding Lines...")
        with lines_file.open(newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                name = row["line_name"].strip()
                color = row.get("line_color", "").strip()
                Line.objects.using("mysql").update_or_create(
                    line_name=name,
                    defaults={"line_color": color},
                )

        # 2. Seed Stations and Link to Lines
        self.stdout.write("Seeding Stations and Linking...")
        line_3, _ = Line.objects.using("mysql").get_or_create(line_name="3호선")
        
        with stations_file.open(newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                code = row["station_code"].strip()
                name = row["station_name"].strip()
                is_enabled = row.get("is_enabled", "true").lower() == "true"

                station, created = Station.objects.using("mysql").update_or_create(
                    station_code=code,
                    defaults={
                        "station_name": name,
                        "is_enabled": is_enabled,
                    },
                )
                
                # '3-'로 시작하는 코드는 3호선으로 자동 연결
                if code.startswith("3-"):
                    station.lines.add(line_3)
                    station.save(using="mysql")

        self.stdout.write(self.style.SUCCESS("Database Seeding Completed!"))
