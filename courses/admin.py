from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from django.utils.html import format_html
from django.urls import reverse
from django.utils.safestring import mark_safe
from django.db.models import Count, Q
from .models import (
    Batch, StudentProfile, Course, Module, ModuleCompletion,
    Resource, Announcement, Bulletin, Certificate, SiteConfiguration
)


# ============================================
# CUSTOMIZE ADMIN SITE HEADER & TITLE
# ============================================
admin.site.site_header = "🏥 Premier Medical And Technical Institute - Admin Panel"
admin.site.site_title = "Nursing Admin"
admin.site.index_title = "Welcome to Premier Medical And Technical Institute Administration"


# ============================================
# USER & STUDENT MANAGEMENT
# ============================================

class StudentProfileInline(admin.StackedInline):
    """Student profile information attached to User"""
    model = StudentProfile
    can_delete = False
    verbose_name_plural = '👤 Student Profile Information'
    
    fieldsets = (
        ('📋 Basic Information', {
            'fields': ('student_id', 'phone', 'batch'),
            'description': 'Essential student identification and contact details'
        }),
        ('📝 Additional Details', {
            'fields': ('date_of_birth', 'address', 'profile_picture'),
            'classes': ('collapse',),
            'description': 'Optional personal information'
        }),
        ('✅ Status & Verification', {
            'fields': ('is_active', 'is_verified', 'verified_at', 'enrolled_courses'),
            'description': 'Control student account access, verification status, and course enrollment'
        }),
    )
    readonly_fields = ('verified_at',)
    filter_horizontal = ('enrolled_courses',)


class UserAdmin(BaseUserAdmin):
    """Enhanced User admin with student information"""
    inlines = (StudentProfileInline,)
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff', 'get_student_id', 'get_batch', 'get_status')
    list_filter = ('is_staff', 'is_superuser', 'is_active', 'student_profile__batch')
    
    def get_student_id(self, obj):
        try:
            return obj.student_profile.student_id
        except:
            return '—'
    get_student_id.short_description = '🆔 Registration No'
    
    def get_batch(self, obj):
        try:
            batch = obj.student_profile.batch
            if batch:
                return format_html('<span style="background: #e3f2fd; padding: 3px 8px; border-radius: 4px;">{}</span>', batch.name)
            return '—'
        except:
            return '—'
    get_batch.short_description = '📚 Batch'
    
    def get_status(self, obj):
        try:
            if obj.student_profile.is_active:
                return format_html('<span style="color: #10b981; font-weight: bold;">✓ Active</span>')
            return format_html('<span style="color: #ef4444; font-weight: bold;">✗ Inactive</span>')
        except:
            return '—'
    get_status.short_description = '📊 Status'


admin.site.unregister(User)
admin.site.register(User, UserAdmin)


@admin.register(Batch)
class BatchAdmin(admin.ModelAdmin):
    """Manage student batches and groups"""
    list_display = ('get_batch_name', 'start_date', 'end_date', 'get_status', 'student_count', 'course_count')
    list_filter = ('is_active', 'start_date', 'end_date')
    search_fields = ('name', 'description')
    
    fieldsets = (
        ('📚 Batch Information', {
            'fields': ('name', 'description'),
            'description': 'Enter batch name and description (e.g., "Batch 2024-A")'
        }),
        ('📅 Schedule', {
            'fields': ('start_date', 'end_date'),
            'description': 'Set the batch start and end dates'
        }),
        ('✅ Status', {
            'fields': ('is_active',),
            'description': 'Active batches are visible to students'
        }),
    )
    
    def get_batch_name(self, obj):
        return format_html('<strong style="color: #1e3a8a;">{}</strong>', obj.name)
    get_batch_name.short_description = '📚 Batch Name'
    
    def get_status(self, obj):
        if obj.is_active:
            return format_html('<span style="background: #d1fae5; color: #065f46; padding: 4px 12px; border-radius: 12px; font-weight: 600;">● Active</span>')
        return format_html('<span style="background: #fee2e2; color: #991b1b; padding: 4px 12px; border-radius: 12px; font-weight: 600;">● Inactive</span>')
    get_status.short_description = '📊 Status'
    
    def student_count(self, obj):
        count = obj.students.count()
        return format_html('<span style="background: #dbeafe; padding: 4px 10px; border-radius: 8px; font-weight: 600;">{} students</span>', count)
    student_count.short_description = '👥 Students'
    
    def course_count(self, obj):
        count = obj.courses.count()
        return format_html('<span style="background: #fef3c7; padding: 4px 10px; border-radius: 8px; font-weight: 600;">{} courses</span>', count)
    course_count.short_description = '📖 Courses'


