import os
from merchant_repository import MongoAtlasConnection, MerchantSeeder, MerchantQueries


def print_queries(queries):
    print("=" * 55)
    print("CONSULTA 1: Comerciantes premium")
    for c in queries.premium_merchants():
        print(f"  ★ {c['nombre_comercio']} ({c['tipo']}) — {c['calificacion']}")

    print("\nCONSULTA 2: Comercios con delivery en Lima que facturan > S/10,000/mes")
    for c in queries.high_value_delivery_merchants():
        print(f"  → {c['nombre_comercio']} ({c['distrito']}): S/{c['monto_mensual_soles']:,.0f}/mes")

    print("\nCONSULTA 3: Bodegas O farmacias")
    for c in queries.bodegas_or_pharmacies():
        print(f"  → [{c['tipo']}] {c['nombre_comercio']}")

    print("\n📊 REPORTE COMERCIAL YAPE — FACTURACIÓN POR TIPO:")
    print(f"{'TIPO':<20} {'COMERCIOS':>9} {'FACTURACIÓN/MES':>16} {'RATING':>7} {'C/DELIVERY':>11}")
    print("-" * 67)

    for r in queries.billing_report_pipeline():
        print(f"{r['tipo_comercio']:<20} {r['total_comercios']:>9} "
              f"S/{r['facturacion_total']:>13,.0f} {r['calificacion_prom']:>7} "
              f"{r['con_delivery']:>11}")


if __name__ == "__main__":
    CONNECTION_STRING = (
    "mongodb+srv://giancarlosalegria39_db_user:"
    "8NzjqYu37ayHOefl@clusteryape.zectgfc.mongodb.net/"
    "?retryWrites=true&w=majority&appName=ClusterYape")   
     
    if not CONNECTION_STRING:
        raise ValueError("Debes configurar la variable de entorno MONGO_URI")

    connection = MongoAtlasConnection(CONNECTION_STRING)
    comerciantes = connection.connect()

    seeder = MerchantSeeder(comerciantes)
    seeder.reset_collection()
    seeder.insert_merchants()

    queries = MerchantQueries(comerciantes)
    print_queries(queries)