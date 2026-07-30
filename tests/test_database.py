import unittest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from backend.core.database import Base
from backend.models.prospect import ProspectoB2BModel
from backend.services.prospect_repository import (
    listar_prospectos, crear_prospecto, buscar_prospecto_por_place_id
)

class TestDatabasePersistence(unittest.TestCase):
    def setUp(self):
        # Crear base de datos en memoria para pruebas
        self.engine = create_engine("sqlite:///:memory:")
        TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)
        Base.metadata.create_all(bind=self.engine)
        self.db = TestingSessionLocal()

    def tearDown(self):
        self.db.close()

    def test_seeding_and_listing(self):
        prospectos = listar_prospectos(self.db)
        self.assertGreater(len(prospectos), 0)
        self.assertEqual(prospectos[-1].place_id, "pyme_001")

    def test_crear_y_buscar_prospecto(self):
        nuevo_datos = {
            "nombre": "Empresa Test SA",
            "ciudad_busqueda": "Mendoza, AR",
            "tipo_busqueda": "Vinos",
            "telefono": "+54 261 400-0000"
        }
        creado = crear_prospecto(self.db, nuevo_datos)
        self.assertIsNotNone(creado.place_id)
        
        buscado = buscar_prospecto_por_place_id(self.db, creado.place_id)
        self.assertIsNotNone(buscado)
        self.assertEqual(buscado.nombre, "Empresa Test SA")

if __name__ == "__main__":
    unittest.main()
