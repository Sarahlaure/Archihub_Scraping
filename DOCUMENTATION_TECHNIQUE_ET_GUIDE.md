# 📖 Document Explicatif Exhaustif : Projet Archi.Comp

Ce document est un guide pédagogique complet et détaillé expliquant le fonctionnement de la plateforme **Archi.Comp**, le choix des technologies, la démarche étape par étape et la procédure pour déployer et maintenir le projet.

---

## 1. 💡 C'est quoi exactement ce projet ?

**Archi.Comp** est une plateforme web moderne qui agit comme un **agrégateur d'opportunités pour le monde de l'architecture**.

Dans le domaine de l'architecture, les opportunités (concours d'idées, appels à projets internationaux, offres d'emploi en agence et actualités majeures) sont éparpillées sur des dizaines de sites web différents (Bustler, ArchDaily, Dezeen, Competitions.archi, etc.).

Notre solution résout ce problème en :
1. **Scrappant automatique** (aspirant) les données de ces sites sources chaque jour.
2. **Filtrant et nettoyant** les informations (en éliminant les concours expirés ou sans date limite, et en corrigeant les résumés peu clairs).
3. **Affichant ces opportunités sur une interface web moderne, claire et intuitive** où les professionnels et étudiants peuvent naviguer rapidement sans perdre de temps.

---

## 2. 🛡️ Légalité et Ethique du Scraping

Une question cruciale lors de la publication d'un tel site est la **conformité légale**.

### Analyse des règles :
- **Données factuelles publiques :** Les titres de concours, les dates limites, les noms d'agences et les lieux d'emploi sont des **informations factuelles d'intérêt public**. Leur agrégation est légale tant qu'elle ne constitue pas un vol de propriété intellectuelle.
- **Respect du fichier `robots.txt` :** Nous interrogeons les serveurs à des fréquences très raisonnables (1 fois par 24h via GitHub Actions) sans surcharger leurs serveurs.
- **Redirection systématique vers la source officielle :** Chaque carte sur le site contient un bouton d'action ("En savoir plus", "Postuler", "Lire l'article") qui redirige directement l'utilisateur vers la page officielle du créateur ou recruteur (`target="_blank"`). Nous ne cachons pas la source originelle.

---

## 3. 🏗️ Architecture & Fonctionnement Technique

Le projet repose sur **deux piliers principaux** :

```
┌────────────────────────────────────────────────────────┐
│ 1. SCRAPER ENGINE (Python / Playwright / BS4)          │
│    - Visite les sites d'architecture                   │
│    - Extrait Concours, Emplois, Actualités             │
│    - Génère 3 fichiers JSON dans public/               │
└───────────────────────────┬────────────────────────────┘
                            │ (Fichiers public/*.json)
                            ▼
┌────────────────────────────────────────────────────────┐
│ 2. FRONTEND DASHBOARD (Next.js 15 / React / Tailwind)  │
│    - Lit les fichiers JSON                             │
│    - Affiche une interface fluide avec onglets         │
│    - Propose la navigation sticky & filtres            │
└────────────────────────────────────────────────────────┘
```

### A. Le moteur de Scraping (`tools/scraper.py`)

Le script Python utilise deux techniques de scraping :
1. **Requests + BeautifulSoup4 :** Pour les sites simples et rapides qui fournissent du HTML direct.
2. **Playwright (Chromium Headless) :** Pour les sites complexes qui utilisent du JavaScript dynamique (ex: Bustler, ArchDaily). Playwright ouvre un vrai navigateur Chromium en arrière-plan sans interface graphique pour charger la page entièrement avant d'extraire les éléments.

#### Traitement des données :
- **Filtrage des dates :** Le script analyse les chaînes de texte contenant des dates limite (ex: `"Deadline: Oct 15, 2026"`), les convertit en format standardisé et élimine toutes les opportunités dont l'échéance est déjà dépassée.
- **Nettoyage du bruit :** Un système d'expressions régulières (`ARCH_COM_JUNK_PATTERNS`) élimine les faux concours (pages de profils d'utilisateurs, conditions d'utilisation, etc.).
- **Format de sortie :** Les données sont sauvegardées sous forme de 3 fichiers JSON structurés dans le dossier `public/` :
  - `public/competitions.json`
  - `public/jobs.json`
  - `public/news.json`

### B. Le Frontend Dashboard (`src/app/page.tsx`)

Développé avec **Next.js 15**, **React** et **Tailwind CSS v4**, le frontend offre :
- **Optimisation de l'espace écran :** Une bannière d'en-tête (Hero section) compacte pour laisser la place principale au contenu dès le chargement.
- **Barre d'onglets collante (Sticky Tabs) :** La barre de navigation (`Concours`, `Emplois`, `Actualités`, `Archives`) reste fixe en haut de l'écran lors du défilement. L'utilisateur peut ainsi changer de rubrique à tout moment sans devoir remonter tout en haut.
- **Génération de descriptions de qualité :** Si le scraping n'a pas pu récupérer un résumé clair ou si celui-ci fait moins de 35 caractères, le composant génère automatiquement une description professionnelle de remplacement invitant à consulter le cahier des charges officiel.

---

## 4. 🌐 Comment Déployer le Site et le Rendre Accessible à Tous

Pour que votre site soit accessible via un lien public (ex: `https://votre-site.vercel.app`) :

### Étape 1 : Mettre le code sur GitHub
1. Créez un compte sur [GitHub](https://github.com) si vous n'en avez pas.
2. Créez un nouveau dépôt nommé `Archihub_Scraping`.
3. Poussez votre code local vers GitHub :
   ```bash
   git init
   git add .
   git commit -m "Initial commit - Fully operational Archi.Comp"
   git branch -M main
   git remote add origin https://github.com/VOTRE_PSEUDO/Archihub_Scraping.git
   git push -u origin main
   ```

### Étape 2 : Automatiser la mise à jour des données
Le projet contient un fichier d'automation `.github/workflows/daily_sync.yml`.
Dès que votre projet est sur GitHub, **GitHub Actions exécutera automatiquement le scraper tous les jours à 06h00 UTC**. Il mettra à jour les fichiers JSON et fera un commit automatique sur votre dépôt.

### Étape 3 : Déployer gratuitement sur Vercel
1. Créez un compte gratuit sur [Vercel](https://vercel.com) avec votre compte GitHub.
2. Cliquez sur **"New Project"** -> Sélectionnez `Archihub_Scraping`.
3. Cliquez sur **"Deploy"**.
4. En 1 minute, votre site est en ligne avec un lien SSL HTTPS sécurisé que vous pouvez partager à tout le monde !

---

## 5. 🛠️ Résumé pour Reproduire le Projet à Partir de Zéro

Si une personne novice souhaite refaire ce projet :
1. **Installer Python et Node.js** sur son ordinateur.
2. **Cloner ce dépôt** et installer les paquets :
   - Python : `pip install -r requirements.txt` puis `playwright install chromium`
   - Node.js : `npm install`
3. **Lancer le scraper** avec `python tools/scraper.py` pour alimenter la base de données JSON.
4. **Lancer le serveur web** avec `npm run dev`.
5. Ouvrir `http://localhost:3000` pour vérifier l'application.