@admin.register(StudentProfile)
class StudentProfileAdmin(admin.ModelAdmin):
    """Manage student profiles and track progress"""
    list_display = ('get_student_id', 'get_full_name', 'get_batch', 'phone', 'enrollment_date', 'get_verification_status', 'get_status', 'view_profile')
    list_filter = ('batch', 'is_active', 'is_verified', 'enrollment_date')
    search_fields = ('student_id', 'user__first_name', 'user__last_name', 'user__email', 'phone')
    readonly_fields = ('enrollment_date', 'verified_at', 'get_progress_summary')
    filter_horizontal = ('enrolled_courses',)
    actions = ['verify_users', 'unverify_users']
    
    fieldsets = (
        ('👤 User Account', {
            'fields': ('user', 'student_id'),
            'description': 'Link to Django user account and assign unique registration number'
        }),
        ('📞 Contact Information', {
            'fields': ('phone', 'address'),
            'description': 'Student contact details'
        }),
        ('📝 Personal Details', {
            'fields': ('date_of_birth', 'profile_picture'),
            'classes': ('collapse',),
            'description': 'Optional personal information'
        }),
        ('📚 Academic Information', {
            'fields': ('batch', 'enrollment_date', 'enrolled_courses', 'is_active'),
            'description': 'Student course enrollment and status'
        }),
        ('✅ Verification Status', {
            'fields': ('is_verified', 'verified_at'),
            'description': 'User verification by admin - users must be verified to login'
        }),
        ('📊 Progress Summary', {
            'fields': ('get_progress_summary',),
            'classes': ('collapse',),
            'description': 'View student learning progress'
        }),
    )
    
    def get_student_id(self, obj):
        return format_html('<strong style="color: #1e3a8a; font-family: monospace;">{}</strong>', obj.student_id)
    get_student_id.short_description = '🆔 Registration No'
    
    def get_full_name(self, obj):
        name = obj.user.get_full_name() or obj.user.username
        return format_html('<strong>{}</strong>', name)
    get_full_name.short_description = '👤 Full Name'
    
    def get_batch(self, obj):
        if obj.batch:
            return format_html('<span style="background: #e3f2fd; padding: 3px 10px; border-radius: 4px; font-weight: 600;">{}</span>', obj.batch.name)
        return '—'
    get_batch.short_description = '📚 Batch'
    
    def get_verification_status(self, obj):
        if obj.is_verified:
            verified_date = obj.verified_at.strftime('%Y-%m-%d') if obj.verified_at else 'N/A'
            return format_html('<span style="background: #d1fae5; color: #065f46; padding: 4px 12px; border-radius: 12px; font-weight: 600;">✓ Verified</span><br><small style="color: #6b7280;">{}</small>', verified_date)
        return format_html('<span style="background: #fef3c7; color: #92400e; padding: 4px 12px; border-radius: 12px; font-weight: 600;">⏳ Pending</span>')
    get_verification_status.short_description = '✅ Verification'
    
    def get_status(self, obj):
        if obj.is_active:
            return format_html('<span style="color: #10b981; font-weight: bold;">✓ Active</span>')
        return format_html('<span style="color: #ef4444; font-weight: bold;">✗ Inactive</span>')
    get_status.short_description = '📊 Status'
    
    def get_progress_summary(self, obj):
        completed_modules = obj.get_completed_modules()
        
        html = f'''
        <div style="background: #f9fafb; padding: 15px; border-radius: 8px; border-left: 4px solid #3b82f6;">
            <p style="margin: 5px 0;"><strong>📚 Completed Modules:</strong> <span style="color: #10b981; font-weight: bold;">{completed_modules}</span></p>
        </div>
        '''
        return format_html(html)
    get_progress_summary.short_description = '📊 Learning Progress'
    
    def view_profile(self, obj):
        url = reverse('student_profile', args=[obj.id])
        return format_html('<a href="{}" target="_blank" style="background: #3b82f6; color: white; padding: 5px 12px; border-radius: 4px; text-decoration: none;">👁️ View Profile</a>', url)
    view_profile.short_description = '🔗 Actions'
    
    def verify_users(self, request, queryset):
        """Admin action to verify selected users"""
        from django.utils import timezone
        updated = queryset.update(is_verified=True, verified_at=timezone.now())
        self.message_user(request, f'{updated} user(s) have been verified successfully.')
    verify_users.short_description = '✅ Verify selected users'
    
    def unverify_users(self, request, queryset):
        """Admin action to unverify selected users"""
        updated = queryset.update(is_verified=False, verified_at=None)
        self.message_user(request, f'{updated} user(s) have been unverified.')
    unverify_users.short_description = '❌ Unverify selected users'


