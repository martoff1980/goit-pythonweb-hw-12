<!-- @format -->

# Як запускати тести

pytest -v

Або з coverage:

Запуск з корнової папки

pytest --cov=app --cov-report=term-missing

set PYTHONPATH=. py -m pytest tests/ --cov=routers --cov=services

pytest --collect-only -v
