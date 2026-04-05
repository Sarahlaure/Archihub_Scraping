const DATA_PATH = '.tmp/articles.json';
const articlesGrid = document.getElementById('articles-grid');
const btnLatest = document.getElementById('btn-latest');
const btnSaved = document.getElementById('btn-saved');

let allArticles = [];
let savedIds = JSON.parse(localStorage.getItem('savedArticles') || '[]');

async function loadArticles() {
    try {
        const response = await fetch(DATA_PATH);
        if (!response.ok) throw new Error('Données indisponibles');
        allArticles = await response.json();
        renderArticles(allArticles);
    } catch (err) {
        console.error(err);
        articlesGrid.innerHTML = `
            <div class="loading-state">
                <p style="color: #ef4444">⚠️ Erreur de synchronisation. Veuillez lancer le scraper.</p>
            </div>
        `;
    }
}

function renderArticles(articles) {
    if (articles.length === 0) {
        articlesGrid.innerHTML = `
            <div class="loading-state">
                <p>Aucune actualité trouvée ces dernières 24h. Revenez plus tard !</p>
            </div>
        `;
        return;
    }

    articlesGrid.innerHTML = '';
    articles.forEach(article => {
        const isSaved = savedIds.includes(article.id);
        const card = document.createElement('div');
        card.className = 'article-card';
        card.innerHTML = `
            <div class="source-badge">${article.source}</div>
            <h3 class="article-title">${article.title}</h3>
            <p class="article-summary">${article.summary || 'Résumé en cours de préparation...'}</p>
            <div class="article-footer">
                <a href="${article.link}" target="_blank" class="read-btn">En savoir plus →</a>
                <button onclick="toggleSave('${article.id}')" class="save-btn ${isSaved ? 'saved' : ''}" id="save-${article.id}">
                    <svg viewBox="0 0 24 24"><path d="M19 21l-7-5-7 5V5a2 2 0 0 1 2-2h10a2 2 0 0 1 2 2z"></path></svg>
                </button>
            </div>
        `;
        articlesGrid.appendChild(card);
    });
}

function toggleSave(id) {
    const btn = document.getElementById(`save-${id}`);
    if (savedIds.includes(id)) {
        savedIds = savedIds.filter(savedId => savedId !== id);
        btn.classList.remove('saved');
    } else {
        savedIds.push(id);
        btn.classList.add('saved');
    }
    localStorage.setItem('savedArticles', JSON.stringify(savedIds));

    if (btnSaved.classList.contains('active')) {
        renderSaved();
    }
}

function renderSaved() {
    const savedArticles = allArticles.filter(a => savedIds.includes(a.id));
    renderArticles(savedArticles);
}

btnLatest.addEventListener('click', () => {
    btnLatest.classList.add('active');
    btnSaved.classList.remove('active');
    renderArticles(allArticles);
});

btnSaved.addEventListener('click', () => {
    btnSaved.classList.add('active');
    btnLatest.classList.remove('active');
    renderSaved();
});

// Initial load
loadArticles();
