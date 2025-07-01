from django import forms
from django.utils import timezone
from django.core.exceptions import ValidationError
import re
from tareas.models import Pacientes

class PacienteForm(forms.ModelForm):
    class Meta:
        model = Pacientes
        fields = [
            'nombres', 'apellidos', 'numerodocumento', 'tipodocumento',
            'fechanacimiento', 'edad', 'genero', 'direccion', 'telefono',
            'nombre_contacto_emergencia', 'telefono_contacto_emergencia',
            'parentesco_contacto_emergencia',
            'email', 'gruposanguineo', 'alergias',
            'observaciones', 'enfermedades_base', 'idioma_principal',
            'estado', 'fecharegistro'
        ]
        widgets = {
            'fechanacimiento': forms.DateInput(attrs={'type': 'date'}),
            # Hide registration timestamp from the form; it will be set automatically
            'fecharegistro': forms.HiddenInput()
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        required_fields = [
            'nombres', 'apellidos', 'numerodocumento',
            'tipodocumento', 'fechanacimiento', 'genero', 'direccion',
            'telefono', 'estado'
        ]
        for field in required_fields:
            self.fields[field].required = True
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

        self.fields['nombres'].widget.attrs.update({
            'pattern': r'[A-Za-zÁÉÍÓÚáéíóúÑñ ]+',
            'title': 'Solo letras'
        })
        self.fields['apellidos'].widget.attrs.update({
            'pattern': r'[A-Za-zÁÉÍÓÚáéíóúÑñ ]+',
            'title': 'Solo letras'
        })
        self.fields['numerodocumento'].widget.attrs.update({
            'pattern': r'\d+',
            'title': 'Solo dígitos'
        })
        self.fields['telefono'].widget.attrs.update({
            'pattern': r'\d{7,15}',
            'title': 'Entre 7 y 15 dígitos'
        })
        self.fields['telefono_contacto_emergencia'].widget.attrs.update({
            'pattern': r'\d{7,15}',
            'title': 'Entre 7 y 15 dígitos'
        })
        self.fields['email'] = forms.EmailField(required=False, widget=forms.EmailInput())
        self.fields['edad'].widget.attrs.update({'min': 0, 'max': 120})
        self.fields['gruposanguineo'].widget.attrs.update({
            'pattern': r'^(A|B|AB|O)[+-]?$',
            'title': 'Ejemplo: A+, O-'
        })

    def save(self, commit=True):
        """Calcula la edad y fecha de registro automáticamente."""
        paciente = super().save(commit=False)
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

    # Validaciones del lado del servidor
    def clean_nombres(self):
        nombres = self.cleaned_data.get('nombres', '')
        if not re.fullmatch(r'[A-Za-zÁÉÍÓÚáéíóúÑñ ]+', nombres):
            raise ValidationError('El nombre debe contener solo letras y espacios.')
        return nombres

    def clean_apellidos(self):
        apellidos = self.cleaned_data.get('apellidos', '')
        if not re.fullmatch(r'[A-Za-zÁÉÍÓÚáéíóúÑñ ]+', apellidos):
            raise ValidationError('El apellido debe contener solo letras y espacios.')
        return apellidos

    def clean_numerodocumento(self):
        nd = self.cleaned_data.get('numerodocumento', '')
        if not nd.isdigit():
            raise ValidationError('El número de documento debe ser numérico.')
        return nd

    def clean_telefono(self):
        tel = self.cleaned_data.get('telefono', '')
        if tel and not re.fullmatch(r'\d{7,15}', tel):
            raise ValidationError('El teléfono debe contener entre 7 y 15 dígitos.')
        return tel

    def clean_edad(self):
        edad = self.cleaned_data.get('edad')
        if edad is not None and (edad < 0 or edad > 120):
            raise ValidationError('Edad fuera de rango válido.')
        return edad

    def clean_gruposanguineo(self):
        grupo = self.cleaned_data.get('gruposanguineo', '')
        if grupo and not re.fullmatch(r'^(A|B|AB|O)[+-]?$', grupo):
            raise ValidationError('Grupo sanguíneo inválido.')
        return grupo

class PacienteEditForm(PacienteForm):
    class Meta(PacienteForm.Meta):
        pass
