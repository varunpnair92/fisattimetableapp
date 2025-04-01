import csv
from django.core.management.base import BaseCommand
from fisat.models import LabAllotment

class Command(BaseCommand):
    help = 'Import lab allotments from a CSV file'

    def add_arguments(self, parser):
        parser.add_argument('csv_file', type=str, help='Path to CSV file')

    def handle(self, *args, **kwargs):
        file_path = kwargs['csv_file']
        
        with open(file_path, 'r') as file:
            reader = csv.reader(file)
            next(reader)  # Skip header if exists
            
            lab_allotments = [
                LabAllotment(
                    lab_name=row[0],
                    day_allotted=row[1],
                    hours_allotted=row[2],
                    subject_name=row[3],
                    class_name=row[4],
                    start_date=row[5],
                    end_date=row[6]
                )
                for row in reader
            ]
            LabAllotment.objects.bulk_create(lab_allotments)
            
            self.stdout.write(self.style.SUCCESS('Successfully imported lab allotments!'))

