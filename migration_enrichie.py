import pandas as pd
import sqlite3
import re
import os

# --- CONFIGURATION ---
FICHIER_EXCEL = "crimes-et-delits.xlsx"
DB_NAME = "crimes_france_enrichie.db"

# --- DONNEES STATIQUES ---
REGIONS_MAP = {
    'Auvergne-Rhône-Alpes': ['01', '03', '07', '15', '26', '38', '42', '43', '63', '69', '73', '74'],
    'Bourgogne-Franche-Comté': ['21', '25', '39', '58', '70', '71', '89', '90'],
    'Bretagne': ['22', '29', '35', '56'],
    'Centre-Val de Loire': ['18', '28', '36', '37', '41', '45'],
    'Corse': ['2A', '2B'],
    'Grand Est': ['08', '10', '51', '52', '54', '55', '57', '67', '68', '88'],
    'Hauts-de-France': ['02', '59', '60', '62', '80'],
    'Île-de-France': ['75', '77', '78', '91', '92', '93', '94', '95'],
    'Normandie': ['14', '27', '50', '61', '76'],
    'Nouvelle-Aquitaine': ['16', '17', '19', '23', '24', '33', '40', '47', '64', '79', '86', '87'],
    'Occitanie': ['09', '11', '12', '30', '31', '32', '34', '46', '48', '65', '66', '81', '82'],
    'Pays de la Loire': ['44', '49', '53', '72', '85'],
    'Provence-Alpes-Côte d\'Azur': ['04', '05', '06', '13', '83', '84'],
    'Outre-Mer': ['971', '972', '973', '974', '976', '978', '987', '988', '986']
}

DEPT_TO_REGION = {d: region for region, depts in REGIONS_MAP.items() for d in depts}

DEPT_NOMS = {
    '01': 'Ain', '02': 'Aisne', '03': 'Allier', '04': 'Alpes-de-Haute-Provence', '05': 'Hautes-Alpes',
    '06': 'Alpes-Maritimes', '07': 'Ardèche', '08': 'Ardennes', '09': 'Ariège', '10': 'Aube',
    '11': 'Aude', '12': 'Aveyron', '13': 'Bouches-du-Rhône', '14': 'Calvados', '15': 'Cantal',
    '16': 'Charente', '17': 'Charente-Maritime', '18': 'Cher', '19': 'Corrèze', '2A': 'Corse-du-Sud',
    '2B': 'Haute-Corse', '21': 'Côte-d\'Or', '22': 'Côtes-d\'Armor', '23': 'Creuse', '24': 'Dordogne',
    '25': 'Doubs', '26': 'Drôme', '27': 'Eure', '28': 'Eure-et-Loir', '29': 'Finistère',
    '30': 'Gard', '31': 'Haute-Garonne', '32': 'Gers', '33': 'Gironde', '34': 'Hérault',
    '35': 'Ille-et-Vilaine', '36': 'Indre', '37': 'Indre-et-Loire', '38': 'Isère', '39': 'Jura',
    '40': 'Landes', '41': 'Loir-et-Cher', '42': 'Loire', '43': 'Haute-Loire', '44': 'Loire-Atlantique',
    '45': 'Loiret', '46': 'Lot', '47': 'Lot-et-Garonne', '48': 'Lozère', '49': 'Maine-et-Loire',
    '50': 'Manche', '51': 'Marne', '52': 'Haute-Marne', '53': 'Mayenne', '54': 'Meurthe-et-Moselle',
    '55': 'Meuse', '56': 'Morbihan', '57': 'Moselle', '58': 'Nièvre', '59': 'Nord',
    '60': 'Oise', '61': 'Orne', '62': 'Pas-de-Calais', '63': 'Puy-de-Dôme', '64': 'Pyrénées-Atlantiques',
    '65': 'Hautes-Pyrénées', '66': 'Pyrénées-Orientales', '67': 'Bas-Rhin', '68': 'Haut-Rhin', '69': 'Rhône',
    '70': 'Haute-Saône', '71': 'Saône-et-Loire', '72': 'Sarthe', '73': 'Savoie', '74': 'Haute-Savoie',
    '75': 'Paris', '76': 'Seine-Maritime', '77': 'Seine-et-Marne', '78': 'Yvelines', '79': 'Deux-Sèvres',
    '80': 'Somme', '81': 'Tarn', '82': 'Tarn-et-Garonne', '83': 'Var', '84': 'Vaucluse',
    '85': 'Vendée', '86': 'Vienne', '87': 'Haute-Vienne', '88': 'Vosges', '89': 'Yonne',
    '90': 'Territoire de Belfort', '91': 'Essonne', '92': 'Hauts-de-Seine', '93': 'Seine-Saint-Denis', '94': 'Val-de-Marne',
    '95': 'Val-d\'Oise', '971': 'Guadeloupe', '972': 'Martinique', '973': 'Guyane', '974': 'La Réunion',
    '976': 'Mayotte', '978': 'Saint-Martin','986': 'Wallis-et-Futuna', '987': 'Polynésie française', '988': 'Nouvelle-Calédonie'
}

