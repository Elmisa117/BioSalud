from django import forms
from django.utils import timezone
from django.core.exceptions import ValidationError
import re
from tareas.models import Servicios

class ServicioForm(forms.ModelForm):
    class Meta:
        model = Servicios
        fields = [
            'nombre', 'descripcion', 'costo', 'costopacienteasegurado',
            'requiereprescripcion', 'estado', 'fechacreacion'
        ]
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
        self.fields['requiereprescripcion'] = forms.TypedChoiceField(
            choices=[(True, 'Sí'), (False, 'No')],
            coerce=lambda x: x == 'True',
            empty_value=None
        )
        self.fields['nombre'].widget.attrs.update({
            'pattern': r'[A-Za-zÁÉÍÓÚáéíóúÑñ ]+',
            'title': 'Solo letras'
        })
        self.fields['costo'].widget.attrs.update({'min': 0, 'step': '0.01'})
        self.fields['costopacienteasegurado'].widget.attrs.update({'min': 0, 'step': '0.01'})

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

    def clean_costo(self):
        costo = self.cleaned_data.get('costo')
        if costo is not None and costo < 0:
            raise ValidationError('El costo debe ser positivo.')
        return costo

    def clean_costopacienteasegurado(self):
        costo = self.cleaned_data.get('costopacienteasegurado')
        if costo is not None and costo < 0:
            raise ValidationError('El costo debe ser positivo.')
        return costo
