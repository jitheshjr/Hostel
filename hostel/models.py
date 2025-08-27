from django.db import models
from django.core.validators import RegexValidator
from PIL import Image
from io import BytesIO
from django.core.files.base import ContentFile
import os

# Create your models here.

class Department(models.Model):
    dept_name = models.CharField(max_length=100,unique=True)

    def __str__(self):
        return self.dept_name

class Programme(models.Model):
    pgm_name = models.CharField(max_length=100,unique=True)
    dept_id = models.ForeignKey(Department,on_delete=models.CASCADE)
    
    def __str__(self):
        return self.pgm_name

class Student(models.Model):
    admn_no = models.PositiveIntegerField(unique=True)
    name = models.CharField(max_length=50)
    pgm = models.ForeignKey(Programme, on_delete=models.CASCADE)
    dob = models.DateField()
    email = models.EmailField()
    photo = models.ImageField(upload_to="images/", blank=True, null=True)
    contact_regex = RegexValidator(regex=r'^\d{10}$',message="Contact number must be a 10-digit number.")
    contact = models.CharField(validators=[contact_regex], max_length=10)  # Using CharField for contact with max length 10
    date_joined = models.DateField(auto_now_add=True)

    CATEGORY_CHOICES = [
        ('GENERAL', 'GENERAL'),
        ('OBC', 'OBC'),
        ('OEC', 'OEC'),
        ('SC', 'SC'),
        ('ST', 'ST'),
    ]
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default='GENERAL')
    
    EGRANTZ_CHOICES = [
        (True, 'Yes'),
        (False, 'No'),
    ]
    E_Grantz = models.BooleanField(choices=EGRANTZ_CHOICES)
    
    def save(self, *args, **kwargs):
        # Keep reference of uploaded photo
        original_photo = self.photo

        # Save first to make sure file exists on disk
        super().save(*args, **kwargs)

        if original_photo and self.photo:  
            photo_path = self.photo.path
            if os.path.exists(photo_path):   
                img = Image.open(photo_path)

                if img.mode != 'RGB':
                    img = img.convert('RGB')

                # Maintain 3:4 ratio
                desired_ratio = 3 / 4
                width, height = img.size
                current_ratio = width / height

                if current_ratio > desired_ratio:
                    new_width = int(height * desired_ratio)
                    left = (width - new_width) / 2
                    right = left + new_width
                    img = img.crop((left, 0, right, height))
                elif current_ratio < desired_ratio:
                    new_height = int(width / desired_ratio)
                    top = (height - new_height) / 2
                    bottom = top + new_height
                    img = img.crop((0, top, width, bottom))

                # Save as WebP
                buffer = BytesIO()
                img.save(buffer, format='WEBP', quality=85)
                webp_filename = os.path.splitext(original_photo.name)[0] + ".webp"

                # Replace file in DB
                self.photo.save(webp_filename, ContentFile(buffer.getvalue()), save=False)

                # Delete original (non-WebP) file if still exists
                original_path = original_photo.path
                if os.path.exists(original_path) and not original_path.endswith(".webp"):
                    os.remove(original_path)

                # Final save to update DB with WebP image
                super().save(*args, **kwargs)



    def __str__(self):
        return self.name


class Trash(models.Model):
    admn_no = models.PositiveIntegerField(unique=True)
    name = models.CharField(max_length=50)
    pgm = models.ForeignKey(Programme, on_delete=models.CASCADE)
    dob = models.DateField()
    email = models.EmailField()
    photo = models.ImageField(upload_to="images/")
    contact_regex = RegexValidator(regex=r'^\d{10}$',message="Contact number must be a 10-digit number.")
    contact = models.CharField(validators=[contact_regex], max_length=10)  # Using CharField for contact with max length 10
    date_joined = models.DateField()
    date_exited = models.DateField(null=True,blank=True)
    
    CATEGORY_CHOICES = [
        ('GENERAL', 'GENERAL'),
        ('OBC', 'OBC'),
        ('OEC', 'OEC'),
        ('SC', 'SC'),
        ('ST', 'ST'),
    ]
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default='GENERAL')
    
    EGRANTZ_CHOICES = [
        (True, 'Yes'),
        (False, 'No'),
    ]
    E_Grantz = models.BooleanField(choices=EGRANTZ_CHOICES)

    def __str__(self):
        return self.name
    
    
