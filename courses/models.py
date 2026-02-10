from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone
from io import BytesIO
from django.core.files.base import ContentFile
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib import colors


class Batch(models.Model):
    """Batch model for grouping students"""
    name = models.CharField(max_length=100, unique=True)
    start_date = models.DateField()
    end_date = models.DateField()
    is_active = models.BooleanField(default=True)
    description = models.TextField(blank=True)
    
    class Meta:
        verbose_name_plural = "Batches"
        ordering = ['-start_date']
    
    def __str__(self):
        return self.name


class StudentProfile(models.Model):
    """Extended profile for students linked to Django User model"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='student_profile')
    student_id = models.CharField(max_length=20, unique=True, verbose_name="Registration No")
    phone = models.CharField(max_length=15)
    batch = models.ForeignKey(Batch, on_delete=models.SET_NULL, null=True, related_name='students')
    date_of_birth = models.DateField(null=True, blank=True)
    address = models.TextField(blank=True)
    profile_picture = models.ImageField(upload_to='profiles/', blank=True, null=True)
    enrollment_date = models.DateField(auto_now_add=True)
    is_active = models.BooleanField(default=True)
    is_verified = models.BooleanField(default=False, help_text="Admin must verify this user before they can access the platform")
    verified_at = models.DateTimeField(null=True, blank=True, help_text="Date and time when admin verified this user")
    enrolled_courses = models.ManyToManyField('Course', related_name='enrolled_students', blank=True, help_text="Courses assigned to this student by admin")
    
    class Meta:
        ordering = ['student_id']
    
    def __str__(self):
        return f"{self.student_id} - {self.user.get_full_name()}"
    
    def get_completed_modules(self):
        """Get count of completed modules"""
        return self.module_completions.filter(completed=True).count()
    



class Course(models.Model):
    """Course model"""
    title = models.CharField(max_length=200)
    description = models.TextField()
    thumbnail = models.ImageField(upload_to='course_thumbnails/', blank=True, null=True)
    duration = models.CharField(max_length=100, default="12 Weeks")
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    batches = models.ManyToManyField(Batch, related_name='courses', blank=True)
    
    class Meta:
        ordering = ['title']
    
    def __str__(self):
        return self.title
    
    @property
    def name(self):
        """Alias for title to support template consistency"""
        return self.title
    
    def get_modules_count(self):
        return self.modules.count()
    



class Module(models.Model):
    """Module model for course content"""
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='modules')
    title = models.CharField(max_length=200)
    description = models.TextField()
    order = models.IntegerField(default=0)
    content = models.TextField(help_text="Main content of the module")
    video_url = models.URLField(blank=True, help_text="YouTube or video URL")
    is_published = models.BooleanField(default=False)
    admin_completed = models.BooleanField(default=False, verbose_name="Mark Completed (Admin)", help_text="If checked, this module is considered completed for ALL students.")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['course', 'order']
        unique_together = ['course', 'order']
    
    def __str__(self):
        return f"{self.course.title} - Module {self.order}: {self.title}"


class ModuleCompletion(models.Model):
    """Track module completion by students"""
    student = models.ForeignKey(StudentProfile, on_delete=models.CASCADE, related_name='module_completions')
    module = models.ForeignKey(Module, on_delete=models.CASCADE, related_name='completions')
    completed = models.BooleanField(default=False)
    completed_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        unique_together = ['student', 'module']
    
    def __str__(self):
        return f"{self.student.student_id} - {self.module.title}"
    
    def mark_complete(self):
        self.completed = True
        self.completed_at = timezone.now()
        self.save()


class Resource(models.Model):
    """PDF and file resources for courses"""
    RESOURCE_TYPES = (
        ('PDF', 'PDF Document'),
        ('DOC', 'Word Document'),
        ('PPT', 'Presentation'),
        ('OTHER', 'Other'),
    )
    
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='resources')
    module = models.ForeignKey(Module, on_delete=models.CASCADE, related_name='resources', null=True, blank=True)
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    file = models.FileField(upload_to='resources/')
    resource_type = models.CharField(max_length=10, choices=RESOURCE_TYPES, default='PDF')
    uploaded_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        ordering = ['-uploaded_at']
    
    def __str__(self):
        return f"{self.course.title} - {self.title}"
    
    def get_file_size(self):
        """Return file size in MB"""
        if self.file:
            return round(self.file.size / (1024 * 1024), 2)
        return 0





class Announcement(models.Model):
    """Announcements for batches"""
    title = models.CharField(max_length=200)
    content = models.TextField()
    batch = models.ForeignKey(Batch, on_delete=models.CASCADE, related_name='announcements', null=True, blank=True)
    is_global = models.BooleanField(default=False, help_text="Show to all students")
    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return self.title


class Bulletin(models.Model):
    """Bengali scrolling bulletin"""
    text = models.CharField(max_length=500, help_text="Bengali text for scrolling bulletin")
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name_plural = "Bulletins"
        ordering = ['-created_at']
    
    def __str__(self):
        return self.text[:50]


class Certificate(models.Model):
    """Student certificates"""
    student = models.ForeignKey(StudentProfile, on_delete=models.CASCADE, related_name='certificates')
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='certificates')
    issue_date = models.DateField(auto_now_add=True)
    certificate_number = models.CharField(max_length=50, unique=True)
    pdf_file = models.FileField(upload_to='certificates/', blank=True, null=True)
    
    class Meta:
        unique_together = ['student', 'course']
        ordering = ['-issue_date']
    
    def __str__(self):
        return f"Certificate - {self.student.student_id} - {self.course.title}"
    
    def generate_certificate_number(self):
        """Generate unique certificate number"""
        from datetime import datetime
        year = datetime.now().year
        return f"NCC-{year}-{self.student.student_id}"

    def generate_pdf(self):
        """Generate and save PDF certificate"""
        if not self.certificate_number:
            self.certificate_number = self.generate_certificate_number()
            self.save()
            
        buffer = BytesIO()
        p = canvas.Canvas(buffer, pagesize=A4)
        width, height = A4
        
        # Certificate design
        # Border
        p.setStrokeColor(colors.HexColor('#1e3a8a'))
        p.setLineWidth(3)
        p.rect(30, 30, width - 60, height - 60, stroke=1, fill=0)
        
        # Inner border
        p.setStrokeColor(colors.HexColor('#3b82f6'))
        p.setLineWidth(1)
        p.rect(40, 40, width - 80, height - 80, stroke=1, fill=0)
        
        # Title
        p.setFont("Helvetica-Bold", 36)
        p.setFillColor(colors.HexColor('#1e3a8a'))
        p.drawCentredString(width / 2, height - 100, "CERTIFICATE OF COMPLETION")
        
        # Subtitle
        p.setFont("Helvetica", 16)
        p.setFillColor(colors.black)
        p.drawCentredString(width / 2, height - 140, "This is to certify that")
        
        # Student name
        p.setFont("Helvetica-Bold", 28)
        p.setFillColor(colors.HexColor('#1e3a8a'))
        student_name = self.student.user.get_full_name() or self.student.user.username
        p.drawCentredString(width / 2, height - 200, student_name.upper())
        
        # Student ID
        p.setFont("Helvetica", 14)
        p.setFillColor(colors.black)
        p.drawCentredString(width / 2, height - 230, f"Student ID: {self.student.student_id}")
        
        # Course completion text
        p.setFont("Helvetica", 16)
        p.drawCentredString(width / 2, height - 280, "has successfully completed the course")
        
        # Course name
        p.setFont("Helvetica-Bold", 22)
        p.setFillColor(colors.HexColor('#1e3a8a'))
        p.drawCentredString(width / 2, height - 320, self.course.title)
        
        # Date
        issue_date_str = self.issue_date.strftime('%B %d, %Y') if self.issue_date else timezone.now().strftime('%B %d, %Y')
        p.setFont("Helvetica", 14)
        p.drawCentredString(width / 2, height - 400, f"Date of Issue: {issue_date_str}")
        
        # Certificate number
        p.setFont("Helvetica", 10)
        p.drawCentredString(width / 2, height - 430, f"Certificate No: {self.certificate_number}")
        
        # Signature line
        p.setFont("Helvetica-Bold", 12)
        p.drawCentredString(width / 2, 150, "___________________________")
        p.drawCentredString(width / 2, 130, "Principal's Signature")
        
        # Institution name
        p.setFont("Helvetica-Bold", 14)
        p.setFillColor(colors.HexColor('#1e3a8a'))
        p.drawCentredString(width / 2, 80, "Premier Medical And Technical Institute")
        
        p.showPage()
        p.save()
        
        # Save PDF to certificate
        buffer.seek(0)
        self.pdf_file.save(
            f'certificate_{self.certificate_number}.pdf',
            ContentFile(buffer.getvalue()),
            save=True
        )
from django.db import models
from django.core.files.storage import default_storage

class SiteConfiguration(models.Model):
    """Singleton model for site configuration"""
    site_name = models.CharField(max_length=200, default="Premier Medical And Technical Institute")
    logo = models.ImageField(upload_to='site_config/', blank=True, null=True, help_text="Upload a PNG logo")
    hero_background = models.ImageField(upload_to='site_config/', blank=True, null=True, help_text="Background image for homepage hero section")
    dashboard_background = models.ImageField(upload_to='site_config/', blank=True, null=True, help_text="Background image for dashboard header")


    whatsapp_number = models.CharField(max_length=20, blank=True, help_text="Enter number with country code (e.g., 88017...)")
    facebook_url = models.URLField(blank=True, help_text="Full Facebook Page URL")
    contact_phone = models.CharField(max_length=20, blank=True, help_text="Main contact phone number")
    
    class Meta:
        verbose_name = "Site Configuration"
        verbose_name_plural = "Site Configuration"
    
    def __str__(self):
        return "Site Configuration"
    
    def save(self, *args, **kwargs):
        # Ensure only one instance exists
        if not self.pk and SiteConfiguration.objects.exists():
            # If we're trying to save a new instance but one exists, update the existing one
            return
        return super(SiteConfiguration, self).save(*args, **kwargs)

    @classmethod
    def get_solo(cls):
        obj, created = cls.objects.get_or_create(pk=1)
        return obj


class BranchPhone(models.Model):
    """Additional phone numbers"""
    branch_name = models.CharField(max_length=100, verbose_name="Label (e.g. Office, Support)")
    phone_number = models.CharField(max_length=20)
    is_active = models.BooleanField(default=True)
    order = models.IntegerField(default=0, help_text="Order to display")

    class Meta:
        ordering = ['order', 'branch_name']
        verbose_name = "Additional Phone Number"
        verbose_name_plural = "Additional Phone Numbers"

    def __str__(self):
        return f"{self.branch_name}: {self.phone_number}"


class GalleryImage(models.Model):
    """Photo gallery model for campus images"""
    image = models.ImageField(upload_to='gallery/', help_text="Upload gallery image")
    caption = models.CharField(max_length=200, blank=True, help_text="Optional caption for the image")
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = "Gallery Image"
        verbose_name_plural = "Gallery Images"
    
    def __str__(self):
        return self.caption if self.caption else f"Gallery Image {self.id}"


class Branch(models.Model):
    """Branches for the institution"""
    name = models.CharField(max_length=200, help_text="Branch Name")
    image = models.ImageField(upload_to='branches/', help_text="Upload branch image")
    phone_number = models.CharField(max_length=20, help_text="Contact Number for this branch")
    address = models.TextField(blank=True, help_text="Branch Address")
    google_map_link = models.URLField(blank=True, help_text="Google Maps Location Link")
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name_plural = "Branches"
        ordering = ['created_at']
    
    def __str__(self):
        return self.name

    @property
    def phone(self):
        """Alias for phone_number to support template consistency"""
        return self.phone_number

    @property
    def location(self):
        """Alias for address to support template consistency"""
        return self.address

    @property
    def contact(self):
        """Alias for phone_number"""
        return self.phone_number

    @property
    def addr(self):
        """Short alias for address"""
        return self.address

