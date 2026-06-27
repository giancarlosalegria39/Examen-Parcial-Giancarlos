# P3_mongodb_atlas.py
# Base de Datos NoSQL de Comerciantes Yape en MongoDB Atlas

from pymongo import MongoClient


class MongoAtlasConnection:
    """Administra la conexión a MongoDB Atlas."""

    def __init__(self, connection_string, db_name="yape_db", collection_name="comerciantes"):
        self.connection_string = connection_string
        self.db_name = db_name
        self.collection_name = collection_name
        self.client = None
        self.db = None
        self.collection = None

    def connect(self):
        self.client = MongoClient(self.connection_string)
        self.db = self.client[self.db_name]
        self.collection = self.db[self.collection_name]
        print("✅ Conectado a MongoDB Atlas")
        print(f"   DB: {self.db.name} | Colección: {self.collection.name}")
        return self.collection


class MerchantSeeder:
    """Inserta comerciantes con esquemas flexibles."""

    @staticmethod
    def sample_merchants():
        return [
            {
                "ruc": "10456789012",
                "nombre_comercio": "Bodega La Esquina de Don Mario",
                "tipo": "bodega",
                "propietario": "Mario Quispe Condori",
                "distrito": "San Juan de Lurigancho",
                "departamento": "Lima",
                "calificacion": 4.2,
                "yape_activo": True,
                "monto_mensual_soles": 4500.00,
                "categorias": ["abarrotes", "bebidas", "snacks"],
                "horario": {"apertura": "06:00", "cierre": "22:00"},
                "acepta_delivery": False
            },
            {
                "ruc": "20512345678",
                "nombre_comercio": "Cevichería El Muelle SAC",
                "tipo": "restaurante",
                "representante_legal": "Ana Flores Rojas",
                "distrito": "Miraflores",
                "departamento": "Lima",
                "calificacion": 4.8,
                "yape_activo": True,
                "monto_mensual_soles": 28000.00,
                "carta": [
                    {"plato": "Ceviche clásico", "precio": 28.00},
                    {"plato": "Leche de tigre", "precio": 18.00},
                    {"plato": "Tiradito", "precio": 32.00}
                ],
                "capacidad_mesas": 45,
                "num_empleados": 12,
                "horario": {"apertura": "12:00", "cierre": "17:00"},
                "acepta_delivery": True,
                "plataformas_delivery": ["Rappi", "PedidosYa"]
            },
            {
                "ruc": "10789012345",
                "nombre_comercio": "Farmacia San Pablo Express",
                "tipo": "farmacia",
                "propietario": "Carlos Mendoza Ríos",
                "distrito": "Los Olivos",
                "departamento": "Lima",
                "calificacion": 4.5,
                "yape_activo": True,
                "monto_mensual_soles": 12000.00,
                "productos_destacados": ["paracetamol", "ibuprofeno", "vitaminas"],
                "horario": {"apertura": "07:00", "cierre": "23:00"},
                "venta_con_receta": True,
                "codigo_digemid": "F-2023-00456",
                "acepta_delivery": True
            },
            {
                "ruc": "10234567891",
                "nombre_comercio": "Taxi Express — Luis Tapia",
                "tipo": "taxi",
                "propietario": "Luis Tapia Salcedo",
                "distrito": "Callao",
                "departamento": "Lima",
                "calificacion": 4.0,
                "yape_activo": True,
                "monto_mensual_soles": 3200.00,
                "vehiculo": {"placa": "ABC-123", "modelo": "Toyota Yaris 2022", "capacidad": 4},
                "zonas_cobertura": ["Callao", "Bellavista", "La Perla", "Miraflores"],
                "acepta_delivery": False
            },
            {
                "ruc": "20987654321",
                "nombre_comercio": "Distribuidora Norte SAC",
                "tipo": "empresa",
                "representante_legal": "Patricia Luna Torres",
                "distrito": "Independencia",
                "departamento": "Lima",
                "calificacion": 3.9,
                "yape_activo": True,
                "monto_mensual_soles": 85000.00,
                "num_empleados": 45,
                "sectores": ["abarrotes", "limpieza", "bebidas"],
                "clientes_mayoristas": 230,
                "horario": {"apertura": "08:00", "cierre": "18:00"},
                "acepta_delivery": True,
                "zonas_despacho": ["Lima Norte", "Lima Centro"]
            }
        ]

    def __init__(self, collection):
        self.collection = collection

    def reset_collection(self):
        self.collection.delete_many({})

    def insert_merchants(self):
        merchants = self.sample_merchants()
        result = self.collection.insert_many(merchants)
        print(f"✅ {len(result.inserted_ids)} comerciantes insertados en Atlas")
        for i, id_ in enumerate(result.inserted_ids):
            print(f"   {merchants[i]['tipo'].upper()}: {id_}")
        return result.inserted_ids


