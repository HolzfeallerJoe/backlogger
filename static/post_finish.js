document.addEventListener('DOMContentLoaded', () => {
    const games = JSON.parse(
        document.getElementById('games-data').textContent
    );
    const input = document.getElementById('game');

    const titleEl = document.getElementById('card-game-title');
    const imgEl = document.getElementById('card-game-image');
    const fallbackEl = document.getElementById('card-image-fallback');
    const badgeEl = document.getElementById('card-est-badge');
    const subtitleEl = document.getElementById('card-excitement-value');
    const releasedBlock = document.getElementById('card-released-block');
    const purchasedBlock = document.getElementById('card-purchased-block');

    const starLabels = Array.from(document.querySelectorAll('label[for^="rating-"]'));
    const starInputs = document.querySelectorAll('input[name="rating"]');

    function setTextInactive() {
        titleEl.classList.replace('font-semibold', 'font-medium');
        titleEl.classList.replace('text-gray-900', 'text-gray-400');
        subtitleEl.classList.replace('text-gray-500', 'text-gray-400');
    }

    function setTextActive() {
        titleEl.classList.replace('font-medium', 'font-semibold');
        titleEl.classList.replace('text-gray-400', 'text-gray-900');
        subtitleEl.classList.replace('text-gray-400', 'text-gray-500');
    }

    function styleBlock(block, state) {
        const icon = block.querySelector('svg');
        const label = block.querySelector('span');

        block.classList.remove(
            'bg-gray-50', 'bg-red-100', 'bg-green-100',
            'opacity-50', 'pointer-events-none'
        );
        icon.classList.remove('text-gray-400', 'text-red-800', 'text-green-800');
        label.classList.remove(
            'text-gray-700', 'text-red-800', 'text-green-800',
            'font-medium', 'font-semibold'
        );

        if (state === 'active') {
            block.classList.add('bg-green-100');
            icon.classList.add('text-green-800');
            label.classList.add('text-green-800', 'font-semibold');
        } else if (state === 'inactive') {
            block.classList.add('bg-red-100');
            icon.classList.add('text-red-800');
            label.classList.add('text-red-800', 'font-semibold');
        } else {
            block.classList.add('bg-gray-50', 'opacity-50', 'pointer-events-none');
            icon.classList.add('text-gray-400');
            label.classList.add('text-gray-700', 'font-medium');
        }
    }

    function showNoGame() {
        titleEl.textContent = 'No game selected';
        imgEl.src = '';
        badgeEl.textContent = '–';
        subtitleEl.textContent = '–';
        setTextInactive();
        styleBlock(releasedBlock, 'none');
        styleBlock(purchasedBlock, 'none');
        imgEl.classList.add('hidden');
        fallbackEl.classList.add('hidden');
    }

    function updateStars() {
        const sel = parseInt(
            document.querySelector('input[name="rating"]:checked')?.value || 0,
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

    document
        .querySelectorAll('input[name="rating"]')
        .forEach(radio => radio.addEventListener('change', updateStars));

    showNoGame();
    updateStars();

    input.addEventListener('input', async () => {
        const g = games.find(x => x.name === input.value);
        if (!g) {
            showNoGame();
            return;
        }

        setTextActive();
        titleEl.textContent = g.name;
        badgeEl.textContent = g.est_length ? `${g.est_length}h` : '–';
        subtitleEl.textContent = `Excitement: ${g.excitement}/10`;

        try {
            const res = await fetch(
                `/game_image?game=${encodeURIComponent(g.name)}`
            );
            const {
                image_path
            } = await res.json();

            if (image_path) {
                imgEl.src = image_path;
                imgEl.classList.remove('hidden');
                fallbackEl.classList.add('hidden');
            } else {
                throw new Error('no image');
            }
        } catch {
            imgEl.classList.add('hidden');
            fallbackEl.classList.remove('hidden');
        }

        styleBlock(releasedBlock, g.released ? 'active' : 'inactive');
        styleBlock(purchasedBlock, g.purchased ? 'active' : 'inactive');
    });
});