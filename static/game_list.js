let games = []

document.addEventListener("DOMContentLoaded", async () => {
    const res = await fetch('/games')
    if (!res.ok) {
        console.error(`Failed to load games: ${res.status} ${res.statusText}`);
    } else {
        const resGames = await res.json();
        games = resGames.games
    }

    for (const game of games) {
        const gameItem = document.getElementById(`${game.name}-item`)
        gameItem.addEventListener('click', () => {
            adjustPostFinishCard(game)
        })
    }
})

async function adjustPostFinishCard(game) {
    const gameId = document.getElementById('game-id')
    const rating = document.getElementById('rating')
    const statsCard = document.getElementById('stats-card')
    const postStats = document.getElementById('finish-stats')
    const noStats = document.getElementById('no-stats')
    let post_finish = null

    const res = await fetch(`/games/${game.game_id}/post_finish`)
    if (!res.ok) {
        console.error(`Failed to load games: ${res.status} ${res.statusText}`);
    } else {
        const resPostFinish = await res.json();
        post_finish = resPostFinish["post_finish"]
    }

    statsCard.hidden = false
    gameId.innerHTML = game.name

    if (post_finish !== null) {
        rating.innerHTML = post_finish.rating
        postStats.hidden = false
        noStats.hidden = true

        const timePlayedDuration = document.getElementById('time-played-duration')
        const finishedAt = document.getElementById('finished-at')
        const dropped = document.getElementById('dropped')
        const credits = document.getElementById('credits')
        const worth = document.getElementById('worth')

        timePlayedDuration.innerHTML = `${post_finish.time_played} ${post_finish.time_played === 1 ? 'hour' : 'hours'} in ${post_finish.duration}`
        finishedAt.innerHTML = post_finish.finished_at.split('T')[0]

        if (post_finish.dropped) {
            dropped.classList.remove('bg-red-100')
            dropped.classList.remove('text-red-800')
            dropped.classList.add('bg-green-100')
            dropped.classList.add('text-green-800')
        } else {
            dropped.classList.add('bg-red-100')
            dropped.classList.add('text-red-800')
            dropped.classList.remove('bg-green-100')
            dropped.classList.remove('text-green-800')
        }

        if (post_finish.credits) {
            credits.classList.remove('bg-red-100')
            credits.classList.remove('text-red-800')
            credits.classList.add('bg-green-100')
            credits.classList.add('text-green-800')
        } else {
            credits.classList.add('bg-red-100')
            credits.classList.add('text-red-800')
            credits.classList.remove('bg-green-100')
            credits.classList.remove('text-green-800')
        }

        if (post_finish.worth) {
            worth.classList.remove('bg-red-100')
            worth.classList.remove('text-red-800')
            worth.classList.add('bg-green-100')
            worth.classList.add('text-green-800')
        } else {
            worth.classList.add('bg-red-100')
            worth.classList.add('text-red-800')
            worth.classList.remove('bg-green-100')
            worth.classList.remove('text-green-800')
        }
    } else {
        rating.innerHTML = '-'
        postStats.hidden = true
        noStats.hidden = false
    }
}
