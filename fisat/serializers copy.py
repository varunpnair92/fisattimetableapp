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

        # ✅ Convert hours_allotted to a list (assuming it's a comma-separated string)
        allotted_hours_list = list(map(int, hours_allotted.split(',')))  

        # ✅ Auto-calculate `day_allotted` if missing
        start_date = datetime.strptime(start_date_str, "%d-%m-%Y")
        day_allotted = validated_data.get('day_allotted', start_date.strftime('%A'))  
        validated_data['day_allotted'] = day_allotted  # Ensure it's included

        # ✅ Check for existing conflicts (using list overlap)
        existing_allotments = LabAllotment.objects.filter(
            lab_name=lab_name,
            day_allotted=day_allotted
        ).values_list('hours_allotted', flat=True)  

        conflicting_hours = []
        for existing_hours in existing_allotments:
            existing_hours_list = list(map(int, existing_hours.split(',')))
            # Check if any hour in allotted_hours_list exists in existing_hours_list
            if any(hour in existing_hours_list for hour in allotted_hours_list):
                conflicting_hours.extend(existing_hours_list)

        if conflicting_hours:
            raise serializers.ValidationError({"error": f"Conflict! {lab_name} already allotted on {day_allotted} for hours {conflicting_hours}."})

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
        day_allotted = validated_data['day_allotted']
        hours_allotted = validated_data['hours_allotted']

        start_date = datetime.strptime(start_date_str, "%d-%m-%Y")
        end_date = datetime.strptime(end_date_str, "%d-%m-%Y")

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



