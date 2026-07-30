document.addEventListener("DOMContentLoaded", () => {
  console.log("[Nicho Landing Factory & CRM v2.0] Frontend listo.");

  const form = document.querySelector("#generator-form");
  const crmTableBody = document.querySelector("#crm-table-body");
  const totalCountEl = document.querySelector("#total-landings-count");
  const previewBadge = document.querySelector("#preview-badge");
  const searchInput = document.querySelector("#crm-search");

  // Handler para botones Preset
  const presetButtons = document.querySelectorAll(".btn-preset");
  presetButtons.forEach(btn => {
    btn.addEventListener("click", () => {
      document.querySelector("#nombre_negocio").value = btn.dataset.negocio || "";
      document.querySelector("#rubro").value = btn.dataset.rubro || "";
      document.querySelector("#telefono_whatsapp").value = btn.dataset.tel || "";
      document.querySelector("#email").value = btn.dataset.email || "";

      // Trigger submit automático para demostración fluida
      form.dispatchEvent(new Event("submit", { cancelable: true, bubbles: true }));
    });
  });

  // Handler para generación via AJAX
  if (form) {
    form.addEventListener("submit", async (e) => {
      e.preventDefault();

      const negocio = document.querySelector("#nombre_negocio").value.trim();
      const rubro = document.querySelector("#rubro").value.trim();
      const tel = document.querySelector("#telefono_whatsapp").value.trim();
      const email = document.querySelector("#email").value.trim();

      if (!negocio || !rubro) return;

      if (previewBadge) {
        previewBadge.style.display = "inline-block";
        previewBadge.textContent = "⚙️ Clasificando Rubro & Generando Copy...";
        previewBadge.className = "badge badge-tecnologia fade-in";
      }

      try {
        const response = await fetch("/api/generate", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            nombre_negocio: negocio,
            rubro: rubro,
            telefono_whatsapp: tel,
            email: email
          })
        });

        const data = await response.json();

        if (response.ok && data.status === "success") {
          const cliente = data.cliente;

          if (previewBadge) {
            previewBadge.textContent = `✅ Asignado: ${cliente.categoria_visual}`;
            previewBadge.className = `badge badge-${cliente.categoria_visual} fade-in`;
          }

          // Insertar en la tabla CRM
          if (crmTableBody) {
            const newRow = document.createElement("tr");
            newRow.style.borderBottom = "1px solid var(--color-border)";
            newRow.className = "crm-row fade-in";
            newRow.innerHTML = `
              <td style="padding: 0.875rem;">
                <strong style="color: #fff; font-size: 0.95rem;">${cliente.nombre_negocio}</strong>
                <div style="font-size: 0.75rem; color: var(--color-text-muted);">ID: ${cliente.id}</div>
              </td>
              <td style="padding: 0.875rem; font-size: 0.9rem; color: var(--color-text-muted);">
                ${cliente.rubro}
              </td>
              <td style="padding: 0.875rem;">
                <span class="badge badge-${cliente.categoria_visual}">${cliente.categoria_visual}</span>
              </td>
              <td style="padding: 0.875rem; font-size: 0.85rem;">
                <div>💬 ${cliente.telefono_whatsapp}</div>
                <div style="color: var(--color-text-muted);">✉️ ${cliente.email}</div>
              </td>
              <td style="padding: 0.875rem;">
                <span class="badge badge-corporativo" style="background: rgba(16, 185, 129, 0.15); color: #10b981;">
                  ${cliente.estado_lead}
                </span>
              </td>
              <td style="padding: 0.875rem; text-align: right;">
                <a href="/preview/${cliente.id}" target="_blank" class="btn btn-secondary btn-sm" style="font-size: 0.8rem; padding: 0.4rem 0.85rem;">
                  🌐 Ver Landing Demo &rarr;
                </a>
              </td>
            `;
            crmTableBody.prepend(newRow);
          }

          // Actualizar contador
          if (totalCountEl) {
            const current = parseInt(totalCountEl.textContent) || 0;
            totalCountEl.textContent = current + 1;
          }

          // Abrir la landing generada automáticamente en nueva pestaña si fue botón Preset
          window.open(`/preview/${cliente.id}`, "_blank");

        } else {
          alert(`Error al generar: ${data.detail || 'Fallo inesperado'}`);
        }
      } catch (err) {
        console.error("Error en la solicitud:", err);
        alert("Error de conexión al generar la landing page.");
      }
    });
  }

  // Filtrado de búsqueda en tabla CRM
  if (searchInput && crmTableBody) {
    searchInput.addEventListener("input", (e) => {
      const query = e.target.value.toLowerCase();
      const rows = crmTableBody.querySelectorAll(".crm-row");
      rows.forEach(row => {
        const text = row.textContent.toLowerCase();
        row.style.display = text.includes(query) ? "" : "none";
      });
    });
  }
});
