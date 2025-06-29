const CardGameUI = (() => {
    const els = {
        title: document.getElementById('card-game-title'),
        img: document.getElementById('card-game-image'),
        fallback: document.getElementById('card-image-fallback'),
        badge: document.getElementById('card-est-badge'),
        subtitle: document.getElementById('card-excitement-value'),
        released: document.getElementById('card-released-block'),
        purchased: document.getElementById('card-purchased-block'),
    }

    function setTextState(active) {
        const t = els.title.classList
        const s = els.subtitle.classList

        if (active) {
            t.replace('font-medium', 'font-semibold')
            t.replace('text-gray-400', 'text-gray-900')
            s.replace('text-gray-400', 'text-gray-500')
        } else {
            t.replace('font-semibold', 'font-medium')
            t.replace('text-gray-900', 'text-gray-400')
            s.replace('text-gray-500', 'text-gray-400')
        }
    }

    function styleBlock(name, state) {
        const block = els[name]
        const icon = block.querySelector('svg')
        const label = block.querySelector('span')

        block.classList.remove(
            'bg-gray-50', 'bg-red-100', 'bg-green-100',
            'opacity-50', 'pointer-events-none'
        )
        icon.classList.remove('text-gray-400', 'text-red-800', 'text-green-800')
        label.classList.remove(
            'text-gray-700', 'text-red-800', 'text-green-800',
            'font-medium', 'font-semibold'
        )

        if (state === 'active') apply(block, icon, label, 'green')
        else if (state === 'inactive') apply(block, icon, label, 'red')
        else apply(block, icon, label, 'gray', true)
    }

    function apply(block, icon, label, color) {
        if (color === 'green') {
            block.classList.add('bg-green-100')
            icon.classList.add('text-green-800')
            label.classList.add('text-green-800', 'font-semibold')
        }
        if (color === 'red') {
            block.classList.add('bg-red-100')
            icon.classList.add('text-red-800')
            label.classList.add('text-red-800', 'font-semibold')
        }
        if (color === 'gray') {
            block.classList.add('bg-gray-50', 'opacity-50', 'pointer-events-none')
            icon.classList.add('text-gray-400')
            label.classList.add('text-gray-700', 'font-medium')
        }
    }

    function showNoGame() {
        els.title.textContent = 'No game selected'
        els.img.src = ''
        els.badge.textContent = '–'
        els.subtitle.textContent = '–'
        this.setTextState(false)
        this.styleBlock('released', 'none')
        this.styleBlock('purchased', 'none')
        els.img.classList.add('hidden')
        els.fallback.classList.add('hidden')
    }

    return {
        setTextState,
        styleBlock,
        showNoGame,
        els
    }
})()

let games = []

document.addEventListener('DOMContentLoaded', async () => {
    const res = await fetch('/games?finished_at=NULL')
    if (!res.ok) {
        console.error(`Failed to load games: ${res.status} ${res.statusText}`);
    } else {
        const resGames = await res.json();
        games = resGames.games
    }

    const gameInput = document.getElementById('game');
    const form = document.getElementById('add-post-finish-form');

    const durationInput = document.getElementById('duration');

    createRegex(gameInput)

    CardGameUI.showNoGame();
    updateStars();
    updatePeriodLabels();
    updateSendButton();

    gameInput.addEventListener('input', async () => {
        const g = games.find(x => x.name === gameInput.value);
        if (!g) {
            CardGameUI.showNoGame();
            return;
        }

        gameInput.setCustomValidity("")

        CardGameUI.setTextState(true);
        CardGameUI.els.title.textContent = g.name;
        CardGameUI.els.badge.textContent = g.est_length ? `${g.est_length}h` : '–';
        CardGameUI.els.subtitle.textContent = `Excitement: ${g.excitement}/10`;

        try {
            const res = await fetch(
                `/game_image?game=${encodeURIComponent(g.name)}`
            );
            const {
                image_path
            } = await res.json();

            CardGameUI.els.img.src = image_path;
            CardGameUI.els.img.classList.remove('hidden');
            CardGameUI.els.fallback.classList.add('hidden');

        } catch {
            CardGameUI.els.img.classList.add('hidden');
            CardGameUI.els.fallback.classList.remove('hidden');
        }

        CardGameUI.styleBlock('released', g.released ? 'active' : 'inactive');
        CardGameUI.styleBlock('purchased', g.purchased ? 'active' : 'inactive');
        updateSendButton()
    });

    gameInput.addEventListener('invalid', () => {
        const v = gameInput.value.trim()
        if (!v) {
            gameInput.setCustomValidity('Please select a game')
        } else {
            gameInput.setCustomValidity(
                gameNames.includes(v) ?
                '' :
                'Please select a valid game'
            )
        }
    })

    form.addEventListener('submit', (e) => {
        if (!form.checkValidity()) {
            e.preventDefault();
            form.reportValidity();
        }
    });

    document
        .querySelectorAll('input[name="rating"]')
        .forEach(radio => radio.addEventListener('change', updateStars));

    durationInput.addEventListener('input', updatePeriodLabels);

    form.addEventListener('input', updateSendButton);
    form.addEventListener('change', updateSendButton);

    document.getElementById('post-finish-submit').addEventListener('click', send_post_finish);
});

