Sí. Ya revisé los SQL que adjuntaste. Actualmente tienes una base bastante completa: 25 tablas, 2 vistas, y ya cargaste marcas, categorías, territorios, lista de precios, fuentes de promoción, una Switch 125 con variante/precio y sus alias.

El siguiente paso correcto es crear la API. No haría todavía el sistema gráfico. Primero debemos conseguir que toda la operación administrativa se pueda hacer correctamente mediante FastAPI; cuando Swagger permita crear una moto completa, promociones, precios, inventario, etc., el frontend será relativamente sencillo.

## 1. Cómo pensar FastAPI viniendo de NestJS

La traducción mental sería:

| NestJS           | FastAPI                           |
| ---------------- | --------------------------------- |
| Controller       | `APIRouter`                       |
| DTO              | Pydantic Schema                   |
| Entity           | SQLAlchemy Model                  |
| Service          | Service                           |
| Repository       | Repository                        |
| Module           | Package/módulo Python             |
| TypeORM          | SQLAlchemy                        |
| ConfigService    | `pydantic-settings`               |
| Guards           | `Depends()`                       |
| Pipes            | Pydantic                          |
| Exception Filter | Exception Handler                 |
| Migration        | Alembic                           |
| Swagger          | FastAPI lo genera automáticamente |

No vamos a hacer un proyecto Python donde todo esté metido en `main.py`.

---

# 2. Arquitectura general que vamos a construir

Quiero separar dos APIs lógicas desde el comienzo:

```text
                      FASTAPI
                         │
          ┌──────────────┴───────────────┐
          │                              │
          ▼                              ▼
    ADMIN API                         BOT API
          │                              │
CRUD / gestión completa          consultas controladas
          │                              │
          └──────────────┬───────────────┘
                         │
                     SERVICES
                         │
                    REPOSITORIES
                         │
                    PostgreSQL
```

Por ejemplo:

```text
/api/v1/admin/brands
/api/v1/admin/categories
/api/v1/admin/colors
/api/v1/admin/motorcycles
/api/v1/admin/promotions
/api/v1/admin/inventory
```

Mientras ElevenLabs tendrá posteriormente cosas como:

```text
/api/v1/bot/motorcycles/search
/api/v1/bot/motorcycles/{id}
/api/v1/bot/financing/calculate
```

Esto es importante.

ElevenLabs nunca tendrá acceso a endpoints como:

```text
DELETE /admin/motorcycles/...
PUT /admin/prices/...
```

---

# 3. Estructura del proyecto

Yo arrancaría así:

```text
japolandia-ai-api/
│
├── app/
│   ├── main.py
│   │
│   ├── core/
│   │   ├── config.py
│   │   ├── database.py
│   │   ├── exceptions.py
│   │   └── security.py
│   │
│   ├── common/
│   │   ├── pagination.py
│   │   ├── responses.py
│   │   └── utils.py
│   │
│   ├── modules/
│   │   │
│   │   ├── brands/
│   │   │   ├── model.py
│   │   │   ├── schemas.py
│   │   │   ├── repository.py
│   │   │   ├── service.py
│   │   │   └── router.py
│   │   │
│   │   ├── categories/
│   │   ├── colors/
│   │   ├── motorcycles/
│   │   ├── specifications/
│   │   ├── territories/
│   │   ├── stores/
│   │   ├── pricing/
│   │   ├── inventory/
│   │   ├── promotions/
│   │   ├── documents/
│   │   └── financing/
│   │
│   └── api/
│       ├── admin.py
│       └── bot.py
│
├── alembic/
│
├── tests/
│
├── .env
├── .env.example
├── alembic.ini
├── requirements.txt
├── README.md
└── pyproject.toml
```

Esto se parece bastante conceptualmente a cómo estructurarías módulos en NestJS.

---

# 4. No haría un CRUD bruto por cada tabla

Este punto va a ser importante cuando hagamos el panel.

Claro que tendremos:

```http
POST /brands
POST /colors
POST /categories
```

pero para crear una motocicleta no quiero que el frontend tenga que hacer:

```text
crear modelo
↓
crear alias 1
↓
crear alias 2
↓
crear variante
↓
crear precio
↓
crear inventario
↓
crear especificación
↓
crear especificación
...
```

