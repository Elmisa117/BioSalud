from django import forms
from django.core.exceptions import ValidationError
import re
from tareas.models import Personal, Especialidades

class PersonalForm(forms.ModelForm):
    class Meta:
        model = Personal
        fields = [
            'nombres', 'apellidos', 'numerodocumento', 'tipodocumento',
            'fechanacimiento', 'genero', 'direccion', 'telefono', 'email',
            'fechaingreso', 'rol', 'especialidadid', 'usuario', 'contrasena',
            'estado'
        ]
        widgets = {
            'contrasena': forms.PasswordInput(),
            'fechanacimiento': forms.DateInput(attrs={'type': 'date'}),
            'fechaingreso': forms.DateInput(attrs={'type': 'date'}),
        }

    def __init__(self, *args, **kwargs):
        super(PersonalForm, self).__init__(*args, **kwargs)

        # 1. Campos obligatorios
        campos_requeridos = [
            'nombres', 'apellidos', 'numerodocumento', 'tipodocumento',
            'fechanacimiento', 'genero', 'direccion', 'telefono', 'email',
            'fechaingreso', 'rol', 'usuario', 'contrasena', 'estado'
        ]
        for campo in campos_requeridos:
            self.fields[campo].required = True

        # 2. Género desplegable M / F
        self.fields['genero'] = forms.ChoiceField(
            choices=[('', 'Seleccione...'), ('M', 'Masculino'), ('F', 'Femenino')],
            required=True
        )

        # 3. Rol restringido a los válidos
        ROLES_VALIDOS = [
            ('Administrador', 'Administrador'),
            ('Doctor', 'Doctor'),
            ('Enfermería', 'Enfermería'),
            ('Caja', 'Caja')
        ]
        self.fields['rol'] = forms.ChoiceField(
            choices=[('', 'Seleccione un rol...')] + ROLES_VALIDOS,
            required=True
        )

        # 4. Especialidad opcional, con opción vacía
        self.fields['especialidadid'].queryset = Especialidades.objects.all()
        self.fields['especialidadid'].required = False
        self.fields['especialidadid'].empty_label = '--- Sin especialidad ---'

        # 5. Estado como desplegable Activo/Inactivo
        self.fields['estado'] = forms.ChoiceField(
            choices=[(True, 'Activo'), (False, 'Inactivo')],
            widget=forms.Select()
        )

        # Validaciones HTML
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
        self.fields['email'] = forms.EmailField(required=True, widget=forms.EmailInput())

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
        numero = self.cleaned_data.get('numerodocumento', '')
        if not numero.isdigit():
            raise ValidationError('El número de documento debe ser numérico.')
        return numero

    def clean_telefono(self):
        telefono = self.cleaned_data.get('telefono', '')
        if telefono and not re.fullmatch(r'\d{7,15}', telefono):
            raise ValidationError('El teléfono debe contener entre 7 y 15 dígitos.')
        return telefono
class PersonalEditForm(PersonalForm):
    """Formulario para editar personal sin requerir la contraseña"""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['contrasena'].required = False