# ============================================
# COURSE & MODULE MANAGEMENT
# ============================================

class ModuleInline(admin.TabularInline):
    """Add modules directly within course"""
    model = Module
    extra = 1
    fields = ('order', 'title', 'is_published', 'admin_completed')
    ordering = ('order',)
    verbose_name = "📖 Module"
    verbose_name_plural = "📖 Course Modules (Add modules here)"


class ResourceInline(admin.TabularInline):
    """Add resources directly within course"""
    model = Resource
    extra = 1
    fields = ('module', 'title', 'resource_type', 'file', 'is_active')
    verbose_name = "📄 Resource"
    verbose_name_plural = "📄 Course Resources (PDFs, Documents)"





@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    """Manage courses with modules, exams, and resources"""
    list_display = ('get_course_title', 'duration', 'get_status', 'modules_count', 'resources_count')
    list_filter = ('is_active', 'created_at', 'batches')
    search_fields = ('title', 'description')
    filter_horizontal = ('batches',)
    inlines = [ModuleInline, ResourceInline]
    
    fieldsets = (
        ('📚 Course Information', {
            'fields': ('title', 'description', 'thumbnail'),
            'description': 'Enter course details and upload a thumbnail image'
        }),
        ('⚙️ Course Settings', {
            'fields': ('duration', 'is_active'),
            'description': 'Configure course duration and visibility'
        }),
        ('👥 Assign to Batches', {
            'fields': ('batches',),
            'description': 'Select which batches can access this course'
        }),
    )
    
    
    def get_course_title(self, obj):
        return format_html('<strong style="color: #1e3a8a;">{}</strong>', obj.title)
    get_course_title.short_description = '📚 Course Title'
    
    def get_status(self, obj):
        if obj.is_active:
            return format_html('<span style="background: #d1fae5; color: #065f46; padding: 4px 12px; border-radius: 12px; font-weight: 600;">● Active</span>')
        return format_html('<span style="background: #fee2e2; color: #991b1b; padding: 4px 12px; border-radius: 12px; font-weight: 600;">● Inactive</span>')
    get_status.short_description = '📊 Status'
    
    def modules_count(self, obj):
        count = obj.modules.count()
        color = '#10b981' if count > 0 else '#9ca3af'
        return format_html('<span style="color: {}; font-weight: bold;">📖 {}</span>', color, count)
    modules_count.short_description = '📖 Modules'
    

    
    def resources_count(self, obj):
        count = obj.resources.count()
        color = '#3b82f6' if count > 0 else '#9ca3af'
        return format_html('<span style="color: {}; font-weight: bold;">📄 {}</span>', color, count)
    resources_count.short_description = '📄 Resources'


