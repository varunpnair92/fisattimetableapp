from django.db import models
from django.db.models.signals import pre_save
from django.dispatch import receiver
from datetime import datetime

class LabAllotment(models.Model):
    id = models.AutoField(primary_key=True,db_column="id") 
    lab_name = models.CharField(max_length=50)
    day_allotted = models.CharField(max_length=10, blank=True)  # Make it optional to allow auto-filling
    hours_allotted = models.CharField(max_length=50)
    subject_name = models.CharField(max_length=100)
    class_name = models.CharField(max_length=100)
    start_date = models.CharField(max_length=100)  # Default start date
    end_date = models.CharField(max_length=100)    # Default end date
    external =  models.CharField(max_length=10,default="external")

    def __str__(self):
        return f"{self.lab_name} - {self.subject_name} - {self.day_allotted}"

    class Meta:
        db_table = 'lab_allotment'

# Signal handler to auto-fill the day_allotted field
@receiver(pre_save, sender=LabAllotment)
def auto_fill_day_allotted(sender, instance, **kwargs):
    if not instance.day_allotted:
        try:
            start_date = datetime.strptime(instance.start_date, "%d-%m-%Y")
            instance.day_allotted = start_date.strftime('%A')
        except ValueError:
            pass  # Handle the case where start_date format is incorrect


#sign in table

class User(models.Model):
    email = models.EmailField(unique=True)
    name = models.CharField(max_length=100)
    privilege = models.IntegerField(default=0)  # 1 for admin, 0 for normal user

    def __str__(self):
        return self.email
    class Meta:
        db_table = 'user_table'
