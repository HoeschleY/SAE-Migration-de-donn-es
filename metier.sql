/* ==========================================================================
   SCRIPT SQL - VALIDATION MÉTIER (SQLITE)
   Ce script contient 10 requêtes pour l'analyse des crimes et délits.
   ==========================================================================
*/

-- 1. Classement des départements par volume total de crimes (toutes années)
SELECT d.nom_dept, SUM(f.nombre) as total 
FROM T_FAIT f 
JOIN T_SERVICE s ON f.id_service = s.id_service 
JOIN T_DEPARTEMENT d ON s.code_dept = d.code_dept 
GROUP BY d.nom_dept 
ORDER BY total DESC;

-- 2. Top 5 des crimes les plus fréquents dans le département 'Ain'
SELECT c.libelle_index, SUM(f.nombre) as total 
FROM T_FAIT f 
JOIN T_CRIME c ON f.id_crime = c.id_crime 
JOIN T_SERVICE s ON f.id_service = s.id_service 
JOIN T_DEPARTEMENT d ON s.code_dept = d.code_dept 
WHERE d.nom_dept = 'Ain' 
GROUP BY c.libelle_index 
ORDER BY total DESC 
LIMIT 5;

-- 3. Volume total de crimes par Région
SELECT r.nom_region, SUM(f.nombre) as total 
FROM T_FAIT f 
JOIN T_SERVICE s ON f.id_service = s.id_service 
JOIN T_DEPARTEMENT d ON s.code_dept = d.code_dept 
JOIN T_REGION r ON d.id_region = r.id_region 
GROUP BY r.nom_region 
ORDER BY total DESC;

-- 4. Répartition du nombre de services (Police vs Gendarmerie) par Région
SELECT r.nom_region, s.force_ordre, COUNT(s.id_service) as nb_services 
FROM T_SERVICE s 
JOIN T_DEPARTEMENT d ON s.code_dept = d.code_dept 
JOIN T_REGION r ON d.id_region = r.id_region 
GROUP BY r.nom_region, s.force_ordre;

-- 5. Évolution annuelle du volume total de faits constatés
SELECT f.annee, SUM(f.nombre) as total_annuel
FROM T_FAIT f 
GROUP BY f.annee 
ORDER BY f.annee;

-- 6. Départements les plus touchés par la catégorie 'Vols et Cambriolages'
SELECT d.nom_dept, SUM(f.nombre) as total 
FROM T_FAIT f 
JOIN T_CRIME c ON f.id_crime = c.id_crime 
JOIN T_CATEGORIE_CRIME cat ON c.id_cat = cat.id_cat 
JOIN T_SERVICE s ON f.id_service = s.id_service 
JOIN T_DEPARTEMENT d ON s.code_dept = d.code_dept 
WHERE cat.nom_cat = 'Vols et Cambriolages' 
GROUP BY d.nom_dept 
ORDER BY total DESC;

-- 7. Distribution globale des crimes entre Police (PN) et Gendarmerie (GN)
SELECT s.force_ordre, SUM(f.nombre) as total 
FROM T_FAIT f 
JOIN T_SERVICE s ON f.id_service = s.id_service 
GROUP BY s.force_ordre;

-- 8. Top 3 des régions les plus concernées par les 'Violences Physiques'
SELECT r.nom_region, SUM(f.nombre) as total 
FROM T_FAIT f 
JOIN T_CRIME c ON f.id_crime = c.id_crime 
JOIN T_CATEGORIE_CRIME cat ON c.id_cat = cat.id_cat 
JOIN T_SERVICE s ON f.id_service = s.id_service 
JOIN T_DEPARTEMENT d ON s.code_dept = d.code_dept 
JOIN T_REGION r ON d.id_region = r.id_region 
WHERE cat.nom_cat = 'Violences Physiques' 
GROUP BY r.nom_region 
ORDER BY total DESC 
LIMIT 3;

-- 9. Identification des services ayant enregistré plus de 1000 faits en 2021
SELECT s.nom_service, SUM(f.nombre) as total 
FROM T_FAIT f 
JOIN T_SERVICE s ON f.id_service = s.id_service 
WHERE f.annee = 2021 
GROUP BY s.nom_service 
HAVING total > 1000 
ORDER BY total DESC;

-- 10. Tendance annuelle pour la catégorie 'Stupéfiants'
SELECT f.annee, SUM(f.nombre) as total_an
FROM T_FAIT f 
JOIN T_CRIME c ON f.id_crime = c.id_crime 
JOIN T_CATEGORIE_CRIME cat ON c.id_cat = cat.id_cat 
WHERE cat.nom_cat = 'Stupéfiants' 
GROUP BY f.annee 
ORDER BY f.annee;