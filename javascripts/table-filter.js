document$.subscribe(function () {
  document.querySelectorAll(".filterable").forEach(function (wrapper) {
    const table = wrapper.querySelector("table");
    if (!table) return;

    // Don't add a second filter if one already exists
    if (wrapper.querySelector(".table-filter")) return;

    const rows = table.querySelectorAll("tbody tr");

    const input = document.createElement("input");
    input.type = "text";
    input.placeholder = "Filter values...";
    input.className = "table-filter md-input md-input--stretch";
    input.style.cssText = "margin-bottom: 1rem; padding: 0.5rem; width: 100%; border: 1px solid var(--md-default-fg-color--lighter); border-radius: 0.25rem;";

    wrapper.insertBefore(input, table);

    input.addEventListener("input", function () {
      var query = input.value.toLowerCase();
      rows.forEach(function (row) {
        var text = row.textContent.toLowerCase();
        row.style.display = text.includes(query) ? "" : "none";
      });
    });
  });
});
