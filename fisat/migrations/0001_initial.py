# Generated by Django 2.2.12 on 2024-08-01 10:11

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='LabAllotment',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('lab_name', models.CharField(max_length=50)),
                ('day_allotted', models.CharField(max_length=10)),
                ('hours_allotted', models.CharField(max_length=50)),
                ('subject_name', models.CharField(max_length=100)),
                ('class_name', models.CharField(max_length=100)),
                ('start_date', models.DateField(default='2024-08-01')),
                ('end_date', models.DateField(default='2024-12-31')),
            ],
            options={
                'db_table': 'lab_allotment',
            },
        ),
    ]
