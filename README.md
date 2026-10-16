# Mesa de Partes Digital

Prototipo web desarrollado en Python + FastAPI para digitalizar la recepción, seguimiento y trazabilidad de trámites documentarios.

## Funciones principales
- Login con JWT y usuario administrador.
- Registro de trámites con archivos adjuntos.
- Generación automática de código de seguimiento.
- Consulta pública del estado del trámite.
- Dashboard con indicadores por estado y prioridad.
- Gestión de áreas, usuarios y movimientos.

## Estructura
```text
mesa-partes-digital/
├── app/
│   ├── main.py
│   ├── database.py
│   ├── models.py
│   ├── schemas.py
│   ├── auth.py
│   └── routers/
├── static/
├── uploads/
├── docs/
├── requirements.txt
└── README.md
```

## Ejecución local
```bash
python -m venv venv
venv\Scripts\activate      # Windows
# source venv/bin/activate    # Linux/Mac
pip install -r requirements.txt
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

## Accesos
- Aplicación web: http://localhost:8000/static/index.html
- Documentación API: http://localhost:8000/docs
- Usuario demo: `admin`
- Contraseña demo: `admin123`

## Repositorio Git sugerido
```bash
git init
git add .
git commit -m "feat: prototipo inicial mesa de partes digital"
git branch -M main
git remote add origin https://github.com/tuusuario/mesa-partes-digital.git
git push -u origin main
```
