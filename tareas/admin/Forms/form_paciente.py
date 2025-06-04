from django import forms
from django.utils import timezone
from tareas.models import Pacientes

class PacienteForm(forms.ModelForm):
    class Meta:
        model = Pacientes
        fields = [
            'nombres', 'apellidos', 'numerodocumento', 'tipodocumento',
            'fechanacimiento', 'edad', 'genero', 'direccion', 'telefono',
            'email', 'seguro', 'gruposanguineo', 'alergias',
            'observaciones', 'estado', 'fecharegistro'
        ]
        widgets = {
            'fechanacimiento': forms.DateInput(attrs={'type': 'date'}),
            # Hide registration timestamp from the form; it will be set automatically
            'fecharegistro': forms.HiddenInput()
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        required_fields = [
            'nombres', 'apellidos', 'numerodocumento', 'tipodocumento',
            'fechanacimiento', 'genero', 'direccion', 'telefono',
            'seguro', 'estado'
        ]
        for field in required_fields:
            self.fields[field].required = True

        # Selección de tipo de documento con opción para describir "Otro"
        self.fields['tipodocumento'] = forms.ChoiceField(
            choices=[
                ('', 'Seleccione...'),
                ('Cédula de identidad', 'Cédula de identidad'),
                ('Pasaporte', 'Pasaporte'),
                ('Otro', 'Otro')
            ],
            required=True,
            label='Tipo de documento'
        )
        # Campo adicional para detallar el documento si se elige "Otro"
        self.fields['otrodocumento'] = forms.CharField(
            required=False,
            label='Otro (especifique)'
        )

        self.fields['genero'] = forms.ChoiceField(
            choices=[('', 'Seleccione...'), ('M', 'Masculino'), ('F', 'Femenino')],
            required=True
        )
        self.fields['estado'] = forms.TypedChoiceField(
            choices=[(True, 'Activo'), (False, 'Inactivo')],
            coerce=lambda x: x == 'True',
            empty_value=None,
            widget=forms.Select()
        )

    def save(self, commit=True):
        """Calcula la edad y fecha de registro automáticamente."""
        paciente = super().save(commit=False)
        # Si se seleccionó "Otro", guardar la descripción escrita
        if self.cleaned_data.get('tipodocumento') == 'Otro':
            paciente.tipodocumento = self.cleaned_data.get('otrodocumento', '')
        else:
            paciente.tipodocumento = self.cleaned_data.get('tipodocumento')
        if not paciente.fecharegistro:
            paciente.fecharegistro = timezone.now()
        if paciente.fechanacimiento and not self.cleaned_data.get('edad'):
            today = timezone.now().date()
            paciente.edad = today.year - paciente.fechanacimiento.year - (
                (today.month, today.day) < (paciente.fechanacimiento.month, paciente.fechanacimiento.day)
            )
        if commit:
            paciente.save()
        return paciente

class PacienteEditForm(PacienteForm):
    class Meta(PacienteForm.Meta):
        pass