@admin.register(Module)
class ModuleAdmin(admin.ModelAdmin):
    """Manage individual course modules"""
    list_display = ('get_module_name', 'get_course', 'order', 'get_published', 'get_completed', 'created_at')
    list_filter = ('course', 'is_published', 'admin_completed', 'created_at')
    search_fields = ('title', 'description', 'course__title')
    list_editable = ('order',)
    
    fieldsets = (
        ('📖 Module Information', {
            'fields': ('course', 'title', 'order', 'description'),
            'description': 'Basic module details and ordering'
        }),
        ('📝 Module Content', {
            'fields': ('content', 'video_url'),
            'description': 'Add text content and optional video link (YouTube, Vimeo, etc.)'
        }),
        ('⚙️ Publishing & Status', {
            'fields': ('is_published', 'admin_completed'),
            'description': '✅ Published: Visible to students | ✅ Completed: Marks module as done for all students'
        }),
    )
    
    def get_module_name(self, obj):
        return format_html('<strong style="color: #1e3a8a;">Module {}: {}</strong>', obj.order, obj.title)
    get_module_name.short_description = '📖 Module'
    
    def get_course(self, obj):
        return format_html('<span style="background: #fef3c7; padding: 3px 8px; border-radius: 4px;">{}</span>', obj.course.title)
    get_course.short_description = '📚 Course'
    
    def get_published(self, obj):
        if obj.is_published:
            return format_html('<span style="color: #10b981; font-weight: bold;">✓ Published</span>')
        return format_html('<span style="color: #9ca3af;">✗ Draft</span>')
    get_published.short_description = '📊 Status'
    
    def get_completed(self, obj):
        if obj.admin_completed:
            return format_html('<span style="color: #10b981; font-weight: bold;">✓ Completed</span>')
        return format_html('<span style="color: #9ca3af;">○ In Progress</span>')
    get_completed.short_description = '✅ Completion'


@admin.register(Resource)
class ResourceAdmin(admin.ModelAdmin):
    """Manage course resources (PDFs, documents, etc.)"""
    list_display = ('get_title', 'get_course', 'get_module', 'resource_type', 'file_size', 'uploaded_at', 'get_status')
    list_filter = ('course', 'module', 'resource_type', 'is_active', 'uploaded_at')
    search_fields = ('title', 'description', 'course__title', 'module__title')
    
    fieldsets = (
        ('📄 Resource Information', {
            'fields': ('course', 'module', 'title', 'description'),
            'description': 'Assign resource to a course and optionally to a specific module'
        }),
        ('📎 File Upload', {
            'fields': ('file', 'resource_type'),
            'description': 'Upload the file and select its type'
        }),
        ('⚙️ Status', {
            'fields': ('is_active',),
            'description': 'Only active resources are visible to students'
        }),
    )
    
    def get_title(self, obj):
        return format_html('<strong style="color: #1e3a8a;">{}</strong>', obj.title)
    get_title.short_description = '📄 Title'
    
    def get_course(self, obj):
        return format_html('<span style="background: #fef3c7; padding: 3px 8px; border-radius: 4px;">{}</span>', obj.course.title)
    get_course.short_description = '📚 Course'
    
    def get_module(self, obj):
        if obj.module:
            return format_html('<span style="background: #e3f2fd; padding: 3px 8px; border-radius: 4px;">Module {}</span>', obj.module.order)
        return '—'
    get_module.short_description = '📖 Module'
    
    def file_size(self, obj):
        size = obj.get_file_size()
        if size > 0:
            return format_html('<span style="color: #6b7280; font-family: monospace;">{} MB</span>', size)
        return '—'
    file_size.short_description = '💾 Size'
    
    def get_status(self, obj):
        if obj.is_active:
            return format_html('<span style="color: #10b981; font-weight: bold;">✓ Active</span>')
        return format_html('<span style="color: #ef4444; font-weight: bold;">✗ Inactive</span>')
    get_status.short_description = '📊 Status'





# ============================================
# ANNOUNCEMENTS & COMMUNICATIONS
# ============================================

