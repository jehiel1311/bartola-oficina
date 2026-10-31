#!/usr/bin/env python3
"""Genera datos.json (cifrado) a partir del TABLERO exportado como CSV.

Uso:
    OFICINA_CLAVE='...' python3 herramientas/generar.py tablero.csv

La clave se pasa por variable de entorno y nunca se escribe en el repo.
Cifrado: PBKDF2-SHA256 (250.000 vueltas) + AES-GCM 256, compatible con
WebCrypto del navegador (index.html).
"""
import base64, csv, json, os, sys
from datetime import datetime, timezone, timedelta
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes

ITER = 250_000

def main():
    if len(sys.argv) != 2:
        sys.exit("Uso: OFICINA_CLAVE='...' python3 herramientas/generar.py tablero.csv")
    clave = os.environ.get("OFICINA_CLAVE")
    if not clave:
        sys.exit("Falta la variable OFICINA_CLAVE")
    with open(sys.argv[1], encoding="utf-8-sig", newline="") as f:
        filas = [
            {k.strip(): (v or "").strip() for k, v in fila.items() if k}
            for fila in csv.DictReader(f)
            if (fila.get("ID") or "").strip()
        ]
    ar = timezone(timedelta(hours=-3))
    ruta_enlaces = os.path.join(os.path.dirname(os.path.abspath(__file__)), "enlaces.json")
    enlaces = json.load(open(ruta_enlaces, encoding="utf-8")) if os.path.exists(ruta_enlaces) else []
    datos = {
        "actualizado": datetime.now(ar).strftime("%d/%m/%Y %H:%M"),
        "filas": filas,
        "enlaces": enlaces,
    }
    sal, iv = os.urandom(16), os.urandom(12)
    kdf = PBKDF2HMAC(algorithm=hashes.SHA256(), length=32, salt=sal, iterations=ITER)
    llave = kdf.derive(clave.encode("utf-8"))
    ct = AESGCM(llave).encrypt(iv, json.dumps(datos, ensure_ascii=False).encode("utf-8"), None)
    b = lambda x: base64.b64encode(x).decode()
    salida = {"v": 1, "iter": ITER, "sal": b(sal), "iv": b(iv), "datos": b(ct)}
    with open("datos.json", "w", encoding="utf-8") as f:
        json.dump(salida, f)
    print(f"datos.json listo: {len(filas)} filas, actualizado {datos['actualizado']}")

if __name__ == "__main__":
    main()
