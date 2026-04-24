# Kit complet d'implémentation — Détection d'anomalies administratives et financières

Ce kit met en œuvre le besoin décrit dans le sujet : détecter plus tôt les anomalies administratives ou financières, sécuriser la qualité de la chaîne de transformation, et produire un tableau d'alertes priorisées avec justification, historique, statut de traitement et criticité.

## Contenu du kit

- `docs/Kit_Implementation_Anomalies_MOA_MOE.docx` : dossier de cadrage, architecture, MOA/MOE, recette, exploitation
- `workbook/Registre_Anomalies_et_Recette.xlsx` : registre opérationnel prêt pour Google Sheets
- `data/*.csv` : jeux de données source, règles, mapping, cas de recette, alertes
- `src/detect_anomalies.py` : moteur de détection des anomalies
- `src/app_streamlit.py` : application interactive Streamlit
- `sql/schema_duckdb_sqlite.sql` : schéma SQL
- `sql/anomaly_detection_queries.sql` : requêtes SQL de détection
- `notebooks/colab_demo.ipynb` : notebook prêt pour Google Colab
- `config/thresholds.json` : seuils et paramètres
- `deployment/requirements.txt` : dépendances Python

## Jeux de données fournis

- `students.csv` : référentiel scolarité
- `payments.csv` : paiements
- `grades.csv` : notes
- `hr_staff.csv` : référentiel RH / centres de coûts
- `finance_transactions.csv` : écritures financières
- `alerts_output.csv` : alertes calculées
- `cas_recette.csv` : scénarios de recette
- `regles_detection.csv` : règles de contrôle
- `mapping_departements.csv` : mapping métier

## Démarrage ultra-rapide

### Option A — Google Colab
1. Ouvrir Google Colab.
2. Importer `notebooks/colab_demo.ipynb`.
3. Téléverser le dossier `data/`.
4. Exécuter toutes les cellules.
5. Télécharger le fichier `alerts_output.csv` généré.

### Option B — Streamlit local ou Community Cloud
1. Créer un dépôt GitHub.
2. Copier dans le dépôt les dossiers `src/`, `data/`, `config/`, `deployment/`.
3. Renommer `deployment/requirements.txt` en `requirements.txt` à la racine ou copier son contenu.
4. En local :
   ```bash
   pip install -r deployment/requirements.txt
   streamlit run src/app_streamlit.py
   ```
5. Sur Streamlit Community Cloud :
   - connecter GitHub,
   - choisir le dépôt,
   - choisir le fichier principal `src/app_streamlit.py`,
   - déployer.

### Option C — Google Sheets
1. Créer un classeur Google Sheets.
2. Importer `workbook/Registre_Anomalies_et_Recette.xlsx`.
3. Partager avec MOA, MOE, finance, scolarité.
4. Mettre à jour les colonnes de validation et de traitement des alertes.

### Option D — SQL interactif dans le navigateur
1. Ouvrir DuckDB Web Shell.
2. Importer les CSV du dossier `data/`.
3. Exécuter les scripts `sql/schema_duckdb_sqlite.sql` puis `sql/anomaly_detection_queries.sql`.

## Commandes Python

```bash
python src/detect_anomalies.py --data_dir data --output data/alerts_output.csv --config config/thresholds.json
```

## Résultat attendu

Le pipeline livre un tableau d'alertes priorisées avec :
- identifiant d'alerte
- type d'anomalie
- niveau de criticité
- justification
- système source
- action recommandée
- rôle propriétaire
- statut de traitement
- note historique

## Bonnes pratiques d'exploitation

- Valider les règles avec la MOA avant industrialisation.
- Versionner les seuils dans `config/thresholds.json`.
- Journaliser les statuts de traitement dans le classeur partagé.
- Conserver une piste d'audit entre source, règle, alerte, décision de traitement.

## Résumé des anomalies générées dans l'échantillon

```json
{
  "generated_on": "2026-04-22",
  "students_rows": 42,
  "payments_rows": 85,
  "grades_rows": 126,
  "finance_rows": 87,
  "alerts_rows": 13,
  "severities": {
    "HIGH": 9,
    "CRITICAL": 3,
    "MEDIUM": 1
  }
}
```
