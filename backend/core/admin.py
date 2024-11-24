from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

# We won't be implementing translation; just future proofing:
from django.utils.translation import gettext_lazy as _

from core import models


class UserAdmin(BaseUserAdmin):
    """Define Admin Page for Users."""
    ordering = ['id']
    list_display = ['email', 'name']  # test_user_listed_on_admin_page()

    # Change User page: /admin/core/user/1/change/
    # N.B. The value of 'fieldsets[i]' must be a list or tuple.
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        (_('Permissions'), {'fields': ('is_active', 'is_staff', 'is_superuser',)}),
        (_('Important Dates'), {'fields': ('last_login',)})
    )

    readonly_fields = ['last_login']

    # Add User Page: /admin/core/user/add/
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': (
                'email', 'password1', 'password2', 'name',
                'is_active', 'is_staff', 'is_superuser'
            )
        }),  # N.B. if not `,` here => TypeError: cannot unpack non-iterable NoneType object
        # Note >>> x, z = (1,), (1); type(x) <tuple>, type(z) <int>
    )


# Register your models here.
# Also pass our custom `UserAdmin` to register our desired changes as well.
admin.site.register(models.User, UserAdmin)
admin.site.register(models.Recipe)
admin.site.register(models.Tag)
