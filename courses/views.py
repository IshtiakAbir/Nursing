from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.contrib import messages
from django.http import HttpResponse, FileResponse, Http404
from django.utils import timezone
from django.db.models import Q, Count, Avg
from io import BytesIO
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.units import inch
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from datetime import datetime

from .models import (
    StudentProfile, Course, Module, ModuleCompletion,
    Resource, Announcement, Bulletin, Certificate, Batch,
    GalleryImage, Branch
)
from .forms import StudentRegistrationForm


def home(request):
    """Public home page"""
    context = {
        'active_courses': Course.objects.filter(is_active=True)[:6],
        'latest_gallery_images': GalleryImage.objects.all()[:6],
        'branches': Branch.objects.filter(is_active=True),
    }
    return render(request, 'home.html', context)


def gallery(request):
    """Public gallery page"""
    gallery_images = GalleryImage.objects.all()
    return render(request, 'gallery.html', {'gallery_images': gallery_images})


def contact(request):
    """Contact Us page"""
    return render(request, 'contact.html')


def student_login(request):
    """Student login view"""
    if request.user.is_authenticated:
        return redirect('dashboard')
    
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                # Check if user has student profile
                if hasattr(user, 'student_profile'):
                    # Check if user is verified
                    if not user.student_profile.is_verified:
                        messages.warning(request, 'Your account is pending verification by the administrator. Please wait for approval.')
                        return redirect('login')
                    
                    login(request, user)
                    messages.success(request, f'Welcome back, {user.get_full_name()}!')
                    return redirect('dashboard')
                else:
                    messages.error(request, 'This account is not a student account.')
            else:
                messages.error(request, 'Invalid username or password.')
        else:
            messages.error(request, 'Invalid username or password.')
    else:
        form = AuthenticationForm()
    
    return render(request, 'login.html', {'form': form})


def student_register(request):
    """Student registration view"""
    if request.user.is_authenticated:
        return redirect('dashboard')
    
    if request.method == 'POST':
        form = StudentRegistrationForm(request.POST, request.FILES)
        if form.is_valid():
            user = form.save()
            messages.success(request, 'Registration successful! Your account is pending verification by the administrator. You will be able to login once your account is approved.')
            return redirect('login')
    else:
        form = StudentRegistrationForm()
    
    return render(request, 'register.html', {'form': form})


def student_logout(request):
    """Student logout view"""
    logout(request)
    messages.info(request, 'You have been logged out successfully.')
    return redirect('home')


@login_required
def dashboard(request):
    """Student dashboard"""
    try:
        student = request.user.student_profile
    except StudentProfile.DoesNotExist:
        messages.error(request, 'Student profile not found.')
        return redirect('home')
    
    # Get student's enrolled courses (assigned by admin)
    enrolled_courses = student.enrolled_courses.filter(
        is_active=True
    ).prefetch_related('modules')
    
    # Get recent announcements
    announcements = Announcement.objects.filter(
        Q(batch=student.batch) | Q(is_global=True),
        is_active=True
    ).order_by('-created_at')[:5]
    
    # Get completed modules count (Admin completed modules in enrolled courses)
    completed_modules = Module.objects.filter(
        course__in=enrolled_courses,
        admin_completed=True
    ).count()
    
    # Get all branches
    branches = Branch.objects.all()
    
    # Get recent gallery images
    gallery_images = GalleryImage.objects.all().order_by('-created_at')[:4]
    
    context = {
        'student': student,
        'courses': enrolled_courses,
        'announcements': announcements,
        'completed_modules': completed_modules,
        'branches': branches,
        'gallery_images': gallery_images,
    }
    return render(request, 'dashboard.html', context)


def course_detail(request, course_id):
    """Course detail view - Publicly viewable for overview"""
    course = get_object_or_404(Course, id=course_id, is_active=True)
    student = None
    
    if request.user.is_authenticated:
        try:
            student = request.user.student_profile
        except StudentProfile.DoesNotExist:
            pass

    # Access control: Only show content if public or student is in a batch for this course
    # However, user wants it public, so we let everyone see the list.
    # We only restrict the 'enrolled' status/completions if student is logged in.
    
    # Get modules
    modules = course.modules.filter(is_published=True).order_by('order')
    
    # Get module completion status (only for logged-in students)
    completed_module_ids = []
    if student:
        completed_module_ids = modules.filter(admin_completed=True).values_list('id', flat=True)
    
    # Get general resources
    resources = course.resources.filter(is_active=True).order_by('-uploaded_at')
    
    context = {
        'course': course,
        'modules': modules,
        'completed_module_ids': list(completed_module_ids),
        'resources': resources,
        'is_enrolled': student.enrolled_courses.filter(id=course_id).exists() if student else False,
        'certificate': Certificate.objects.filter(student=student, course=course).first() if student else None,
    }
    return render(request, 'course_detail.html', context)


@login_required
def module_detail(request, module_id):
    """Module detail view"""
    try:
        student = request.user.student_profile
    except StudentProfile.DoesNotExist:
        messages.error(request, 'Student profile not found.')
        return redirect('home')
    
    module = get_object_or_404(Module, id=module_id, is_published=True)
    
    # Check if student has access (must be enrolled in the course)
    if not student.enrolled_courses.filter(id=module.course.id).exists():
        messages.error(request, 'You do not have access to this module.')
        return redirect('dashboard')
    
    # Get or create completion record
    completion, created = ModuleCompletion.objects.get_or_create(
        student=student,
        module=module
    )
    
    
    # Track student viewed the module (optional implicit completion tracking if needed later)
    # But for now, we only use admin_completed for status.
    # We can keep the record for "last viewed" purposes if we add a field, but current model has completed_at.
    # Let's just create the record so we know they visited, but ignoring its 'completed' field for logic.

    
    
    # Fetch resources
    resources = module.resources.filter(is_active=True)
    
    context = {
        'module': module,
        'completion': completion,
        'resources': resources,
    }
    return render(request, 'module_detail.html', context)


