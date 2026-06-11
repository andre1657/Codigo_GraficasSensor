import csv
from datetime import datetime, timedelta
from pathlib import Path
from .IO_Utils import detectar_delimitador

NA_TOKENS = {"", "na", "n/a", "nan", "null", "none", "error", "??"}

def parse_ts_ms(s: str):
    """Parsea ts_ms (int ms) a datetime relativo (base hoy automática)."""
    s = (s or "").strip()
    if not s.isdigit():
        return None
    ms = int(s)
    base_time = datetime.today()  # Base: fecha actual automática (00:00:00)
    return base_time + timedelta(milliseconds=ms)

def parse_v(s: str):
    """Convierte a float, admitiendo coma decimal y tokens NA."""
    if s is None:
        return None
    s = str(s).strip().replace(",", ".").lower()
    if s in NA_TOKENS:
        return None
    try:
        return float(s)
    except ValueError:
        return None

def clean_file(
    in_path: Path,
    out_path: Path,
    ts_col="ts_ms",
    sensor_col="sensor_id",
    v_col="valor",
    avg_col="valor_avg",
    estado_col="estado"
):
    """
    Lee CSV crudo con ts_ms,sensor_id,valor,valor_avg,estado.
    Limpia y escribe CSV con timestamp (ISO),sensor_id,valor,valor_avg,estado.
    Devuelve: (ts_list, valor_list, avg_list, estado_list, stats_dict)
    """
    delim = detectar_delimitador(in_path)
    ts_list, valor_list, avg_list, estado_list = [], [], [], []
    total = kept = bad_ts = bad_val = 0

    with in_path.open("r", encoding="utf-8", newline="") as fin, \
         out_path.open("w", encoding="utf-8", newline="") as fout:
        reader = csv.DictReader(fin, delimiter=delim)
        writer = csv.DictWriter(fout, fieldnames=["timestamp", "sensor_id", "valor", "valor_avg", "estado"])
        writer.writeheader()

        for row in reader:
            total += 1
            ts_raw = row.get(ts_col, "").strip()
            t = parse_ts_ms(ts_raw)
            if t is None:
                bad_ts += 1
                continue

            sensor = row.get(sensor_col, "").strip()
            v = parse_v(row.get(v_col))
            avg = parse_v(row.get(avg_col))
            estado = row.get(estado_col, "").strip().upper()
            if v is None or avg is None or estado not in {"OK", "ALERT"}:
                bad_val += 1
                continue

            # Filtrar valores fuera de rango razonable para DS18B20 (-55°C a 125°C)
            if v < -55 or v > 125:
                bad_val += 1
                continue

            writer.writerow({
                "timestamp": t.strftime("%Y-%m-%dT%H:%M:%S"),
                "sensor_id": sensor,
                "valor": f"{v:.3f}",
                "valor_avg": f"{avg:.3f}",
                "estado": estado
            })

            ts_list.append(t)
            valor_list.append(v)
            avg_list.append(avg)
            estado_list.append(estado)
            kept += 1

    stats = {
        "filas_totales": total,
        "filas_validas": kept,
        "descartes_timestamp": bad_ts,
        "descartes_valor": bad_val,
        "%descartadas": round(((bad_ts + bad_val) / total * 100.0) if total else 0.0, 2)
    }
    return ts_list, valor_list, avg_list, estado_list, stats