from django import forms
from django.utils import timezone
from django.core.exceptions import ValidationError
import re
from tareas.models import Metodospago

class MetodoPagoForm(forms.ModelForm):
    class Meta:
        model = Metodospago
        fields = ['nombre', 'descripcion', 'requiereverificacion', 'estado', 'fechacreacion']
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
        self.fields['requiereverificacion'] = forms.TypedChoiceField(
            choices=[(True, 'Sí'), (False, 'No')],
            coerce=lambda x: x == 'True',
            empty_value=None
        )
        self.fields['nombre'].widget.attrs.update({
            'pattern': r'[A-Za-zÁÉÍÓÚáéíóúÑñ ]+',
            'title': 'Solo letras'
        })

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