Eso sería muy malo para el frontend.

Crearemos un endpoint de negocio:

```http
POST /api/v1/admin/motorcycles
```

que pueda recibir algo parecido a:

```json
{
  "brand_id": "uuid",
  "category_id": "uuid",

  "name": "SWITCH 125",
  "engine_cc": 125,

  "short_description": "Motocicleta para trabajo y uso diario",

  "aliases": [
    "switch",
    "switch 125",
    "victory switch",
    "victory switch 125"
  ],

  "variants": [
    {
      "sku": "60005599",
      "model_year": 2026,
      "color_id": "uuid",

      "price": {
        "price_list_id": "uuid",
        "amount": 7449000
      },

      "inventory": [
        {
          "store_id": "uuid",
          "quantity": 2
        }
      ]
    }
  ]
}
```

Y el backend hará todo dentro de una única transacción:

```text
BEGIN

crear modelo
crear alias
crear variantes
crear precios
crear inventario

COMMIT
```

Si algo falla:

```text
ROLLBACK
```

Eso es considerablemente más robusto.

---

# 5. Primer paso práctico: crear proyecto Python

En Windows PowerShell:

```powershell
mkdir japolandia-ai-api
cd japolandia-ai-api

python -m venv .venv
```

Activarlo:

```powershell
.\.venv\Scripts\Activate.ps1
```

Luego actualizar pip:

```powershell
python -m pip install --upgrade pip
```

---

# 6. Dependencias iniciales

Usaremos FastAPI + SQLAlchemy 2 + PostgreSQL asíncrono.

```powershell
pip install fastapi
pip install "uvicorn[standard]"
pip install sqlalchemy
pip install asyncpg
pip install alembic
pip install pydantic-settings
pip install python-slugify
```

Para pruebas:

```powershell
pip install pytest pytest-asyncio httpx
```

Y para mantener el código limpio:

```powershell
pip install ruff
```

No necesitas aprender 20 librerías. Las fundamentales serán:

```text
FastAPI
    API

Pydantic
    DTO / validación

SQLAlchemy
    ORM

asyncpg
    PostgreSQL

Alembic
    migraciones
```

---

# 7. Crear estructura inicial

Puedes crear:

```text
app/
app/core/
app/common/
app/modules/
app/api/
tests/
```

Y un `__init__.py` dentro de los paquetes.

Algo así:

```text
app/
├── __init__.py
├── main.py
│
├── core/
│   ├── __init__.py
│   ├── config.py
│   └── database.py
│
├── api/
│   ├── __init__.py
│   ├── admin.py
│   └── bot.py
│
└── modules/
    └── __init__.py
```

---

# 8. Configuración `.env`

Tu `.env`:

```env
APP_NAME=Japolandia AI API
APP_ENV=development
DEBUG=true

DATABASE_URL=postgresql+asyncpg://USUARIO:PASSWORD@HOST:5432/NOMBRE_BD
```

Por ejemplo local:

```env
DATABASE_URL=postgresql+asyncpg://postgres:123456@localhost:5432/japolandia_ai
```

Nunca pondremos credenciales directamente en Python.

---

# 9. Configuración central

`app/core/config.py`:

```python
from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "Japolandia AI API"
    app_env: str = "development"
    debug: bool = False

    database_url: str

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
```

En NestJS esto sería equivalente aproximadamente a tu:

```text
ConfigModule
ConfigService
```

---

# 10. Conexión PostgreSQL

`app/core/database.py`:

```python
from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from app.core.config import settings


engine = create_async_engine(
    settings.database_url,
    echo=settings.debug,
    pool_pre_ping=True,
)

AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()
```

Mentalmente:

```text
AsyncSession ≈ EntityManager / Repository context
```

---

# 11. Crear `main.py`

`app/main.py`:

```python
from fastapi import FastAPI

from app.core.config import settings


app = FastAPI(
    title=settings.app_name,
    version="1.0.0",
)


@app.get("/health")
async def health():
    return {
        "status": "ok",
        "service": settings.app_name,
    }
```

Ahora:

```powershell
uvicorn app.main:app --reload
```

Abres:

```text
http://127.0.0.1:8000
```

Y FastAPI automáticamente te genera Swagger:

