# P4_docker.py
# Conexión Python a MongoDB local ejecutándose en Docker Desktop

from pymongo import MongoClient


class DockerMongoConnection:
    """Administra la conexión a MongoDB en contenedor Docker local."""

    def __init__(self, uri="mongodb://admin:yape2026@localhost:27017/",
                 db_name="yape_local", collection_name="comerciantes_test"):
        self.uri = uri
        self.db_name = db_name
        self.collection_name = collection_name
        self.client = None
        self.db = None
        self.collection = None

    def connect(self):
        self.client = MongoClient(self.uri, authSource="admin")
        self.db = self.client[self.db_name]
        self.collection = self.db[self.collection_name]
        return self.collection


class DockerMerchantTestRepository:
    """Repositorio de pruebas para insertar y validar comerciantes locales."""

    def __init__(self, collection):
        self.collection = collection

    def insert_test_merchant(self):
        return self.collection.insert_one({
            "nombre_comercio": "Bodega Test Docker",
            "tipo": "bodega",
            "distrito": "Lima",
            "monto_mensual_soles": 1500.00,
            "yape_activo": True,
            "entorno": "docker_local"
        })

    def find_test_merchant(self):
        return self.collection.find_one({"nombre_comercio": "Bodega Test Docker"})

    def count_documents(self):
        return self.collection.count_documents({})


def main():
    connection = DockerMongoConnection()
    col_local = connection.connect()

    repository = DockerMerchantTestRepository(col_local)
    repository.insert_test_merchant()
    doc = repository.find_test_merchant()

    print("✅ Documento guardado en MongoDB Docker:")
    print(f"   Nombre:   {doc['nombre_comercio']}")
    print(f"   Entorno:  {doc['entorno']}")
    print(f"   ID:       {doc['_id']}")
    print(f"\nTotal documentos en Docker: {repository.count_documents()}")


if __name__ == "__main__":
    main()
