import sqlite3
import os
from neo4j import GraphDatabase

# --- CONFIGURATION ---
SQLITE_DB = "crimes_france_enrichie.db"
NEO4J_URI = "bolt://localhost:7687"
NEO4J_USER = "neo4j"
NEO4J_PWD = "azerty123!"

class Neo4jMigrator:
    def __init__(self, uri, user, password):
        self.driver = GraphDatabase.driver(uri, auth=(user, password))

    def close(self):
        self.driver.close()

    def query(self, cypher, parameters=None):
        with self.driver.session() as session:
            session.run(cypher, parameters)

    def migrate(self, sqlite_conn):
        cursor = sqlite_conn.cursor()

        print("1. Création des contraintes et index...")
        self.query("CREATE CONSTRAINT IF NOT EXISTS FOR (r:Region) REQUIRE r.nom IS UNIQUE")
        self.query("CREATE CONSTRAINT IF NOT EXISTS FOR (d:Departement) REQUIRE d.code IS UNIQUE")
        self.query("CREATE CONSTRAINT IF NOT EXISTS FOR (c:Crime) REQUIRE c.code IS UNIQUE")
        self.query("CREATE CONSTRAINT IF NOT EXISTS FOR (cat:Categorie) REQUIRE cat.nom IS UNIQUE")
        self.query("CREATE INDEX IF NOT EXISTS FOR (s:Service) ON (s.nom)")

        print("2. Migration des Régions et Départements...")
        cursor.execute("""
            SELECT r.nom_region, d.code_dept, d.nom_dept 
            FROM T_DEPARTEMENT d 
            JOIN T_REGION r ON d.id_region = r.id_region
        """)
        for reg_nom, dept_code, dept_nom in cursor.fetchall():
            self.query("""
                MERGE (r:Region {nom: $reg_nom})
                MERGE (d:Departement {code: $dept_code})
                SET d.nom = $dept_nom
                MERGE (d)-[:APPARTIENT_A]->(r)
            """, {"reg_nom": reg_nom, "dept_code": str(dept_code), "dept_nom": dept_nom})

        print("3. Migration des Services (Lien Géo)...")
        # On crée le Service et on le lie au Département
        cursor.execute("SELECT nom_service, force_ordre, code_dept FROM T_SERVICE")
        for nom, force, code_dept in cursor.fetchall():
            self.query("""
                MERGE (s:Service {nom: $nom, force: $force})
                WITH s
                MATCH (d:Departement {code: $code_dept})
                MERGE (s)-[:SITUE_DANS]->(d)
            """, {"nom": nom, "force": force, "code_dept": str(code_dept)})

        print("4. Migration des Catégories et Crimes...")
        cursor.execute("""
            SELECT c.code_index, c.libelle_index, cat.nom_cat 
            FROM T_CRIME c 
            JOIN T_CATEGORIE_CRIME cat ON c.id_cat = cat.id_cat
        """)
        for code, libelle, cat_nom in cursor.fetchall():
            self.query("""
                MERGE (cat:Categorie {nom: $cat_nom})
                MERGE (c:Crime {code: $code})
                SET c.libelle = $libelle
                MERGE (c)-[:TYPE_DE]->(cat)
            """, {"cat_nom": cat_nom, "code": str(code), "libelle": libelle})

        print("5. Migration des Faits (Relations A_ENREGISTRE)...")
        cursor.execute("""
            SELECT s.nom_service, s.force_ordre, c.code_index, f.annee, f.nombre 
            FROM T_FAIT f
            JOIN T_SERVICE s ON f.id_service = s.id_service
            JOIN T_CRIME c ON f.id_crime = c.id_crime
        """)
        facts = cursor.fetchall()
        
        # Batching pour performance (evite MemoryPool Error)
        batch_query = """
            UNWIND $batch AS row
            MATCH (s:Service {nom: row.nom, force: row.force})
            MATCH (c:Crime {code: row.code})
            CREATE (s)-[:A_ENREGISTRE {annee: row.annee, nombre: row.nb}]->(c)
        """
        
        batch = [{"nom": f[0], "force": f[1], "code": str(f[2]), "annee": int(f[3]), "nb": int(f[4])} for f in facts]
        
        for i in range(0, len(batch), 1000):
            self.query(batch_query, {"batch": batch[i:i+1000]})
            print(f"   -> {min(i + 1000, len(batch))} faits migrés...")

        print("6. Migration des relations d'adjacence (Voisinage)...")
        try:
            cursor.execute("SELECT code_dept1, code_dept2 FROM T_ADJACENCE")
            adjacences = cursor.fetchall()
            for c1, c2 in adjacences:
                self.query("""
                    MATCH (d1:Departement {code: $c1})
                    MATCH (d2:Departement {code: $c2})
                    MERGE (d1)-[:TOUCHE]-(d2)
                """, {"c1": str(c1), "c2": str(c2)})
            print(f"   -> {len(adjacences)} relations de voisinage créées.")
        except sqlite3.OperationalError:
            print("   -> Table T_ADJACENCE absente, étape ignorée.")

if __name__ == "__main__":
    if not os.path.exists(SQLITE_DB):
        print(f"Erreur : {SQLITE_DB} introuvable.")
    else:
        sqlite_conn = sqlite3.connect(SQLITE_DB)
        migrator = Neo4jMigrator(NEO4J_URI, NEO4J_USER, NEO4J_PWD)
        try:
            migrator.migrate(sqlite_conn)
            print("\n--- MIGRATION VERS NEO4J RÉUSSIE ---")
        finally:
            migrator.close()
            sqlite_conn.close()