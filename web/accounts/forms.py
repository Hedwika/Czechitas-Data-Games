from django.contrib.auth import get_user_model
from django import forms

#check for unique e-mail and username

User = get_user_model()

class RegisterForm(forms.Form):
    username = forms.CharField(
        label='Uživatelské jméno',
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
            }
        )
    )
    email = forms.EmailField(
        label='E-mailová adresa',
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
            }
        )
    )
    password1 = forms.CharField(
        label='Heslo',
        widget=forms.PasswordInput(
            attrs={
                "class": "form-control",
                "id": "user-password"
            }
        )
    )

    password2 = forms.CharField(
        label='Heslo znovu',
        widget=forms.PasswordInput(
            attrs={
                "class": "form-control",
                "id": "user-confirm-password"
            }
        )
    )

    def clean_username(self):
        username = self.cleaned_data.get("username")
        qs = User.objects.filter(username__iexact=username)
        if qs.exists():
            raise forms.ValidationError("Neplatné uživatelské jméno, vyberte si prosím jiné.")
        return username

    def clean_email(self):
        email = self.cleaned_data.get("email")
        qs = User.objects.filter(email__iexact=email)
        if qs.exists():
            raise forms.ValidationError("Tento e-mail už se používá, vyberte si prosím jiný.")
        return email

    def clean(self):
        cleaned_data = super(RegisterForm, self).clean()
        password = cleaned_data.get("password1")
        confirm_password = cleaned_data.get("password2")

        if password != confirm_password:
            raise forms.ValidationError("Hesla se neshodují, zkuste to prosím znovu.")

class LoginForm(forms.Form):
    username = forms.CharField(
        label='Uživatelské jméno',
        widget=forms.TextInput(
            attrs={
                "class": "form-control"
            }
        )
    )
    password = forms.CharField(
        label='Heslo',
        widget=forms.PasswordInput(
            attrs={
                "class": "form-control",
                "id": "user-password"
            }
        )
    )

    def clean_username(self):
        username = self.cleaned_data.get("username")
        qs = User.objects.filter(username=username)
        # TODO: return to the row after migration to PostgreSQL
        #qs = User.objects.filter(username_iexact=username) #UzivatelskeJmeno == uzivatelskejmeno
        if not qs.exists():
            raise forms.ValidationError("Neplatný uživatel.")
        return username

