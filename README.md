# 🏛️ Archi.Comp — Plateforme d'Opportunités & d'Actualités en Architecture

[![Daily Architecture Data Sync](https://github.com/Sarahlaure/Archihub_Scraping/actions/workflows/daily_sync.yml/badge.svg)](https://github.com/Sarahlaure/Archihub_Scraping/actions/workflows/daily_sync.yml)
[![Next.js](https://img.shields.io/badge/Next.js-15-black?logo=next.js)](https://nextjs.org/)
[![Python Playwright](https://img.shields.io/badge/Python-Playwright-green?logo=python)](https://playwright.dev/python/)

**Archi.Comp** (Archihub) est une plateforme web moderne et entièrement automatisée conçue pour les architectes ou étudiants et professionnels du secteur. Le site agrège en temps réel les **concours internationaux**, les **offres d'emploi en agence** et les **dernières actualités** du monde de l'architecture.

---

## ✨ Caractéristiques Principales

-  **Concours avec Échéances Vérifiées :** Seules les compétitions disposant de dates limites claires et à venir sont affichées (filtrage automatique des opportunités expirées).
-  **Navigation Persistante (Sticky Navigation) :** Basculez entre les onglets *Concours*, *Emplois* et *Actualités* à n'importe quel moment du défilement sans devoir remonter en haut de la page.
-  **Descriptifs Clarifiés :** Résumés enrichis et fallback automatisé pour garantir des informations toujours lisibles et professionnelles.
-  **Automatisation Quotidienne (GitHub Actions) :** Le scraper s'exécute automatiquement chaque jour à 06:00 UTC pour maintenir les données à jour sans intervention humaine.
-  **Conformité & Respect des Sources :** Tous les contenus affichés dirigent directement l'utilisateur vers le site officiel de l'organisateur ou du recruteur.

---

## 🛠️ Stack Technique

### Frontend
- **Framework :** Next.js 15 (App Router, React 19)
- **Styling :** Tailwind CSS v4, Font Outfit & Inter (Google Fonts)
- **Icons & UI :** Lucide React, Glassmorphism, Micro-animations CSS

### Backend / Data Scraping
- **Langage :** Python 3.11
- **Scraping Engine :** Playwright (Chromium Headless) & BeautifulSoup4
- **Sources d'information :** `competitions.archi`, `bustler.net`, `architecturecompetitions.com`, `archdaily.com`, `dezeen.com`

### Automation & Deployment
- **CI/CD :** GitHub Actions (`daily_sync.yml`)
- **Hosting :** Vercel

---

## 🚀 Prise en main & Installation Locale

### Prerequisites
- Node.js 18+ et npm
- Python 3.11+ et pip

### 1. Cloner le projet
```bash
git clone https://github.com/Sarahlaure/Archihub_Scraping.git
cd Archihub_Scraping
```

### 2. Installer les dépendances Frontend & Backend
```bash
# Frontend
npm install

# Backend Scraper
pip install -r requirements.txt
playwright install chromium
```

### 3. Exécuter le Scraper (Génération des données JSON)
```bash
python tools/scraper.py
```
*Cette commande va générer/mettre à jour `public/competitions.json`, `public/jobs.json` et `public/news.json`.*

### 4. Lancer l'application web
```bash
npm run dev
```
Ouvrez [http://localhost:3000](http://localhost:3000) dans votre navigateur pour voir le résultat.

---

## 🌐 Déploiement en Ligne (Vercel)

1. Connectez votre dépôt GitHub à **[Vercel](https://vercel.com)**.
2. Vercel détectera automatiquement Next.js et déploiera le site.
3. Chaque commit poussé par le workflow GitHub Actions mettra automatiquement à jour le site en ligne !

---

## 📝 Licence & Droits
Projet développé dans le cadre d'un agrégateur d'opportunités d'architecture. Toutes les données appartiennent à leurs organisateurs et éditeurs respectifs.