ADJACENCES = {
    '01': ['38', '39', '69', '71', '73', '74'], '02': ['08', '51', '59', '60', '77', '80'],
    '03': ['18', '23', '42', '58', '63', '71'], '04': ['05', '06', '13', '26', '83', '84'],
    '05': ['04', '26', '38', '73'], '06': ['04', '83'], '07': ['26', '30', '38', '42', '43', '48', '84'],
    '08': ['02', '51', '55'], '09': ['11', '31', '66'], '10': ['21', '51', '52', '77', '89'],
    '11': ['09', '31', '34', '66', '81'], '12': ['15', '30', '34', '46', '48', '81', '82'],
    '13': ['04', '30', '83', '84'], '14': ['27', '50', '61'], '15': ['12', '19', '43', '46', '48', '63'],
    '16': ['17', '24', '79', '86', '87'], '17': ['16', '24', '33', '79', '85'],
    '18': ['03', '18', '21', '23', '36', '41', '45', '58'], '19': ['15', '23', '24', '46', '63', '87'],
    '21': ['10', '39', '52', '58', '70', '71', '89'], '22': ['29', '35', '56'],
    '23': ['03', '18', '19', '36', '63', '87'], '24': ['16', '17', '19', '33', '46', '47', '87'],
    '25': ['39', '70', '90'], '26': ['04', '05', '07', '38', '84'], '27': ['14', '28', '60', '61', '76', '78', '95'],
    '28': ['27', '41', '45', '61', '72', '78', '91'], '29': ['22', '56'], '30': ['07', '12', '13', '34', '48', '84'],
    '31': ['09', '11', '32', '65', '81', '82'], '32': ['31', '40', '47', '64', '65', '82'],
    '33': ['17', '24', '40', '47'], '34': ['11', '12', '30', '81'], '35': ['22', '44', '49', '50', '53', '56'],
    '36': ['18', '23', '37', '41', '86', '87'], '37': ['36', '41', '49', '72', '86'],
    '38': ['01', '05', '07', '26', '42', '69', '73'], '39': ['01', '21', '25', '70', '71'],
    '40': ['32', '33', '47', '64'], '41': ['18', '28', '36', '37', '45', '72'],
    '42': ['03', '07', '38', '43', '63', '69', '71'], '43': ['07', '15', '42', '48', '63'],
    '44': ['35', '49', '56', '85'], '45': ['18', '28', '41', '58', '77', '89', '91'],
    '46': ['12', '15', '19', '24', '47', '82'], '47': ['24', '32', '33', '40', '46', '82'],
    '48': ['07', '12', '15', '30', '43'], '49': ['35', '37', '44', '53', '72', '79', '85'],
    '50': ['14', '35', '53', '61'], '51': ['02', '08', '10', '52', '55', '77'],
    '52': ['10', '21', '51', '54', '55', '70', '88'], '53': ['35', '49', '50', '61', '72'],
    '54': ['52', '55', '57', '67', '88'], '55': ['08', '51', '52', '54'],
    '56': ['22', '29', '35', '44'], '57': ['54', '67'], '58': ['03', '18', '21', '45', '71', '89'],
    '59': ['02', '62', '80'], '60': ['02', '27', '76', '77', '80', '95'],
    '61': ['14', '27', '28', '50', '53', '72'], '62': ['59', '80'],
    '63': ['03', '15', '19', '23', '42', '43'], '64': ['32', '40', '65'],
    '65': ['31', '32', '64'], '66': ['09', '11'], '67': ['54', '57', '68'], '68': ['67', '70', '88', '90'],
    '69': ['01', '38', '42', '71'], '70': ['21', '25', '39', '52', '68', '88', '90'],
    '71': ['01', '03', '21', '39', '42', '58', '69'], '72': ['28', '37', '41', '49', '53', '61'],
    '73': ['01', '05', '38', '74'], '74': ['01', '73'], '75': ['92', '93', '94'],
    '76': ['27', '60', '80'], '77': ['02', '10', '45', '51', '60', '89', '91', '93', '94'],
    '78': ['27', '28', '91', '92', '95'], '79': ['16', '17', '49', '85', '86'],
    '80': ['02', '59', '60', '62', '76'], '81': ['11', '12', '31', '34', '82'],
    '82': ['12', '31', '32', '46', '47', '81'], '83': ['04', '06', '13', '84'],
    '84': ['04', '07', '13', '26', '30', '83'], '85': ['17', '44', '49', '79'],
    '86': ['16', '36', '37', '49', '79', '87'], '87': ['16', '19', '23', '24', '36', '86'],
    '88': ['52', '54', '67', '68', '70', '90'], '89': ['10', '21', '45', '58', '77'],
    '90': ['25', '68', '70', '88'], '91': ['28', '45', '77', '78', '92', '94'],
    '92': ['75', '78', '91', '93', '94', '95'], '93': ['75', '77', '92', '94', '95'],
    '94': ['75', '77', '91', '92', '93'], '95': ['27', '60', '78', '92', '93'],
    '2A': ['2B'], '2B': ['2A'],
    '971': [], '972': [], '973': [], '974': [], '976': []
}

