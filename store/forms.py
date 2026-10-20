import re
from django import forms
from django.contrib.auth.models import User
from decimal import Decimal

class RegisterForm(forms.ModelForm):
    username = forms.CharField(
        max_length=150,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter your username'
        })
    )
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'name@example.com'
        })
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Minimum 6 characters'
        })
    )
    confirm_password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Re-enter your password'
        })
    )

    class Meta:
        model = User
        fields = ['username', 'email', 'password']

    def clean_username(self):
        username = self.cleaned_data.get('username')
        if User.objects.filter(username__iexact=username).exists():
            raise forms.ValidationError("A user with that username already exists.")
        return username

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError("A user with that email address already exists.")
        return email

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        confirm_password = cleaned_data.get("confirm_password")

        if password and confirm_password and password != confirm_password:
            self.add_error('confirm_password', "Passwords do not match.")
            raise forms.ValidationError("Passwords do not match.")
        
        if password and len(password) < 6:
            self.add_error('password', "Password must be at least 6 characters long.")
            
        return cleaned_data

class AddToCartForm(forms.Form):
    quantity = forms.IntegerField(
        min_value=1,
        initial=1,
        widget=forms.NumberInput(attrs={
            'class': 'form-control quantity-input',
            'min': 1,
            'max': 100,
            'value': 1
        })
    )

class CheckoutForm(forms.Form):
    full_name = forms.CharField(
        max_length=150,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'e.g. Rahul Sharma'
        }),
        required=True,
        label="Full Name"
    )
    phone_number = forms.CharField(
        max_length=15,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': '10-digit mobile number'
        }),
        required=True,
        label="Mobile Number"
    )
    pincode = forms.CharField(
        max_length=6,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': '6-digit PIN code (e.g. 560001)'
        }),
        required=True,
        label="Pincode"
    )
    city = forms.CharField(
        max_length=100,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'City / District'
        }),
        required=True,
        label="City"
    )
    state = forms.CharField(
        max_length=100,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'State'
        }),
        required=True,
        label="State"
    )
    shipping_address = forms.CharField(
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 3,
            'placeholder': 'Flat, House no., Building, Company, Apartment, Area, Street, Landmark'
        }),
        required=True,
        label="Address (Area and Street)"
    )
    address_type = forms.ChoiceField(
        choices=[
            ('Home', 'Home (All day delivery)'),
            ('Work', 'Work (Delivery between 9 AM - 6 PM)')
        ],
        widget=forms.RadioSelect(attrs={'class': 'address-type-radio'}),
        initial='Home',
        required=True,
        label="Address Type"
    )
    payment_method = forms.ChoiceField(
        choices=[
            ('Cash on Delivery (COD)', 'Cash on Delivery (Pay at doorstep)'),
            ('UPI / NetBanking / Cards', 'UPI / NetBanking / Debit & Credit Card (Sandbox Demo)')
        ],
        widget=forms.RadioSelect(attrs={'class': 'payment-method-radio'}),
        initial='Cash on Delivery (COD)',
        required=True,
        label="Payment Options"
    )

    def clean_phone_number(self):
        phone = self.cleaned_data.get('phone_number', '').strip()
        # Remove any leading +91 or spaces
        clean_phone = re.sub(r'[\s\-\+]', '', phone)
        if clean_phone.startswith('91') and len(clean_phone) == 12:
            clean_phone = clean_phone[2:]
        if not re.match(r'^[6-9]\d{9}$', clean_phone):
            raise forms.ValidationError("Please enter a valid 10-digit Indian mobile number.")
        return clean_phone

    def clean_pincode(self):
        pincode = self.cleaned_data.get('pincode', '').strip()
        if not re.match(r'^\d{6}$', pincode):
            raise forms.ValidationError("Please enter a valid 6-digit Indian PIN code.")
        return pincode