```text
http://127.0.0.1:8000/docs
```

Eso será nuestro Postman provisional.

---

# 12. SQLAlchemy: no volveremos a crear las tablas

Tu base ya existe.

Por lo tanto no quiero meter cosas como:

```python
Base.metadata.create_all()
```

en el proyecto.

Vamos a representar esas tablas mediante modelos SQLAlchemy.

Por ejemplo:

```python
class Brand(Base):
    __tablename__ = "brands"
```

pero PostgreSQL seguirá siendo administrado mediante migraciones.

---

# 13. Aquí entra Alembic

Alembic para ti sería prácticamente:

```text
Prisma migrations
```

o:

```text
TypeORM migrations
```

Lo instalamos desde ahora porque cuando agreguemos una columna como:

```text
logo_url
```

no quiero que hagas manualmente:

```sql
ALTER TABLE ...
```

en producción.

Inicializamos:

```powershell
alembic init alembic
```

Como tu esquema ya existe, no vamos a ejecutar una migración que intente volver a crear esas 25 tablas.

Consideraremos tu SQL actual:

```text
consulta_bot_town_motorcycles.sql
```

como nuestro esquema/base V1.

Y a partir de aquí cualquier modificación irá mediante Alembic.

---

# 14. Orden de módulos

No empezaría intentando implementar las 25 tablas simultáneamente.

Vamos por dependencias.

Primero:

```text
brands
categories
colors
territories
stores
price_lists
specification_definitions
promotion_funding_sources
```

Son catálogos.

Después:

```text
motorcycle_models
motorcycle_aliases
motorcycle_variants
model_spec_values
```

Después:

```text
variant_prices
inventory
```

Después:

```text
promotions
```

Y finalmente:

```text
documents
financing
```

---

# 15. CRUD que necesitaremos para catálogos

Por ejemplo marcas:

```http
GET    /api/v1/admin/brands
GET    /api/v1/admin/brands/{id}
POST   /api/v1/admin/brands
PATCH  /api/v1/admin/brands/{id}
DELETE /api/v1/admin/brands/{id}
```

Lo mismo para:

```text
categories
colors
stores
territories
price-lists
specifications
```

Pero probablemente el `DELETE` real no borrará información.

Será:

```text
active = false
```

especialmente para datos que ya tengan relaciones.

---

# 16. Para motos tendremos endpoints más potentes

Además del CRUD:

```http
GET /api/v1/admin/motorcycles
```

con filtros:

```text
?brand=victory
&category=trabajo
&year=2026
&active=true
&search=switch
&page=1
&limit=20
```

Tendremos:

```http
POST /api/v1/admin/motorcycles
```

crear todo el agregado.

También:

```http
GET /api/v1/admin/motorcycles/{id}
PATCH /api/v1/admin/motorcycles/{id}
```

Variantes:

```http
POST   /api/v1/admin/motorcycles/{id}/variants
PATCH  /api/v1/admin/variants/{id}
```

Alias:

```http
POST   /api/v1/admin/motorcycles/{id}/aliases
DELETE /api/v1/admin/motorcycles/{id}/aliases/{alias_id}
```

Especificaciones:

```http
PUT /api/v1/admin/motorcycles/{id}/specifications
```

---

# 17. Precios necesitan endpoints específicos

Porque tienes historial.

No haría:

```text
PATCH motorcycle.price
```

porque conceptualmente eso destruiría el historial.

Haríamos:

```http
POST /api/v1/admin/variants/{id}/prices
```

Por ejemplo:

```json
{
  "price_list_id": "uuid",
  "amount": 7599000,
  "valid_from": "2026-09-15"
}
```

El `PricingService`:

```text
1. cierra precio anterior
2. pone valid_until
3. crea nuevo precio
4. todo en transacción
```

---

# 18. Inventario también tendrá su propio servicio

Por ejemplo:

```http
PUT /api/v1/admin/variants/{id}/inventory/{store_id}
```

Body:

```json
{
  "quantity": 4,
  "reserved_quantity": 0
}
```

No quiero que el panel conozca detalles SQL.

---

# 19. Promociones serán otro agregado

No quiero que quien carga el comunicado tenga que entender tus tablas relacionales.

