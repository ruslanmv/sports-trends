document.addEventListener('click', (event) => {
  const button = event.target.closest('[data-sports-filters] button');
  if (!button) return;
  const sport = button.dataset.sport;
  button.parentElement.querySelectorAll('button').forEach((item) => item.classList.remove('active'));
  button.classList.add('active');
  document.querySelectorAll('[data-tomorrow-matches] [data-sport]').forEach((card) => {
    card.hidden = sport !== 'all' && card.dataset.sport !== sport;
  });
});
