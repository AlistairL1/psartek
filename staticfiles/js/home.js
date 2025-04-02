function handleHeartClick() {
    const heartsContainer = document.getElementById('hearts-container');

    const newHearts = Array.from({ length: 50 }, () => {
        const heart = document.createElement('div');
        heart.classList.add('heart');
        heart.textContent = '❤️';

        // Position horizontale aléatoire
        heart.style.left = `${Math.random() * 100}%`;

        // Délai d'animation aléatoire
        const delay = Math.random() * 2;
        heart.style.animationDelay = `${delay}s`;

        heartsContainer.appendChild(heart);

        // Supprimer le cœur après 10 secondes
        setTimeout(() => {
            heartsContainer.removeChild(heart);
        }, 10000);

        return heart;
    });
}
