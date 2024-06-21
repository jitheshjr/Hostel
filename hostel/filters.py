import django_filters

from .models import Student,Room

class studentFilter(django_filters.FilterSet):
    class Meta:
        model = Student
        exclude = ['name','admn_no','dob','email','photo','contact','parent_name','parent_occupation','address','annual_income','status','date_joined','date_exited']
