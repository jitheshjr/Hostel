from django.shortcuts import redirect,render,get_object_or_404
from .models import *
from .forms import *
from django.contrib.auth.decorators import login_required
from datetime import timedelta,datetime
from django.contrib import messages
from django.core.exceptions import ValidationError
from django.core.files.storage import default_storage
from django.conf import settings
from collections import defaultdict
from .decorators import group_required
from .filters import *
from django.utils import timezone
from django.core.paginator import Paginator
from django.utils.timezone import localtime


def access_denied(request):
    return render(request,'hostel/access_denied.html')

@login_required()
def home(request):
    total_student = Student.objects.count()
    total_room = Room.objects.count()
    date_today = timezone.now().date()
    context = {
        'students':total_student,
        'rooms':total_room,
        'date':date_today
    }
    return render(request,'hostel/home.html',context)


# Student manipulating functions

@group_required('warden', login_url='access_denied')
def student_dashboard(request):
    try:
        total_students = Student.objects.count()
        last_student = Student.objects.last()  # Returns the last created student object

        context = {
            'total_students': total_students,
            'last_student_name': last_student.name if last_student else None
        }

        return render(request, 'hostel/student_dashboard.html', context)
    except Exception:
        return render(request,'hostel/error.html')


@group_required('warden', login_url='access_denied')
def add_student(request):
    try:
        if request.method == "POST":
            form = StudentForm(request.POST, request.FILES)
            admn_no = request.POST.get('admn_no')
            print(admn_no)
            if Student.objects.filter(admn_no=admn_no).exists():
                messages.error(request,f"Sorry, a student with admission number {admn_no} already exists")
            else:
                if form.is_valid():
                    form.save()
                    return redirect('student_dashboard')

                else:
                    # Debugging: Print form errors
                    messages.error(request, "Something went wrong...")
        else:
            form = StudentForm()
        return render(request,'hostel/add_stud.html',{'form':form})
    except Exception:
        return render(request,'hostel/error.html')

