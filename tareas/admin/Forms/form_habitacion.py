from django import forms
from django.utils import timezone
from django.core.exceptions import ValidationError
import re
from tareas.models import Habitaciones, Tiposhabitacion

class HabitacionForm(forms.ModelForm):
    class Meta:
        model = Habitaciones
        fields = ['numero', 'tipohabitacionid', 'capacidad', 'disponible', 'estado', 'fechacreacion']
        widgets = {
            'fechacreacion': forms.DateTimeInput(attrs={'type': 'datetime-local'})
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['estado'] = forms.TypedChoiceField(
            choices=[(True, 'Activo'), (False, 'Inactivo')],
            coerce=lambda x: x == 'True',
            empty_value=None
        )
        self.fields['disponible'] = forms.TypedChoiceField(
            choices=[(True, 'Sí'), (False, 'No')],
            coerce=lambda x: x == 'True',
            empty_value=None
        )
        self.fields['numero'].widget.attrs.update({'pattern': r'\d+', 'title': 'Solo números'})
        self.fields['capacidad'].widget.attrs.update({'min': 1})

    def save(self, commit=True):
        obj = super().save(commit=False)
        if not obj.fechacreacion:
            obj.fechacreacion = timezone.now()
        if commit:
            obj.save()
        return obj

    def clean_numero(self):
        numero = self.cleaned_data.get('numero', '')
        if not re.fullmatch(r'\d+', numero):
            raise ValidationError('El número de habitación debe ser numérico.')
        return numero

    def clean_capacidad(self):
        cap = self.cleaned_data.get('capacidad')
        if cap is not None and cap < 1:
            raise ValidationError('La capacidad debe ser mayor a cero.')
        return cap

class TipoHabitacionForm(forms.ModelForm):
    class Meta:
        model = Tiposhabitacion
        fields = ['nombre', 'descripcion', 'costodiario', 'estado', 'fechacreacion']
        widgets = {
            'fechacreacion': forms.DateTimeInput(attrs={'type': 'datetime-local'})
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['estado'] = forms.TypedChoiceField(
            choices=[(True, 'Activo'), (False, 'Inactivo')],
            coerce=lambda x: x == 'True',
            empty_value=None
        )
        self.fields['nombre'].widget.attrs.update({
            'pattern': r'[A-Za-zÁÉÍÓÚáéíóúÑñ ]+',
            'title': 'Solo letras'
        })
        self.fields['costodiario'].widget.attrs.update({'min': 0, 'step': '0.01'})

    def save(self, commit=True):
        obj = super().save(commit=False)
        if not obj.fechacreacion:
            obj.fechacreacion = timezone.now()
        if commit:
            obj.save()
        return obj

    def clean_nombre(self):
        nombre = self.cleaned_data.get('nombre', '')
        if not re.fullmatch(r'[A-Za-zÁÉÍÓÚáéíóúÑñ ]+', nombre):
            raise ValidationError('El nombre debe contener solo letras.')
        return nombre

    def clean_costodiario(self):
        costo = self.cleaned_data.get('costodiario')
        if costo is not None and costo < 0:
            raise ValidationError('El costo diario debe ser positivo.')
        return costo
