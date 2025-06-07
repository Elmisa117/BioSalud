from django import forms
from django.utils import timezone
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

    def save(self, commit=True):
        obj = super().save(commit=False)
        if not obj.fechacreacion:
            obj.fechacreacion = timezone.now()
        if commit:
            obj.save()
        return obj
