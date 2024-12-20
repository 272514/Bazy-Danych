from django import forms
from .models import Pracownik, Cysterna

class LoginForm(forms.Form):
    login = forms.CharField(max_length=100)
    haslo = forms.CharField(widget=forms.PasswordInput)

    def clean(self):
        cleaned_data = super().clean()
        login = cleaned_data.get("login")
        haslo = cleaned_data.get("haslo")
        
        if login and haslo:
            try:
                user = Pracownik.objects.get(login=login)
                if user.haslo != haslo:
                    raise forms.ValidationError("Nieprawidłowe hasło")
            except Pracownik.DoesNotExist:
                raise forms.ValidationError("Nie znaleziono użytkownika")
        return cleaned_data

class PracownikForm(forms.ModelForm):
    class Meta:
        model = Pracownik
        fields = ['imie', 'nazwisko', 'login', 'haslo', 'numer_kontaktowy']

    widgets = {
        'haslo': forms.PasswordInput(),
    }

class ZamowienieForm(forms.Form):
    rodzaj_paliwa_choices = [
        ('B95', 'B95'),
        ('B98', 'B98'),
        ('ON', 'ON'),
        ('ON+', 'ON+'),
    ]
    
    rodzaj_paliwa = forms.ChoiceField(choices=rodzaj_paliwa_choices, required=True)
    ilosc_paliwa = forms.DecimalField(max_digits=10, decimal_places=2, required=True, label="Ilość paliwa w litrach")
    uwagi = forms.CharField(widget=forms.Textarea, required=False, label="Uwagi")

class CysternaForm(forms.ModelForm):
    class Meta:
        model = Cysterna
        fields = ['numer_rejestracyjny', 'pojemnosc', 'data_przegladu']
        widgets = {
            'data_przegladu': forms.DateInput(attrs={'type': 'date'}),
        }