En el panel verá conceptualmente:

```text
Nueva campaña

Nombre
Fecha inicio
Fecha fin
Marcas
Cobertura

Reglas:
    Moto
    Año
    Colores
    Bono
    UMA
    PDV
```

Y el frontend podrá enviar un JSON grande:

```http
POST /api/v1/admin/promotions
```

La API distribuirá la información entre:

```text
promotion_campaigns
promotion_campaign_brands
promotion_rules
promotion_rule_models
promotion_rule_years
promotion_rule_colors
promotion_rule_territories
promotion_rule_funding
```

Todo dentro de una transacción.

Eso es lo que permitirá que un tercero llene el sistema sin conocer cómo funciona tu BD.

---

# 20. Hay una cosa que agregaría antes de publicar el panel

Ahora que mencionas que lo llenará un externo, necesitaremos posteriormente:

```text
users
roles
audit_logs
```

Porque quiero poder saber:

```text
quién creó una moto
quién cambió un precio
quién creó una promoción
qué cambió
cuándo cambió
```

Eso será fundamental.

Por ejemplo:

```text
audit_logs

id
user_id
action
entity_type
entity_id
old_data JSONB
new_data JSONB
created_at
```

Pero no necesitamos bloquear el desarrollo por eso. Podemos hacer primero el CRUD local y agregar autenticación antes de exponerlo.

---

# 21. Arquitectura interna de un módulo

Por ejemplo `brands`:

```text
brands/
│
├── model.py
├── schemas.py
├── repository.py
├── service.py
└── router.py
```

Responsabilidad:

```text
router.py
     │
     │ HTTP
     ▼
service.py
     │
     │ reglas de negocio
     ▼
repository.py
     │
     │ SQLAlchemy
     ▼
model.py
     │
     ▼
PostgreSQL
```

Esto:

```python
@router.post(...)
```

no va a contener queries ni reglas de negocio.

---

# 22. Ejemplo mental equivalente a NestJS

Si actualmente en NestJS harías:

```typescript
@Controller('brands')
export class BrandsController {

    constructor(
        private readonly brandsService: BrandsService
    ) {}

    @Post()
    create(@Body() dto: CreateBrandDto) {
        return this.brandsService.create(dto);
    }
}
```

En FastAPI terminaremos haciendo algo conceptualmente así:

```python
@router.post("/")
async def create_brand(
    data: BrandCreate,
    db: AsyncSession = Depends(get_db),
):
    service = BrandService(db)

    return await service.create(data)
```

No cambia tanto conceptualmente.

Python tiene menos ceremonia.

---

# 23. La hoja de ruta completa

Yo seguiría este orden:

1. Crear proyecto FastAPI y entorno virtual.
2. Configurar `.env`.
3. Conectar PostgreSQL.
4. Configurar SQLAlchemy.
5. Configurar Alembic.
6. Crear los modelos ORM correspondientes a tus 25 tablas.
7. Implementar `brands`.
8. Implementar `categories`.
9. Implementar `colors`.
10. Implementar territorios/sedes/listas de precio.
11. Probar todo desde `/docs`.
12. Crear módulo `motorcycles`.
13. Crear endpoint transaccional para una moto completa.
14. Crear precios.
15. Crear inventario.
16. Crear promociones.
17. Añadir autenticación y roles.
18. Añadir auditoría.
19. Construir panel administrativo.
20. Crear `/bot/*`.
21. Añadir financiación.
22. Conectar ElevenLabs.
23. Añadir RAG/documentación.

### Lo inmediato

No empezaría todavía por ElevenLabs, RAG, frontend ni crédito.

Estamos exactamente en:

```text
BD ✓

        ↓

FASTAPI ← ESTAMOS AQUÍ

        ↓

Panel administrativo

        ↓

API del bot

        ↓

ElevenLabs
```

Y dentro de FastAPI, nuestro primer objetivo debe ser lograr desde Swagger:

```text
crear marca
       ↓
crear categoría
       ↓
crear color
       ↓
crear modelo
       ↓
crear variante
       ↓
asignar precio
       ↓
asignar inventario
       ↓
consultar la moto completa
```

Cuando ese flujo funcione, ya tendremos el núcleo sobre el cual montar todo lo demás.