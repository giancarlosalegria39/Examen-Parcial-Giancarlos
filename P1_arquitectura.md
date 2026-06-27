# P1 — Arquitectura Big Data Yape

> Herramienta IA usada: ChatGPT como asistente para organizar la arquitectura, completar código base y redactar justificaciones. La selección final de tecnologías se ajustó a los requisitos de la guía: pagos sin pérdida de dinero, 15M usuarios activos, 3.2M transacciones/día, 450 TPS pico y 18 TB/año de historial.

## 1.1 Tabla de arquitectura

| Componente del sistema | Tecnología elegida | Tipo BD/Herramienta | Por qué esta tecnología para Yape |
|---|---|---|---|
| Core de pagos (3.2M transacciones/día, no puede perder dinero) | CockroachDB | NewSQL distribuida, ACID, SQL | El core necesita transacciones ACID para debitar y acreditar saldos sin inconsistencias. CockroachDB permite escalar horizontalmente sin perder consistencia fuerte, algo clave si Yape crece de 15M a 50M usuarios. |
| Sesiones de login activo (15M usuarios, expira en 30 min) | Redis Cluster | Base de datos en memoria key-value | Las sesiones son datos temporales con TTL de 30 minutos, por eso conviene una base rápida en memoria. Redis permite lectura/escritura de baja latencia y expiración automática de claves. |
| Perfil del comerciante (bodega, restaurante, taxi — atributos distintos) | MongoDB Atlas | NoSQL documental | Los comercios tienen estructuras diferentes: carta, vehículo, DIGEMID, zonas de cobertura, etc. MongoDB permite documentos flexibles sin crear muchas columnas nulas como ocurriría en SQL. |
| Historial de transacciones para análisis (18 TB/año) | Databricks + Delta Lake sobre almacenamiento cloud | Lakehouse / Data Lake transaccional | El historial masivo debe procesarse por lotes y soportar analítica histórica. Delta Lake permite capas Bronze, Silver y Gold, con datos confiables, versionados y listos para dashboards. |
| Red de detección de fraude (ciclo A→B→C→A en < 5 min) | Neo4j | Base de datos de grafos | El fraude por ciclos o redes circulares se detecta mejor recorriendo relaciones entre usuarios. Neo4j permite consultas de caminos y ciclos con baja complejidad frente a joins SQL extensos. |
| Dashboard ejecutivo (top 10 distritos, actualización diaria) | Databricks SQL / Power BI sobre capa Gold | BI + Data Warehouse/Lakehouse | El dashboard necesita métricas agregadas, no transacciones crudas. La capa Gold deja tablas resumidas por distrito, hora o tipo de comercio para consultas rápidas y actualización diaria. |

## 1.2 Teorema CAP

| Componente | Combinación CAP | Propiedad sacrificada | ¿Por qué ese sacrificio es correcto o incorrecto para este caso? |
|---|---|---|---|
| Core de pagos (débito/crédito de saldos) | CP | Disponibilidad | Es preferible rechazar o pausar una operación antes que confirmar un pago con saldo inconsistente. Para dinero, la consistencia es obligatoria: no se debe duplicar, perder ni acreditar incorrectamente una transacción. |
| Historial “mis últimas 50 transacciones” | AP | Consistencia fuerte inmediata | Es aceptable que el historial tarde segundos en reflejar una transacción reciente. El usuario puede ver datos eventualmente consistentes, pero el sistema debe seguir disponible y responder rápido. |

## 1.3 NewSQL

### a) ¿Qué limitación de Oracle resuelve CockroachDB al escalar de 15M a 50M usuarios?

Resuelve la limitación de escalamiento horizontal del core transaccional. En una arquitectura Oracle tradicional, aumentar capacidad suele depender de escalar verticalmente o de particionamientos complejos. CockroachDB distribuye datos y carga entre nodos, manteniendo SQL y transacciones ACID.

### b) ¿Por qué MongoDB NO puede reemplazar a Oracle para el procesamiento de pagos aunque también escala horizontalmente?

MongoDB es excelente para documentos flexibles, pero el core de pagos necesita transacciones financieras con consistencia fuerte, aislamiento y control estricto de débito/crédito entre cuentas. Aunque MongoDB soporta transacciones, no es la opción natural para un ledger financiero crítico donde el modelo relacional, restricciones, ACID distribuido y consistencia serializable son centrales.

### c) ¿Qué mecanismo técnico usa CockroachDB para mantener ACID en múltiples nodos distribuidos?

**Raft consensus**.
