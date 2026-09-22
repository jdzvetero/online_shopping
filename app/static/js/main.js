/* ===========================================================
   VELOURA — interactivity
   =========================================================== */

document.addEventListener("DOMContentLoaded", () => {
  initNavToggle();
  initRevealOnScroll();
  initAutoDismissFlashes();
});

/* ---------- Mobile nav ---------- */
function initNavToggle() {
  const toggle = document.getElementById("navToggle");
  const links = document.getElementById("navLinks");
  if (!toggle || !links) return;
  toggle.addEventListener("click", () => links.classList.toggle("open"));
}

/* ---------- Scroll reveal ---------- */
function initRevealOnScroll() {
  const targets = document.querySelectorAll(".reveal");
  if (!("IntersectionObserver" in window) || targets.length === 0) {
    targets.forEach((el) => el.classList.add("in-view"));
    return;
  }
  const observer = new IntersectionObserver(
    (entries) => {
      entries.forEach((entry) => {
        if (entry.isIntersecting) {
          entry.target.classList.add("in-view");
          observer.unobserve(entry.target);
        }
      });
    },
    { threshold: 0.1, rootMargin: "0px 0px -40px 0px" }
  );
  targets.forEach((el) => observer.observe(el));
}

/* ---------- Auto-dismiss flash messages ---------- */
function initAutoDismissFlashes() {
  document.querySelectorAll(".flash").forEach((flash) => {
    setTimeout(() => {
      flash.style.transition = "opacity .4s, transform .4s";
      flash.style.opacity = "0";
      flash.style.transform = "translateX(40px)";
      setTimeout(() => flash.remove(), 400);
    }, 5000);
  });
}

/* ---------- Product image thumbnails ---------- */
function setMainImage(src) {
  const main = document.getElementById("mainImage");
  if (main) main.src = src;
  document.querySelectorAll(".thumb").forEach((t) => t.classList.toggle("active", t.src === src));
}

/* ---------- Seller product form: image preview ---------- */
function previewImage(input, previewId) {
  const preview = document.getElementById(previewId);
  if (!preview || !input.files || !input.files[0]) return;
  const reader = new FileReader();
  reader.onload = (e) => {
    preview.src = e.target.result;
    preview.hidden = false;
  };
  reader.readAsDataURL(input.files[0]);
}

/* ---------- Size guide modal ---------- */
function openSizeGuide() {
  document.getElementById("sizeGuideModal")?.classList.add("show");
}
function closeSizeGuide() {
  document.getElementById("sizeGuideModal")?.classList.remove("show");
}
document.addEventListener("click", (e) => {
  if (e.target.id === "sizeGuideModal") closeSizeGuide();
});

/* ---------- Product detail: colour / size / availability ---------- */
function selectColor(name, el) {
  window.state = window.state || {};
  state.color = name;
  document.querySelectorAll("#colorRow .swatch").forEach((s) => s.classList.remove("selected"));
  el.classList.add("selected");
  const label = document.getElementById("selectedColor");
  if (label) label.textContent = name;
  refreshSizeAvailability();
  evaluateSelection();
}

function selectSize(size, el) {
  if (el.classList.contains("disabled")) return;
  window.state = window.state || {};
  state.size = size;
  document.querySelectorAll("#sizeRow .size-pill").forEach((s) => s.classList.remove("selected"));
  el.classList.add("selected");
  evaluateSelection();
}

function findVariant(size, color) {
  if (typeof VARIANTS === "undefined") return null;
  return VARIANTS.find((v) => v.size === size && v.color_name === color) || null;
}

function refreshSizeAvailability() {
  if (typeof VARIANTS === "undefined" || !state.color) return;
  document.querySelectorAll("#sizeRow .size-pill").forEach((pill) => {
    const size = pill.dataset.size;
    const variant = findVariant(size, state.color);
    const disabled = !variant || (variant.status === "in_stock" && variant.stock <= 0);
    pill.classList.toggle("disabled", disabled);
  });
}

