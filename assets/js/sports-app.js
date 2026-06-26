async function sportsFetchJson(path) {
  const response = await fetch(path, { cache: 'no-store' });
  if (!response.ok) throw new Error(`Failed to load ${path}`);
  return response.json();
}

async function sportsInitStatus() {
  const el = document.querySelector('[data-sports-status]');
  if (!el) return;
  try {
    const status = await sportsFetchJson('/assets/data/sports/status.json');
    const updated = new Date(status.last_updated).toLocaleString();
    el.textContent = `Updated ${updated}`;
  } catch (error) {
    el.textContent = 'Using cached demo data';
    console.warn(error);
  }
}

document.addEventListener('DOMContentLoaded', sportsInitStatus);
