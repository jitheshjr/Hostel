from django.contrib.auth.models import User

def group_processor(request):
    if request.user.is_authenticated:
        is_admin_group = request.user.groups.filter(name='admin').exists()
        is_guest_group = request.user.groups.filter(name='guest').exists()  # Adjust as needed
    else:
        is_admin_group = False
        is_guest_group = False

    return {
        'is_admin_group': is_admin_group,
        'is_guest_group': is_guest_group,
    }