from django import forms
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

class PersonalEditForm(PersonalForm):
    """Formulario para editar personal sin requerir la contraseña"""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['contrasena'].required = False
