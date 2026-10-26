# Focus Timer

Cronómetro de enfoque pequeño y modular.

- Cualquier materia o actividad.
- Objetivo de tiempo efectivo.
- Las pausas no cuentan.
- La hora estimada se adapta al pausar/reanudar.
- Historial agrupado por fecha.
- Registros en `registros.json`.

## Ejecución automática

Con Python instalado, ejecuta desde esta carpeta:

```powershell
python run.py
```

`run.py` crea `.venv` si no existe, comprueba/instala las dependencias de
`requirements.txt` y ejecuta la aplicación usando ese entorno. La interfaz se
inicia como un proceso independiente de la terminal; el lanzador espera cinco
segundos y termina sin cerrar la aplicación. No hace falta activar manualmente
el entorno virtual.

## Fish / Linux

```fish
python -m venv .venv
source .venv/bin/activate.fish
pip install -r requirements.txt
python main.py
```
