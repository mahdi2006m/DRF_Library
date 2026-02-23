from django import forms
from django.core.validators import MinValueValidator, EmailValidator, RegexValidator
from .models import *
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm, PasswordChangeForm, PasswordResetForm, \
    SetPasswordForm
from django.db import transaction
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
import datetime


class BookForm(forms.ModelForm):
    title = forms.CharField(
        max_length=200,
        required=True,
        label='Title',
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter title'})
    )

    author = forms.ModelMultipleChoiceField(
        queryset=Author.objects.all(),
        required=True,
        label='Author/Authors',
        widget=forms.CheckboxSelectMultiple(attrs={'class': 'form-check'})
    )

    publisher = forms.ModelChoiceField(
        queryset=Publisher.objects.all(),
        required=False,
        label='Publisher',
        widget=forms.Select(attrs={'class': 'form-control'})
    )

    category = forms.ModelChoiceField(
        queryset=Category.objects.all(),
        required=False,
        label='Category',
        widget=forms.Select(attrs={'class': 'form-control'})
    )

    isbn = forms.CharField(
        max_length=20,
        required=True,
        label='ISBN',
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter ISBN'})
    )

    publication_year = forms.IntegerField(
        required=False,
        label='Publication Year',
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': 'Publication Year'
        }),
        validators=[MinValueValidator(1)]
    )

    total_copies = forms.IntegerField(
        required=True,
        label='Total copies',
        widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Total copies'}),
        validators=[MinValueValidator(1)]
    )

    available_copies = forms.IntegerField(
        required=True,
        label='Available copies',
        widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Available copies'}),
        validators=[MinValueValidator(1)]
    )

    status = forms.ChoiceField(
        choices=Book.STATUS_CHOICES,
        required=True,
        label='Status',
        widget=forms.Select(attrs={'class': 'form-control'})
    )

    cover_image = forms.ImageField(
        required=False,
        label='Cover image',
        widget=forms.FileInput(attrs={'class': 'form-control', 'accept': 'image/*'})
    )

    description = forms.CharField(
        required=False,
        label='Description',
        widget=forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Description'})
    )

    pages = forms.IntegerField(
        required=True,
        label='Pages number',
        widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Pages number'}),
        validators=[MinValueValidator(1)]
    )

    class Meta:
        model = Book
        fields = [
            'title',
            'author',
            'publisher',
            'category',
            'isbn',
            'publication_year',
            'total_copies',
            'available_copies',
            'status',
            'cover_image',
            'description',
            'pages'
        ]

    def clean_title(self):
        title = self.cleaned_data.get('title')
        if title and len(title.strip()) == 0:
            raise forms.ValidationError('Title cannot be empty or just whitespace.')
        return title

    def clean_author(self):
        authors = self.cleaned_data.get('author')
        if not authors or authors.count() == 0:
            raise forms.ValidationError('At least one author must be selected.')
        return authors

    def clean_isbn(self):
        isbn = self.cleaned_data.get('isbn')
        if isbn:
            isbn = isbn.strip().replace('-', '').replace(' ', '')
            if len(isbn) < 10 and len(isbn) < 20:
                raise forms.ValidationError('ISBN must be between 10 and 20 characters.')
            if not isbn.isdigit():
                raise forms.ValidationError('ISBN must contain only number.')
        return isbn

    def clean_publication_year(self):
        year = self.cleaned_data.get('publication_year')
        current_year = datetime.datetime.now().year
        if year and (year < 1000 or year > current_year + 1):
            raise forms.ValidationError(f'Publication year must be between 1000 and {current_year + 1}.')
        return year

    def clean_total_copies(self):
        total_copies = self.cleaned_data.get('total_copies')
        if total_copies and total_copies < 1:
            raise forms.ValidationError('Total copies must be at least 1.')
        if total_copies and total_copies > 10000:
            raise forms.ValidationError('Total copies cannot exceed 10,000.')
        return total_copies

    def clean_available_copies(self):
        available_copies = self.cleaned_data.get('available_copies')
        if available_copies and available_copies < 0:
            raise forms.ValidationError('Available copies cannot be negative.')
        return available_copies

    def clean_pages(self):
        pages = self.cleaned_data.get('pages')
        if pages and pages < 1:
            raise forms.ValidationError('Number of pages must be at least 1.')
        if pages and pages > 50000:
            raise forms.ValidationError('Number of pages cannot exceed 50,000.')
        return pages

    def clean_cover_image(self):
        image = self.cleaned_data.get('cover_image')
        if image:
            if image.size > 10 * 1024 * 1024:  # 5MB limit
                raise forms.ValidationError('Cover image size cannot exceed 5MB.')
            if not image.content_type.startswith('image/'):
                raise forms.ValidationError('Uploaded file must be an image.')
        return image

    def clean(self):
        cleaned_data = super().clean()
        total_copies = cleaned_data.get('total_copies')
        available_copies = cleaned_data.get('available_copies')

        if total_copies and available_copies:
            if available_copies > total_copies:
                raise forms.ValidationError('Available copies cannot exceed total copies.')

        return cleaned_data


class EmailForm(forms.Form):
    name = forms.CharField(max_length=30, required=True, label="name")
    email = forms.EmailField(required=True, label="email")
    subject = forms.CharField(max_length=20, required=True, label="subject")
    message = forms.CharField(widget=forms.Textarea, required=True, label="message")


