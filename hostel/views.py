from django.shortcuts import redirect,render,get_object_or_404
from django.http import HttpResponse
from .models import *
from .forms import *
from django.contrib.auth.decorators import login_required
from datetime import timedelta,date
from django.contrib import messages
from decimal import Decimal
from django.core.files.storage import default_storage
from django.conf import settings
from django.http import Http404
from collections import defaultdict
# Create your views here.

@login_required()
def home(request):
    return render(request,'hostel/home.html')


# Student manipulating functions

@login_required()
def add_student(request):
    if request.method == "POST":
        form = StudentForm(request.POST, request.FILES)
        admn_no = request.POST.get('admn_no')
        if Student.objects.filter(admn_no=admn_no).exists():
            messages.error(request,f"Sorry, a student with admission number {admn_no} already exists")
    
        elif form.is_valid():
            form.save()
            return redirect('view_student')
        else:
            messages.error(request,"Something went wrong...")
    else:
        form = StudentForm()
    return render(request,'hostel/add_stud.html',{'form':form})


@login_required()
def view_students(request):
    stud = Student.objects.select_related('pgm').all().order_by('pgm')
    if not stud.exists():
        messages.error(request,"Currently there are no students")
    return render(request,'hostel/students.html',{'stud':stud})


@login_required()
def view_details(request, student_id):
    student = Student.objects.filter(id=student_id).select_related('pgm').first()
    room = Allotment.objects.filter(name_id=student_id).select_related('room_number').first()
    student_image_url = None
    if student and student.photo:
        student_image_url = settings.MEDIA_URL + str(student.photo)
    return render(request, "hostel/details.html", {'student': student, 'student_image_url': student_image_url,'room':room})


@login_required()
def edit_student(request, student_id):
    student = get_object_or_404(Student, id=student_id)
    prev_admn_no = student.admn_no
    print(prev_admn_no)
    form = StudentForm(instance=student)

    if request.method == "POST":
        form = StudentForm(request.POST, request.FILES, instance=student)  # Include request.FILES to handle file uploads
        new_admn_no = request.POST.get('admn_no')
        print(new_admn_no)
        if prev_admn_no == new_admn_no:
            print("hello")
            if form.is_valid():
                if 'image' in form.changed_data:
                # Delete old image file if it exists
                    if student.image:
                        default_storage.delete(student.image.path)
            
                # Save form data including the image field
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
                    return redirect('view_student')
    return render(request, 'hostel/edit.html', {'form': form})


@login_required()
def delete_student(request,student_id):
    if request.method == 'GET':
        student = Student.objects.get(id=student_id)
        student.delete()
        return redirect('view_student')
    else:
        return render(request,'hostel/error.html')

# Room allocation functions

@login_required()
def allot_student(request):
    if request.method == "POST":
        form = AllotementForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('view_allotement')
    else:
        form = AllotementForm()
    return render(request,'hostel/allot_stud.html',{'form':form})

@login_required()
def edit_allocation(request,student_name):

    Alloted_object = Allotment.objects.get(name__name=student_name)
    #name is a OneToOneField to the Student model. The double underscore is used to access fields within related models.
    alloc_form = AllotementForm(instance=Alloted_object)

    if request.method == "POST":
        alloc_form = AllotementForm(request.POST,instance=Alloted_object)
        if alloc_form.is_valid():
            alloc_form.save()
            return redirect('view_allotement')
    return render(request,'hostel/edit_allocation.html',{'form':alloc_form})

@login_required()
def delete_allocation(request,student_name):
    if request.method == "GET":
        allot_obj = Allotment.objects.get(name__name=student_name)
        allot_obj.delete()
        return redirect('view_allotement')
    else:
        return HttpResponse("Error Occured")

@login_required()
def view_allotement(request):
    alloted_list = Allotment.objects.select_related('room_number','name').all().order_by('room_number')
    return render(request,'hostel/allotements.html',{'alloted':alloted_list})



# Attendance functions

