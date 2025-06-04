from django import forms
from tareas.models import Pacientes

class PacienteForm(forms.ModelForm):
    class Meta:
        model = Pacientes
        fields = [
            'nombres', 'apellidos', 'numerodocumento', 'tipodocumento',
            'fechanacimiento', 'genero', 'direccion', 'telefono', 'email',
            'seguro', 'observaciones', 'estado'
        ]
        widgets = {
            'fechanacimiento': forms.DateInput(attrs={'type': 'date'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        required_fields = [
            'nombres', 'apellidos', 'numerodocumento',
            'tipodocumento', 'fechanacimiento', 'genero', 'direccion',
            'telefono', 'seguro', 'estado'
        ]
        for field in required_fields:
            self.fields[field].required = True
        self.fields['genero'] = forms.ChoiceField(
            choices=[('', 'Seleccione...'), ('M', 'Masculino'), ('F', 'Femenino')],
            required=True
        )
        self.fields['estado'] = forms.ChoiceField(
            choices=[(True, 'Activo'), (False, 'Inactivo')],
            widget=forms.Select()
        )

class PacienteEditForm(PacienteForm):
    class Meta(PacienteForm.Meta):
        pass
