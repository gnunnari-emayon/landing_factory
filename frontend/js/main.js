document.addEventListener("DOMContentLoaded", () => {
  console.log("[Nicho Landing Factory & CRM] Frontend listo.");
  
  const form = document.querySelector("#generator-form");
  if (form) {
    form.addEventListener("submit", (e) => {
      e.preventDefault();
      const negocio = document.querySelector("#nombre_negocio").value;
      const rubro = document.querySelector("#rubro").value;
      
      const badgeContainer = document.querySelector("#preview-badge");
      if (badgeContainer) {
        badgeContainer.textContent = "Procesando...";
        badgeContainer.className = "badge badge-corporativo fade-in";
      }
    });
  }
});
