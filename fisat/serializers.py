from rest_framework import serializers
from rest_framework.response import Response
from .models import LabAllotment
from datetime import datetime, timedelta

# class LabAllotmentSerializer(serializers.ModelSerializer):
#     allot = serializers.CharField(write_only=True, default='repeat')

#     class Meta:
#         model = LabAllotment
#         fields = ['id','lab_name', 'day_allotted', 'hours_allotted', 'subject_name', 'class_name', 'start_date', 'end_date', 'allot','external']

#     def create(self, validated_data):
#         allot = validated_data.pop('allot', 'repeat')
#         start_date_str = validated_data['start_date']
#         end_date_str = validated_data['end_date']

#         start_date = datetime.strptime(start_date_str, "%d-%m-%Y")
#         end_date = datetime.strptime(end_date_str, "%d-%m-%Y")

#         new_entries = []

#         if allot == 'continue':
#             current_date = start_date
#             while current_date <= end_date:
#                 # Automatically populate the day_allotted field via signal
#                 validated_data['start_date'] = current_date.strftime("%d-%m-%Y")
#                 validated_data['end_date'] = current_date.strftime("%d-%m-%Y")
#                 new_entry = LabAllotment.objects.create(**validated_data)
#                 new_entries.append(new_entry)
#                 current_date += timedelta(days=1)
#         else:
#             # Automatically populate the day_allotted field via signal
#             new_entry = LabAllotment.objects.create(**validated_data)
#             new_entries.append(new_entry)

#         return new_entries if len(new_entries) > 1 else new_entries[0]


from rest_framework import serializers
from datetime import datetime, timedelta
from .models import LabAllotment

class LabAllotmentSerializer(serializers.ModelSerializer):
    allot = serializers.CharField(write_only=True, default='repeat')

    class Meta:
        model = LabAllotment
        fields = ['id', 'lab_name', 'day_allotted', 'hours_allotted', 'subject_name', 
                  'class_name', 'start_date', 'end_date', 'allot', 'external']

    def create(self, validated_data):
        allot = validated_data.pop('allot', 'repeat')
        start_date_str = validated_data['start_date']
        end_date_str = validated_data['end_date']
        lab_name = validated_data['lab_name']
        hours_allotted = validated_data['hours_allotted']

        # ✅ Convert hours_allotted to a set for fast lookup
        allotted_hours_set = set(map(int, hours_allotted.split(',')))

        # ✅ Auto-calculate `day_allotted` if missing
        start_date = datetime.strptime(start_date_str, "%d-%m-%Y")
        day_allotted = validated_data.get('day_allotted', start_date.strftime('%A'))  
        validated_data['day_allotted'] = day_allotted  # Ensure it's included
        new_hours_set = set(map(int, hours_allotted.split(',')))

        # ✅ Fetch existing allotments that overlap in date and weekday
        allotments = LabAllotment.objects.filter(
            lab_name=lab_name,
            day_allotted=day_allotted,
        )

        # ✅ Check for hour conflicts
        conflicting_hours = set()
        for allotment in allotments:
            allotment_start = datetime.strptime(allotment.start_date, "%d-%m-%Y").date()
            allotment_end = datetime.strptime(allotment.end_date, "%d-%m-%Y").date()
            print(f"Allotment Start: {allotment_start}, Allotment End: {allotment_end}")
            print(f"Requested Start: {start_date.date()}")  # Convert to date for comparison

            # Convert `start_date` to date before comparison
            if allotment_start <= start_date.date() <= allotment_end:
                print("Inside date range check")
                existing_hours_set = set(map(int, allotment.hours_allotted.split(",")))
                overlap = new_hours_set & existing_hours_set
                if overlap:
                    conflicting_hours.update(overlap)

        # ✅ If conflict detected, raise an error
        if conflicting_hours:
            raise serializers.ValidationError({
                "error": f"Conflict! {lab_name} already allotted on {day_allotted} for hours {sorted(conflicting_hours)}."
            })

        # ✅ If no conflict, proceed with saving
        new_entries = []
        if allot == 'continue':
            current_date = start_date
            while current_date <= datetime.strptime(end_date_str, "%d-%m-%Y"):
                validated_data['start_date'] = current_date.strftime("%d-%m-%Y")
                validated_data['end_date'] = current_date.strftime("%d-%m-%Y")
                new_entry = LabAllotment.objects.create(**validated_data)
                new_entries.append(new_entry)
                current_date += timedelta(days=1)
        else:
            new_entry = LabAllotment.objects.create(**validated_data)
            new_entries.append(new_entry)

        return new_entries if len(new_entries) > 1 else new_entries[0]





from datetime import datetime, timedelta
from rest_framework import serializers
from .models import LabAllotment

class LabAllotmentContinueSerializer(serializers.ModelSerializer):
    class Meta:
        model = LabAllotment
        fields = ['id', 'lab_name', 'day_allotted', 'hours_allotted', 'subject_name',
                  'class_name', 'start_date', 'end_date', 'external']

    def create(self, validated_data):
        allot = validated_data.pop('allot', 'repeat')
        start_date_str = validated_data['start_date']
        end_date_str = validated_data['end_date']
        lab_name = validated_data['lab_name']
        hours_allotted = validated_data['hours_allotted']

        start_date = datetime.strptime(start_date_str, "%d-%m-%Y")
        end_date = datetime.strptime(end_date_str, "%d-%m-%Y")

        # If 'day_allotted' is missing, calculate it from start_date
        day_allotted = validated_data.get('day_allotted', start_date.strftime('%A'))
        validated_data['day_allotted'] = day_allotted  # Ensure it's included

        new_entries = []
        if allot == 'continue':
            current_date = start_date
            while current_date <= end_date:
                validated_data['start_date'] = current_date.strftime("%d-%m-%Y")
                validated_data['end_date'] = current_date.strftime("%d-%m-%Y")
                new_entry = LabAllotment.objects.create(**validated_data)
                new_entries.append(new_entry)
                current_date += timedelta(days=1)
        else:
            new_entry = LabAllotment.objects.create(**validated_data)
            new_entries.append(new_entry)

        return new_entries if len(new_entries) > 1 else new_entries[0]



