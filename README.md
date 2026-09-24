# SurveyFlow CX

**Plateforme web d'automatisation du traitement, de l'enrichissement et de l'historisation des données d'enquêtes clients.**

Développée pour le département *Customer Experience* de MTN Côte d'Ivoire, SurveyFlow CX remplace une chaîne manuelle (scripts SAS + recherches VLOOKUP dans Excel) par un flux web guidé. Un traitement qui prenait environ **45 minutes** se fait désormais en **quelques secondes, sans écrire de code**.

![Python](https://img.shields.io/badge/Python-3.10-3776AB?logo=python&logoColor=white)
![Django](https://img.shields.io/badge/Django-4.2-092E20?logo=django&logoColor=white)
![Vue.js](https://img.shields.io/badge/Vue.js-3-4FC08D?logo=vuedotjs&logoColor=white)
![MySQL](https://img.shields.io/badge/MySQL-8-4479A1?logo=mysql&logoColor=white)

---

## 🎯 Le problème résolu

Les enquêtes de satisfaction (FTTH, 4G, Roaming, VOC EBU…) sont diffusées via SurveyMonkey puis exportées en Excel. Ces fichiers sont difficiles à exploiter : deux lignes d'en-tête, questions à choix multiples éclatées sur plusieurs colonnes, colonnes système inutiles, et une jointure manuelle par `N° REC` pour récupérer les informations client. SurveyFlow CX automatise toute cette chaîne.

## ✨ Fonctionnalités clés

- **Détection automatique** de la structure SurveyMonkey (lignes d'en-tête, colonnes système, questions à choix multiples).
- **Nettoyage intelligent** : fusion des choix multiples, séparation des verbatims, calcul automatique des statuts NPS (Détracteur / Neutre / Promoteur).
- **Mapping des colonnes** par renommage et **glisser-déposer** pour réordonner.
- **Modèles réutilisables** : le format est enregistré à la première configuration et réappliqué automatiquement aux imports suivants.
- **Enrichissement par jointure** : détection automatique de la feuille et de la colonne `N° REC`, correspondance intelligente, et **correction automatique** lorsqu'un agent a saisi un téléphone à la place du `N° REC`.
- **Score NPS calculé automatiquement**, avec suivi de son **évolution période sur période**.
- **Historisation complète** et **traçabilité** (qui, quand, quelle action).
- **Gestion des rôles** (Agent / Manager / Administrateur) avec cloisonnement des données.
- **Export** Excel / CSV : fichier nettoyé, enrichi, ou base cumulative.

## 🛠️ Stack technique

| Couche | Technologies |
|---|---|
| **Frontend** | Vue.js 3, Vue Router, Pinia, Tailwind CSS, PrimeVue, Vite, Axios |
| **Backend** | Python, Django 4.2, Django REST Framework, SimpleJWT |
| **Traitement de données** | pandas, OpenPyXL, python-calamine, fuzzywuzzy |
| **Base de données** | MySQL (connecteur PyMySQL) |

## 🏗️ Architecture

Backend Django organisé en applications à responsabilité unique :

```
backend/apps/
├── auth_app/    # Utilisateurs, rôles, authentification JWT
├── imports/     # Import, moteur d'analyse et de nettoyage, modèles
├── joins/       # Jointure et correspondance intelligente
├── exports/     # Génération des fichiers Excel / CSV
├── history/     # Historisation et journal d'activité
└── dashboard/   # Tableaux de bord agent et manager
```

## 🚀 Installation

### Prérequis
- Python 3.10+
- Node.js 18+
- MySQL (ou XAMPP)

### Backend

```bash
cd backend
python -m venv venv
venv\Scripts\activate          # Windows
pip install -r requirements.txt
copy .env.example .env         # puis renseignez vos identifiants MySQL
python manage.py migrate
python manage.py runserver
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

L'application est ensuite accessible sur **http://localhost:5173**.

## 📸 Captures d'écran

<!-- Ajoutez ici vos captures : tableau de bord, écran de nettoyage, jointure, score NPS. -->
*(à venir)*

## 👤 Auteur

Projet réalisé dans le cadre d'un mémoire de fin de cycle MIAGE — département Customer Experience, MTN Côte d'Ivoire.
