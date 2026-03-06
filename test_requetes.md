# Rapport de Validation Métier (SQL vsCypher)
Ce document compile les 10 requêtes clés pour valider la migration de la base relationnelle (SQLite) vers le modèle Graphe (Neo4j).

## 1. Classement des départements par volume total de crimes
Objectif : Vérifier les totaux par département (toutes années confondues).

SQL

```sql
SELECT d.nom_dept, SUM(f.nombre) as total 
FROM T_FAIT f 
JOIN T_SERVICE s ON f.id_service = s.id_service 
JOIN T_DEPARTEMENT d ON s.code_dept = d.code_dept 
GROUP BY d.nom_dept 
ORDER BY total DESC
LIMIT 10;
```
Résultats

```txt
nom_dept         |total  |
-----------------+-------+
Paris            |2624819|
Nord             |1567528|
Bouches-du-Rhône |1551583|
Seine-Saint-Denis|1400269|
Rhône            |1278887|
Hauts-de-Seine   |1064364|
Val-de-Marne     | 891165|
Gironde          | 885659|
Haute-Garonne    | 875000|
Val-d'Oise       | 817864|
```

Cypher

```py
MATCH (d:Departement)<-[:SITUE_DANS]-(s:Service)-[f:A_ENREGISTRE]->()
RETURN d.nom as nom_dept, sum(f.nombre) as total
ORDER BY total DESC
LIMIT 10;
```

Résultats

```txt
╒═══════════════════╤═══════╕
│nom_dept           │total  │
╞═══════════════════╪═══════╡
│"Paris"            │2624819│
├───────────────────┼───────┤
│"Nord"             │1567528│
├───────────────────┼───────┤
│"Bouches-du-Rhône" │1551583│
├───────────────────┼───────┤
│"Seine-Saint-Denis"│1400269│
├───────────────────┼───────┤
│"Rhône"            │1278887│
├───────────────────┼───────┤
│"Hauts-de-Seine"   │1064364│
├───────────────────┼───────┤
│"Val-de-Marne"     │891165 │
├───────────────────┼───────┤
│"Gironde"          │885659 │
├───────────────────┼───────┤
│"Haute-Garonne"    │875000 │
├───────────────────┼───────┤
│"Val-d'Oise"       │817864 │
└───────────────────┴───────┘
```

## 2. Top 5 des crimes les plus fréquents dans l'Ain
Objectif : Vérifier le filtrage spécifique sur un département.

SQL

```sql
SELECT c.libelle_index, SUM(f.nombre) as total 
FROM T_FAIT f 
JOIN T_CRIME c ON f.id_crime = c.id_crime 
JOIN T_SERVICE s ON f.id_service = s.id_service 
JOIN T_DEPARTEMENT d ON s.code_dept = d.code_dept 
WHERE d.nom_dept = 'Ain' 
GROUP BY c.libelle_index 
ORDER BY total DESC 
LIMIT 5;
```

Résultats

```txt
libelle_index                                                               |total|
----------------------------------------------------------------------------+-----+
Cambriolages de locaux d'habitations principales                            |21280|
Escroqueries et abus de confiance                                           |19550|
Autres vols simples contre des particuliers dans des locaux ou lieux publics|16898|
Vols à la roulotte                                                          |15603|
Autres coups et blessures volontaires criminels ou correctionnels           |15042|
```

Cypher

```py
MATCH (d:Departement {nom: 'Ain'})<-[:SITUE_DANS]-(s:Service)-[f:A_ENREGISTRE]->(c:Crime)
RETURN c.libelle as libelle_index, sum(f.nombre) as total
ORDER BY total DESC
LIMIT 5;
```

Résultats