def detecter_categorie(libelle):
    lib = libelle.lower()
    if 'vol' in lib or 'cambriolage' in lib: return 'Vols et Cambriolages'
    if 'violence' in lib or 'coups' in lib or 'homicide' in lib: return 'Violences Physiques'
    if 'escroquerie' in lib or 'abus de confiance' in lib: return 'Escroqueries et Délits Financiers'
    if 'stupéfiant' in lib or 'drogue' in lib: return 'Stupéfiants'
    if 'dégradations' in lib or 'destructions' in lib or 'incendies' in lib: return 'Dégradations'
    if 'sexuelle' in lib or 'viol' in lib: return 'Violences Sexuelles'
    return 'Autres Crimes et Délits'

def init_db():
    if os.path.exists(DB_NAME): os.remove(DB_NAME)
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    script = """
    CREATE TABLE T_REGION (id_region INTEGER PRIMARY KEY AUTOINCREMENT, nom_region VARCHAR(100) UNIQUE);
    CREATE TABLE T_CATEGORIE_CRIME (id_cat INTEGER PRIMARY KEY AUTOINCREMENT, nom_cat VARCHAR(100) UNIQUE);
    CREATE TABLE T_DEPARTEMENT (code_dept VARCHAR(5) PRIMARY KEY, nom_dept VARCHAR(100), id_region INTEGER, FOREIGN KEY(id_region) REFERENCES T_REGION(id_region));
    CREATE TABLE T_CRIME (id_crime INTEGER PRIMARY KEY AUTOINCREMENT, code_index VARCHAR(10), libelle_index VARCHAR(255), id_cat INTEGER, UNIQUE(code_index), FOREIGN KEY(id_cat) REFERENCES T_CATEGORIE_CRIME(id_cat));
    CREATE TABLE T_SERVICE (id_service INTEGER PRIMARY KEY AUTOINCREMENT, nom_service VARCHAR(255), type_service VARCHAR(50), force_ordre VARCHAR(10), code_dept VARCHAR(5), UNIQUE(nom_service, code_dept, force_ordre), FOREIGN KEY(code_dept) REFERENCES T_DEPARTEMENT(code_dept));
    CREATE TABLE T_FAIT (id_fait INTEGER PRIMARY KEY AUTOINCREMENT, annee INTEGER, nombre INTEGER, id_service INTEGER, id_crime INTEGER, FOREIGN KEY(id_service) REFERENCES T_SERVICE(id_service), FOREIGN KEY(id_crime) REFERENCES T_CRIME(id_crime));
    CREATE TABLE T_ADJACENCE (code_dept1 VARCHAR(5), code_dept2 VARCHAR(5), PRIMARY KEY (code_dept1, code_dept2), FOREIGN KEY (code_dept1) REFERENCES T_DEPARTEMENT(code_dept), FOREIGN KEY (code_dept2) REFERENCES T_DEPARTEMENT(code_dept));
    """
    cursor.executescript(script)
    for reg in REGIONS_MAP.keys():
        cursor.execute("INSERT OR IGNORE INTO T_REGION (nom_region) VALUES (?)", (reg,))
    conn.commit()
    return conn

