const GameDefaults = {
  name: "",
  released: false,
  purchased: false,
  excitement: 0
};

document.addEventListener('DOMContentLoaded', () => {
    const form        = document.getElementById('add-game-form');
    const submitBtn = document.getElementById('submit-btn');

    function updateColorOnly() {
        if (form.checkValidity()) {
            submitBtn.classList.replace('bg-gray-400', 'bg-indigo-600');
            submitBtn.classList.replace('cursor-default', 'cursor-pointer');
        } else {
            submitBtn.classList.replace('bg-indigo-600', 'bg-gray-400');
            submitBtn.classList.replace('cursor-pointer', 'cursor-default');
        }
    }

    form.addEventListener('input',  updateColorOnly);
    form.addEventListener('change', updateColorOnly);

    updateColorOnly();


    const gameInput   = document.getElementById('game');
    const dataList    = document.getElementById('game-list');

    gameInput.addEventListener('input', () => {
        const opts = Array.from(dataList.options).map(o => o.value);
        if (!opts.includes(gameInput.value)) {
            gameInput.setCustomValidity('Please select a game from the suggestions list.');
        } else {
            gameInput.setCustomValidity('');
        }
    });

    form.addEventListener('submit', (e) => {
        if (!form.checkValidity()) {
            e.preventDefault();
            form.reportValidity();
        }
    });
});

async function send_game(event) {
    event.preventDefault();
    const form = document.getElementById('add-game-form')
    const formData = new FormData(form);
    const payload = {
        name: formData.get('game') || '',
        released: formData.get('released') === 'on',
        purchased: formData.get('purchased') === 'on',
        excitement: parseInt(formData.get('excitement'))
    };

    const postRes = await fetch('/games', {
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify(payload),
    });

    const container = document.getElementById('alert-container');
    let template;
    if (postRes.ok) {
      template = document.getElementById('alert-success-template').innerHTML;
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
