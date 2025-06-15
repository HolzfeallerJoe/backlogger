document.addEventListener('DOMContentLoaded', () => {
    const raw = document.getElementById('games-data').textContent;
    const games = JSON.parse(raw);

    const input = document.getElementById('game');
    const nameEl = document.getElementById('card-game-name');
    const estVal = document.getElementById('card-est-length-value');
    const releasedVal = document.getElementById('card-released-value');
    const purchasedVal = document.getElementById('card-purchased-value');
    const excitementVal = document.getElementById('card-excitement-value');

    function showNoGame() {
        nameEl.textContent = 'No game selected';
        estVal.textContent = '-';
        releasedVal.textContent = '-';
        purchasedVal.textContent = '-';
        excitementVal.textContent = '-';
    }

    showNoGame();

    input.addEventListener('input', () => {
        const val = input.value;
        const g = games.find(x => x.name === val);
        if (!g) {
            showNoGame();
            return;
        }

        nameEl.textContent = g.name;
        estVal.textContent = `${g.est_length} hour${g.est_length !== 1 ? 's' : ''}`;
        releasedVal.textContent = g.released ? 'Yes' : 'No';
        purchasedVal.textContent = g.purchased ? 'Yes' : 'No';
        excitementVal.textContent = g.excitement;
    });
});
