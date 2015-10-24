from django.contrib.admin.views.decorators import \
    staff_member_required as django_staff_member_required


def staff_member_required(view_func):
    return django_staff_member_required(view_func, login_url='login')
