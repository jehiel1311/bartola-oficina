#!/usr/bin/env python3
"""Genera datos.json (cifrado) a partir del TABLERO exportado como CSV.

Uso:
    OFICINA_CLAVE='...' python3 herramientas/generar.py tablero.csv [--aviso "texto"]...

--aviso agrega un aviso extra en "Para tener en cuenta" (por ejemplo, la
Papelera llena). Se puede repetir.
--propuesta agrega una propuesta de mejora para Yeyo. Las propuestas
anteriores se conservan (se leen del datos.json actual) y quedan las 8 más
nuevas. --quitar-propuesta N saca la propuesta número N (cuando Yeyo la
acepta o la descarta). --listar-propuestas muestra las actuales y termina.

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

def leer_propuestas_previas(clave):
    """Lee las propuestas del datos.json actual (si existe y abre con la clave)."""
    try:
        p = json.load(open("datos.json", encoding="utf-8"))
        d = lambda x: base64.b64decode(x)
        kdf = PBKDF2HMAC(algorithm=hashes.SHA256(), length=32, salt=d(p["sal"]), iterations=p["iter"])
        plano = AESGCM(kdf.derive(clave.encode("utf-8"))).decrypt(d(p["iv"]), d(p["datos"]), None)
        return json.loads(plano).get("propuestas", [])
    except Exception:
        return []


def main():
    args = sys.argv[1:]
    if "--listar-propuestas" in args:
        clave = os.environ.get("OFICINA_CLAVE") or sys.exit("Falta la variable OFICINA_CLAVE")
        for p in leer_propuestas_previas(clave):
            print(f'{p["n"]}. ({p["fecha"]}) {p["texto"]}')
        return
    avisos, nuevas, quitar = [], [], []
    for flag, destino in (("--aviso", avisos), ("--propuesta", nuevas), ("--quitar-propuesta", quitar)):
        while flag in args:
            i = args.index(flag)
            destino.append(args[i + 1])
            del args[i:i + 2]
    if len(args) != 1:
        sys.exit("Uso: OFICINA_CLAVE='...' python3 herramientas/generar.py tablero.csv [--aviso texto]")
    clave = os.environ.get("OFICINA_CLAVE")
    if not clave:
        sys.exit("Falta la variable OFICINA_CLAVE")
    with open(args[0], encoding="utf-8-sig", newline="") as f:
        filas = [
            {k.strip(): (v or "").strip() for k, v in fila.items() if k}
            for fila in csv.DictReader(f)
            if (fila.get("ID") or "").strip()
        ]
    ar = timezone(timedelta(hours=-3))
    propuestas = leer_propuestas_previas(clave)
    quitar_n = {int(q) for q in quitar}
    propuestas = [p for p in propuestas if p.get("n") not in quitar_n]
    siguiente = max([p.get("n", 0) for p in propuestas] + [0]) + 1
    for texto in nuevas:
        propuestas.append({"n": siguiente, "fecha": datetime.now(ar).strftime("%d/%m/%Y"), "texto": texto})
        siguiente += 1
    propuestas = propuestas[-8:]
    ruta_enlaces = os.path.join(os.path.dirname(os.path.abspath(__file__)), "enlaces.json")
    enlaces = json.load(open(ruta_enlaces, encoding="utf-8")) if os.path.exists(ruta_enlaces) else []
    datos = {
        "actualizado": datetime.now(ar).strftime("%d/%m/%Y %H:%M"),
        "filas": filas,
        "enlaces": enlaces,
        "avisos": avisos,
        "propuestas": propuestas,
        "manual": json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "manual.json"), encoding="utf-8")) if os.path.exists(os.path.join(os.path.dirname(os.path.abspath(__file__)), "manual.json")) else None,
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
