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
        # Parse the date and get the day of the week
        date = datetime.strptime(date_str, '%d-%m-%Y')
        day_of_week = date.strftime('%A')
        print(day_of_week)
    except ValueError:
        return Response({"error": "Invalid date format. Use DD-MM-YYYY."}, status=400)
    
    # Map the day of the week to the choices used in the model
    day_map = {
        'Monday': 'M',
        'Tuesday': 'T',
        'Wednesday': 'W',
        'Thursday': 'Th',
        'Friday': 'F'
        
    }
    
    day_code = day_map.get(day_of_week)
    
    if not day_code:
        return Response({"error": "No allotments available for weekends."}, status=400)
    
    # Filter the allotments based on the day of the week
    lab_allotments = LabAllotment.objects.filter(day_allotted=day_of_week)
    serializer = LabAllotmentSerializer(lab_allotments, many=True)
    
    # Use a dictionary to keep only the latest allotment for each lab and hour slot
    latest_allotments = {}
    
    for allotment in serializer.data:
        lab_name = allotment['lab_name']
        hours = allotment['hours_allotted']
        key = (lab_name, hours)
        
        if key not in latest_allotments:
            latest_allotments[key] = allotment
        else:
            existing_allotment_date = datetime.strptime(latest_allotments[key]['start_date'], '%d-%m-%Y')
            current_allotment_date = datetime.strptime(allotment['start_date'], '%d-%m-%Y')
            
            if current_allotment_date > existing_allotment_date:
                latest_allotments[key] = allotment
    
    # Group the data by lab_name
    grouped_data = defaultdict(list)
    for allotment in latest_allotments.values():
        lab_name = allotment['lab_name']
        grouped_data[lab_name].append({
            'class_name': allotment['class_name'],
            'subject_name': allotment['subject_name'],
            'day': allotment['day_allotted'],
            'hours': allotment['hours_allotted'],
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



