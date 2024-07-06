from django import forms
from .models import *


class StudentForm(forms.ModelForm):
    class Meta:
        model = Student
        fields = '__all__'

        widgets = {
            'dob': forms.TextInput(attrs={'placeholder':'YYYY-MM-DD'}),
            'contact': forms.TextInput(attrs={'pattern': '\d{10}', 'placeholder': 'Please enter a valid mobile number.'}),
        }

        labels = {
            'admn_no': 'Admission Number',
            'year_of_admn': 'Year of Admission',
            'dob': 'Date of Birth',
            'contact': 'Contact Number',
        }
    
class AllotementForm(forms.ModelForm):
    class Meta:
        model = Allotment
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super(AllotementForm, self).__init__(*args, **kwargs)
        allocated_students = Allotment.objects.values_list('name_id', flat=True)
        self.fields['name'].queryset = Student.objects.exclude(id__in=allocated_students)


class BillForm(forms.Form):
    start_date = forms.DateField(label='Start Date', widget=forms.DateInput(attrs={'type': 'date'}))
    end_date = forms.DateField(label='End Date', widget=forms.DateInput(attrs={'type': 'date'}))
    number_of_students = forms.IntegerField(label='Total Students', min_value=0,required=False)
    total_mess_amount = forms.DecimalField(label='Amount', min_value=0)
    room_rent = forms.DecimalField(label='Room Rent', min_value=0, initial=500)
    staff_salary = forms.DecimalField(label='Staff Salary', min_value=0, initial=10000)
    electricity_bill = forms.DecimalField(label='Electricity Bill', min_value=0)

class AttendanceForm(forms.Form):
    date = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date'}),
        label='Date'
        )

    absentees = forms.ModelMultipleChoiceField(
        queryset=Student.objects.all(),
        required=False,
        widget=forms.CheckboxSelectMultiple,
        label='Students'
        )