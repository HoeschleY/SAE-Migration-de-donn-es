// ==========================================================================
// SCRIPT CYPHER - VALIDATION MÉTIER (NEO4J)
// Ce script contient les 10 mêmes requêtes adaptées au modèle Graphe.
// ==========================================================================

// 1. Classement des départements par volume total de crimes (toutes années)
MATCH (d:Departement)<-[:SITUE_DANS]-(s:Service)-[f:A_ENREGISTRE]->(c:Crime) 
RETURN d.nom, sum(f.nombre) as total 
ORDER BY total DESC;

// 2. Top 5 des crimes les plus fréquents dans le département 'Ain'
MATCH (d:Departement {nom: "Ain"})<-[:SITUE_DANS]-(s:Service)-[f:A_ENREGISTRE]->(c:Crime) 
RETURN c.libelle, sum(f.nombre) as total 
ORDER BY total DESC 
LIMIT 5;

// 3. Volume total de crimes par Région
MATCH (r:Region)<-[:APPARTIENT_A]-(d:Departement)<-[:SITUE_DANS]-(s:Service)-[f:A_ENREGISTRE]->(c:Crime) 
RETURN r.nom, sum(f.nombre) as total 
ORDER BY total DESC;

// 4. Répartition du nombre de services (Police vs Gendarmerie) par Région
MATCH (r:Region)<-[:APPARTIENT_A]-(d:Departement)<-[:SITUE_DANS]-(s:Service) 
RETURN r.nom, s.force, count(s) as nb_services 
ORDER BY r.nom, s.force;

// 5. Évolution annuelle du volume total de faits constatés
MATCH ()-[f:A_ENREGISTRE]->() 
RETURN f.annee as annee, sum(f.nombre) as total_annuel 
ORDER BY annee;

// 6. Départements les plus touchés par la catégorie 'Vols et Cambriolages'
MATCH (cat:Categorie {nom: "Vols et Cambriolages"})<-[:TYPE_DE]-(c:Crime)<-[f:A_ENREGISTRE]-(s:Service)-[:SITUE_DANS]->(d:Departement) 
RETURN d.nom, sum(f.nombre) as total 
ORDER BY total DESC;

// 7. Distribution globale des crimes entre Police (PN) et Gendarmerie (GN)
MATCH (s:Service)-[f:A_ENREGISTRE]->() 
RETURN s.force, sum(f.nombre) as total;

// 8. Top 3 des régions les plus concernées par les 'Violences Physiques'
MATCH (cat:Categorie {nom: "Violences Physiques"})<-[:TYPE_DE]-(c:Crime)<-[f:A_ENREGISTRE]-(s:Service)-[:SITUE_DANS]->(d:Departement)-[:APPARTIENT_A]->(r:Region) 
RETURN r.nom, sum(f.nombre) as total 
ORDER BY total DESC 
LIMIT 3;

// 9. Identification des services ayant enregistré plus de 1000 faits en 2021
MATCH (s:Service)-[f:A_ENREGISTRE]->() 
WHERE f.annee = 2021 
WITH s, sum(f.nombre) as total 
WHERE total > 1000 
RETURN s.nom, total 
ORDER BY total DESC;

// 10. Tendance annuelle pour la catégorie 'Stupéfiants'
MATCH (cat:Categorie {nom: "Stupéfiants"})<-[:TYPE_DE]-(:Crime)<-[f:A_ENREGISTRE]-() 
RETURN f.annee as annee, sum(f.nombre) as total_an 
ORDER BY annee;