@group_required('warden', login_url='access_denied')  #new
def view_students(request):
    stud = Student.objects.select_related('pgm').order_by('id')

    # Apply filters
    students_filter = studentFilter(request.GET, queryset=stud)
    filtered_students = students_filter.qs

    # Custom search by name
    search_query = request.GET.get('search', '')
    if search_query:
        filtered_students = filtered_students.filter(name__icontains=search_query)

    # Count total
    total_students = filtered_students.count()

    # Pagination AFTER search
    paginator = Paginator(filtered_students, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    if not filtered_students.exists():
        messages.error(request, "Currently there are no students")

    return render(request, 'hostel/students.html', {
        'filter': students_filter,
        'page_obj': page_obj,
        'total_students': total_students,
        'search_query': search_query,
        'student':stud
    })


@group_required('warden', login_url='access_denied')
def view_details(request, student_id):
    student = Student.objects.filter(id=student_id).select_related('pgm').first()
    room = Allotment.objects.filter(name_id=student_id).select_related('room_number').first()
    student_image_url = None
    if student and student.photo:
        student_image_url = settings.MEDIA_URL + str(student.photo)
    return render(request, "hostel/details.html", {'student': student, 'student_image_url': student_image_url,'room':room})


def inactive_students(request, login_url='access_denied'):
    try:
        stud = Trash.objects.all().select_related('pgm').all().order_by('id')
        students_filter = studentFilter(request.GET, queryset=stud)
        if not stud.exists():
            messages.error(request,"Trash is empty")
        return render(request,'hostel/inact_students.html',{'filter':students_filter})
    except Exception:
        return render(request,'hostel/error.html')


@group_required('warden', login_url='access_denied')
def view_inactive_details(request, student_id):
    try:
        student = Trash.objects.filter(id=student_id).select_related('pgm').first()
        student_image_url = None
        if student and student.photo:
            student_image_url = settings.MEDIA_URL + str(student.photo)
        return render(request, "hostel/inact_details.html", {'student': student, 'student_image_url': student_image_url})
    except Exception:
        return render(request,'hostel/error.html')


@group_required('warden', login_url='access_denied')
def edit_student(request, student_id):
    try:
        student = get_object_or_404(Student, id=student_id)
        prev_admn_no = student.admn_no
        form = StudentForm(instance=student)

        if request.method == "POST":
            form = StudentForm(request.POST, request.FILES, instance=student)  # Include request.FILES to handle file uploads
            new_admn_no = request.POST.get('admn_no')
            if int(prev_admn_no) == int(new_admn_no):
                if form.is_valid():
                    if 'photo' in form.changed_data:  
                        # Delete old photo file if it exists
                        if student.photo and default_storage.exists(student.photo.path):
                            default_storage.delete(student.photo.path)

                    # Save form data (new photo if uploaded, otherwise keeps old one)
                    student = form.save()
                    return redirect('view_student')

            else:
                if Student.objects.filter(admn_no=new_admn_no).exists():
                    messages.error(request,f"Sorry, a student with admission number {new_admn_no} already exists")
                else:
                    if form.is_valid():
                        if 'image' in form.changed_data:
                            # Delete old image file if it exists
                            if student.image:
                                default_storage.delete(student.image.path)
                        
                        # Save form data including the image field
                        student = form.save()
                        return redirect('view_students')
        return render(request, 'hostel/edit.html', {'form': form})
    except Exception:
        return render(request,'hostel/error.html')


@group_required('warden', login_url='access_denied')
def delete_student(request,student_id):

    if request.method == 'GET':
        student = get_object_or_404(Student, id=student_id)

        # Get room number if allotted
        #room_no = None
        allotment = Allotment.objects.filter(name=student).first()
        if allotment:
            #room_no = allotment.room_number.room_number
            allotment.delete()

        # Move student data to Trash
        trash_obj = Trash(
            admn_no=student.admn_no,
            name=student.name,
            pgm=student.pgm,
            dob=student.dob,
            email=student.email,
            photo=student.photo,
            contact=student.contact,
            date_joined=student.date_joined,
            date_exited=timezone.now(),
            #room_no=room_no,
            category=student.category,
            E_Grantz=student.E_Grantz,
        )
        trash_obj.save()

        # Delete the student
        student.delete()
        return redirect('view_student')



# Room allocation functions

@group_required('warden', login_url='access_denied')
def room_dashboard(request):
    try:
        total_rooms = Room.objects.count()
        total_capacity = Room.objects.aggregate(total_capacity=models.Sum('capacity'))['total_capacity'] or 0
        current_allotted = Allotment.objects.count()
        available_slots = total_capacity - current_allotted

        context = {
            'total_rooms': total_rooms,
            'available_slots': available_slots
        }

        return render(request, 'hostel/room_dashboard.html', context)

    except Exception:
        return render(request, 'hostel/error.html')

@group_required('warden', login_url='access_denied')
def allot_student(request):
    try:
        if request.method == "POST":
            form = AllotementForm(request.POST)
            if form.is_valid():
                room = form.cleaned_data['room_number']
                if room.allotment_set.count() < room.capacity:
                    form.save()
                    messages.success(request, "Student successfully allotted to room.")
                    return redirect('allot_student')
                else:
                    messages.error(request, "Room capacity exceeded. Please choose a different room.")
            else:
                messages.error(request, "There was an error with your submission. Please try again.")
        else:
            form = AllotementForm()
        return render(request,'hostel/allot_stud.html',{'form':form})
    except Exception:
        return render(request,'hostel/error.html')


@group_required('warden', login_url='access_denied')
def edit_allocation(request,student_name):
    try:
        Alloted_object = Allotment.objects.get(name__name=student_name)
        # name is a OneToOneField to the Student model. The double underscore is used to access fields within related models.
        alloc_form = AllotementForm(instance=Alloted_object)

        if request.method == "POST":
            alloc_form = AllotementForm(request.POST,instance=Alloted_object)
            if alloc_form.is_valid():
                alloc_form.save()
                messages.success(request, "Room allocation edited successfully.")

        return render(request,'hostel/edit_allocation.html',{'form':alloc_form})
    except Exception:
        return render(request,'hostel/error.html')


@group_required('warden', login_url='access_denied')
def delete_allocation(request,student_name):
    try:
        if request.method == "GET":
            allot_obj = Allotment.objects.get(name__name=student_name)
            allot_obj.delete()
            messages.success(request,f"Deleted successfully")
            return redirect('view_allotement')

    except Exception:
        return render(request,'hostel/error.html')


@group_required('warden', login_url='access_denied')
def view_allotement(request):
    try:
        filter = roomFilter(request.GET, queryset=Allotment.objects.select_related('room_number', 'name').order_by('room_number'))
        alloted_list = filter.qs

        paginator = Paginator(alloted_list, 6)
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)

        query_params = request.GET.copy()
        if 'page' in query_params:
            query_params.pop('page')

        return render(request, 'hostel/allotements.html', {'alloted': page_obj, 'filter': filter, 'query_params': query_params})
    except Exception:
        return render(request,'hostel/error.html')


