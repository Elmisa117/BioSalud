# 🏥 BioSalud Pro - Sistema de Gestión Clínica con Biometría


## 📌 Tabla de Contenidos

- [Características](#-características-principales)
- [Tecnologías](#-tecnologías-utilizadas)
- [Instalación](#-instalación)
- [Configuración](#-configuración)
- [Estructura del Proyecto](#-estructura-del-proyecto)
- [API Biométrica](#-api-biométrica)
- [Modelo de Datos](#️-modelo-de-datos)
- [Seguridad](#-seguridad)
- [Despliegue](#-despliegue-en-producción)
- [Equipo](#-equipo-de-desarrollo)
- [Licencia](#-licencia)
- [Contacto](#-contacto)

---

## 🌟 Características Principales

### 🔍 Identificación Biométrica Avanzada

- Captura de huellas con lectores **DigitalPersona U.are.U 5000**
- Reconocimiento en **<3 segundos**
- Precisión del **99.7%** en pruebas controladas

### 💻 Módulos Especializados

| Módulo       | Funcionalidades |
|--------------|-----------------|
| Administrativo | Gestión de usuarios, roles, configuración del sistema |
| Médico         | Historias clínicas, diagnósticos, prescripciones |
| Enfermería     | Signos vitales, hospitalización, control de medicamentos |
| Cajero         | Facturación, pagos, reportes financieros |

### 📊 Dashboard Integral

- Estadísticas en tiempo real
- Reportes personalizables
- Exportación a PDF/Excel

---

## 🛠 Tecnologías Utilizadas

### Backend

| Tecnología     | Versión | Uso             |
|----------------|---------|------------------|
| Python         | 3.13    | Lenguaje principal |
| Django         | 5.2.1   | Framework web    |
| Django REST    | 3.16.0  | API biométrica   |
| PostgreSQL     | 14      | Almacenamiento seguro |

### Frontend

- Django Templates (HTML5, CSS3)
- Bootstrap 5 (Diseño responsive)
- Chart.js (Gráficos estadísticos)

### Biometría

- C# (.NET 4.7.2) - Aplicación de escritorio
- DigitalPersona SDK - Captura de huellas
- Windows Forms - Interfaz de usuario

---

## 🚀 Instalación

### Requisitos Previos

```bash
# PostgreSQL
sudo apt-get install postgresql postgresql-contrib

# Python
sudo apt-get install python3.13 python3.13-venv

# Dependencias del sistema
sudo apt-get install build-essential libpq-dev
```

### Configuración Inicial

```bash
# 1. Clonar repositorio
git clone https://github.com/tu-repo/biosalud.git
cd biosalud

# 2. Entorno virtual
python3.13 -m venv venv
source venv/bin/activate

# 3. Instalar dependencias
pip install -r requirements/production.txt

# 4. Configurar base de datos (ver sección Configuración)
```

---

## ⚙ Configuración

### Archivo `settings.py`

```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'BioSalud',
        'USER': 'bio_user',
        'PASSWORD': 'SecurePassword123!',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}

BIOMETRIC_CONFIG = {
    'MAX_RETRIES': 3,
    'TIMEOUT': 5,
    'ENCRYPTION_KEY': os.getenv('BIO_ENCRYPTION_KEY'),
}
```

### Variables de Entorno

Crear archivo `.env`:

```ini
DB_NAME=BioSalud
DB_USER=bio_user
DB_PASSWORD=SecurePassword123!
SECRET_KEY=tu-secret-key-unica
DEBUG=False
ALLOWED_HOSTS=.tudominio.com
```

---

## 📁 Estructura del Proyecto

```bash
📦tareas
 ┣ 📂admin
 ┃ ┣ 📂Forms
 ┃ ┃ ┣ 📂__pycache__
 ┃ ┃ ┃ ┣ 📜form_config.cpython-313.pyc
 ┃ ┃ ┃ ┣ 📜form_especialidad.cpython-313.pyc
 ┃ ┃ ┃ ┣ 📜form_habitacion.cpython-313.pyc
 ┃ ┃ ┃ ┣ 📜form_metodo_pago.cpython-313.pyc
 ┃ ┃ ┃ ┣ 📜form_paciente.cpython-313.pyc
 ┃ ┃ ┃ ┣ 📜form_personal.cpython-313.pyc
 ┃ ┃ ┃ ┗ 📜form_servicio.cpython-313.pyc
 ┃ ┃ ┣ 📜form_config.py
 ┃ ┃ ┣ 📜form_especialidad.py
 ┃ ┃ ┣ 📜form_habitacion.py
 ┃ ┃ ┣ 📜form_metodo_pago.py
 ┃ ┃ ┣ 📜form_paciente.py
 ┃ ┃ ┣ 📜form_personal.py
 ┃ ┃ ┗ 📜form_servicio.py
 ┃ ┣ 📂templates
 ┃ ┃ ┗ 📂admin
 ┃ ┃ ┃ ┣ 📜configuraciones.html
 ┃ ┃ ┃ ┣ 📜control_accesos.html
 ┃ ┃ ┃ ┣ 📜detalle_consulta.html
 ┃ ┃ ┃ ┣ 📜editar_paciente.html
 ┃ ┃ ┃ ┣ 📜editar_personal.html
 ┃ ┃ ┃ ┣ 📜historial_paciente.html
 ┃ ┃ ┃ ┣ 📜listar_consultas.html
 ┃ ┃ ┃ ┣ 📜listar_especialidades.html
 ┃ ┃ ┃ ┣ 📜listar_facturas.html
 ┃ ┃ ┃ ┣ 📜listar_habitaciones.html
 ┃ ┃ ┃ ┣ 📜listar_metodos_pago.html
 ┃ ┃ ┃ ┣ 📜listar_pacientes.html
 ┃ ┃ ┃ ┣ 📜listar_pagos.html
 ┃ ┃ ┃ ┣ 📜listar_personal.html
 ┃ ┃ ┃ ┣ 📜listar_servicios.html
 ┃ ┃ ┃ ┣ 📜listar_tipos_habitacion.html
 ┃ ┃ ┃ ┣ 📜MenuAdmin.html
 ┃ ┃ ┃ ┣ 📜registrar_especialidad.html
 ┃ ┃ ┃ ┣ 📜registrar_habitacion.html
 ┃ ┃ ┃ ┣ 📜registrar_metodo_pago.html
 ┃ ┃ ┃ ┣ 📜registrar_paciente.html
 ┃ ┃ ┃ ┣ 📜registrar_personal.html
 ┃ ┃ ┃ ┣ 📜registrar_servicio.html
 ┃ ┃ ┃ ┣ 📜registrar_tipohabitacion.html
 ┃ ┃ ┃ ┣ 📜reportes.html
 ┃ ┃ ┃ ┗ 📜ver_paciente.html
 ┃ ┣ 📂__pycache__
 ┃ ┃ ┣ 📜config_utils.cpython-313.pyc
 ┃ ┃ ┣ 📜context_processors.cpython-313.pyc
 ┃ ┃ ┣ 📜urls_admin.cpython-313.pyc
 ┃ ┃ ┗ 📜views_admin.cpython-313.pyc
 ┃ ┣ 📜config_utils.py
 ┃ ┣ 📜context_processors.py
 ┃ ┣ 📜urls_admin.py
 ┃ ┗ 📜views_admin.py
 ┣ 📂cajero
 ┃ ┣ 📂templates
 ┃ ┃ ┗ 📂cajero
 ┃ ┃ ┃ ┣ 📜BuscarPaciente.html
 ┃ ┃ ┃ ┣ 📜FacturaImpresion.html
 ┃ ┃ ┃ ┣ 📜GenerarFactura.html
 ┃ ┃ ┃ ┣ 📜panel_cajero.html
 ┃ ┃ ┃ ┣ 📜PerfilPaciente.html
 ┃ ┃ ┃ ┣ 📜VerPagosPaciente.html
 ┃ ┃ ┃ ┗ 📜ver_facturas_pagadas.html
 ┃ ┣ 📂__pycache__
 ┃ ┃ ┣ 📜urls_cajero.cpython-313.pyc
 ┃ ┃ ┗ 📜views_cajero.cpython-313.pyc
 ┃ ┣ 📜urls_cajero.py
 ┃ ┗ 📜views_cajero.py
 ┣ 📂doctor
 ┃ ┣ 📂templates
 ┃ ┃ ┗ 📂doctor
 ┃ ┃ ┃ ┗ 📜MenuDoctor.html
 ┃ ┣ 📂__pycache__
 ┃ ┃ ┣ 📜urls_doctor.cpython-313.pyc
 ┃ ┃ ┗ 📜views_doctor.cpython-313.pyc
 ┃ ┣ 📜urls_doctor.py
 ┃ ┗ 📜views_doctor.py
 ┣ 📂enfermeria
 ┃ ┣ 📂templates
 ┃ ┃ ┗ 📂enfermeria
 ┃ ┃ ┃ ┣ 📂Hospitalizacion
 ┃ ┃ ┃ ┃ ┗ 📜Hospitalizacion.html
 ┃ ┃ ┃ ┣ 📂Paciente
 ┃ ┃ ┃ ┃ ┣ 📂FichaClinico
 ┃ ┃ ┃ ┃ ┃ ┗ 📜FichaClinico.html
 ┃ ┃ ┃ ┃ ┣ 📂Historial
 ┃ ┃ ┃ ┃ ┃ ┣ 📜Historial.html
 ┃ ┃ ┃ ┃ ┃ ┗ 📜VerHistorial.html
 ┃ ┃ ┃ ┃ ┣ 📂RegistrarPaciente
 ┃ ┃ ┃ ┃ ┃ ┗ 📜RegistrarPaciente.html
 ┃ ┃ ┃ ┃ ┣ 📜Paciente.html
 ┃ ┃ ┃ ┃ ┗ 📜PerfilPaciente.html
 ┃ ┃ ┃ ┣ 📜MenuEnfermera.html
 ┃ ┃ ┃ ┗ 📜Perfil.html
 ┃ ┣ 📂__pycache__
 ┃ ┃ ┣ 📜urls_enfermeria.cpython-313.pyc
 ┃ ┃ ┗ 📜views_enfermeria.cpython-313.pyc
 ┃ ┣ 📜urls_enfermeria.py
 ┃ ┗ 📜views_enfermeria.py
 ┣ 📂migrations
 ┃ ┣ 📂__pycache__
 ┃ ┃ ┣ 📜0001_initial.cpython-313.pyc
 ┃ ┃ ┗ 📜__init__.cpython-313.pyc
 ┃ ┣ 📜0001_initial.py
 ┃ ┗ 📜__init__.py
 ┣ 📂static
 ┃ ┣ 📂admin
 ┃ ┃ ┣ 📂css
 ┃ ┃ ┃ ┣ 📜listar_pacientes.css
 ┃ ┃ ┃ ┣ 📜listar_personal.css
 ┃ ┃ ┃ ┣ 📜MenuAdmin.css
 ┃ ┃ ┃ ┣ 📜registrar_paciente.css
 ┃ ┃ ┃ ┗ 📜registrar_personal.css
 ┃ ┃ ┣ 📂img
 ┃ ┃ ┃ ┗ 📜bienvenido.png
 ┃ ┃ ┗ 📂js
 ┃ ┃ ┃ ┣ 📜listar_pacientes.js
 ┃ ┃ ┃ ┣ 📜listar_personal.js
 ┃ ┃ ┃ ┣ 📜MenuAdmin.js
 ┃ ┃ ┃ ┣ 📜registrar_paciente.js
 ┃ ┃ ┃ ┗ 📜registrar_personal.js
 ┃ ┣ 📂cajero
 ┃ ┃ ┣ 📂css
 ┃ ┃ ┃ ┣ 📜base_cajero.css
 ┃ ┃ ┃ ┣ 📜buscar_paciente.css
 ┃ ┃ ┃ ┣ 📜factura_styles.css
 ┃ ┃ ┃ ┣ 📜menu_caja.css
 ┃ ┃ ┃ ┣ 📜panel_cajero.css
 ┃ ┃ ┃ ┣ 📜perfil_paciente.css
 ┃ ┃ ┃ ┣ 📜ver_facturas_pagadas.css
 ┃ ┃ ┃ ┗ 📜ver_pagos.css
 ┃ ┃ ┗ 📂js
 ┃ ┃ ┃ ┣ 📜buscar_paciente.js
 ┃ ┃ ┃ ┣ 📜dashboard.js
 ┃ ┃ ┃ ┣ 📜factura_script.js
 ┃ ┃ ┃ ┗ 📜ver_pagos.js
 ┃ ┣ 📂css
 ┃ ┃ ┗ 📜login.css
 ┃ ┣ 📂doctor
 ┃ ┃ ┣ 📂css
 ┃ ┃ ┃ ┗ 📜dashboard.css
 ┃ ┃ ┗ 📂js
 ┃ ┃ ┃ ┗ 📜dashboard.js
 ┃ ┣ 📂enfermeria
 ┃ ┃ ┣ 📂css
 ┃ ┃ ┃ ┣ 📜FichaClinico.css
 ┃ ┃ ┃ ┣ 📜Historial.css
 ┃ ┃ ┃ ┣ 📜Hospitalizacion.css
 ┃ ┃ ┃ ┣ 📜MenuEnfermera.css
 ┃ ┃ ┃ ┣ 📜Paciente.css
 ┃ ┃ ┃ ┣ 📜Perfil.css
 ┃ ┃ ┃ ┣ 📜PerfilPaciente.css
 ┃ ┃ ┃ ┣ 📜RegistrarPaciente.css
 ┃ ┃ ┃ ┗ 📜VerHistorial.css
 ┃ ┃ ┗ 📂js
 ┃ ┃ ┃ ┣ 📜FichaClinico.js
 ┃ ┃ ┃ ┣ 📜Historial.js
 ┃ ┃ ┃ ┣ 📜Hospitalizacion.js
 ┃ ┃ ┃ ┣ 📜MenuEnfermera.js
 ┃ ┃ ┃ ┣ 📜Paciente.js
 ┃ ┃ ┃ ┣ 📜Perfil.js
 ┃ ┃ ┃ ┣ 📜PerfilPaciente.js
 ┃ ┃ ┃ ┣ 📜RegistrarPaciente.js
 ┃ ┃ ┃ ┗ 📜VerHistorial.js
 ┃ ┣ 📂img
 ┃ ┃ ┣ 📜actualizar.png
 ┃ ┃ ┣ 📜alerta.gif
 ┃ ┃ ┣ 📜BuscarPaciente.png
 ┃ ┃ ┣ 📜CerrarSesion.png
 ┃ ┃ ┣ 📜dormitorio.png
 ┃ ┃ ┣ 📜fondo_clinica.jpg
 ┃ ┃ ┣ 📜Guardar.png
 ┃ ┃ ┣ 📜Hospitalizacion.png
 ┃ ┃ ┣ 📜paciente.png
 ┃ ┃ ┣ 📜perfil.gif
 ┃ ┃ ┣ 📜Personal.gif
 ┃ ┃ ┣ 📜registro.gif
 ┃ ┃ ┣ 📜regresar.png
 ┃ ┃ ┗ 📜verificado.gif
 ┃ ┗ 📂js
 ┃ ┃ ┗ 📜login.js
 ┣ 📂templates
 ┃ ┗ 📜login.html
 ┣ 📂__pycache__
 ┃ ┣ 📜admin_dispositivotoken.cpython-313.pyc
 ┃ ┣ 📜apps.cpython-313.pyc
 ┃ ┣ 📜models.cpython-313.pyc
 ┃ ┣ 📜views.cpython-313.pyc
 ┃ ┗ 📜__init__.cpython-313.pyc
 ┣ 📜admin_dispositivotoken.py
 ┣ 📜apps.py
 ┣ 📜config.json
 ┣ 📜models.py
 ┣ 📜urls.py
 ┣ 📜views.py
 ┗ 📜__init__.py
```

---

## 🔌 API Biométrica

### Endpoints Principales

| Método | Endpoint | Parámetros | Respuesta |
|--------|----------|------------|-----------|
| POST   | `/api/biometric/register/` | paciente_id, fingerprint (Base64), finger_index | `{status: "success"}` |
| GET    | `/api/biometric/verify/`   | fingerprint (Base64) | `{match: bool, paciente_id: int}` |

### Ejemplo cURL

```bash
curl -X POST "http://localhost:8000/api/biometric/register/" -H "Authorization: Token tu-token" -H "Content-Type: application/json" -d '{"paciente_id": 123, "fingerprint": "base64encoded...", "finger_index": 1}'
```

---

## 🗃️ Modelo de Datos

### Tablas Clave

```python
class Paciente(models.Model):
    nombre = models.CharField(max_length=100)
    apellido = models.CharField(max_length=100)
    dni = models.CharField(max_length=20, unique=True)
    fecha_nacimiento = models.DateField()

class HuellaDigital(models.Model):
    paciente = models.ForeignKey(Paciente, on_delete=models.CASCADE)
    dedo = models.PositiveSmallIntegerField()
    template = models.BinaryField()
    fecha_registro = models.DateTimeField(auto_now_add=True)
```

---

## 🔐 Seguridad

### Medidas Implementadas

- **Autenticación:**
  - Tokens JWT
  - Cookies seguras
  - Autenticación en dos factores (2FA)

- **Datos Biométricos:**
  - Encriptación AES-256
  - Almacenamiento seguro en PostgreSQL

- **Protección Web:**
  - CSRF Protection
  - XSS Filtering
  - Rate Limiting

### Configuración Recomendada

```python
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_BROWSER_XSS_FILTER = True
X_FRAME_OPTIONS = 'DENY'
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
```

---

## 🚀 Despliegue en Producción

### Opción 1: Docker

```bash
docker-compose -f docker-compose.prod.yml up -d --build
```

### Opción 2: Manual (Gunicorn + Nginx)

```bash
pip install gunicorn
gunicorn --bind 0.0.0.0:8000 --workers 4 core.wsgi:application
```

**Configuración Nginx:**

```nginx
server {
    listen 80;
    server_name biosalud.tudominio.com;
    return 301 https://$host$request_uri;
}

server {
    listen 443 ssl;
    server_name biosalud.tudominio.com;

    ssl_certificate /etc/letsencrypt/live/biosalud/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/biosalud/privkey.pem;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    location /static/ {
        alias /ruta/a/tu/proyecto/static/;
    }

    location /media/ {
        alias /ruta/a/tu/proyecto/media/;
    }
}
```

---

## 👥 Equipo de Desarrollo

| Rol           | Nombre               | Responsabilidades           |
|---------------|----------------------|-----------------------------|
| Product Owner | Cristian Romero      | Requerimientos, planificación |
| Scrum Master  | Pilar Aguilar        | Metodología, coordinación    |
| Backend Dev   | Misael Sejas         | API, lógica de negocio       |
| Frontend Dev  | Elías Terrazas       | UI/UX, templates             |
| DB Engineer   | Equipo               | Modelado, optimización       |

**Asesor:** Ing. José Gabriel Zurita Castro  
**Institución:** Universidad Autónoma "Gabriel René Moreno"  
**Facultad:** Integral de Ichilo  
**Carrera:** Ingeniería en Sistemas

---

## 📜 Licencia

Este proyecto está bajo la **licencia GPL-3.0**.  
Para uso comercial del módulo biométrico, se requiere licencia especial.

```
Copyright (C) 2025 BioSalud

Este programa es software libre: usted puede redistribuirlo y/o modificarlo
bajo los términos de la GNU General Public License publicada por
la Free Software Foundation, ya sea la versión 3 de la Licencia, o
(a su elección) cualquier versión posterior.
```


¡Gracias por usar **BioSalud**! 🚀  
*Innovación tecnológica al servicio de la salud*