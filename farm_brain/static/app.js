(() => {
  const menuToggle = document.querySelector('[data-menu-toggle]');
  const menu = document.querySelector('[data-menu]');
  if (menuToggle && menu) {
    menuToggle.addEventListener('click', () => {
      const expanded = menuToggle.getAttribute('aria-expanded') === 'true';
      menuToggle.setAttribute('aria-expanded', String(!expanded));
      menu.classList.toggle('is-open', !expanded);
    });
  }

  const division = document.querySelector('[data-division-select]');
  const category = document.querySelector('[data-category-select]');
  if (division && category && window.FB_CATEGORIES) {
    const updateCategories = (selected = '') => {
      const options = window.FB_CATEGORIES[division.value] || [];
      category.replaceChildren();
      options.forEach((name) => {
        const option = document.createElement('option');
        option.value = name;
        option.textContent = name;
        option.selected = name === selected;
        category.appendChild(option);
      });
      updateTransportVisibility();
    };
    const updateTransportVisibility = () => {
      const panel = document.querySelector('[data-transport-panel]');
      if (panel) {
        const isTransport = division.value === 'Agri Business' && category.value === 'Transport';
        panel.hidden = !isTransport;
      }
    };
    const initial = category.value;
    division.addEventListener('change', () => updateCategories());
    category.addEventListener('change', updateTransportVisibility);
    updateCategories(initial);
  }

  const marketDivision = document.querySelector('[data-market-division]');
  const marketCategory = document.querySelector('[data-market-category]');
  if (marketDivision && marketCategory && window.FB_CATEGORIES) {
    const updateMarketCategories = (selected = '') => {
      const all = Object.values(window.FB_CATEGORIES).flat();
      const names = marketDivision.value ? (window.FB_CATEGORIES[marketDivision.value] || []) : [...new Set(all)];
      marketCategory.replaceChildren();
      const any = document.createElement('option');
      any.value = '';
      any.textContent = 'All categories';
      marketCategory.appendChild(any);
      names.forEach((name) => {
        const option = document.createElement('option');
        option.value = name;
        option.textContent = name;
        option.selected = name === selected;
        marketCategory.appendChild(option);
      });
    };
    marketDivision.addEventListener('change', () => updateMarketCategories());
    updateMarketCategories(marketCategory.value);
  }
})();
