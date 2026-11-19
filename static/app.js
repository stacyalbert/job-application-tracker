// Confirm before destructive actions: <form data-confirm="Message">
document.addEventListener("submit", (e) => {
  const message = e.target.dataset.confirm;
  if (message && !window.confirm(message)) e.preventDefault();
});

// Dismiss flash messages
document.querySelectorAll(".flash-close").forEach((btn) => {
  btn.addEventListener("click", () => btn.parentElement.remove());
});

// Live table search: <input data-filter-table="#table-id" data-filter-count="#counter-id">
document.querySelectorAll("[data-filter-table]").forEach((input) => {
  const rows = document.querySelectorAll(input.dataset.filterTable + " tbody tr");
  const counter = document.querySelector(input.dataset.filterCount);
  input.addEventListener("input", () => {
    const query = input.value.trim().toLowerCase();
    let shown = 0;
    rows.forEach((row) => {
      const match = row.textContent.toLowerCase().includes(query);
      row.hidden = !match;
      if (match) shown++;
    });
    if (counter) {
      counter.textContent = shown === rows.length ? rows.length + " total" : shown + " of " + rows.length;
    }
  });
});