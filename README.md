## Titulo
Limpieza de Datos para archivos .csv de sensor de temperatura usando python

## Integrantes
Bendezu Corimayhua, Andre Teofanes /	 
Carbajal Coral Joshua

## Descripción
Este pipeline en Python procesa archivos CSV crudos de sensores con timestamps y voltajes. Limpia los datos, convierte voltajes a temperaturas (°C), calcula KPIs, genera gráficos y crea un reporte CSV.

**Nota**: Los datos de temperatura se etiquetan como `humedad`, lo cual es incorrecto. Son temperaturas (°C). Se recomienda cambiar `humedad` a `temperatura`.
## Requisitos
- Python 3.11 o superior
- `matplotlib`

Instala las dependencias:
```bash
pip install matplotlib
```
## Estructura de los documentos
    LABORATORIO-2
        data
            processed
                archivos procesados de sucio a Limpio
            raw
                archivos sucios
        plots
            graficas en linea, histograma y boxplot
        reports
            reporte respecto a KPIS
        src
            pipeline
                __init__.py
                cleaning.py
                IO_Utils.py
                kpis.py
                plotting.py
        run_pipeline.py
                
## Uso y como funciona el codigo
1. Coloca tus CSVs crudos en `data/raw/` (ejemplo: `humedad_sucio_01.csv`).
   - Formato: Columnas `timestamp` (ej. `YYYY-MM-DDTHH:MM:SS`) y `voltage_V` (o `voltaje`, `value`).
2. Ejecuta el pipeline:
   ```bash
   python run_pipeline.py
   ```
3. Revisa los resultados en:
   - `data/processed/` (CSVs limpios)
   - `plots/` (gráficos)
   - `reports/` (reporte)

## Entradas
- **CSVs crudos**: En `data/raw/` (ejemplo: `humedad_sucio_01.csv`).
  - Columnas: `timestamp`, `voltage_V` (o similar).
  - Delimitador: `;` o `,` (detectado automáticamente).

## Salidas
- **CSVs limpios**: En `data/processed/` (ejemplo: `humedad_limpio_01.csv`).
  - Columnas: `timestamp`, `voltage_V`, `humedad` (temperatura en °C).
- **Gráficos**:
  - Línea: `plots/humedad_limpio_XX__volt_line__80.0V.png` (temperatura vs. tiempo, umbral 80°C).
  - Histograma: `plots/humedad_limpio_XX__volt_hist.png` (distribución de temperaturas).
  - Boxplot: `plots/boxplot_todos_sensores.png` (temperaturas por sensor, IDs como `S-01`).
- **Reporte**: `reports/kpis_por_archivo.csv` con:
  - Nombres de archivos, estadísticas (filas totales/válidas, descartes), KPIs (conteo, mín, máx, promedio, alertas > 80°C, % alertas).