class Room(models.Model):
    room_number = models.SmallIntegerField(unique=True)
    floor_choices = [('Ground','Ground'),('First','First')]
    floor = models.CharField(max_length=50, choices=floor_choices)
    capacity = models.PositiveIntegerField(default=3)

    def __str__(self):
        return str(self.room_number)
    
class Allotment(models.Model):
    room_number = models.ForeignKey(Room,on_delete=models.CASCADE)
    name = models.OneToOneField(Student,on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.name} in {self.room_number}" 
    
    def save(self, *args, **kwargs):
        if self.room_number.allotment_set.count() >= self.room_number.capacity:
            raise ValueError("Room capacity exceeded")
        super().save(*args, **kwargs)

class AttendanceDate(models.Model):
    date = models.DateField(unique=True)
    MONTH_CHOICES = [
        ('January', 'January'),
        ('February', 'February'),
        ('March', 'March'),
        ('April', 'April'),
        ('May', 'May'),
        ('June', 'June'),
        ('July', 'July'),
        ('August', 'August'),
        ('September', 'September'),
        ('October', 'October'),
        ('November', 'November'),
        ('December', 'December'),
    ]
    month = models.CharField(max_length=10,choices=MONTH_CHOICES)
    year = models.IntegerField()

    def __str__(self):
        return str(self.date)

class Attendance(models.Model):
    date = models.ForeignKey(AttendanceDate,on_delete=models.CASCADE)
    name = models.ForeignKey(Student,on_delete=models.CASCADE)
    class Meta:
        unique_together = ('date','name')

    def __str__(self):
        return f"{self.name.name} was absent on {self.date.date}"


class MessBill(models.Model):
    no_of_students = models.SmallIntegerField()
    MONTH_CHOICES = [
        ('January', 'January'),
        ('February', 'February'),
        ('March', 'March'),
        ('April', 'April'),
        ('May', 'May'),
        ('June', 'June'),
        ('July', 'July'),
        ('August', 'August'),
        ('September', 'September'),
        ('October', 'October'),
        ('November', 'November'),
        ('December', 'December'),
    ]
    month = models.CharField(max_length=42,choices=MONTH_CHOICES)
    mess_days = models.SmallIntegerField()
    mess_amount = models.DecimalField(max_digits=10,decimal_places=2)
    room_rent = models.DecimalField(max_digits=10,decimal_places=2)
    staff_salary = models.DecimalField(max_digits=10,decimal_places=2)
    electricity_bill = models.DecimalField(max_digits=10,decimal_places=2)
    total = models.DecimalField(max_digits=10,decimal_places=2)
    year = models.SmallIntegerField()

    class Meta:
        unique_together = ['month','year']

    def __str__(self):
        return f"{self.month}-{self.year}"

class StudentBill(models.Model):
    bill_id = models.ForeignKey(MessBill,on_delete=models.CASCADE)
    name = models.ForeignKey(Student,on_delete=models.CASCADE)
    total = models.DecimalField(max_digits=10,decimal_places=2)
    MONTH_CHOICES = [
        ('January', 'January'),
        ('February', 'February'),
        ('March', 'March'),
        ('April', 'April'),
        ('May', 'May'),
        ('June', 'June'),
        ('July', 'July'),
        ('August', 'August'),
        ('September', 'September'),
        ('October', 'October'),
        ('November', 'November'),
        ('December', 'December'),
    ]
    month = models.CharField(max_length=20,choices=MONTH_CHOICES)
    year = models.SmallIntegerField()

    class Meta:
        unique_together = ['name','month','year']

    def __str__(self):
        return f"{self.name} - {self.month}"
    
class ContinuousAbsence(models.Model):
    bill_id = models.ForeignKey(MessBill,on_delete=models.CASCADE)
    name = models.ForeignKey(Student,on_delete=models.CASCADE)
    streak = models.IntegerField()
    MONTH_CHOICES = [
        ('January', 'January'),
        ('February', 'February'),
        ('March', 'March'),
        ('April', 'April'),
        ('May', 'May'),
        ('June', 'June'),
        ('July', 'July'),
        ('August', 'August'),
        ('September', 'September'),
        ('October', 'October'),
        ('November', 'November'),
        ('December', 'December'),
    ]
    month = models.CharField(max_length=20,choices=MONTH_CHOICES)
    year = models.IntegerField()

    class Meta:
        unique_together =  ['name','month','year']

    def __str__(self):
        return f"{self.name} for {self.streak} days"