class LoginForm(AuthenticationForm):
    remember_me = forms.BooleanField(
        required=False,
        initial=False,
        widget=forms.CheckboxInput(attrs={
            'id': 'remember_me',
            'class': 'remember-checkbox'
        }),
        label="Remember me"
    )

    def confirm_login_allowed(self, user):
        if not user.is_active:
            raise forms.ValidationError(
                self.error_messages['disabled_account'],
                code='disabled_account',
            )
        if not Member.objects.filter(user=user).exists():
            raise forms.ValidationError(
                self.error_messages['disabled_account'],
                code='disabled_account',
            )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Enter your username',
            'autocomplete': 'username'
        })
        self.fields['password'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Enter your password',
            'autocomplete': 'current-password'
        })
        self.fields['remember_me'].label = False


class MemberRegistrationForm(UserCreationForm):
    email = forms.EmailField(
        required=True,
        label="email",
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter your email',
            'autocomplete': 'email'
        })
    )

    first_name = forms.CharField(
        max_length=50,
        required=True,
        label="First name",
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter your first name',
            'autocomplete': 'first-name'
        })
    )

    last_name = forms.CharField(
        max_length=50,
        required=False,
        label="Last name",
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter your last name',
            'autocomplete': 'last-name'
        })
    )

    phone = forms.CharField(
        max_length=11,
        required=False,
        label="Number phone",
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter your number phone: 09xxxxxxxxx',
            'autocomplete': 'tel'
        }),
        validators=[
            RegexValidator(
                regex=r"^09\d{9}$",
                message="Phone number must start with 09 and be 11 digits long.",
                code="invalid_phone"
            )
        ]
    )

    address = forms.CharField(
        required=False,
        label='Address',
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'placeholder': 'Enter your address',
            'autocomplete': 'address'
        })
    )

    role = forms.ChoiceField(
        choices=Member.ROLE_CHOICES,
        required=True,
        label='Role',
        widget=forms.Select(attrs={
            'class': 'form-control'
        })
    )

    profile_image = forms.ImageField(
        required=False,
        label="Profile image",
        widget=forms.FileInput(attrs={
            'class': 'form-control',
            'accept': 'image/*'
        })
    )

    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email', 'password1', 'password2')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].widget.attrs.update({
            'class': "form-control",
            'placeholder': "Enter your email",
            'autocomplete': "email",
        })

        self.fields['password1'].widget.attrs.update({
            'class': "form-control",
            'placeholder': "Enter your email",
            'autocomplete': "email"
        })

        self.fields['password2'].widget.attrs.update({
            'class': "form-control",
            'placeholder': "Enter your email",
            'autocomplete': "email"
        })

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError('Email already exists.')
        return email

    def clean_phone(self):
        phone = self.cleaned_data.get('phone')
        if phone and Member.objects.filter(phone=phone).exists():
            raise forms.ValidationError('Phone number already exists.')
        return phone

    def clean_username(self):
        username = self.cleaned_data.get('username')
        if User.objects.filter(username=username).exists():
            raise forms.ValidationError('Username already exists.')
        return username

    def clean_profile_image(self):
        image = self.cleaned_data.get('profile_image')
        if image:
            if image.size > 10 * 1024 * 1024:  # 5MB limit
                raise forms.ValidationError('Profile image size cannot exceed 5MB.')
            if not image.content_type.startswith('image/'):
                raise forms.ValidationError('Uploaded file must be an image.')
        return image

    def save(self, commit=True):
        with transaction.atomic():
            user = super().save(commit=False)
            user.first_name = self.cleaned_data.get('first_name')
            user.last_name = self.cleaned_data.get('last_name')
            user.email = self.cleaned_data.get('email')

            if commit:
                user.save()
                Member.objects.create(
                    user=user,
                    phone=self.cleaned_data.get('phone'),
                    address=self.cleaned_data.get('address'),
                    role=self.cleaned_data.get('role'),
                    profile_image=self.cleaned_data.get('profile_image')
                )
            return user


class CustomChangePasswordForm(PasswordChangeForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['old_password'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Enter your old password',
            'autocomplete': 'current-password',
            'required': 'True'
        })
        self.fields['old_password'].label = "Old password"
        self.fields['old_password'].required = True

        self.fields['new_password1'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Enter your new password',
            'autocomplete': 'new-password',
            'required': 'True'
        })
        self.fields['new_password1'].label = "New password"
        self.fields['new_password1'].required = True

        self.fields['new_password2'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Enter your confirm password',
            'autocomplete': 'new-password',
            'required': 'True'
        })
        self.fields['new_password2'].label = "confirm password"
        self.fields['new_password2'].required = True


class CustomPasswordResetForm(PasswordResetForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['email'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Enter your email',
            'autocomplete': 'email',
            'required': 'True'
        })
        self.fields['email'].label = "Email"
        self.fields['email'].required = True


class CustomSetPasswordForm(SetPasswordForm):
    def __init__(self, user, *args, **kwargs):
        super().__init__(user, *args, **kwargs)
        self.fields['new_password1'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Enter your new password',
            'autocomplete': 'new-password',
            'required': 'True'
        })
        self.fields['new_password1'].label = 'New password'
        self.fields['new_password1'].required = True

        self.fields['new_password2'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Enter your confirm password',
            'autocomplete': 'new-password',
            'required': 'True'
        })
        self.fields['new_password2'].label = 'Confirm password'
        self.fields['new_password2'].required = True