function evaluateSelection() {
  const badge = document.getElementById("availabilityBadge");
  const message = document.getElementById("availabilityMessage");
  const addBtn = document.getElementById("addToBagBtn");
  const variantInput = document.getElementById("variantIdInput");

  if (!state.size || !state.color) {
    if (message) message.classList.remove("show");
    if (badge) {
      badge.textContent = "Select options";
      badge.className = "badge badge-in_stock";
    }
    if (addBtn) addBtn.disabled = true;
    return;
  }

  const variant = findVariant(state.size, state.color);
  if (!variant) {
    if (badge) {
      badge.textContent = "Unavailable";
      badge.className = "badge badge-unavailable";
    }
    if (message) {
      message.textContent = "This combination isn't available.";
      message.className = "availability-message show wait";
    }
    if (addBtn) addBtn.disabled = true;
    if (variantInput) variantInput.value = "";
    return;
  }

  if (badge) {
    badge.className = "badge badge-" + variant.status;
    badge.textContent =
      variant.status === "in_stock" ? "In stock" : variant.status === "preorder" ? "Pre-order" : "Made to order";
  }
  if (message) {
    message.textContent = variant.label;
    message.className = "availability-message show " + (variant.status === "in_stock" ? "ok" : "wait");
  }
  if (variantInput) variantInput.value = variant.purchasable ? variant.id : "";
  if (addBtn) addBtn.disabled = !variant.purchasable;
}

function stepQty(delta) {
  const input = document.getElementById("qtyInput");
  if (!input) return;
  let value = parseInt(input.value || "1", 10) + delta;
  value = Math.max(1, Math.min(20, value));
  input.value = value;
}

/* ---------- Checkout: delivery vs pickup ---------- */
function setFulfillment(type, el) {
  document.querySelectorAll(".fulfillment-toggle .toggle-btn").forEach((b) => b.classList.remove("active"));
  el.classList.add("active");
  document.getElementById("fulfillmentInput").value = type;

  const deliveryFields = document.getElementById("deliveryFields");
  const pickupFields = document.getElementById("pickupFields");
  const isDelivery = type === "delivery";
  deliveryFields.hidden = !isDelivery;
  pickupFields.hidden = isDelivery;

  deliveryFields.querySelectorAll("input[required]").forEach((i) => (i.disabled = !isDelivery));
  pickupFields.querySelectorAll("input, select").forEach((i) => (i.disabled = isDelivery));

  const feeRow = document.getElementById("deliveryFeeRow");
  const totalRow = document.getElementById("totalRow");
  if (typeof SUBTOTAL !== "undefined" && totalRow) {
    const fee = isDelivery ? DELIVERY_FEE : 0;
    if (feeRow) feeRow.style.display = isDelivery ? "flex" : "none";
    totalRow.querySelector("span:last-child").textContent = "$" + (SUBTOTAL + fee).toFixed(2);
  }
}

/* ---------- Register: role toggle ---------- */
function setRole(role, el) {
  document.querySelectorAll(".role-toggle .toggle-btn").forEach((b) => b.classList.remove("active"));
  el.classList.add("active");
  document.getElementById("roleInput").value = role;
  const brandField = document.getElementById("brandField");
  if (brandField) brandField.hidden = role !== "seller";
}

/* ---------- Seller: dynamic variant rows ---------- */
function addVariantRow(prefill) {
  const template = document.getElementById("variantRowTemplate");
  const container = document.getElementById("variantRows");
  if (!template || !container) return;

  const clone = template.content.cloneNode(true);
  const row = clone.querySelector(".variant-row");

  if (prefill) {
    row.querySelector('[name="variant_size[]"]').value = prefill.size || "";
    row.querySelector('[name="variant_color_name[]"]').value = prefill.color_name || "";
    row.querySelector('[name="variant_color_hex[]"]').value = prefill.color_hex || "#4169E1";
    const statusSelect = row.querySelector('[name="variant_status[]"]');
    statusSelect.value = prefill.availability_status || "in_stock";
    row.querySelector('[name="variant_stock[]"]').value = prefill.stock_quantity ?? 10;
    row.querySelector('[name="variant_date[]"]').value = prefill.available_date || "";
    row.querySelector('[name="variant_leadtime[]"]').value = prefill.lead_time_days || 7;
    container.appendChild(clone);
    toggleVariantFields(container.lastElementChild.querySelector('[name="variant_status[]"]'));
  } else {
    container.appendChild(clone);
  }
}

function toggleVariantFields(selectEl) {
  const row = selectEl.closest(".variant-row");
  const status = selectEl.value;
  row.querySelector(".v-stock").hidden = status !== "in_stock";
  row.querySelector(".v-date").hidden = status !== "preorder";
  row.querySelector(".v-lead").hidden = status !== "made_to_order";
}

document.addEventListener("DOMContentLoaded", () => {
  if (document.getElementById("variantRows")) {
    if (typeof EXISTING_VARIANTS !== "undefined" && EXISTING_VARIANTS.length > 0) {
      EXISTING_VARIANTS.forEach((v) => addVariantRow(v));
    } else {
      addVariantRow();
    }
  }
});
