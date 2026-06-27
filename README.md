# Proyecto Yape — Big Data DD283

## Descripción

Este proyecto propone e implementa una arquitectura Big Data para Yape usando:

- CockroachDB para el core de pagos.
- Redis para sesiones activas.
- MongoDB Atlas para perfiles flexibles de comerciantes.
- Databricks + Delta Lake para el historial transaccional.
- Neo4j para detección de fraude por grafos.
- Capa Gold para dashboards ejecutivos.

## Arquitectura Medallion

- **Bronze:** datos crudos de transacciones Yape.
- **Silver:** datos limpios, filtrados y enriquecidos.
- **Gold:** métricas de negocio listas para dashboards, como top distritos e ingresos por comisión.

## Estructura del proyecto

```text
semana_04/Soluciones/TuNombre_TuCodigo/
│
├── P1_arquitectura.md
├── P2_databricks_yape.py
├── P3_mongodb_atlas.py
├── P4_docker.py
├── docs/
│   └── P4_analisis_docker_vs_atlas.md
├── screenshots/
│   ├── databricks_celda1.png
│   ├── databricks_celda2.png
│   ├── databricks_celda3.png
│   ├── databricks_dashboard.png
│   ├── atlas_collections.png
│   ├── atlas_pipeline_output.png
│   └── docker_desktop.png
└── src/
    ├── databricks/
    │   └── pipeline.py
    ├── mongodb/
    │   └── merchant_repository.py
    └── docker/
        └── docker_mongo_client.py
```

## Clases y métodos principales

### Databricks

- `BronzeTransactionLoader.generate_dataset()`
- `BronzeTransactionLoader.save()`
- `SilverTransactionTransformer.read_bronze()`
- `SilverTransactionTransformer.transform()`
- `SilverTransactionTransformer.save()`
- `GoldMetricsAggregator.read_silver()`
- `GoldMetricsAggregator.create_view()`
- `GoldMetricsAggregator.top_districts()`
- `GoldMetricsAggregator.commissions_by_hour()`
- `GoldMetricsAggregator.save_gold()`

### MongoDB Atlas

- `MongoAtlasConnection.connect()`
- `MerchantSeeder.sample_merchants()`
- `MerchantSeeder.reset_collection()`
- `MerchantSeeder.insert_merchants()`
- `MerchantQueries.premium_merchants()`
- `MerchantQueries.high_value_delivery_merchants()`
- `MerchantQueries.bodegas_or_pharmacies()`
- `MerchantQueries.billing_report_pipeline()`

### Docker

- `DockerMongoConnection.connect()`
- `DockerMerchantTestRepository.insert_test_merchant()`
- `DockerMerchantTestRepository.find_test_merchant()`
- `DockerMerchantTestRepository.count_documents()`

## Video de sustentación

Enlace del video: `https://______________________________`

## Evidencias pendientes

Agregar screenshots en la carpeta `screenshots/` después de ejecutar Databricks, MongoDB Atlas y Docker Desktop.