@group_required('warden', login_url='access_denied')
def room_list(request):
    rooms = Room.objects.all()
    room_data = []

    for room in rooms:
        allotted_count = room.allotment_set.count()
        available = room.capacity - allotted_count
        room_data.append({
            'room_number': room.room_number,
            'capacity': room.capacity,
            'available': available,
            'floor': room.floor
        })

    paginator = Paginator(room_data, 8)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {'page_obj': page_obj}
    return render(request, "hostel/roomList.html", context)

# Attendance functions
@login_required()
def attendance_dashboard(request):
    today = localtime().date()
    total_students = Student.objects.count()

    last_attendance = AttendanceDate.objects.last()
    last_date = last_attendance.date
    date_id = last_attendance.id
    recent_absent = Attendance.objects.filter(date=date_id).count()

    # Check today's attendance
    attendance_date = AttendanceDate.objects.filter(date=today).first()

    if attendance_date:
        attendance_taken = True
        absent_count = Attendance.objects.filter(date=attendance_date).count()
        present_count = total_students - absent_count
        attendance_percentage = round((present_count / total_students) * 100, 2) if total_students > 0 else 0
    else:
        attendance_taken = False
        present_count = absent_count = attendance_percentage = None

    context = {
        'attendance_taken': attendance_taken,
        'present_count': present_count,
        'absent_count': absent_count,
        'attendance_percentage': attendance_percentage,
        'recent_absent': recent_absent, 
        'last_date':last_date
    }
    return render(request, 'hostel/attendance_dashboard.html', context)



@login_required()
def mark_attendance(request):
    try:
        if request.method == "POST":
            form = AttendanceForm(request.POST)
            if form.is_valid():
                date = form.cleaned_data['date']
                if AttendanceDate.objects.filter(date=date).exists():
                    messages.error(request, f"Attendance has already been recorded for {date}")
                else:
                    month = date.strftime('%B')
                    year = date.year
                    attendance_date_obj = AttendanceDate(date=date,month=month,year=year)
                    attendance_date_obj.save()

                    absentees = form.cleaned_data['absentees']
                    for absentee in absentees:
                        stud = Student.objects.get(name=absentee)
                        att = AttendanceDate.objects.get(date=date)
                        absenti = Attendance(date=att,name=stud)
                        absenti.save()
                    messages.success(request, f"Attendance for {date} recorded successfully.")
        else:
            form=AttendanceForm()
        students = Student.objects.all()
        return render(request,"hostel/attendance.html",{'form':form,'students':students})
    except Exception:
        return render(request,'hostel/error.html')


@login_required()
def view_attendance(request):
    filter = attendanceFilter(request.GET, queryset=AttendanceDate.objects.all().order_by('-date'))
    attendance_list = filter.qs

    # Pagination
    paginator = Paginator(attendance_list, 8)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    # for filter
    query_params = request.GET.copy()
    if 'page' in query_params:
        query_params.pop('page')

    return render(request, "hostel/summary.html", {'page_obj': page_obj, 'filter': filter, 'query_params': query_params})

@login_required()
def detailed_attendance(request, date_id):
    try:
        attendance_date = get_object_or_404(AttendanceDate, id=date_id)        
        absentees = Attendance.objects.filter(date=attendance_date)
        total_absentees = absentees.count()

        paginator = Paginator(absentees, 7)  
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)

        context = {
            'date': attendance_date,
            'absentees': page_obj,
            'total_absentees': total_absentees,
        }
        return render(request, "hostel/attendance_detail.html", context)

    except Exception:
        return render(request, 'hostel/error.html')

@login_required()
def delete_attendance(request, date_id):
    try:
        attendance_instance = get_object_or_404(AttendanceDate, id=date_id)
        if request.method == "GET":
            attendance_instance.delete()
            messages.success(request, f"Deleted successfully.")
            return redirect('view_attendance')
        else:
            messages.error(request,f"Something went wrong.")
        return redirect('view_attendance')
    except Exception:
        return render(request,'hostel/error.html')

