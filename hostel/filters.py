import django_filters
from django.forms.widgets import DateInput
from .models import *

class studentFilter(django_filters.FilterSet):
    class Meta:
        model = Student
        exclude = ['name','admn_no','dob','email','photo','contact','parent_name','parent_occupation','address','annual_income','status','date_joined','date_exited']

class billFilter(django_filters.FilterSet):
    class Meta:
        model = StudentBill
        exclude = ['bill_id','total']

class roomFilter(django_filters.FilterSet):
    class Meta:
        model = Allotment
        fields = ['room_number']

class streakFilter(django_filters.FilterSet):
    class Meta:
        model = ContinuousAbsence
        fields = ['name','month','year']

class monthbillFilter(django_filters.FilterSet):
    class Meta:
        model = MessBill
        fields = ['month','year']

class attendanceFilter(django_filters.FilterSet):
    class Meta:
        model = AttendanceDate
        fields = ['month','year']