@login_required()
def mark_attendance(request):
    if request.method == "POST":
        form = AttendanceForm(request.POST)
        if form.is_valid():
            date = form.cleaned_data['date']
            if AttendanceDate.objects.filter(date=date).exists():
                messages.error(request, f"Attendance has already been recorded for {date}")
            else:
                attendance_date_obj = AttendanceDate(date=date)
                attendance_date_obj.save()

                absentees = form.cleaned_data['absentees']
                for absentee in absentees:
                    stud = Student.objects.get(name=absentee)
                    att = AttendanceDate.objects.get(date=date)
                    absenti = Attendance(date=att,name=stud)
                    absenti.save()
                return redirect('view_attendance')
    else:
        form=AttendanceForm()
    return render(request,"hostel/attendance.html",{'form':form})


@login_required()
def view_attendance(request):
    attendance_list = Attendance.objects.all().select_related('name').order_by('name')
    return render(request,"hostel/summary.html",{'summary':attendance_list})



# mess bill functions

#function to find continuous absences
def find_continuous_absences(start_date, end_date):
    absences = Attendance.objects.filter(date__date__range=(start_date, end_date)).order_by('name', 'date__date')
    
    #Initialize a dictionary to store the continuous absences for each student
    continuous_absences = defaultdict(int)

    current_student = None
    current_streak = 0
    last_date = None

    for absence in absences:
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


@login_required()
def generate_mess_bill(request):
    if request.method == "POST":
        form = BillForm(request.POST)
        if form.is_valid():
            start_date = form.cleaned_data['start_date']
            end_date = form.cleaned_data['end_date']

            if AttendanceDate.objects.filter(date=start_date).exists() and AttendanceDate.objects.filter(date=end_date).exists():
                number_of_students = form.cleaned_data['number_of_students']
                total_mess_amount = form.cleaned_data['total_mess_amount']
                room_rent = form.cleaned_data['room_rent']
                staff_salary = form.cleaned_data['staff_salary']
                electricity_bill = form.cleaned_data['electricity_bill']

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
                        print(f"Student ID: {student_id}, Continuous Absences: {days_absent}")

                    for value in streak.values():
                        reduction_days += value
                    
                    total_mess_days = (mess_days * number_of_students) - reduction_days 
                    mess_bill_per_day = total_mess_amount/total_mess_days 
                    other_expenses_per_student = ((room_rent*number_of_students) + (staff_salary + electricity_bill)) / number_of_students 


                    #printing every details on the terminal
                    print(f"Start date: {start_date}")
                    print(f"End date: {end_date}")
                    print(f"Total students: {number_of_students}")
                    print(f"Total mess amount: {total_mess_amount}")
                    print(f"Total mess working days: {mess_days}")
                    print(f"Total mess days after reduction: {total_mess_days}")
                    print(f"Mess bill per day: {mess_bill_per_day}")
                    print(f"Other expenses per student: {other_expenses_per_student}")

                    students = Student.objects.all()

                    for student in students:
                        if student.id in streak:
                            name_id = student.id
                            days_present = mess_days - (streak[name_id])
                            mess_bill = round((mess_bill_per_day*days_present)+other_expenses_per_student,2)
                            print(f"Mess bill of {student} is {mess_bill}")
                            sum += mess_bill
                            student_bill = StudentBill(bill_id=bill_id,name=student,total=mess_bill,month=month,year=year)
                            student_bill.save()
                        else:
                            name_id = student.id
                            days_present = mess_days
                            mess_bill = round((mess_bill_per_day*days_present)+other_expenses_per_student,2)
                            print(f"Mess bill of {student} is {mess_bill}")
                            sum += mess_bill
                            student_bill = StudentBill(bill_id=bill_id,name=student,total=mess_bill,month=month,year=year)
                            student_bill.save()
                    print(f"Sum: {sum}")

                    return redirect('view_monthly_bill',month,year)
            else:
                messages.error(request,f"Attendance has not been taken between {start_date} and {end_date}")
    else:
        form = BillForm()
    return render(request, "hostel/billform.html", {'form': form})


@login_required()
def view_bill(request):
    context = StudentBill.objects.all().select_related('name')
    return render(request,"hostel/bill.html",{'bills':context})

@login_required()
def view_monthly_bill(request,month,year):
    current_month = month
    current_year = year
    bills = StudentBill.objects.filter(month=current_month,year=current_year).select_related('name')
    return render(request,"hostel/month_bill.html",{'bills':bills})