```txt
Table
Text
Code
╒══════════════════════════════════════════════════════════════════════╤═════╕
│c.libelle                                                             │total│
╞══════════════════════════════════════════════════════════════════════╪═════╡
│"Cambriolages de locaux d'habitations principales"                    │21280│
├──────────────────────────────────────────────────────────────────────┼─────┤
│"Escroqueries et abus de confiance"                                   │19550│
├──────────────────────────────────────────────────────────────────────┼─────┤
│"Autres vols simples contre des particuliers dans des locaux ou lieux │16898│
│publics"                                                              │     │
├──────────────────────────────────────────────────────────────────────┼─────┤
│"Vols à la roulotte"                                                  │15603│
├──────────────────────────────────────────────────────────────────────┼─────┤
│"Autres coups et blessures volontaires criminels ou correctionnels"   │15042│
└──────────────────────────────────────────────────────────────────────┴─────┘
```

## 3. Volume total de crimes par Région
Objectif : Valider l'agrégation au niveau régional.

SQL

```sql
SELECT r.nom_region, SUM(f.nombre) as total 
FROM T_FAIT f 
JOIN T_SERVICE s ON f.id_service = s.id_service 
JOIN T_DEPARTEMENT d ON s.code_dept = d.code_dept 
JOIN T_REGION r ON d.id_region = r.id_region 
GROUP BY r.nom_region 
ORDER BY total DESC;
```

Résultats

```txt
nom_region                |total  |
--------------------------+-------+
Île-de-France             |9077943|
Auvergne-Rhône-Alpes      |4067293|
Provence-Alpes-Côte d'Azur|3369805|
Hauts-de-France           |3176455|
Occitanie                 |3089204|
Nouvelle-Aquitaine        |2584759|
Grand Est                 |2413026|
Pays de la Loire          |1653005|
Normandie                 |1377920|
Outre-Mer                 |1343894|
Bretagne                  |1236490|
Bourgogne-Franche-Comté   |1128115|
Centre-Val de Loire       |1087822|
Corse                     | 140100|
```

Cypher

```py
MATCH (r:Region)<-[:APPARTIENT_A]-(d:Departement)<-[:SITUE_DANS]-(s:Service)-[f:A_ENREGISTRE]->()
RETURN r.nom as nom_region, sum(f.nombre) as total
ORDER BY total DESC;
```

Résultats

```txt
╒════════════════════════════╤═══════╕
│r.nom                       │total  │
╞════════════════════════════╪═══════╡
│"Île-de-France"             │9077943│
├────────────────────────────┼───────┤
│"Auvergne-Rhône-Alpes"      │4067293│
├────────────────────────────┼───────┤
│"Provence-Alpes-Côte d'Azur"│3369805│
├────────────────────────────┼───────┤
│"Hauts-de-France"           │3176455│
├────────────────────────────┼───────┤
│"Occitanie"                 │3089204│
├────────────────────────────┼───────┤
│"Nouvelle-Aquitaine"        │2584759│
├────────────────────────────┼───────┤
│"Grand Est"                 │2413026│
├────────────────────────────┼───────┤
│"Pays de la Loire"          │1653005│
├────────────────────────────┼───────┤
│"Normandie"                 │1377920│
├────────────────────────────┼───────┤
│"Outre-Mer"                 │1343894│
├────────────────────────────┼───────┤
│"Bretagne"                  │1236490│
├────────────────────────────┼───────┤
│"Bourgogne-Franche-Comté"   │1128115│
├────────────────────────────┼───────┤
│"Centre-Val de Loire"       │1087822│
├────────────────────────────┼───────┤
│"Corse"                     │140100 │
└────────────────────────────┴───────┘
```

## 4. Répartition des services (Police vs Gendarmerie) par Région
Objectif : Compter le nombre de nœuds Service par zone.

SQL

```sql
SELECT r.nom_region, s.force_ordre, COUNT(s.id_service) as nb_services 
FROM T_SERVICE s 
JOIN T_DEPARTEMENT d ON s.code_dept = d.code_dept 
JOIN T_REGION r ON d.id_region = r.id_region 
GROUP BY r.nom_region, s.force_ordre;
```

Résultats

