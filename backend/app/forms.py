from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.hashers import make_password
import re
from .models import Problem

class UserRegistrationForm(forms.ModelForm):
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter your password'
        }),
        min_length=8,
        help_text="Password must be at least 8 characters long."
    )
    confirm_password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Confirm your password'
        }),
        help_text="Enter the same password as before, for verification."
    )

    class Meta:
        model = User
        fields = ['username', 'email', 'password']
        widgets = {
            'username': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter your username'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter your email'
            }),
        }

    def clean_username(self):
        username = self.cleaned_data['username']
        if User.objects.filter(username=username).exists():
            raise forms.ValidationError("Username already exists.")
        if len(username) < 3:
            raise forms.ValidationError("Username must be at least 3 characters long.")
        if not re.match("^[a-zA-Z0-9_]+$", username):
            raise forms.ValidationError("Username can only contain letters, numbers, and underscores.")
        return username

    def clean_email(self):
        email = self.cleaned_data['email']
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("Email already registered.")
        return email

    def clean_confirm_password(self):
        password = self.cleaned_data.get('password')
        confirm_password = self.cleaned_data['confirm_password']
        
        if password and confirm_password and password != confirm_password:
            raise forms.ValidationError("Passwords don't match.")
        return confirm_password

    def clean_password(self):
        password = self.cleaned_data['password']
        
        # Password strength validation
        if len(password) < 8:
            raise forms.ValidationError("Password must be at least 8 characters long.")
        
        if not re.search(r'[A-Z]', password):
            raise forms.ValidationError("Password must contain at least one uppercase letter.")
        
        if not re.search(r'[a-z]', password):
            raise forms.ValidationError("Password must contain at least one lowercase letter.")
        
        if not re.search(r'\d', password):
            raise forms.ValidationError("Password must contain at least one digit.")
        
        return password

    def save(self, commit=True):
        # Use Django's create_user method which properly hashes the password
        user = User.objects.create_user(
            username=self.cleaned_data['username'],
            email=self.cleaned_data['email'],
            password=self.cleaned_data['password']
        )
        return user

class LoginForm(forms.Form):
    username = forms.CharField(
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter your username'
        })
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter your password'
        })
    )

class ProblemForm(forms.ModelForm):
    class Meta:
        model = Problem
        # --- ADD 'category' TO FIELDS ---
        fields = ['question', 'answer', 'difficulty', 'category']
        widgets = {
            'question': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., 5 + 7 or What is 10 x 3?'}),
            'answer': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., 12 or 30'}),
            'difficulty': forms.Select(choices=[('easy', 'Easy'), ('medium', 'Medium'), ('hard', 'Hard')], attrs={'class': 'form-control'}),
            # --- ADD WIDGET FOR CATEGORY ---
            'category': forms.Select(choices=Problem.CATEGORY_CHOICES, attrs={'class': 'form-control'}),
        }

    def clean_difficulty(self):
        difficulty = self.cleaned_data.get('difficulty', '').lower()
        if difficulty not in ['easy', 'medium', 'hard']:
            raise forms.ValidationError("Difficulty must be 'easy', 'medium', or 'hard'.")
        return difficulty

    # --- ADD VALIDATION FOR CATEGORY ---
    def clean_category(self):
        category = self.cleaned_data.get('category', '').lower()
        valid_categories = [c[0] for c in Problem.CATEGORY_CHOICES]
        if category not in valid_categories:
            raise forms.ValidationError("Invalid category.")
        return category

    def clean_answer(self):
        # Basic check: Ensure answer isn't empty
        answer = self.cleaned_data.get('answer', '').strip()
        if not answer:
            raise forms.ValidationError("Answer cannot be empty.")
        # You could add more validation here (e.g., try converting to number)
        return answer