@admin.register(Announcement)
class AnnouncementAdmin(admin.ModelAdmin):
    """Manage announcements for students"""
    list_display = ('get_title', 'get_target', 'created_at', 'get_status')
    list_filter = ('batch', 'is_global', 'is_active', 'created_at')
    search_fields = ('title', 'content')
    
    fieldsets = (
        ('📢 Announcement Content', {
            'fields': ('title', 'content'),
            'description': 'Enter announcement title and message'
        }),
        ('🎯 Target Audience', {
            'fields': ('batch', 'is_global'),
            'description': '✅ Global: Show to all students | OR select specific batch'
        }),
        ('⚙️ Status', {
            'fields': ('is_active',),
            'description': 'Only active announcements are visible'
        }),
    )
    
    def get_title(self, obj):
        return format_html('<strong style="color: #1e3a8a;">📢 {}</strong>', obj.title)
    get_title.short_description = '📢 Title'
    
    def get_target(self, obj):
        if obj.is_global:
            return format_html('<span style="background: #fef3c7; color: #92400e; padding: 4px 12px; border-radius: 8px; font-weight: 600;">🌐 All Students</span>')
        elif obj.batch:
            return format_html('<span style="background: #e3f2fd; padding: 4px 12px; border-radius: 8px; font-weight: 600;">📚 {}</span>', obj.batch.name)
        return '—'
    get_target.short_description = '🎯 Target'
    
    def get_status(self, obj):
        if obj.is_active:
            return format_html('<span style="color: #10b981; font-weight: bold;">✓ Active</span>')
        return format_html('<span style="color: #ef4444; font-weight: bold;">✗ Inactive</span>')
    get_status.short_description = '📊 Status'


@admin.register(Bulletin)
class BulletinAdmin(admin.ModelAdmin):
    """Manage scrolling bulletin bar"""
    list_display = ('get_text_preview', 'get_status', 'created_at', 'updated_at')
    list_filter = ('is_active', 'created_at')
    search_fields = ('text',)
    
    fieldsets = (
        ('📰 Bulletin Content', {
            'fields': ('text',),
            'description': '📝 Enter text for the scrolling bulletin bar (supports Bengali and English)'
        }),
        ('⚙️ Status', {
            'fields': ('is_active',),
            'description': 'Only one active bulletin will be displayed at a time'
        }),
    )
    
    def get_text_preview(self, obj):
        preview = obj.text[:80] + '...' if len(obj.text) > 80 else obj.text
        return format_html('<span style="color: #1e3a8a;">{}</span>', preview)
    get_text_preview.short_description = '📰 Bulletin Text'
    
    def get_status(self, obj):
        if obj.is_active:
            return format_html('<span style="background: #d1fae5; color: #065f46; padding: 4px 12px; border-radius: 12px; font-weight: 600;">● Active</span>')
        return format_html('<span style="background: #fee2e2; color: #991b1b; padding: 4px 12px; border-radius: 12px; font-weight: 600;">● Inactive</span>')
    get_status.short_description = '📊 Status'


# ============================================
# CERTIFICATES
# ============================================

@admin.register(Certificate)
class CertificateAdmin(admin.ModelAdmin):
    """Manage student certificates"""
    list_display = ('get_certificate_number', 'get_student', 'get_course', 'issue_date', 'download_link')
    list_filter = ('course', 'issue_date')
    search_fields = ('certificate_number', 'student__student_id', 'student__user__first_name', 'student__user__last_name', 'course__title')
    readonly_fields = ('issue_date', 'certificate_number')
    
    actions = ['generate_certificate_pdf']
    
    fieldsets = (
        ('🎓 Certificate Information', {
            'fields': ('student', 'course', 'certificate_number', 'issue_date'),
            'description': 'Certificate details (number is auto-generated)'
        }),
        ('📄 PDF File', {
            'fields': ('pdf_file',),
            'description': 'Upload the generated certificate PDF'
        }),
    )
    
    def get_certificate_number(self, obj):
        return format_html('<strong style="background: #dbeafe; padding: 4px 10px; border-radius: 4px; font-family: monospace; color: #1e3a8a;">{}</strong>', obj.certificate_number)
    get_certificate_number.short_description = '🎓 Certificate #'
    
    def get_student(self, obj):
        return format_html('<strong>{}</strong> ({})', obj.student.user.get_full_name(), obj.student.student_id)
    get_student.short_description = '👤 Student'
    
    def get_course(self, obj):
        return format_html('<span style="background: #fef3c7; padding: 3px 8px; border-radius: 4px;">{}</span>', obj.course.title)
    get_course.short_description = '📚 Course'
    
    def download_link(self, obj):
        if obj.pdf_file:
            return format_html('<a href="{}" target="_blank" style="background: #10b981; color: white; padding: 5px 12px; border-radius: 4px; text-decoration: none;">📥 Download PDF</a>', obj.pdf_file.url)
        return format_html('<span style="color: #9ca3af;">No file</span>')
    download_link.short_description = '📥 Download'
    
    def save_model(self, request, obj, form, change):
        if not obj.certificate_number:
            obj.certificate_number = obj.generate_certificate_number()
        super().save_model(request, obj, form, change)
        
        # Auto-generate PDF if missing (admin convenience)
        if not obj.pdf_file:
            obj.generate_pdf()
            
    def generate_certificate_pdf(self, request, queryset):
        """Action to generate PDFs for selected certificates"""
        count = 0
        for certificate in queryset:
            if not certificate.pdf_file:
                certificate.generate_pdf()
                count += 1
        self.message_user(request, f'{count} certificate PDF(s) generated successfully.')
    generate_certificate_pdf.short_description = '📄 Generate PDF for selected certificates'