class MerchantQueries:
    """Consultas operacionales y analíticas para comerciantes."""

    def __init__(self, collection):
        self.collection = collection

    def premium_merchants(self):
        return list(self.collection.find(
            {"calificacion": {"$gt": 4.3}, "yape_activo": True},
            {"nombre_comercio": 1, "tipo": 1, "calificacion": 1, "_id": 0}
        ).sort("calificacion", -1))

    def high_value_delivery_merchants(self):
        return list(self.collection.find(
            {
                "acepta_delivery": True,
                "departamento": "Lima",
                "monto_mensual_soles": {"$gt": 10000}
            },
            {"nombre_comercio": 1, "monto_mensual_soles": 1, "distrito": 1, "_id": 0}
        ))

    def bodegas_or_pharmacies(self):
        return list(self.collection.find(
            {"tipo": {"$in": ["bodega", "farmacia"]}},
            {"nombre_comercio": 1, "tipo": 1, "_id": 0}
        ))

    def billing_report_pipeline(self):
        pipeline_reporte = [
            {"$match": {"yape_activo": True, "departamento": "Lima"}},
            {"$group": {
                "_id": "$tipo",
                "total_comercios": {"$sum": 1},
                "facturacion_total": {"$sum": "$monto_mensual_soles"},
                "calificacion_prom": {"$avg": "$calificacion"},
                "con_delivery": {"$sum": {"$cond": ["$acepta_delivery", 1, 0]}}
            }},
            {"$sort": {"facturacion_total": -1}},
            {"$project": {
                "tipo_comercio": "$_id",
                "total_comercios": 1,
                "facturacion_total": 1,
                "calificacion_prom": {"$round": ["$calificacion_prom", 1]},
                "con_delivery": 1,
                "_id": 0
            }}
        ]
        return list(self.collection.aggregate(pipeline_reporte))


def print_queries(queries):
    print("=" * 55)
    print("CONSULTA 1: Comerciantes premium (calificación > 4.3 y activos)")
    for c in queries.premium_merchants():
        print(f"  ★ {c['nombre_comercio']} ({c['tipo']}) — {c['calificacion']}")

    print("\nCONSULTA 2: Comercios con delivery en Lima que facturan > S/10,000/mes")
    for c in queries.high_value_delivery_merchants():
        print(f"  → {c['nombre_comercio']} ({c['distrito']}): S/{c['monto_mensual_soles']:,.0f}/mes")

    print("\nCONSULTA 3: Bodegas O farmacias (operador $in)")
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
    # Reemplaza con tu connection string de Atlas:
    CONNECTION_STRING = "mongodb+srv://<usuario>:<password>@<cluster>.mongodb.net/"
    connection = MongoAtlasConnection(CONNECTION_STRING)
    comerciantes = connection.connect()

    seeder = MerchantSeeder(comerciantes)
    # Opcional para evitar duplicados durante pruebas:
    # seeder.reset_collection()
    seeder.insert_merchants()

    queries = MerchantQueries(comerciantes)
    print_queries(queries)
