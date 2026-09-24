# SurveyFlow CX — Guide de démarrage

## Prérequis
- Python 3.10+
- Node.js 18+
- PostgreSQL 14+

---

## 1. Backend (Django)

```bash
cd surveyflow-cx/backend

# Copier la config
copy .env.example .env
# Éditer .env avec vos paramètres PostgreSQL

# Installer les dépendances
pip install -r requirements.txt

# Créer la base de données PostgreSQL
# (dans psql) CREATE DATABASE surveyflow_db;

# Migrations
python manage.py makemigrations
python manage.py migrate

# Créer un superadmin
python manage.py createsuperuser

# Démarrer
python manage.py runserver
```

API disponible sur : http://localhost:8000/api/

---

## 2. Frontend (Vue.js)

```bash
cd surveyflow-cx/frontend

npm install
npm run dev
```

Application disponible sur : http://localhost:5173/

---

## Structure du projet

```
surveyflow-cx/
├── backend/
│   ├── apps/
│   │   ├── auth_app/       # Authentification JWT + gestion utilisateurs
│   │   ├── imports/        # Upload, analyse SurveyMonkey, nettoyage
│   │   ├── joins/          # Moteur de jointure + correspondance intelligente
│   │   ├── history/        # Historisation + journaux d'activité
│   │   ├── exports/        # Export XLSX/CSV + backlog
│   │   └── dashboard/      # Statistiques Agent/Manager/Admin
│   └── config/             # Settings Django
└── frontend/
    └── src/
        ├── views/          # Pages principales
        ├── components/     # Composants réutilisables
        ├── stores/         # Pinia (état global)
        └── router/         # Routes Vue Router
```

---

## Flux utilisateur typique (VOC EBU)

1. **Connexion** → `/login`
2. **Import** → `/import` — glisser le fichier SURVEY VOC EBU_202549.xlsx
3. **Configuration** → `/import/:id/configure`
   - Détection automatique des 2 lignes d'en-tête SurveyMonkey
   - Suppression colonnes système (IP, dates, collector_id…)
   - Renommage des colonnes métier
4. **Jointure** → `/import/:id/join`
   - Importer listedetickets.xlsx comme fichier de référence
   - Correspondance automatique N° REC ↔ N°REC détectée
   - Sélectionner colonnes à importer (STATUT, SLA, MOTIF…)
5. **Export** → fichier enrichi XLSX ou CSV
6. **Historique** → `/history` — backlog cumulatif par période
