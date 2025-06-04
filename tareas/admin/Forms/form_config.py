from django import forms

class ConfiguracionForm(forms.Form):
    nombre_clinica = forms.CharField(label='Nombre de la clínica', max_length=100)
    logo_url = forms.CharField(label='URL del logo', max_length=255, required=False)
