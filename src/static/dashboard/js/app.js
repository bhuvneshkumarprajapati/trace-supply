(() => {
  const body = document.body;
  if (!body.classList.contains("dashboard-page")) return;

  const apiBase = body.dataset.apiBase;
  const loginUrl = body.dataset.loginUrl;
  const state = { shipments: [], status: "all", query: "", activeShipment: null };
  const statuses = {
    pending: { label: "Pending", className: "status-pending" },
    in_transit: { label: "In transit", className: "status-transit" },
    delivered: { label: "Delivered", className: "status-delivered" },
    cancelled: { label: "Cancelled", className: "status-cancelled" },
  };
  const transitions = {
    pending: ["in_transit", "cancelled"],
    in_transit: ["delivered", "cancelled"],
    delivered: [],
    cancelled: [],
  };
  const elements = {
    rows: document.querySelector("#shipment-rows"),
    empty: document.querySelector("#empty-state"),
    emptyTitle: document.querySelector("#empty-title"),
    emptyCopy: document.querySelector("#empty-copy"),
    count: document.querySelector("#result-count"),
    loadState: document.querySelector("#load-state"),
    search: document.querySelector("#search-input"),
    createDialog: document.querySelector("#create-dialog"),
    createForm: document.querySelector("#create-form"),
    detailDialog: document.querySelector("#detail-dialog"),
    statusForm: document.querySelector("#status-form"),
    toast: document.querySelector("#toast"),
  };

  function csrfToken() {
    const cookie = document.cookie.split("; ").find((item) => item.startsWith("csrftoken="));
    return cookie ? decodeURIComponent(cookie.slice("csrftoken=".length)) : "";
  }

  async function request(url, options = {}) {
    const headers = { Accept: "application/json", ...options.headers };
    if (options.body) headers["Content-Type"] = "application/json";
    if (options.method && options.method !== "GET") headers["X-CSRFToken"] = csrfToken();
    const response = await fetch(url, { credentials: "same-origin", ...options, headers });
    if (response.status === 401) {
      window.location.assign(loginUrl);
      throw new Error("Sign in required");
    }
    const payload = response.headers.get("content-type")?.includes("application/json")
      ? await response.json()
      : null;
    if (!response.ok) throw new Error(payload?.detail || "The request could not be completed.");
    return payload;
  }

  function showToast(message, isError = false) {
    elements.toast.textContent = message;
    elements.toast.classList.toggle("is-error", isError);
    elements.toast.classList.add("is-visible");
    window.clearTimeout(showToast.timeout);
    showToast.timeout = window.setTimeout(() => elements.toast.classList.remove("is-visible"), 3200);
  }

  function formatDate(value) {
    if (!value) return "—";
    return new Intl.DateTimeFormat(undefined, { month: "short", day: "numeric", year: "numeric" })
      .format(new Date(value));
  }

  function statusBadge(status) {
    const meta = statuses[status] || { label: status, className: "" };
    const badge = document.createElement("span");
    badge.className = `status-label ${meta.className}`;
    const dot = document.createElement("i");
    dot.setAttribute("aria-hidden", "true");
    const label = document.createElement("span");
    label.textContent = meta.label;
    badge.append(dot, label);
    return badge;
  }

  function addCell(row, content, className = "") {
    const cell = document.createElement("td");
    if (className) cell.className = className;
    if (content instanceof Node) cell.append(content);
    else cell.textContent = content;
    row.append(cell);
    return cell;
  }

  function visibleShipments() {
    const query = state.query.trim().toLowerCase();
    return state.shipments.filter((shipment) => {
      const matchesStatus = state.status === "all" || shipment.status === state.status;
      const searchable = [shipment.id, shipment.origin, shipment.destination]
        .join(" ").toLowerCase();
      return matchesStatus && (!query || searchable.includes(query));
    });
  }

  function updateMetrics() {
    const count = (status) => state.shipments.filter((shipment) => shipment.status === status).length;
    document.querySelector("#metric-total").textContent = String(state.shipments.length);
    document.querySelector("#metric-transit").textContent = String(count("in_transit"));
    document.querySelector("#metric-pending").textContent = String(count("pending"));
    document.querySelector("#metric-delivered").textContent = String(count("delivered"));
  }

  function renderRows() {
    const shipments = visibleShipments();
    elements.rows.replaceChildren();
    elements.count.textContent = String(shipments.length);
    elements.empty.hidden = shipments.length > 0;
    if (!shipments.length) {
      const noRecords = state.shipments.length === 0;
      elements.emptyTitle.textContent = noRecords ? "No shipments yet" : "No matching shipments";
      elements.emptyCopy.textContent = noRecords
        ? "Create a shipment to start the movement log."
        : "Try another search or status filter.";
      document.querySelector("#empty-create-button").hidden = !noRecords;
    }

    for (const shipment of shipments) {
      const row = document.createElement("tr");
      const reference = document.createElement("span");
      reference.className = "reference-id";
      reference.textContent = shipment.id;
      reference.title = shipment.id;
      addCell(row, reference);

      const route = document.createElement("div");
      route.className = "route-cell";
      const origin = document.createElement("span");
      origin.textContent = shipment.origin;
      const destination = document.createElement("span");
      destination.textContent = shipment.destination;
      route.append(origin, destination);
      addCell(row, route, "route-column");

      addCell(row, statusBadge(shipment.status));
      addCell(row, shipment.events[0]?.location || "—", "checkpoint-cell");
      addCell(row, formatDate(shipment.updated_at), "date-cell");

      const openButton = document.createElement("button");
      openButton.type = "button";
      openButton.className = "table-action";
      openButton.textContent = "Open";
      openButton.setAttribute("aria-label", `Open shipment ${shipment.id}`);
      openButton.addEventListener("click", () => openDetails(shipment.id));
      addCell(row, openButton, "action-cell");
      elements.rows.append(row);
    }
  }

  async function loadShipments() {
    elements.loadState.textContent = "Refreshing records";
    try {
      state.shipments = await request(apiBase);
      updateMetrics();
      renderRows();
      elements.loadState.textContent = `${state.shipments.length} records loaded`;
    } catch (error) {
      if (error.message !== "Sign in required") {
        elements.loadState.textContent = "Connection error";
        showToast(error.message, true);
      }
    }
  }

  function openCreateDialog() {
    elements.createForm.reset();
    elements.createDialog.showModal();
    document.querySelector("#origin-input").focus();
  }

  function addTimelineEvent(event, isLatest) {
    const item = document.createElement("li");
    item.className = isLatest ? "timeline-item is-latest" : "timeline-item";
    const marker = document.createElement("span");
    marker.className = "timeline-marker";
    marker.setAttribute("aria-hidden", "true");
    const content = document.createElement("div");
    content.className = "timeline-content";
    const top = document.createElement("div");
    top.className = "timeline-top";
    top.append(statusBadge(event.status));
    const time = document.createElement("time");
    time.textContent = formatDate(event.occurred_at);
    time.dateTime = event.occurred_at;
    top.append(time);
    const location = document.createElement("strong");
    location.textContent = event.location;
    content.append(top, location);
    if (event.note) {
      const note = document.createElement("p");
      note.textContent = event.note;
      content.append(note);
    }
    item.append(marker, content);
    return item;
  }

  async function openDetails(shipmentId) {
    try {
      const shipment = await request(`${apiBase}${encodeURIComponent(shipmentId)}/`);
      state.activeShipment = shipment;
      document.querySelector("#detail-reference").textContent = shipment.id;
      document.querySelector("#detail-origin").textContent = shipment.origin;
      document.querySelector("#detail-destination").textContent = shipment.destination;
      const detailStatus = document.querySelector("#detail-status");
      detailStatus.replaceChildren(statusBadge(shipment.status));

      const timeline = document.querySelector("#event-timeline");
      timeline.replaceChildren(...shipment.events.map((event, index) => addTimelineEvent(event, index === 0)));
      document.querySelector("#timeline-count").textContent = String(shipment.events.length);

      const nextStatuses = transitions[shipment.status] || [];
      const select = document.querySelector("#status-input");
      select.replaceChildren();
      for (const status of nextStatuses) {
        const option = document.createElement("option");
        option.value = status;
        option.textContent = statuses[status].label;
        select.append(option);
      }
      const isTerminal = nextStatuses.length === 0;
      document.querySelector("#terminal-status-note").hidden = !isTerminal;
      document.querySelector("#save-status-button").hidden = isTerminal;
      document.querySelector("#location-input").required = !isTerminal;
      elements.detailDialog.showModal();
    } catch (error) {
      showToast(error.message, true);
    }
  }

  elements.createForm.addEventListener("submit", async (event) => {
    event.preventDefault();
    const button = elements.createForm.querySelector("[type=submit]");
    button.disabled = true;
    try {
      await request(apiBase, {
        method: "POST",
        body: JSON.stringify({
          origin: document.querySelector("#origin-input").value,
          destination: document.querySelector("#destination-input").value,
        }),
      });
      elements.createDialog.close();
      await loadShipments();
      showToast("Shipment created");
    } catch (error) {
      showToast(error.message, true);
    } finally {
      button.disabled = false;
    }
  });

  elements.statusForm.addEventListener("submit", async (event) => {
    event.preventDefault();
    if (!state.activeShipment) return;
    const button = document.querySelector("#save-status-button");
    button.disabled = true;
    try {
      await request(`${apiBase}${encodeURIComponent(state.activeShipment.id)}/status/`, {
        method: "PATCH",
        body: JSON.stringify({
          status: document.querySelector("#status-input").value,
          location: document.querySelector("#location-input").value,
          note: document.querySelector("#note-input").value,
        }),
      });
      elements.detailDialog.close();
      await loadShipments();
      showToast("Shipment update recorded");
    } catch (error) {
      showToast(error.message, true);
    } finally {
      button.disabled = false;
    }
  });

  document.querySelectorAll("[data-close]").forEach((button) => {
    button.addEventListener("click", () => document.getElementById(button.dataset.close).close());
  });
  document.querySelector("#new-shipment-button").addEventListener("click", openCreateDialog);
  document.querySelector("#empty-create-button").addEventListener("click", openCreateDialog);
  document.querySelector("#refresh-button").addEventListener("click", loadShipments);
  elements.search.addEventListener("input", (event) => {
    state.query = event.target.value;
    renderRows();
  });
  document.querySelectorAll(".filter-button").forEach((button) => {
    button.addEventListener("click", () => {
      state.status = button.dataset.status;
      document.querySelectorAll(".filter-button").forEach((filter) => {
        const selected = filter === button;
        filter.classList.toggle("is-selected", selected);
        filter.setAttribute("aria-pressed", String(selected));
      });
      renderRows();
    });
  });
  document.querySelector("#current-date").textContent = new Intl.DateTimeFormat(undefined, {
    weekday: "short", month: "short", day: "numeric", year: "numeric",
  }).format(new Date()).toUpperCase();
  document.addEventListener("keydown", (event) => {
    if (event.key === "/" && !["INPUT", "TEXTAREA"].includes(document.activeElement.tagName)) {
      event.preventDefault();
      elements.search.focus();
    }
  });

  loadShipments();
})();
