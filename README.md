# PagoClaro API

Backend local en FastAPI y SQLite. Expone exactamente cinco operaciones funcionales:

| Método | Ruta | Uso |
|---|---|---|
| POST | `/api/auth/login` | Iniciar sesión |
| GET | `/api/dashboard` | Consultar métricas según el rol |
| GET | `/api/payments` | Listar pagos visibles |
| POST | `/api/payments` | Crear una solicitud de pago |
| PATCH | `/api/payments/{payment_id}` | Cambiar el estado de un pago |

FastAPI expone además sus rutas técnicas automáticas `/docs`, `/redoc` y `/openapi.json`.

## Inicio rápido

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
Copy-Item .env.example .env
uvicorn app.main:app --reload --port 8000
```

La base `payments.db` y los usuarios de demostración se crean al arrancar.

## Cuentas de demostración

| Rol | Usuario | Contraseña |
|---|---|---|
| Administrador | `admin@pagoclaro.co` | `Admin123!` |
| Operador | `operador@pagoclaro.co` | `Operador123!` |
| Cliente | `cliente@pagoclaro.co` | `Cliente123!` |

## Flujo de uso

1. El Cliente crea una solicitud de pago.
2. El Operador consulta la bandeja y cambia el estado permitido.
3. El Administrador supervisa todos los pagos y puede establecer cualquier estado.
4. Cada cliente únicamente puede consultar sus propios registros.

El frontend correspondiente está en [frontAdopcionBOCC](https://github.com/AcamposPeriferia/frontAdopcionBOCC).

Consulta [docs/EVOLUTIVO.md](docs/EVOLUTIVO.md) para la propuesta de comprobantes y doble aprobación.

## Pruebas

```powershell
pytest -q
```


