from django.db import models


class LabAllotment(models.Model):
    lab_name = models.CharField(max_length=50)
    day_allotted = models.CharField(max_length=10)  # You can use a ChoiceField if there are predefined days
    hours_allotted = models.CharField(max_length=50)
    subject_name = models.CharField(max_length=100)
    class_name = models.CharField(max_length=100)
    start_date = models.CharField(max_length=100)  # Default start date
    end_date = models.CharField(max_length=100)    # Default end date

    def __str__(self):
        return f"{self.lab_name} - {self.subject_name} - {self.day_allotted}"

    class Meta:
        db_table = 'lab_allotment'