@group_required('warden', login_url='access_denied')
def absent_records(request, student_id):
    student = get_object_or_404(Student,id=student_id)
    absences = Attendance.objects.filter(name=student).select_related('date').order_by('date__date')

    paginator = Paginator(absences,5)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request,"hostel/absent_days.html",{'student':student,'page_obj':page_obj})

# mess bill functions

@group_required('warden', login_url='access_denied')
def bill_dashboard(request):
        last_bill = MessBill.objects.last()
        return render(request, "hostel/bill_dashboard.html", {'bill':last_bill})


#function to find continuous absences
def find_continuous_absences(start_date, end_date):
    absences = Attendance.objects.filter(date__date__range=(start_date, end_date)).order_by('name', 'date__date')
    
    #Initialize a dictionary to store the continuous absences for each student
    continuous_absences = defaultdict(int)

    current_student = None
    current_streak = 0
    last_date = None

    for absence in absences:

        #new
        stud = absence.name
        if stud.E_Grantz: # Skip students with eGrantz
            continue

        student_id = absence.name.id
        absence_date = absence.date.date

        # Check if the current absence record belongs to a different student
        if current_student != student_id:
            # If the previous student had a streak of 7 or more absences, add it to the dictionary
            if current_streak >= 7:
                continuous_absences[current_student] += current_streak
            
            # Update current student and reset streak for the new student
            current_student = student_id
            current_streak = 1
            last_date = absence_date
        else:
            # Check if the current absence is continuous with the previous one
            if absence_date == last_date + timedelta(days=1):
                current_streak += 1
            else:
                # If the absence is not continuous, check if the streak is 7 or more
                if current_streak >= 7:
                    continuous_absences[current_student] += current_streak
                # Reset the streak for the new absence streak
                current_streak = 1
            # Update the last absence date for the current student
            last_date = absence_date
    
    # Final check for the last student in the list
    if current_streak >= 7:
        continuous_absences[current_student] += current_streak
    
    return dict(continuous_absences)


@group_required('warden', login_url='access_denied')
def generate_mess_bill(request):
    if request.method == "POST":
        form = BillForm(request.POST)
        if form.is_valid():
            start_date = form.cleaned_data['start_date']
            end_date = form.cleaned_data['end_date']

            if AttendanceDate.objects.filter(date=start_date).exists() and AttendanceDate.objects.filter(date=end_date).exists():
                number_of_students = Student.objects.count()
                total_mess_amount = form.cleaned_data['total_mess_amount']
                room_rent = form.cleaned_data['room_rent']
                staff_salary = form.cleaned_data['staff_salary']
                electricity_bill = form.cleaned_data['electricity_bill']

                total = total_mess_amount + (room_rent*number_of_students) + staff_salary + electricity_bill

                year = start_date.year
                month = start_date.strftime('%B')

                reduction_days = 0
                sum = 0

                existing_bill = MessBill.objects.filter(month=month,year=year).exists()
                if existing_bill:
                    messages.error(request,f"Bill for {month}, {year} already exists")
                else:
                    mess_days = (end_date-start_date).days + 1

                    messbill = MessBill(
                        no_of_students=number_of_students,
                        month=month,
                        mess_days=mess_days,
                        mess_amount=total_mess_amount,
                        room_rent=room_rent,
                        staff_salary=staff_salary,
                        electricity_bill=electricity_bill,
                        total=total,
                        year=year
                    )
                    messbill.save()
                    bill_id = get_object_or_404(MessBill, month=month,year=year)


                    streak = find_continuous_absences(start_date, end_date)

                    #just for printing the continuouse absentees in the terminal
                    for student_id, days_absent in streak.items():
                        stud = get_object_or_404(Student, id=student_id)
                        continous_absent = ContinuousAbsence(bill_id=bill_id,name=stud,streak=days_absent,month=month,year=year)
                        continous_absent.save()
                        #print(f"Student ID: {student_id}, Continuous Absences: {days_absent}")

                    for value in streak.values():
                        reduction_days += value
                    
                    total_mess_days = (mess_days * number_of_students) - reduction_days 
                    mess_bill_per_day = total_mess_amount/total_mess_days 
                    other_expenses_per_student = ((room_rent*number_of_students) + (staff_salary + electricity_bill)) / number_of_students 
                    
                    #new
                    est = 300
                    other_expenses_per_student_4_egrantz = (((room_rent*number_of_students) + (staff_salary + electricity_bill)) / number_of_students ) + est


                    #printing every details on the terminal
                    print(f"Start date: {start_date}")
                    print(f"End date: {end_date}")
                    print(f"Total students: {number_of_students}")
                    print(f"Total mess amount: {total_mess_amount}")
                    print(f"Total mess working days: {mess_days}")
                    print(f"Total mess reduction days: {reduction_days}")
                    print(f"Total mess days after reduction: {total_mess_days}")
                    print(f"Mess bill per day: {mess_bill_per_day}")
                    print(f"Other expenses per student: {other_expenses_per_student}")
                    print(f"Other expenses per student: {other_expenses_per_student_4_egrantz}")

                    students = Student.objects.all()

                    for student in students:
                        if student.id in streak:
                            name_id = student.id
                            days_present = mess_days - (streak[name_id])
                            mess_bill = round((mess_bill_per_day*days_present)+other_expenses_per_student,2)
                            #print(f"Mess bill of {student} is {mess_bill}")
                            sum += mess_bill
                            student_bill = StudentBill(bill_id=bill_id,name=student,total=mess_bill,month=month,year=year)
                            student_bill.save()
                        else:
                            name_id = student.id
                            days_present = mess_days
                            mess_bill = round((mess_bill_per_day*days_present)+other_expenses_per_student_4_egrantz,2)
                            #print(f"Mess bill of {student} is {mess_bill}")
                            sum += mess_bill
                            student_bill = StudentBill(bill_id=bill_id,name=student,total=mess_bill,month=month,year=year)
                            student_bill.save()
                    print(f"Sum: {sum}")

                    return redirect('view_monthly_bill',month,year)
            else:
                messages.error(request,f"Attendance has not been taken between {start_date} and {end_date}")
        else:
            messages.error(request, "Make sure your entries are correct.")
    else:
        form = BillForm()
    return render(request, "hostel/billform.html", {'form': form})

