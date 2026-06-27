# P2_databricks_yape.py
# Pipeline de transacciones Yape en Databricks Community Edition
# Arquitectura Medallion: Bronze → Silver → Gold

import numpy as np
import pandas as pd
from pyspark.sql import functions as F
from pyspark.sql.types import *

class BronzeTransactionLoader:
    """Genera y guarda el dataset sintético en la capa Bronze."""

    def __init__(self, spark_session, output_path="/FileStore/yape/bronze/transacciones"):
        self.spark = spark_session
        self.output_path = output_path

    def generate_dataset(self, n=2000, seed=42):
        np.random.seed(seed)
        distritos = ["Miraflores", "San Isidro", "SJL", "Comas", "Villa El Salvador",
                     "Los Olivos", "Surco", "Ate", "Callao", "Independencia"]
        tipos = ["persona_a_persona", "persona_a_comercio", "retiro_bcp", "recarga"]
        estados = ["completada", "completada", "completada", "rechazada", "pendiente"]

        data = {
            "id_transaccion": [f"YP{i:07d}" for i in range(1, n + 1)],
            "fecha": pd.date_range("2025-01-01", periods=n, freq="1h").strftime("%Y-%m-%d").tolist(),
            "hora": [f"{h:02d}:{m:02d}" for h, m in zip(np.random.randint(0, 24, n), np.random.randint(0, 60, n))],
            "monto_soles": np.round(np.random.exponential(45, n), 2).tolist(),
            "tipo": np.random.choice(tipos, n).tolist(),
            "distrito_origen": np.random.choice(distritos, n).tolist(),
            "estado": np.random.choice(estados, n, p=[0.75, 0.1, 0.05, 0.07, 0.03]).tolist(),
            "id_usuario": [f"USR{np.random.randint(1000, 9999)}" for _ in range(n)],
            "es_comercio": np.random.choice([True, False], n, p=[0.4, 0.6]).tolist()
        }
        return self.spark.createDataFrame(pd.DataFrame(data))

    def save(self, df):
        df.write.mode("overwrite").parquet(self.output_path)
        return df.count()


class SilverTransactionTransformer:
    """Limpia y enriquece las transacciones válidas."""

    def __init__(self, spark_session,
                 input_path="/FileStore/yape/bronze/transacciones",
                 output_path="/FileStore/yape/silver/transacciones_limpias"):
        self.spark = spark_session
        self.input_path = input_path
        self.output_path = output_path

    def read_bronze(self):
        return self.spark.read.parquet(self.input_path)

    def transform(self, df_bronze):
        return df_bronze \
            .filter(df_bronze.estado == "completada") \
            .filter(df_bronze.monto_soles > 0) \
            .withColumn("categoria_monto",
                F.when(F.col("monto_soles") < 20, "micro")
                 .when(F.col("monto_soles") < 100, "medio")
                 .otherwise("alto")) \
            .withColumn("es_hora_pico",
                F.when(F.col("hora").between("12:00", "14:00"), True)
                 .when(F.col("hora").between("18:00", "22:00"), True)
                 .otherwise(False)) \
            .withColumn("comision_yape",
                F.when(F.col("tipo") == "persona_a_comercio",
                       F.round(F.col("monto_soles") * 0.015, 2))
                 .otherwise(0.0))

    def save(self, df_silver):
        df_silver.write.mode("overwrite").parquet(self.output_path)
        return df_silver.count()


