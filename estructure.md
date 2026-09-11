## Estructura inicial
app/
app/core/
app/common/
app/modules/
app/api/
tests/

Y crear un __init__.py en cada carpeta
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