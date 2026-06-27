# Estructura y arquitectura del proyecto Yape

Este documento resume la estructura propuesta del proyecto y las decisiones de arquitectura solicitadas en la guía.

## Arquitectura general

```text
App Yape / Canales
        │
        ▼
API Gateway + servicios de pagos
        │
        ├── Core transaccional: CockroachDB
        ├── Sesiones activas: Redis Cluster
        ├── Comerciantes: MongoDB Atlas
        ├── Fraude: Neo4j
        └── Eventos de transacciones
                  │
                  ▼
        Databricks Lakehouse
        Bronze → Silver → Gold
                  │
                  ▼
        Dashboard ejecutivo / BI
```

## Capas de datos

| Capa | Objetivo | Tecnología | Salida |
|---|---|---|---|
| Bronze | Guardar transacciones crudas | Parquet en Databricks | `/FileStore/yape/bronze/transacciones` |
| Silver | Filtrar completadas, monto > 0, categorizar monto, calcular comisión | PySpark | `/FileStore/yape/silver/transacciones_limpias` |
| Gold | Agregar métricas para dashboard | Spark SQL | `/FileStore/yape/gold/top_distritos`, `/FileStore/yape/gold/ingresos_por_hora` |

## Estructura de carpetas entregable

```text
semana_04/Soluciones/TuNombre_TuCodigo/
├── P1_arquitectura.md
├── P2_databricks_yape.py
├── P3_mongodb_atlas.py
├── P4_docker.py
├── docs/
│   └── P4_analisis_docker_vs_atlas.md
├── screenshots/
└── src/
    ├── databricks/
    ├── mongodb/
    └── docker/
```

## Responsabilidades por módulo

### `src/databricks/pipeline.py`

Implementa la arquitectura Medallion.

- `BronzeTransactionLoader`: genera y guarda transacciones crudas.
- `SilverTransactionTransformer`: limpia, filtra y enriquece datos.
- `GoldMetricsAggregator`: crea métricas ejecutivas.

### `src/mongodb/merchant_repository.py`

Implementa la gestión documental de comerciantes.

- `MongoAtlasConnection`: conexión a Atlas.
- `MerchantSeeder`: carga los 5 documentos con esquemas distintos.
- `MerchantQueries`: consultas y pipeline de agregación.

### `src/docker/docker_mongo_client.py`

Implementa la conexión local a MongoDB en Docker.

- `DockerMongoConnection`: conexión al contenedor local.
- `DockerMerchantTestRepository`: inserción y validación del documento de prueba.

## Respuestas completadas de la guía

Las respuestas de P1.1, P1.2 y P1.3 están en `P1_arquitectura.md`.

El código completado para Databricks está en `P2_databricks_yape.py`.

El código completo para MongoDB Atlas está en `P3_mongodb_atlas.py`.

El código de conexión a MongoDB Docker está en `P4_docker.py`.

El análisis de Docker vs Atlas está en `docs/P4_analisis_docker_vs_atlas.md`.