# ============================================
# SITE CONFIGURATION
# ============================================


@admin.register(SiteConfiguration)
class SiteConfigurationAdmin(admin.ModelAdmin):
    """Configure site appearance and branding"""
    
    fieldsets = (
        ('🏥 General Settings', {
            'fields': ('site_name', 'logo'),
            'description': 'Site name and logo (appears in header)'
        }),
        ('📞 Contact Information', {
            'fields': ('contact_phone', 'whatsapp_number', 'facebook_url'),
            'description': 'Social media and contact links'
        }),
        ('🎨 Homepage Hero Section', {
            'fields': ('hero_background',),
            'description': 'Customize the homepage banner section'
        }),
        ('📊 Dashboard Settings', {
            'fields': ('dashboard_background',),
            'description': 'Background image for student dashboard'
        }),
    )

from .models import BranchPhone

@admin.register(BranchPhone)
class BranchPhoneAdmin(admin.ModelAdmin):
    """Manage branch phone numbers"""
    list_display = ('branch_name', 'phone_number', 'is_active', 'order')
    list_editable = ('phone_number', 'is_active', 'order')
    list_filter = ('is_active',)
    search_fields = ('branch_name', 'phone_number')
    
    
    # Removed Singleton restrictions since BranchPhone is a list
    pass


# ============================================
# GALLERY MANAGEMENT
# ============================================

from .models import GalleryImage

@admin.register(GalleryImage)
class GalleryImageAdmin(admin.ModelAdmin):
    """Manage photo gallery images"""
    list_display = ('get_thumbnail', 'caption', 'created_at')
    ordering = ('-created_at',)
    search_fields = ('caption',)
    
    def get_thumbnail(self, obj):
        if obj.image:
            return format_html('<img src="{}" style="width: 60px; height: 60px; object-fit: cover; border-radius: 4px;" />', obj.image.url)
        return "No Image"
    get_thumbnail.short_description = '📷 Thumbnail'



# ============================================
# BRANCH MANAGEMENT
# ============================================

from .models import Branch

@admin.register(Branch)
class BranchAdmin(admin.ModelAdmin):
    """Manage institution branches"""
    list_display = ('get_thumbnail', 'name', 'phone_number', 'is_active', 'created_at')
    list_filter = ('is_active',)
    search_fields = ('name', 'phone_number', 'address')
    
    fieldsets = (
        ('🏥 Branch Details', {
            'fields': ('name', 'image', 'phone_number'),
            'description': 'Basic branch information'
        }),
        ('📍 Location', {
            'fields': ('address', 'google_map_link'),
            'description': 'Address and map link'
        }),
        ('⚙️ Status', {
            'fields': ('is_active',),
            'description': 'Active branches are visible on the dashboard'
        }),
    )
    
    def get_thumbnail(self, obj):
        if obj.image:
            return format_html('<img src="{}" style="width: 60px; height: 60px; object-fit: cover; border-radius: 4px;" />', obj.image.url)
        return "No Image"
    get_thumbnail.short_description = '📷 Thumbnail'