function updateStars() {
    const starLabels = Array.from(document.querySelectorAll('label[for^="rating-"]'));

    const sel = parseInt(
        document.querySelector('input[name="rating"]:checked')?.value || 1,
        10
    );

    starLabels.forEach(label => {
        const val = Number(label.htmlFor.split('-')[1]);
        const svg = label.querySelector('svg');
        const path = svg.querySelector('path');

        svg.classList.remove('text-yellow-400');
        path.setAttribute('stroke-width', '1');

        if (val < sel) {

            svg.classList.remove('text-gray-300');
            svg.classList.add('text-yellow-300');
        } else {
            svg.classList.remove('text-yellow-300');
            svg.classList.add('text-gray-300');
        }

        if (val === sel) {
            path.setAttribute('stroke-width', '4');
            svg.classList.remove('text-yellow-300');
            svg.classList.remove('text-gray-300');
            svg.classList.add('text-yellow-400');
        }
    });
}

function updatePeriodLabels() {
    const durationInput = document.getElementById('duration');
    const periodSelect = document.getElementById('period');
    const n = parseInt(durationInput.value, 10);
    Array.from(periodSelect.options).forEach(opt => {
        const txt = opt.textContent.trim();
        const base = txt.replace(/s$/i, '');
        opt.textContent = n === 1 ? base : base + 's';
    });
}

function updateSendButton() {
    const gameInput = document.getElementById('game');
    const gameSelected = games.some(x => x.name === gameInput.value);

    const form = document.getElementById('add-post-finish-form');
    const submitBtn = document.getElementById('post-finish-submit');

    if (form.checkValidity() && gameSelected) {
        submitBtn.classList.replace('bg-gray-400', 'bg-indigo-600');
        submitBtn.classList.replace('cursor-default', 'cursor-pointer');
    } else {
        submitBtn.classList.replace('bg-indigo-600', 'bg-gray-400');
        submitBtn.classList.replace('cursor-pointer', 'cursor-default');
    }
}

async function send_post_finish() {
    const gameInput = document.getElementById('game');

    if (!gameInput.reportValidity()) {
        return
    }

    const form = document.getElementById('add-post-finish-form')
    const formData = new FormData(form);

    const game = games.find(x => x.name === gameInput.value);

    const rawNum = parseInt(formData.get('duration'), 10) || 1;
    let rawPeriod = formData.get('period');
    if (rawNum === 1) rawPeriod = rawPeriod.replace(/s$/, '');

    const payload = {
        dropped: formData.get('dropped') === 'on',
        credits: formData.get('credits') === 'on',
        time_played: parseInt(formData.get('time_played')),
        duration: `${formData.get('duration')} ${rawPeriod.toLowerCase()}`,
        rating: parseInt(formData.get('rating')),
        worth: formData.get('credits') === 'on',
        reason: formData.get('reason') || '',
        finished_at: new Date().toISOString(),
    };

    const postRes = await fetch(`/games/${game.game_id}/post_finish`, {
        method: 'PATCH',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(payload),
    });

    const container = document.getElementById('alert-container');
    let template;
    if (postRes.ok) {
        template = document.getElementById('alert-success-template').innerHTML
            .replace('__SUCCESS_MESSAGE__', `Your post finish thoughs have been added to ${game.name}`);
        form.reset()
        updateStars()
        updateSendButton()
        removeGame(game.name, gameInput)
        gameInput.value = ''
        gameInput.dispatchEvent(new KeyboardEvent('keyup', {
            bubbles: true,
            cancelable: true
        }));
        CardGameUI.showNoGame();
    } else {
        let errMsg = 'Could not add game. Please try again.';
        try {
            const err = await postRes.json();
            if (err.detail) errMsg = `${err.detail.error}: ${err.detail.message}`;
        } catch {}
        template = document.getElementById('alert-error-template').innerHTML
            .replace('__ERROR_MESSAGE__', errMsg);
    }

    container.innerHTML = template;
    setTimeout(() => container.innerHTML = '', 5000);
}

function createRegex(gameInput) {
    const gameNames = games.map(g => g.name)
    const escapeRe = s => s.replace(/[-/\\^$*+?.()|[\]{}]/g, '\\$&')
    const patternBody = gameNames.map(escapeRe).join('|')
    gameInput.required = true
    gameInput.pattern = `^(${patternBody})$`
}

function removeGame(gameName, gameInput) {
    const idx = games.findIndex(g => g.name === gameName);
    if (idx > -1) games.splice(idx, 1);

    createRegex(gameInput)
}