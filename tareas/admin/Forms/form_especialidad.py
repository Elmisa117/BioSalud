from django import forms
from django.utils import timezone
from django.core.exceptions import ValidationError
import re
from tareas.models import Especialidades

class EspecialidadForm(forms.ModelForm):
    class Meta:
        model = Especialidades
        fields = ['nombreespecialidad', 'descripcion', 'estado', 'fechacreacion']
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
        self.fields['nombreespecialidad'].widget.attrs.update({
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

    def clean_nombreespecialidad(self):
        nombre = self.cleaned_data.get('nombreespecialidad', '')
        if not re.fullmatch(r'[A-Za-zÁÉÍÓÚáéíóúÑñ ]+', nombre):
            raise ValidationError('El nombre debe contener solo letras.')
        return nombre
