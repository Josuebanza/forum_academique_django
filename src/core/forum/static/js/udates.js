/* 
(function() {
  let lastFetch = new Date().toISOString();

  async function fetchUpdates() {
    const url = `/forum/api/updates/${TRAVAIL_ID}/?since=${encodeURIComponent(lastFetch)}`;
    try {
      const resp = await fetch(url);
      if (!resp.ok) throw new Error('Network error');
      const data = await resp.json();
      lastFetch = data.now;

      // 1) Nouvelles contributions
      data.contributions.forEach(c => {
        const container = document.querySelector('#contrib-container');
        const div = document.createElement('div');
        div.id = `contrib-${c.id}`;
        div.innerHTML = `
          <strong>${c.auteur}</strong> <em>${new Date(c.date_post).toLocaleTimeString()}</em><br>
          ${c.texte || `<a href="${c.fichier_url}" target="_blank">📎 Fichier</a>`}
        `;
        container.prepend(div);
      });

      // 2) Nouvelles commentaires
      data.commentaires.forEach(cm => {
        const list = document.querySelector(`#comments-for-${cm.contrib_id}`);
        if (list) {
          const li = document.createElement('li');
          li.textContent = `${cm.auteur} (${new Date(cm.date_com).toLocaleTimeString()}): ${cm.contenu}`;
          list.append(li);
        }
      });

      // 3) Réactions : mise à jour des compteurs
      data.reactions.forEach(r => {
        const likeSpan = document.querySelector(`#contrib-${r.contrib_id} .like-count`);
        const dislikeSpan = document.querySelector(`#contrib-${r.contrib_id} .dislike-count`);
        // Vous pouvez refetch le count via une requête ou maintenir un cache…
      });

    } catch (err) {
      console.error('Erreur de mise à jour :', err);
    }
  }

  // Toutes les 5 s
  setInterval(fetchUpdates, 1000);
  
})();
 */