```txt
nom_region                |force_ordre|nb_services|
--------------------------+-----------+-----------+
Auvergne-Rhône-Alpes      |GN         |         52|
Auvergne-Rhône-Alpes      |PN         |        127|
Bourgogne-Franche-Comté   |GN         |         23|
Bourgogne-Franche-Comté   |PN         |         33|
Bretagne                  |GN         |         19|
Bretagne                  |PN         |         25|
Centre-Val de Loire       |GN         |         21|
Centre-Val de Loire       |PN         |         26|
Corse                     |GN         |          7|
Corse                     |PN         |         13|
Grand Est                 |GN         |         42|
Grand Est                 |PN         |         90|
Hauts-de-France           |GN         |         30|
Hauts-de-France           |PN         |         85|
Normandie                 |GN         |         24|
Normandie                 |PN         |         36|
Nouvelle-Aquitaine        |GN         |         48|
...
```

Cypher

```py
MATCH (r:Region)<-[:APPARTIENT_A]-(d:Departement)<-[:SITUE_DANS]-(s:Service)
RETURN r.nom as nom_region, s.force as force_ordre, count(s) as nb_services
ORDER BY nom_region, force_ordre;
```

Résultats

```txt
╒════════════════════════════╤═══════╤═══════════╕
│r.nom                       │s.force│nb_services│
╞════════════════════════════╪═══════╪═══════════╡
│"Auvergne-Rhône-Alpes"      │"GN"   │52         │
├────────────────────────────┼───────┼───────────┤
│"Auvergne-Rhône-Alpes"      │"PN"   │127        │
├────────────────────────────┼───────┼───────────┤
│"Bourgogne-Franche-Comté"   │"GN"   │23         │
├────────────────────────────┼───────┼───────────┤
│"Bourgogne-Franche-Comté"   │"PN"   │33         │
├────────────────────────────┼───────┼───────────┤
│"Bretagne"                  │"GN"   │19         │
├────────────────────────────┼───────┼───────────┤
│"Bretagne"                  │"PN"   │25         │
├────────────────────────────┼───────┼───────────┤
│"Centre-Val de Loire"       │"GN"   │21         │
├────────────────────────────┼───────┼───────────┤
│"Centre-Val de Loire"       │"PN"   │26         │
├────────────────────────────┼───────┼───────────┤
│"Corse"                     │"GN"   │7          │
├────────────────────────────┼───────┼───────────┤
│"Corse"                     │"PN"   │13         │
├────────────────────────────┼───────┼───────────┤
│"Grand Est"                 │"GN"   │42         │
├────────────────────────────┼───────┼───────────┤
│"Grand Est"                 │"PN"   │90         │
├────────────────────────────┼───────┼───────────┤
│"Hauts-de-France"           │"GN"   │30         │
├────────────────────────────┼───────┼───────────┤
│"Hauts-de-France"           │"PN"   │85         │
├────────────────────────────┼───────┼───────────┤
│"Normandie"                 │"GN"   │24         │
├────────────────────────────┼───────┼───────────┤
│"Normandie"                 │"PN"   │36         │
├────────────────────────────┼───────┼───────────┤
│"Nouvelle-Aquitaine"        │"GN"   │48         │
...
```

## 5. Évolution annuelle du volume total de faits
Objectif : Analyse de la tendance temporelle.

SQL

```sql
SELECT f.annee, SUM(f.nombre) as total_annuel
FROM T_FAIT f 
GROUP BY f.annee 
ORDER BY f.annee;
```

Résultats

```txt
annee|total_annuel|
-----+------------+
 2012|     3477301|
 2013|     3522619|
 2014|     3574902|
 2015|     3578488|
 2016|     3550540|
 2017|     3660964|
 2018|     3671210|
 2019|     3777826|
 2020|     3327737|
 2021|     3604244|
```

Cypher

```py
MATCH ()-[f:A_ENREGISTRE]->()
RETURN f.annee as annee, sum(f.nombre) as total_annuel
ORDER BY annee;
```

Résultats

