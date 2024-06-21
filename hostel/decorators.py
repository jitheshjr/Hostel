from django.contrib.auth.decorators import user_passes_test

def group_required(group_name):
    def in_group(user):
        if user.is_authenticated:
            return user.groups.filter(name=group_name).exists()
        return False
    return user_passes_test(in_group)