@login_required
def download_resource(request, resource_id):
    """Download resource file - restricted to enrolled students"""
    try:
        student = request.user.student_profile
    except StudentProfile.DoesNotExist:
        messages.error(request, 'Student profile not found.')
        return redirect('home')
    
    resource = get_object_or_404(Resource, id=resource_id, is_active=True)
    
    # Check if student has access to this course (must be enrolled)
    if not student.enrolled_courses.filter(id=resource.course.id).exists():
        raise Http404("You do not have permission to download this resource.")
    
    # Serve the file
    try:
        return FileResponse(resource.file.open('rb'), as_attachment=True, filename=resource.file.name.split('/')[-1])
    except Exception as e:
        messages.error(request, 'Error downloading file.')
        return redirect('course_detail', course_id=resource.course.id)





@login_required
def student_profile(request, profile_id=None):
    """Student profile view"""
    if profile_id:
        # Admin viewing student profile
        if not request.user.is_staff:
            messages.error(request, 'Permission denied.')
            return redirect('dashboard')
        student = get_object_or_404(StudentProfile, id=profile_id)
    else:
        # Student viewing own profile
        try:
            student = request.user.student_profile
        except StudentProfile.DoesNotExist:
            messages.error(request, 'Student profile not found.')
            return redirect('home')
    
    # Get student's enrolled courses
    enrolled_courses = student.enrolled_courses.filter(is_active=True)

    # Get statistics
    total_modules = Module.objects.filter(
        course__in=enrolled_courses,
        is_published=True
    ).count()
    
    completed_modules = ModuleCompletion.objects.filter(
        student=student,
        module__course__in=enrolled_courses,
        completed=True
    ).count()
    
    # Get certificates
    certificates = Certificate.objects.filter(student=student).order_by('-issue_date')
    
    context = {
        'student': student,
        'total_modules': total_modules,
        'completed_modules': completed_modules,
        'certificates': certificates,
    }
    return render(request, 'student_profile.html', context)


@login_required
def generate_certificate(request, course_id):
    """Generate PDF certificate for completed course"""
    try:
        student = request.user.student_profile
    except StudentProfile.DoesNotExist:
        messages.error(request, 'Student profile not found.')
        return redirect('home')
    
    course = get_object_or_404(Course, id=course_id)
    
    # Check if student has access (must be enrolled)
    if not student.enrolled_courses.filter(id=course.id).exists():
        messages.error(request, 'You do not have access to this course.')
        return redirect('dashboard')
    
    # Check if all modules are completed
    total_modules = course.modules.filter(is_published=True).count()
    completed_modules = ModuleCompletion.objects.filter(
        student=student,
        module__course=course,
        completed=True
    ).count()
    
    if completed_modules < total_modules:
        messages.error(request, 'You must complete all modules before getting a certificate.')
        return redirect('course_detail', course_id=course.id)
    

    
    # Get or create certificate
    certificate, created = Certificate.objects.get_or_create(
        student=student,
        course=course
    )
    
    if not certificate.certificate_number:
        certificate.certificate_number = certificate.generate_certificate_number()
        certificate.save()
    
    # Generate PDF
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
    p.drawCentredString(width / 2, height - 200, student.user.get_full_name().upper())
    
    # Student ID
    p.setFont("Helvetica", 14)
    p.setFillColor(colors.black)
    p.drawCentredString(width / 2, height - 230, f"Registration No: {student.student_id}")
    
    # Course completion text
    p.setFont("Helvetica", 16)
    p.drawCentredString(width / 2, height - 280, "has successfully completed the course")
    
    # Course name
    p.setFont("Helvetica-Bold", 22)
    p.setFillColor(colors.HexColor('#1e3a8a'))
    p.drawCentredString(width / 2, height - 320, course.title)
    
    # Date
    p.setFont("Helvetica", 14)
    p.drawCentredString(width / 2, height - 400, f"Date of Issue: {certificate.issue_date.strftime('%B %d, %Y')}")
    
    # Certificate number
    p.setFont("Helvetica", 10)
    p.drawCentredString(width / 2, height - 430, f"Certificate No: {certificate.certificate_number}")
    
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
    certificate.pdf_file.save(
        f'certificate_{certificate.certificate_number}.pdf',
        buffer,
        save=True
    )
    
    # Return PDF
    buffer.seek(0)
    response = HttpResponse(buffer.getvalue(), content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="certificate_{certificate.certificate_number}.pdf"'
    
    messages.success(request, 'Certificate generated successfully!')
    return response


@login_required
def announcements(request):
    """View all announcements"""
    try:
        student = request.user.student_profile
    except StudentProfile.DoesNotExist:
        messages.error(request, 'Student profile not found.')
        return redirect('home')
    
    announcements = Announcement.objects.filter(
        Q(batch=student.batch) | Q(is_global=True),
        is_active=True
    ).order_by('-created_at')
    
    context = {
        'announcements': announcements,
    }
    return render(request, 'announcements.html', context)


def branches(request):
    """View all branches"""
    branches = Branch.objects.filter(is_active=True).order_by('created_at')
    return render(request, 'branches.html', {'branches': branches})
def course_list(request):
    """View all active courses"""
    courses = Course.objects.filter(is_active=True).prefetch_related('modules', 'resources')
    
    student = None
    if request.user.is_authenticated:
        try:
            student = request.user.student_profile
        except StudentProfile.DoesNotExist:
            pass
    
    return render(request, 'course_list.html', {
        'courses': courses,
        'student': student
    })