```txt
╒═════╤════════════╕
│annee│total_annuel│
╞═════╪════════════╡
│2012 │3477301     │
├─────┼────────────┤
│2013 │3522619     │
├─────┼────────────┤
│2014 │3574902     │
├─────┼────────────┤
│2015 │3578488     │
├─────┼────────────┤
│2016 │3550540     │
├─────┼────────────┤
│2017 │3660964     │
├─────┼────────────┤
│2018 │3671210     │
├─────┼────────────┤
│2019 │3777826     │
├─────┼────────────┤
│2020 │3327737     │
├─────┼────────────┤
│2021 │3604244     │
└─────┴────────────┘
```

## 6. Départements les plus touchés par 'Vols et Cambriolages'
Objectif : Valider le filtrage par catégorie de crime.

SQL

```sql
SELECT d.nom_dept, SUM(f.nombre) as total 
FROM T_FAIT f 
JOIN T_CRIME c ON f.id_crime = c.id_crime 
JOIN T_CATEGORIE_CRIME cat ON c.id_cat = cat.id_cat 
JOIN T_SERVICE s ON f.id_service = s.id_service 
JOIN T_DEPARTEMENT d ON s.code_dept = d.code_dept 
WHERE cat.nom_cat = 'Vols et Cambriolages' 
GROUP BY d.nom_dept 
ORDER BY total DESC;
```

Résultats

```txt
nom_dept               |total  |
-----------------------+-------+
Paris                  |1696476|
Bouches-du-Rhône       | 987075|
Nord                   | 920526|
Seine-Saint-Denis      | 819104|
Rhône                  | 786551|
Hauts-de-Seine         | 661493|
Haute-Garonne          | 552062|
Val-de-Marne           | 545110|
Gironde                | 542805|
...
```

Cypher

```py
MATCH (cat:Categorie {nom: 'Vols et Cambriolages'})<-[:TYPE_DE]-(c:Crime)<-[f:A_ENREGISTRE]-(s:Service)-[:SITUE_DANS]->(d:Departement)
RETURN d.nom as nom_dept, sum(f.nombre) as total
ORDER BY total DESC;
```

Résultats

```txt
╒═════════════════════════╤═══════╕
│d.nom                    │total  │
╞═════════════════════════╪═══════╡
│"Paris"                  │1696476│
├─────────────────────────┼───────┤
│"Bouches-du-Rhône"       │987075 │
├─────────────────────────┼───────┤
│"Nord"                   │920526 │
├─────────────────────────┼───────┤
│"Seine-Saint-Denis"      │819104 │
├─────────────────────────┼───────┤
│"Rhône"                  │786551 │
├─────────────────────────┼───────┤
│"Hauts-de-Seine"         │661493 │
├─────────────────────────┼───────┤
│"Haute-Garonne"          │552062 │
├─────────────────────────┼───────┤
│"Val-de-Marne"           │545110 │
├─────────────────────────┼───────┤
│"Gironde"                │542805 │
...
```

## 7. Distribution globale Police (PN) vs Gendarmerie (GN)
Objectif : Comparer les volumes enregistrés par force de l'ordre.

SQL

```sql
SELECT s.force_ordre, SUM(f.nombre) as total 
FROM T_FAIT f 
JOIN T_SERVICE s ON f.id_service = s.id_service 
GROUP BY s.force_ordre;
```

Résultats

```txt
force_ordre|total   |
-----------+--------+
GN         |11721787|
PN         |24024044|
```

Cypher

```py
MATCH (s:Service)-[f:A_ENREGISTRE]->()
RETURN s.force as force_ordre, sum(f.nombre) as total;
```

Résultats

```txt
╒═══════╤════════╕
│s.force│total   │
╞═══════╪════════╡
│"PN"   │24024044│
├───────┼────────┤
│"GN"   │11721787│
└───────┴────────┘
```

## 8. Top 3 des régions pour les 'Violences Physiques'
Objectif : Agrégation complexe (Catégorie + Région).

SQL

```sql
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
```

Résultats

```txt
nom_region          |total |
--------------------+------+
Île-de-France       |200717|
Hauts-de-France     | 90792|
Auvergne-Rhône-Alpes| 79834|
```

Cypher

