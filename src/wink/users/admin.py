from django import forms
from django.contrib import admin
from django.contrib.auth.models import Group
from django.contrib.auth.admin import UserAdmin as ContribUserAdmin
from django.contrib.auth.forms import ReadOnlyPasswordHashField

from users.models import User


class UserCreationForm(forms.ModelForm):
    password1 = forms.CharField(label='Password', widget=forms.PasswordInput)
    password2 = forms.CharField(label='Password confirmation', widget=forms.PasswordInput)

    class Meta:
        model = User
        exclude = ()

    def clean_password2(self):
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("Passwords don't match")
        return password2

    def save(self, commit=True):
        user = super(UserCreationForm, self).save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        if commit:
            user.save()
        return user


class UserChangeForm(forms.ModelForm):
    """A form for updating users. Includes all the fields on
    the user, but replaces the password field with admin's
    password hash display field.
    """
    password = ReadOnlyPasswordHashField()

    class Meta:
        model = User
        exclude = ()

    def clean_password(self):
        # Regardless of what the user provides, return the initial value.
        # This is done here, rather than on the field, because the
        # field does not have access to the initial value
        return self.initial["password"]


class UserAdmin(ContribUserAdmin):
    form = UserChangeForm
    add_form = UserCreationForm

    list_display = ('email', 'handle', 'display_name', 'date_of_birth', 'is_admin')
    list_filter = ('is_admin',)

    search_fields = ('email', 'handle', 'display_name')
    ordering = ('email',)
    filter_horizontal = ()
    fieldsets = ()


admin.site.register(User, UserAdmin)
admin.site.unregister(Group)