@group_required('warden', login_url='access_denied')
def delete_bill(request, pk):
    bill_obj = get_object_or_404(MessBill,pk=pk)
    print(bill_obj)
    if request.method == "GET":
        bill_obj.delete()
        messages.success(request,f"Deleted Successfully.")
        return redirect('total_bill')
    else:
        messages.error(request,f"Something went wrong.")

@group_required('warden', login_url='access_denied')
def total_bill(request):
    try:
        bill_filter = monthbillFilter(request.GET, queryset=MessBill.objects.all().order_by('-id'))
        bill_list = bill_filter.qs

        paginator = Paginator(bill_list, 10)
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)

        query_params = request.GET.copy()
        if 'page' in query_params:
            query_params.pop('page')

        return render(request, "hostel/totalbill.html", {'filter': bill_filter, 'page_obj': page_obj, 'query_params': query_params})
    except Exception:
        return render(request, 'hostel/error.html')

@group_required('warden', login_url='access_denied')
def view_monthly_bill(request,month,year):
    try:
        current_month = month
        current_year = year

        students = Student.objects.all()

        e_grantz_students = students.filter(E_Grantz=True)
        non_e_grantz_students = students.filter(E_Grantz=False)

        true_bills = StudentBill.objects.filter(month=current_month,year=current_year,name__in=e_grantz_students).select_related('name')
        false_bills = StudentBill.objects.filter(month=current_month,year=current_year,name__in=non_e_grantz_students).select_related('name')

        return render(request,"hostel/month_bill.html",{'true_bills':true_bills,'false_bills':false_bills})
    except Exception:
        return render(request,'hostel/error.html')

@login_required()
def streak(request):
    try:
        streak_filter = streakFilter(request.GET, queryset=ContinuousAbsence.objects.all().select_related('name').order_by('-id'))
        streak_list = streak_filter.qs

        paginator = Paginator(streak_list, 10)
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)

        # Get the query parameters as a dictionary
        query_params = request.GET.copy()
        if 'page' in query_params:
            query_params.pop('page')

        return render(request, "hostel/streak.html", {'filter': streak_filter, 'page_obj': page_obj, 'query_params': query_params})
    except Exception:
        return render(request, 'hostel/error.html')
