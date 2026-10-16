(function () {
  var theme = 'dark';
  try {
    if (localStorage.getItem('estudo-certo-theme') === 'light') theme = 'light';
  } catch {
    // Sem armazenamento disponível, mantém o padrão escuro nesta aba.
    theme = 'dark';
  }
  document.documentElement.dataset.theme = theme;
  document.documentElement.style.colorScheme = theme;
})();
