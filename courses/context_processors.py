from .models import Bulletin


def bulletin_processor(request):
    """Context processor to add active bulletin to all templates"""
    active_bulletin = Bulletin.objects.filter(is_active=True).first()
    
    # Get Site Config
    from .models import SiteConfiguration, BranchPhone
    try:
        site_config = SiteConfiguration.get_solo()
    except:
        site_config = None
    
    # Get Branch Phone Numbers
    branch_phones = BranchPhone.objects.filter(is_active=True).order_by('order')
        
    return {
        'active_bulletin': active_bulletin,
        'site_config': site_config,
        'branch_phones': branch_phones
    }