def process_excel(conn):
    xls = pd.ExcelFile(FICHIER_EXCEL)
    cursor = conn.cursor()
    region_ids = {row[0]: row[1] for row in cursor.execute("SELECT nom_region, id_region FROM T_REGION").fetchall()}
    cat_map = {}

    for sheet_name in xls.sheet_names:
        force = "PN" if "PN" in sheet_name else "GN" if "GN" in sheet_name else None
        if not force: continue
        match = re.search(r'\d{4}', sheet_name)
        annee = int(match.group()) if match else 2012
        
        df = pd.read_excel(xls, sheet_name=sheet_name, header=None).fillna('')
        depts_raw = df.iloc[0, 2:].values
        data_start = 3 if force == "PN" else 2
        types = df.iloc[1, 2:].values if force == "PN" else ["Gendarmerie"] * len(depts_raw)
        noms = df.iloc[data_start-1, 2:].values
            
        service_col_map = {}
        for i, nom in enumerate(noms):
            if nom == '': continue
            # Nettoyage du code département (Gestion 2A/2B et 01)
            c_raw = str(depts_raw[i]).strip()
            if '.' in c_raw: c_raw = c_raw.split('.')[0]
            code_dept = c_raw.zfill(2) if c_raw.isdigit() else c_raw
            
            # Insertion département avec vrai nom
            id_reg = region_ids.get(DEPT_TO_REGION.get(code_dept, 'Outre-Mer'))
            cursor.execute("INSERT OR IGNORE INTO T_DEPARTEMENT (code_dept, nom_dept, id_region) VALUES (?, ?, ?)", 
                           (code_dept, DEPT_NOMS.get(code_dept, f"Département {code_dept}"), id_reg))
            
            # Insertion Service
            cursor.execute("INSERT OR IGNORE INTO T_SERVICE (nom_service, type_service, force_ordre, code_dept) VALUES (?, ?, ?, ?)", 
                           (str(nom), str(types[i]), force, code_dept))
            cursor.execute("SELECT id_service FROM T_SERVICE WHERE nom_service=? AND code_dept=? AND force_ordre=?", (str(nom), code_dept, force))
            service_col_map[i] = cursor.fetchone()[0]
            
        for _, row in df.iloc[data_start:].iterrows():
            code_idx, libelle = str(row.iloc[0]), str(row.iloc[1])
            if code_idx == '' or 'index' in code_idx.lower() or 'libellé' in libelle.lower(): continue
            
            cat_nom = detecter_categorie(libelle)
            if cat_nom not in cat_map:
                cursor.execute("INSERT OR IGNORE INTO T_CATEGORIE_CRIME (nom_cat) VALUES (?)", (cat_nom,))
                cat_map[cat_nom] = cursor.execute("SELECT id_cat FROM T_CATEGORIE_CRIME WHERE nom_cat=?", (cat_nom,)).fetchone()[0]
            
            cursor.execute("INSERT OR IGNORE INTO T_CRIME (code_index, libelle_index, id_cat) VALUES (?, ?, ?)", (code_idx, libelle, cat_map[cat_nom]))
            id_crime = cursor.execute("SELECT id_crime FROM T_CRIME WHERE code_index=?", (code_idx,)).fetchone()[0]
            
            for col_idx, val in enumerate(row.iloc[2:].values):
                if col_idx in service_col_map:
                    try:
                        nb = int(float(val))
                        if nb > 0: cursor.execute("INSERT INTO T_FAIT (annee, nombre, id_service, id_crime) VALUES (?, ?, ?, ?)", (annee, nb, service_col_map[col_idx], id_crime))
                    except: continue
    conn.commit()

def enrichir_adjacences(conn):
    cursor = conn.cursor()
    adj_list = [(d, v) for d, voisins in ADJACENCES.items() for v in voisins]
    cursor.executemany("INSERT OR IGNORE INTO T_ADJACENCE VALUES (?, ?)", adj_list)
    conn.commit()

if __name__ == "__main__":
    connection = init_db()
    process_excel(connection)
    enrichir_adjacences(connection)
    connection.close()
    print("Migration SQLite terminée : Noms réels, Adjacences et Services rétablis.")