```py
MATCH (cat:Categorie {nom: 'Violences Physiques'})<-[:TYPE_DE]-(c:Crime)<-[f:A_ENREGISTRE]-(s:Service)-[:SITUE_DANS]->(d:Departement)-[:APPARTIENT_A]->(r:Region)
RETURN r.nom as nom_region, sum(f.nombre) as total
ORDER BY total DESC
LIMIT 3;
```

Résultats

```txt
╒══════════════════════╤══════╕
│r.nom                 │total │
╞══════════════════════╪══════╡
│"Île-de-France"       │200717│
├──────────────────────┼──────┤
│"Hauts-de-France"     │90792 │
├──────────────────────┼──────┤
│"Auvergne-Rhône-Alpes"│79834 │
└──────────────────────┴──────┘
```

## 9. Services avec >1000 faits en 2021
Objectif : Valider les conditions granulaires (Année + Seuil).

SQL

```sql
SELECT s.nom_service, SUM(f.nombre) as total 
FROM T_FAIT f 
JOIN T_SERVICE s ON f.id_service = s.id_service 
WHERE f.annee = 2021 
GROUP BY s.nom_service 
HAVING total > 1000 
ORDER BY total DESC;
```

Résultats

```txt
nom_service                          |total |
-------------------------------------+------+
LYON AGGLOMERATION                   |100989|
CSP DE BORDEAUX                      | 55672|
DSP DE LILLE                         | 50762|
CSP DE TOULOUSE                      | 50469|
CIAT CENTRAL DE NANTES               | 39535|
DSP MARSEILLE CENTRE                 | 29585|
CIAT CENTRAL DE STRASBOURG           | 28002|
...
```

Cypher

```py
MATCH (s:Service)-[f:A_ENREGISTRE {annee: 2021}]->()
WITH s, sum(f.nombre) as total
WHERE total > 1000
RETURN s.nom as nom_service, total
ORDER BY total DESC;
```

Résultats

```txt
╒═══════════════════════════════════════╤══════╕
│s.nom                                  │total │
╞═══════════════════════════════════════╪══════╡
│"LYON AGGLOMERATION"                   │100989│
├───────────────────────────────────────┼──────┤
│"CSP DE BORDEAUX"                      │55672 │
├───────────────────────────────────────┼──────┤
│"DSP DE LILLE"                         │50762 │
├───────────────────────────────────────┼──────┤
│"CSP DE TOULOUSE"                      │50469 │
├───────────────────────────────────────┼──────┤
│"CIAT CENTRAL DE NANTES"               │39535 │
├───────────────────────────────────────┼──────┤
│"DSP MARSEILLE CENTRE"                 │29585 │
├───────────────────────────────────────┼──────┤
│"CIAT CENTRAL DE STRASBOURG"           │28002 │
...
```

## 10. Tendance annuelle pour 'Stupéfiants'
Objectif : Évolution temporelle thématique.

SQL

```sql
SELECT f.annee, SUM(f.nombre) as total_an
FROM T_FAIT f 
JOIN T_CRIME c ON f.id_crime = c.id_crime 
JOIN T_CATEGORIE_CRIME cat ON c.id_cat = cat.id_cat 
WHERE cat.nom_cat = 'Stupéfiants' 
GROUP BY f.annee 
ORDER BY f.annee;
```

Résultats

```txt
annee|total_an|
-----+--------+
 2012|  192341|
 2013|  201826|
 2014|  208971|
 2015|  209679|
 2016|  210630|
 2017|  215726|
 2018|  214566|
 2019|  206980|
 2020|  183993|
 2021|  245062|
```

Cypher

```py
MATCH (cat:Categorie {nom: 'Stupéfiants'})<-[:TYPE_DE]-(c:Crime)<-[f:A_ENREGISTRE]-()
RETURN f.annee as annee, sum(f.nombre) as total_an
ORDER BY annee;
```

Résultats

```txt
╒═════╤════════╕
│annee│total_an│
╞═════╪════════╡
│2012 │192341  │
├─────┼────────┤
│2013 │201826  │
├─────┼────────┤
│2014 │208971  │
├─────┼────────┤
│2015 │209679  │
├─────┼────────┤
│2016 │210630  │
├─────┼────────┤
│2017 │215726  │
├─────┼────────┤
│2018 │214566  │
├─────┼────────┤
│2019 │206980  │
├─────┼────────┤
│2020 │183993  │
├─────┼────────┤
│2021 │245062  │
└─────┴────────┘
```

