from django.contrib.auth.models import User

def group_processor(request):
    if request.user.is_authenticated:
        is_warden_group = request.user.groups.filter(name='warden').exists()
        is_secretary_group = request.user.groups.filter(name='secretary').exists()  # Adjust as needed
    else:
        is_warden_group = False
        is_secretary_group = False

    return {
        'is_warden_group': is_warden_group,
        'is_secretary_group': is_secretary_group,
    }