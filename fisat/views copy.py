from datetime import datetime
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .models import LabAllotment
from .serializers import LabAllotmentSerializer
from collections import defaultdict




@api_view(['POST'])
def lab_allotment_view(request):
    date_str = request.data.get('date', None)
    
    if date_str is None:
        return Response({"error": "Date parameter is required."}, status=400)
    
    try:
        date = datetime.strptime(date_str, '%d-%m-%Y')
        day_of_week = date.strftime('%A')
    except ValueError:
        return Response({"error": "Invalid date format. Use DD-MM-YYYY."}, status=400)
    
    # Map days to short form (if applicable)
    day_map = {'Monday': 'M', 'Tuesday': 'T', 'Wednesday': 'W', 'Thursday': 'Th', 'Friday': 'F'}
    day_code = day_map.get(day_of_week)

    if not day_code:
        return Response({"error": "No allotments available for weekends."}, status=400)
    
    # Fetch all allotments for the given day
    lab_allotments = LabAllotment.objects.filter(day_allotted=day_of_week).order_by('id')  # Ensure ordered by ID
    serializer = LabAllotmentSerializer(lab_allotments, many=True)

    # Dictionary to store latest allotments per (lab, time slot)
    latest_allotments = {}

    for allotment in serializer.data:
        lab_name = allotment['lab_name']
        hours = allotment['hours_allotted'].split(',')  # Keep time range as strings
        allotment_id = allotment['id']  # Use ID to determine latest entry

        for hour in hours:
            key = (lab_name, hour)  # Unique per lab & time slot

            if key not in latest_allotments:
                latest_allotments[key] = allotment  # First entry
            else:
                # Keep the latest allotment based on ID (newer entries have higher IDs)
                if allotment_id > latest_allotments[key]['id']:
                    latest_allotments[key] = allotment

    # **Group Data by Lab Name**
    grouped_data = defaultdict(list)

    for (lab_name, hour), allotment in latest_allotments.items():
        grouped_data[lab_name].append({
            'class_name': allotment['class_name'],
            'subject_name': allotment['subject_name'],
            'day': allotment['day_allotted'],
            'hours': hour,  # Use time range as-is
            'start_date': allotment['start_date'],
            'end_date': allotment['end_date'],
            'external': allotment['external']
        })

    return Response(grouped_data)




from .serializers import LabAllotmentSerializer

@api_view(['POST'])
def allot_lab_slot(request):
    data = request.data.copy()

    # Ensure start_date exists and extract the day of the week
    start_date_str = data.get('start_date')
    if not start_date_str:
        return Response({"error": "start_date is required"}, status=400)

    try:
        start_date = datetime.strptime(start_date_str, "%d-%m-%Y")
        day_of_week = start_date.strftime('%A')  # Extract full day name
    except ValueError:
        return Response({"error": "Invalid start_date format. Use DD-MM-YYYY."}, status=400)

    # If day_allotted is missing, populate it automatically
    if 'day_allotted' not in data:
        data['day_allotted'] = day_of_week  # Store the full name

    lab_name = data.get('lab_name')
    hours_allotted = data.get('hours_allotted')

    # Check for conflicts (Same Lab, Same Day, Overlapping Hours)
    existing_allotment = LabAllotment.objects.filter(
        lab_name=lab_name,
        day_allotted=day_of_week,
        hours_allotted=hours_allotted
    ).first()

    if existing_allotment:
        return Response(
            {"error": f"Conflict detected! {lab_name} is already allotted on {day_of_week} for hour {hours_allotted}."},
            status=400
        )

    # If no conflict, save the allotment
    serializer = LabAllotmentSerializer(data=data)
    if serializer.is_valid():
        entries = serializer.save()
        response_data = LabAllotmentSerializer(entries, many=isinstance(entries, list)).data
        return Response(response_data, status=201)

    return Response(serializer.errors, status=400)







    
#lab allotment dtails
@api_view(['GET'])
def labdetailsexternal(request):
    # Filter the allotments based on the external field and order by start_date
    lab_allotments = LabAllotment.objects.filter(
        external='external'
    ).order_by('-start_date')  # Order by start_date in descending order

    serializer = LabAllotmentSerializer(lab_allotments, many=True)

    return Response(serializer.data) 
   
    


from rest_framework.decorators import api_view
from rest_framework.response import Response
from .serializers import LabAllotmentContinueSerializer

@api_view(['POST'])
def allot_lab_slot_continue(request):
    """
    View to continue allotment even in the case of conflict.
    """
    serializer = LabAllotmentContinueSerializer(data=request.data)
    if serializer.is_valid():
        allotment = serializer.save()
        return Response({"message": "Allotment saved with conflict"}, status=201)
    else:
        return Response(serializer.errors, status=400)





from datetime import datetime
from collections import defaultdict
from django.http import JsonResponse
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .models import LabAllotment
from .serializers import LabAllotmentSerializer

@api_view(['POST'])
def lab_allotment_range_view(request):
    start_date_str = request.data.get('start_date')
    end_date_str = request.data.get('end_date')
    
    if not start_date_str or not end_date_str:
        return Response({"error": "Both start_date and end_date are required."}, status=400)

    try:
        start_date = datetime.strptime(start_date_str, '%d-%m-%Y')
        end_date = datetime.strptime(end_date_str, '%d-%m-%Y')
    except ValueError:
        return Response({"error": "Invalid date format. Use DD-MM-YYYY."}, status=400)

    # Fetch lab allotments, order by ID to get the latest first
    lab_allotments = LabAllotment.objects.all().order_by('-id')

    latest_allotments = {}

    # Loop through all lab allotments and filter them based on the date range
    for allotment in lab_allotments:
        # Convert the start_date and end_date from string to datetime (if they are stored as VARCHAR)
        allotment_start_date = datetime.strptime(allotment.start_date, '%d-%m-%Y')  # Assuming the date is in 'dd-mm-yyyy' format
        allotment_end_date = datetime.strptime(allotment.end_date, '%d-%m-%Y')  # Assuming the date is in 'dd-mm-yyyy' format

        # Check if the allotment date falls within the given date range
        if start_date <= allotment_start_date <= end_date:
            lab_name = allotment.lab_name
            hours = allotment.hours_allotted
            key = (lab_name, hours)

            # Store the latest allotment based on the date
            if key not in latest_allotments:
                latest_allotments[key] = allotment
            else:
                # Compare start dates to ensure we have the latest
                existing_date = datetime.strptime(latest_allotments[key].start_date, '%d-%m-%Y')
                current_date = allotment_start_date

                if current_date > existing_date:
                    latest_allotments[key] = allotment

    # Group the results by lab_name
    grouped_data = defaultdict(list)
    for allotment in latest_allotments.values():
        grouped_data[allotment.lab_name].append({
            'class_name': allotment.class_name,
            'subject_name': allotment.subject_name,
            'day': allotment.day_allotted,
            'hours': allotment.hours_allotted,
            'start_date': allotment.start_date,
            'end_date': allotment.end_date,
            'external': allotment.external
        })

    return Response(grouped_data)
