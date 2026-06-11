from pathlib import Path
import csv
from src.pipeline import (Root, ensure_dirs, list_raw_csvs, make_clean_name, safe_stem, clean_file, kpis_temp, plot_temperature_line, plot_temperature_hist, plot_boxplot_by_sensor)
# === Parámetros ===
ROOT = Root(__file__)
RAW_DIR = ROOT / "data" / "raw"
PROC_DIR = ROOT / "data" / "processed"
PLOTS_DIR = ROOT / "plots"
REPORTS_DIR = ROOT / "reports"
UMBRAL_TEMP = 37.0

ensure_dirs(RAW_DIR, PROC_DIR, PLOTS_DIR, REPORTS_DIR)

def main():
    # Buscar específicamente tu archivo raw
    raw_files = list_raw_csvs(RAW_DIR, pattern="Sensor_DS18B20.csv")
    if not raw_files:
        print(f"No hay CSV en crudo 'Sensor_DS18B20.csv' en {RAW_DIR}"); return

    resumen_kpis = []
    sensor_to_temps = {}  # para el boxplot global

    for in_path in raw_files:
        # Nombre de salida limpio
        clean_name = make_clean_name(in_path)
        out_path = PROC_DIR / clean_name

        # 1) Limpiar y escribir CSV limpio
        ts, temps, avg_temps, estados, stats = clean_file(in_path, out_path)
        if not ts:
            print("Sin datos válidos:", in_path.name)
            continue

        # 2) KPIs por archivo (temperatura)
        kt = kpis_temp(temps, umbral=UMBRAL_TEMP)
        resumen_kpis.append({
            "archivo": in_path.name,
            "salida": out_path.name,
            **stats,  # calidad
            "n": kt["n"], "min": kt["min"], "max": kt["max"],
            "prom": kt["prom"], "alerts": kt["alerts"], "alerts_pct": kt["alerts_pct"]
        })

        # 3) Gráficos por archivo
        stem_safe = safe_stem(out_path)
        plot_temperature_line(
            ts, temps, UMBRAL_TEMP,
            title=f"Temperatura vs Tiempo — {out_path.name}",
            out_path=PLOTS_DIR / f"{stem_safe}__temp_line__{UMBRAL_TEMP:.1f}C.png"
        )
        plot_temperature_hist(
            temps,
            title=f"Histograma Temperatura — {out_path.name}",
            out_path=PLOTS_DIR / f"{stem_safe}__temp_hist.png",
            bins=20
        )

        # 4) Acumular para boxplot global (usando sensor_id del CSV)
        sensor_id = "DS18B20_TEMP"  # O extraer dinámicamente si varía
        sensor_to_temps.setdefault(sensor_id, []).extend(temps)

    # 5) Guardar reporte KPIs
    rep_csv = REPORTS_DIR / "kpis_por_archivo.csv"
    with rep_csv.open("w", encoding="utf-8", newline="") as f:
        cols = ["archivo","salida","filas_totales","filas_validas","descartes_timestamp",
                "descartes_valor","%descartadas","n","min","max","prom","alerts","alerts_pct"]
        w = csv.DictWriter(f, fieldnames=cols)
        w.writeheader()
        for row in resumen_kpis:
            w.writerow(row)
    print("Reporte KPIs:", rep_csv)

    # 6) Boxplot global por sensor
    if sensor_to_temps:
        plot_temp_box = PLOTS_DIR / "boxplot_todos_sensores.png"
        plot_boxplot_by_sensor(sensor_to_temps, plot_temp_box)
        print("Boxplot global:", plot_temp_box)

if __name__ == "__main__":
    main()