# 🏛️ ARCHI.SPACE (ArchHub)

Un tableau de bord conçu avec Next.js et Tailwind CSS pour agréger en temps réel les concours d'architecture, les opportunités d'emploi et l'actualité mondiale autour de l'architecture.

## ✨ Fonctionnalités
- **Agrégation Automatisée** : Données extraites et mises à jour via un moteur de scraping en Python.
- **Filtres** : Tri automatique des concours (les concours dont la date d'inscription est dépassée sont déplacés vers l'espace "Archives").
- **Espace Personnel (Favoris)** : Espace pour sauvegarder les opportunités intéressantes grâce à la persistance des données.
- **Multi-Onglets Dynamique** : Navigation instantanée entre Concours, Jobs, Actualités et Archives sans rechargement de page.

## 💻 Stack Technique
- **Frontend** : Next.js (App Router), React, Tailwind CSS, Lucide Icons, next-themes.
- **Data Scraping** : Python (BeautifulSoup, Requests) avec scripts d'automatisation.
- **Déploiement** : Vercel.

## 🚀 Démarrage Rapide (Développement Local)

### 1️⃣ Prérequis
- **Node.js** (v18+) et **Python 3.9+**.

### 2️⃣ Installation & Exécution
```bash
# Cloner le projet (à remplacer par votre propre lien GitHub)
git clone https://github.com/Sarahlaure/archihub.git
cd archihub

# Installer les dépendances Frontend
npm install

# (Optionnel) Pour rafraîchir les données via le scraper
pip install -r requirements.txt
python tools/scraper.py

# Lancer le serveur Next.js
npm run dev
```

> L'application sera accessible sur `http://localhost:3000`.

