from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from .models import MonitoredURL, Alert

class UserRegistrationForm(UserCreationForm):
    email = forms.EmailField(required=True)
    
    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']
    
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("This email address is already in use.")
        return email

class UserLoginForm(AuthenticationForm):
    username = forms.CharField(widget=forms.TextInput(attrs={'autofocus': True}))
    password = forms.CharField(
        label="Password",
        strip=False,
        widget=forms.PasswordInput,
    )

class URLForm(forms.ModelForm):
    def __init__(self, user=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if user:
            from .models import URLGroup
            self.fields['group'].queryset = URLGroup.objects.filter(user=user)
    
    class Meta:
        model = MonitoredURL
        fields = ['name', 'url', 'group', 'frequency', 'response_time_threshold', 
                 'expected_status', 'check_ssl']
        widgets = {
            'name': forms.TextInput(attrs={'placeholder': 'My Website'}),
            'url': forms.URLInput(attrs={'placeholder': 'https://example.com'}),
            'group': forms.Select(),
            'frequency': forms.Select(),
            'response_time_threshold': forms.NumberInput(attrs={'append': 'ms'}),
            'expected_status': forms.NumberInput(),
            'check_ssl': forms.CheckboxInput(),
        }
    
    def clean_url(self):
        url = self.cleaned_data.get('url')
        if not (url.startswith('http://') or url.startswith('https://')):
            raise forms.ValidationError("URL must start with http:// or https://")
        return url

class AlertForm(forms.ModelForm):
    def __init__(self, user, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['url'].queryset = MonitoredURL.objects.filter(user=user, is_active=True)
        
        # Dynamically set destination field based on method
        if 'method' in self.data:
            method = self.data.get('method')
            self.update_destination_field(method)
        elif self.instance.pk:
            self.update_destination_field(self.instance.method)
    
    def update_destination_field(self, method):
        if method == 'email':
            self.fields['destination'] = forms.EmailField(
                label="Email Address",
                widget=forms.EmailInput(attrs={'placeholder': 'your@email.com'})
            )
        elif method == 'telegram':
            self.fields['destination'] = forms.CharField(
                label="Telegram Chat ID",
                widget=forms.TextInput(attrs={'placeholder': '123456789'})
            )
        elif method == 'slack':
            self.fields['destination'] = forms.CharField(
                label="Slack Webhook URL",
                widget=forms.URLInput(attrs={'placeholder': 'https://hooks.slack.com/services/...'})
            )
    
    class Meta:
        model = Alert
        fields = ['url', 'method', 'destination', 'is_active']
        widgets = {
            'method': forms.Select(attrs={'onchange': 'updateDestinationField()'}),
        }

class NotificationSettingsForm(forms.Form):
    email_notifications = forms.BooleanField(
        required=False,
        label="Enable Email Notifications",
        help_text="Receive notifications via email"
    )
    telegram_notifications = forms.BooleanField(
        required=False,
        label="Enable Telegram Notifications",
        help_text="Receive notifications via Telegram"
    )
    slack_notifications = forms.BooleanField(
        required=False,
        label="Enable Slack Notifications",
        help_text="Receive notifications via Slack"
    )
    notification_frequency = forms.ChoiceField(
        choices=[
            ('immediate', 'Immediately'),
            ('hourly', 'Hourly Digest'),
            ('daily', 'Daily Digest'),
        ],
        initial='immediate',
        widget=forms.RadioSelect
    )
    
    def __init__(self, user, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.user = user