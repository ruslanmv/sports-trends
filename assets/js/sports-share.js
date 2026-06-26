document.addEventListener('click', async (event) => {
  const button = event.target.closest('[data-share-match]');
  if (!button) return;
  const url = `${location.origin}/sports/match/${button.dataset.shareMatch}/`;
  if (navigator.share) {
    await navigator.share({ title: 'Ruslan Magana Sports Intelligence', url });
  } else if (navigator.clipboard) {
    await navigator.clipboard.writeText(url);
    button.textContent = 'Copied';
  }
});