## 11. "Criminalité chez les voisins"
Objectif : Pour un département donné (ex: le Rhône '69'), trouver le nombre total de crimes enregistrés dans tous les départements limitrophes.

SQL

```sql
SELECT d2.nom_dept AS Voisin, SUM(f.nombre) AS Total_Crimes
FROM T_ADJACENCE adj
JOIN T_DEPARTEMENT d2 ON adj.code_dept2 = d2.code_dept
JOIN T_SERVICE s ON d2.code_dept = s.code_dept
JOIN T_FAIT f ON s.id_service = f.id_service
WHERE adj.code_dept1 = '69'
GROUP BY d2.nom_dept
ORDER BY Total_Crimes DESC;
```

Résultats

```txt
Voisin        |Total_Crimes|
--------------+------------+
Isère         |      705846|
Loire         |      356506|
Ain           |      249184|
Saône-et-Loire|      194405|
```

Cypher

```py
MATCH (d1:Departement {code: '69'})-[:TOUCHE]-(voisin:Departement)
MATCH (voisin)<-[:SITUE_DANS]-(s:Service)-[f:A_ENREGISTRE]->(c:Crime)
RETURN voisin.nom AS Voisin, sum(f.nombre) AS Total_Crimes
ORDER BY Total_Crimes DESC;
```

Résultats

```txt
╒════════════════╤════════════╕
│Voisin          │Total_Crimes│
╞════════════════╪════════════╡
│"Isère"         │705846      │
├────────────────┼────────────┤
│"Loire"         │356506      │
├────────────────┼────────────┤
│"Ain"           │249184      │
├────────────────┼────────────┤
│"Saône-et-Loire"│194405      │
└────────────────┴────────────┘
```

## 12. "Propagation par catégorie"
Objectif : Lister les 5 catégories de crimes les plus fréquentes dans les départements qui touchent l'Isère ('38').

SQL

```sql
SELECT cat.nom_cat, SUM(f.nombre) AS Total
FROM T_ADJACENCE adj
JOIN T_SERVICE s ON adj.code_dept2 = s.code_dept
JOIN T_FAIT f ON s.id_service = f.id_service
JOIN T_CRIME c ON f.id_crime = c.id_crime
JOIN T_CATEGORIE_CRIME cat ON c.id_cat = cat.id_cat
WHERE adj.code_dept1 = '38'
GROUP BY cat.nom_cat
ORDER BY Total DESC
LIMIT 5;
```

Résultats

```txt
nom_cat                          |Total  |
---------------------------------+-------+
Vols et Cambriolages             |1500478|
Autres Crimes et Délits          | 480729|
Dégradations                     | 168017|
Escroqueries et Délits Financiers| 158865|
Stupéfiants                      | 148813|
```

Cypher

```py
MATCH (d:Departement {code: '38'})-[:TOUCHE]-(voisin:Departement)
MATCH (voisin)<-[:SITUE_DANS]-(:Service)-[f:A_ENREGISTRE]->(c:Crime)-[:TYPE_DE]->(cat:Categorie)
RETURN cat.nom AS Categorie, sum(f.nombre) AS Total
ORDER BY Total DESC
LIMIT 5;
```

Résultats

```txt
╒═══════════════════════════════════╤═══════╕
│Categorie                          │Total  │
╞═══════════════════════════════════╪═══════╡
│"Vols et Cambriolages"             │1500478│
├───────────────────────────────────┼───────┤
│"Autres Crimes et Délits"          │480729 │
├───────────────────────────────────┼───────┤
│"Dégradations"                     │168017 │
├───────────────────────────────────┼───────┤
│"Escroqueries et Délits Financiers"│158865 │
├───────────────────────────────────┼───────┤
│"Stupéfiants"                      │148813 │
└───────────────────────────────────┴───────┘
```