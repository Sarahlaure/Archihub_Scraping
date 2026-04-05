# 🏛️ ARCHI.SPACE (ArchHub)
**L'horizon des professionnels du design et de l'architecture.**

Un tableau de bord premium conçu avec Next.js et Tailwind CSS pour agréger en temps réel les meilleurs concours d'architecture, les opportunités d'emploi exclusives et l'actualité mondiale de l'industrie.

## ✨ Fonctionnalités
- **Agrégation Automatisée** : Données extraites et mises à jour via un moteur de scraping en Python.
- **Interface Premium** : Design minimaliste, accents dorés, mode sombre robuste et typographie asymétrique soignée.
- **Filtres Intelligents** : Tri automatique des concours (les concours dont la date d'inscription est dépassée sont déplacés vers l'espace "Archives").
- **Espace Personnel (Favoris)** : Espace pour sauvegarder les opportunités intéressantes grâce à la persistance des données.
- **Multi-Onglets Dynamique** : Navigation instantanée entre Concours, Jobs, Actualités et Archives sans rechargement de page.

## 💻 Stack Technique
- **Frontend** : Next.js (App Router), React, Tailwind CSS, Lucide Icons, next-themes.
- **Base de données & Auth** : Supabase (Authentification & PostgreSQL).
- **Data Scraping** : Python (BeautifulSoup, Requests) avec scripts d'automatisation.
- **Déploiement** : Vercel.

## 🚀 Démarrage Rapide (Développement Local)

### 1️⃣ Prérequis
- **Node.js** (v18+) et **Python 3.9+**.

### 2️⃣ Installation & Exécution
```bash
# Cloner le projet (à remplacer par votre propre lien GitHub)
git clone https://github.com/VOTRENOMGITHUB/archihub.git
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

---

## 🧑‍💻 À propos de l'auteure

<table style="border: none;">
<tr>
<td style="border: none;">
<strong>Sarahlaure</strong><br>
<em>Développeuse</em><br><br>
Passionnée par le développement web, l'architecture d'interfaces premium et l'automatisation de tâches pour offrir la meilleure expérience utilisateur.
</td>
</tr>
</table>

👉 **Retrouvez mes projets sur GitHub :** [github.com/Sarahlaure](https://github.com/Sarahlaure) (à adapter avec votre vrai pseudo)
