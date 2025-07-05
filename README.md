# 🏥 BioSalud - Sistema de Gestión Clínica con Biometría

## 📌 Tabla de Contenidos

* [Características](#características-principales)
* [Tecnologías](#tecnologías-utilizadas)
* [Instalación](#instalación)
* [Configuración](#configuración)
* [Estructura del Proyecto](#estructura-del-proyecto)
* [API Biométrica](#api-biométrica)
* [Modelo de Datos](#modelo-de-datos)
* [Seguridad](#seguridad)
* [Despliegue](#despliegue-en-producción)
* [Mantenimiento](#mantenimiento)
* [Equipo](#equipo-de-desarrollo)
* [Licencia](#licencia)
* [Contacto](#contacto)

---

## 🌟 Características Principales

### 🔍 Identificación Biométrica

* Registro y verificación de huellas dactilares mediante lector **DigitalPersona U.are.U**.
* Compatible con app de escritorio en C# para captura biométrica.

### 💻 Módulos Funcionales

| Módulo         | Funcionalidades Principales                         |
| -------------- | --------------------------------------------------- |
| Administrativo | Gestión de usuarios, configuración, seguridad       |
| Doctor         | Consulta médica, diagnósticos, historial, servicios |
| Enfermería     | Ficha clínica, hospitalización, signos vitales      |
| Cajero         | Facturación, pagos, servicios, reportes             |

### 📊 Dashboard y Reportes

* Visualización de datos clínicos y financieros en tiempo real.
* Gráficos, filtros, exportación a PDF/Excel.

---

## 🛠 Tecnologías Utilizadas

### Backend

| Tecnología  | Versión | Uso                |
| ----------- | ------- | ------------------ |
| Python      | >= 3.10 | Lenguaje principal | 
| Django      | >= 4.2  | Framework web      |
| Django REST | >= 3.14 | API para biometría |
| PostgreSQL  | >= 14   | Base de datos      |

### Frontend

* HTML5, CSS3, Bootstrap 5
* JavaScript y Chart.js

### App Escritorio (Biometría)

* C# (.NET 4.7.2)
* Windows Forms
* SDK DigitalPersona

---

## 🚀 Instalación (Servidor Linux)

### Requisitos

```bash
sudo apt update && sudo apt install python3 python3-venv python3-pip postgresql libpq-dev nginx
```

### Clonar proyecto

```bash
cd /opt
sudo git clone https://github.com/tu_usuario/biosalud.git
cd biosalud
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### Base de datos

Crear la base de datos y usuario en PostgreSQL:

```sql
CREATE DATABASE biosalud;
CREATE USER bio_user WITH PASSWORD 'tu_password';
GRANT ALL PRIVILEGES ON DATABASE biosalud TO bio_user;
```

---

## ⚙️ Configuración

### `.env`

```ini
DEBUG=False
SECRET_KEY=clave_segura
ALLOWED_HOSTS=biosalud.cloud, www.biosalud.cloud
CSRF_TRUSTED_ORIGINS=https://biosalud.cloud, https://www.biosalud.cloud
DB_NAME=biosalud
DB_USER=bio_user
DB_PASSWORD=tu_password
```

### Aplicar migraciones y archivos estáticos

```bash
python manage.py migrate
python manage.py collectstatic
```

---

## 📁 Estructura del Proyecto

Incluye módulos por rol, templates organizados por rol y directorios `/static/` y `/media/` para archivos estáticos y de usuario.

---

## 🔌 API Biométrica

### Nuevos Endpoints

| Método | URL                         | Descripción                   |
| ------ | --------------------------- | ----------------------------- |
| POST   | /api/registrar_huella/     | Registrar plantilla de huella |
| GET    | /api/resultado_biometrico/ | Validar coincidencia huella   |

La aplicación C# consume estos endpoints mediante `HttpClient` con token según rol (configurado en JSON local).

---

## 📂 Modelo de Datos

Algunos modelos clave:

```python
class Pacientes(models.Model):
    nombres = models.CharField(max_length=100)
    numerodocumento = models.CharField(unique=True)
    edad = models.IntegerField()
    contacto_emergencia = models.CharField(max_length=100)
    enfermedades_base = models.TextField()
    idioma = models.CharField(max_length=50)
```

```python
class Huellas(models.Model):
    paciente = models.ForeignKey(Pacientes, on_delete=models.CASCADE)
    dedo = models.PositiveSmallIntegerField()
    plantilla = models.BinaryField()
    fecha = models.DateTimeField(auto_now_add=True)
```

---

## 🔒 Seguridad

* CSRF, HTTPS obligatorio con Certbot/Let's Encrypt
* Solo dominios confiables en `ALLOWED_HOSTS` y `CSRF_TRUSTED_ORIGINS`
* Validaciones en formularios (correo, teléfono, edad...)

---

## 🚀 Despliegue en Producción

### Gunicorn + Nginx

**Gunicorn Service:** `/etc/systemd/system/gunicorn.service`

```ini
[Unit]
Description=Gunicorn daemon for BioSalud
After=network.target

[Service]
User=ubuntu
Group=www-data
WorkingDirectory=/opt/BioSalud
ExecStart=/opt/BioSalud/venv/bin/gunicorn --workers 3 --bind 127.0.0.1:8000 BioSaludCRUD.wsgi:application

[Install]
WantedBy=multi-user.target
```

**Nginx Site:** `/etc/nginx/sites-available/biosalud`

```nginx
server {
    listen 80;
    server_name biosalud.cloud www.biosalud.cloud;
    return 301 https://$host$request_uri;
}

server {
    listen 443 ssl;
    server_name biosalud.cloud www.biosalud.cloud;

    ssl_certificate /etc/letsencrypt/live/biosalud.cloud/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/biosalud.cloud/privkey.pem;

    location /static/ {
        alias /opt/BioSalud/static/;
    }
    location /media/ {
        alias /opt/BioSalud/media/;
    }
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

---

## ⚖️ Mantenimiento del Sistema

### Actualizar proyecto desde Git

```bash
cd /opt/BioSalud
sudo git pull origin main
source venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py collectstatic --noinput
sudo systemctl restart gunicorn
```

### Renovar certificado SSL manual (si es necesario)

```bash
sudo certbot renew --dry-run
```

---

## 👥 Equipo de Desarrollo

| Rol              | Nombre         | Función Principal                 |
| ---------------- | -------------- | --------------------------------- |
| Desarrollador    | Elías Terrazas | Backend, despliegue, C# Biometría |
| Desarrollador    | Misael Sejas   | Modelado, vistas, seguridad       |
| Asesor Académico | Ing. Zurita    | Revisión técnica y validación     |

**Universidad Autónoma Gabriel Rene Moreno** - Facultad Integral del Ichilo

---

## 📜 Licencia

Este proyecto se distribuye bajo la licencia GPL-3.0. Para usos comerciales del módulo biométrico, contactar al equipo de desarrollo.