class GoldMetricsAggregator:
    """Construye métricas ejecutivas para dashboard."""

    def __init__(self, spark_session,
                 input_path="/FileStore/yape/silver/transacciones_limpias",
                 output_top="/FileStore/yape/gold/top_distritos",
                 output_commissions="/FileStore/yape/gold/ingresos_por_hora"):
        self.spark = spark_session
        self.input_path = input_path
        self.output_top = output_top
        self.output_commissions = output_commissions

    def read_silver(self):
        return self.spark.read.parquet(self.input_path)

    def create_view(self, df_silver):
        df_silver.createOrReplaceTempView("transacciones")

    def top_districts(self):
        return self.spark.sql("""
            SELECT
                distrito_origen,
                COUNT(*) AS total_transacciones,
                ROUND(SUM(monto_soles), 2) AS volumen_total_soles,
                ROUND(AVG(monto_soles), 2) AS ticket_promedio,
                SUM(CASE WHEN es_comercio THEN 1 ELSE 0 END) AS transacciones_comercio
            FROM transacciones
            GROUP BY distrito_origen
            ORDER BY total_transacciones DESC
            LIMIT 5
        """)

    def commissions_by_hour(self):
        return self.spark.sql("""
            SELECT
                SUBSTRING(hora, 1, 2) AS hora_dia,
                COUNT(*) AS num_transacciones,
                ROUND(SUM(comision_yape), 2) AS ingresos_yape_soles
            FROM transacciones
            WHERE comision_yape > 0
            GROUP BY SUBSTRING(hora, 1, 2)
            ORDER BY ingresos_yape_soles DESC
        """)

    def save_gold(self, gold_distritos, gold_comisiones):
        gold_distritos.write.mode("overwrite").parquet(self.output_top)
        gold_comisiones.write.mode("overwrite").parquet(self.output_commissions)


# =========================
# CELDA 1: Bronze
# =========================
bronze_loader = BronzeTransactionLoader(spark)
df_bronze = bronze_loader.generate_dataset()
total_bronze = bronze_loader.save(df_bronze)
print(f"✅ Bronze layer: {total_bronze} transacciones guardadas")
df_bronze.show(5)

# =========================
# CELDA 2: Silver
# =========================
silver_transformer = SilverTransactionTransformer(spark)
df_bronze = silver_transformer.read_bronze()
df_silver = silver_transformer.transform(df_bronze)
total_silver = silver_transformer.save(df_silver)
print(f"✅ Silver layer: {total_silver} transacciones válidas")
print(f"   Eliminadas: {df_bronze.count() - total_silver} (rechazadas/pendientes/monto cero)")
df_silver.groupBy("categoria_monto").count().show()

# =========================
# CELDA 3: Gold
# =========================
gold_aggregator = GoldMetricsAggregator(spark)
df_silver = gold_aggregator.read_silver()
gold_aggregator.create_view(df_silver)
gold_distritos = gold_aggregator.top_districts()
gold_comisiones = gold_aggregator.commissions_by_hour()
gold_aggregator.save_gold(gold_distritos, gold_comisiones)

print("📊 TOP 5 DISTRITOS POR VOLUMEN YAPE:")
gold_distritos.show()

print("💰 INGRESOS YAPE POR HORA (comisión comercios):")
gold_comisiones.show(5)

# =========================
# CELDA 4: Visualización
# =========================
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker

gold_distritos_pd = spark.read.parquet("/FileStore/yape/gold/top_distritos").toPandas()
gold_comisiones_pd = spark.read.parquet("/FileStore/yape/gold/ingresos_por_hora").toPandas()

fig, axes = plt.subplots(1, 2, figsize=(14, 5))
fig.suptitle("Dashboard Ejecutivo YAPE — Análisis de Transacciones", fontsize=14, fontweight='bold')

axes[0].barh(gold_distritos_pd["distrito_origen"], gold_distritos_pd["volumen_total_soles"],
             color=["#c41230", "#e63950", "#f47a8a", "#f9b4bc", "#fde8ea"])
axes[0].set_xlabel("Volumen total (S/)")
axes[0].set_title("Top 5 Distritos — Volumen de Pagos")
axes[0].xaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"S/{x:,.0f}"))

gold_comisiones_sorted = gold_comisiones_pd.sort_values("hora_dia")
axes[1].plot(gold_comisiones_sorted["hora_dia"], gold_comisiones_sorted["ingresos_yape_soles"],
             marker='o', color='#c41230', linewidth=2)
axes[1].fill_between(gold_comisiones_sorted["hora_dia"], gold_comisiones_sorted["ingresos_yape_soles"],
                     alpha=0.15, color='#c41230')
axes[1].set_xlabel("Hora del día")
axes[1].set_ylabel("Comisión recaudada (S/)")
axes[1].set_title("Ingresos Yape por Hora")
axes[1].tick_params(axis='x', rotation=45)

plt.tight_layout()
plt.savefig("/dbfs/FileStore/yape/gold/dashboard_yape.png", dpi=150, bbox_inches='tight')
plt.show()

print("✅ Dashboard guardado en /FileStore/yape/gold/dashboard_yape.png")
