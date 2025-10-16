(function initGiftcardAdmin() {
    console.log("GiftCard admin script loaded");

    const giftCardsSection = document.getElementById("giftcards-section");
    const ordersSection = document.getElementById("orders-section");
    const customerId = giftCardsSection?.dataset.customerId;
    const createBtn = document.getElementById("create-giftcard-btn");
    const recordUsageBtn = document.getElementById("record-usage-btn");
    const modal = document.getElementById("modal-container");
    const modalTitle = document.getElementById("modal-title");
    const modalFields = document.getElementById("modal-fields");
    const cancelBtn = document.getElementById("modal-cancel");
    const saveBtn = document.getElementById("modal-save");

    if (!giftCardsSection || !createBtn || !recordUsageBtn || !modal || !modalFields || !cancelBtn || !saveBtn || !ordersSection) {
        console.error("GiftCard admin script could not find required elements", {
            giftCardsSection, createBtn, recordUsageBtn, modal, modalFields, cancelBtn, saveBtn, ordersSection
        });
        return;
    }

    // --- CSRF Utility ---
    function getCookie(name) {
        let cookieValue = null;
        if (document.cookie && document.cookie !== "") {
            const cookies = document.cookie.split(";");
            for (const c of cookies) {
                const cookie = c.trim();
                if (cookie.startsWith(name + "=")) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }

    // --- Modal ---
    function openModal(title, fieldsHTML) {
        modalTitle.textContent = title;
        modalFields.innerHTML = fieldsHTML;
        modal.style.display = "flex";
    }

    function closeModal() {
        modal.style.display = "none";
    }

    cancelBtn.onclick = closeModal;

    // --- Pagination state ---
    const PAGE_SIZE = 5;
    let gcPage = 0;
    let ordersPage = 0;
    let currentCustomer = null;

    // --- Render GiftCards ---
    function renderGiftCards() {
        const giftcards = currentCustomer.giftcards || [];
        const start = gcPage * PAGE_SIZE;
        const end = start + PAGE_SIZE;
        const pageItems = giftcards.slice(start, end);

        if (!pageItems.length) {
            giftCardsSection.innerHTML = "<p>No gift cards yet</p>";
            return;
        }

        let html = `
            <table class="admin-table">
                <thead>
                    <tr>
                        <th>Code</th>
                        <th>Name</th>
                        <th>Amount</th>
                        <th>Remaining</th>
                    </tr>
                </thead>
                <tbody>
        `;

        for (const card of pageItems) {
            html += `
                <tr>
                    <td>${card.code}</td>
                    <td>${card.name || '-'}</td>
                    <td>${card.initial_amount}</td>
                    <td>${card.current_amount}</td>
                </tr>
            `;
        }

        html += "</tbody></table>";

        // Pagination controls
        html += `<div class="pagination-controls">
                    <button id="gc-prev" ${gcPage === 0 ? 'disabled' : ''}>◀ Prev</button>
                    <button id="gc-next" ${(end >= giftcards.length) ? 'disabled' : ''}>Next ▶</button>
                </div>`;

        giftCardsSection.innerHTML = html;

        document.getElementById("gc-prev")?.addEventListener("click", () => {
            if (gcPage > 0) { gcPage--; renderGiftCards(); }
        });
        document.getElementById("gc-next")?.addEventListener("click", () => {
            if (end < giftcards.length) { gcPage++; renderGiftCards(); }
        });
    }

    // --- Render Orders ---
    function renderOrders() {
        const orders = currentCustomer.orders || [];
        const start = ordersPage * PAGE_SIZE;
        const end = start + PAGE_SIZE;
        const pageItems = orders.slice(start, end);

        if (!pageItems.length) {
            ordersSection.innerHTML = "<p>No orders yet</p>";
            return;
        }

        let html = `
            <table class="admin-table">
                <thead>
                    <tr>
                        <th>ID</th>
                        <th>Total Amount</th>
                        <th>Created At</th>
                    </tr>
                </thead>
                <tbody>
        `;

        for (const order of pageItems) {
            html += `
                <tr>
                    <td>${order.id}</td>
                    <td>${order.total_amount}</td>
                    <td>${new Date(order.created_at).toLocaleString()}</td>
                </tr>
            `;
        }

        html += "</tbody></table>";

        // Pagination controls
        html += `<div class="pagination-controls">
                    <button id="orders-prev" ${ordersPage === 0 ? 'disabled' : ''}>◀ Prev</button>
                    <button id="orders-next" ${(end >= orders.length) ? 'disabled' : ''}>Next ▶</button>
                </div>`;

        ordersSection.innerHTML = html;

        document.getElementById("orders-prev")?.addEventListener("click", () => {
            if (ordersPage > 0) { ordersPage--; renderOrders(); }
        });
        document.getElementById("orders-next")?.addEventListener("click", () => {
            if (end < orders.length) { ordersPage++; renderOrders(); }
        });
    }

    // --- Load customer ---
    async function loadCustomer() {
        try {
            const resp = await fetch(`/api/customer/${customerId}/`);
            if (!resp.ok) throw new Error(`HTTP ${resp.status}`);
            currentCustomer = await resp.json();

            gcPage = 0;
            ordersPage = 0;

            renderGiftCards();
            renderOrders();
        } catch (err) {
            console.error("Failed to load customer", err);
            giftCardsSection.innerHTML = "<p style='color:red;'>Failed to load gift cards</p>";
            ordersSection.innerHTML = "<p style='color:red;'>Failed to load orders</p>";
        }
    }

    // --- Create Gift Card ---
    createBtn.addEventListener("click", () => {
        const fields = `
            <label><strong>Code</strong></label><br>
            <input type="text" id="giftcard-code" required><br><br>
            <label><strong>Amount</strong></label><br>
            <input type="number" id="giftcard-amount" required><br><br>
            <label><strong>Name</strong></label><br>
            <input type="text" id="giftcard-name"><br>
        `;
        openModal("Create Gift Card", fields);

        saveBtn.onclick = async () => {
            const payload = {
                user: customerId,
                code: document.getElementById("giftcard-code")?.value,
                name: document.getElementById("giftcard-name")?.value,
                initial_amount: document.getElementById("giftcard-amount")?.value,
                current_amount: document.getElementById("giftcard-amount")?.value,
            };

            if (!payload.code || !payload.initial_amount) {
                alert("Please fill out all required fields.");
                return;
            }

            try {
                const resp = await fetch("/api/giftcards/", {
                    method: "POST",
                    headers: {
                        "Content-Type": "application/json",
                        "X-CSRFToken": getCookie("csrftoken"),
                    },
                    body: JSON.stringify(payload),
                });

                if (!resp.ok) throw new Error(`HTTP ${resp.status}`);
                closeModal();
                await loadCustomer();
            } catch (err) {
                console.error("Failed to create gift card", err);
                alert("Failed to create gift card");
            }
        };
    });

    // --- Record Order Usage ---
    recordUsageBtn.addEventListener("click", () => {
        if (!currentCustomer) return alert("Customer data not loaded yet");

        const fields = `
            <label><strong>Gift Card</strong></label><br>
            <select id="usage-giftcard">
                ${currentCustomer.giftcards.map(c => `<option value="${c.id}">${c.code} (${c.current_amount})</option>`).join('')}
            </select><br><br>

            <label><strong>Order</strong></label><br>
            <select id="usage-order">
                ${currentCustomer.orders.map(o => `<option value="${o.id}">#${o.id} (${o.total_amount})</option>`).join('')}
            </select><br><br>

            <label><strong>Amount to Use</strong></label><br>
            <input type="number" id="usage-amount" min="0" required><br>
        `;
        openModal("Record Order Usage", fields);

        saveBtn.onclick = async () => {
            const giftcardId = document.getElementById("usage-giftcard").value;
            const orderId = document.getElementById("usage-order").value;
            const amountUsed = parseFloat(document.getElementById("usage-amount").value);

            const selectedCard = currentCustomer.giftcards.find(c => c.id == giftcardId);
            const selectedOrder = currentCustomer.orders.find(o => o.id == orderId);

            if (!amountUsed || amountUsed <= 0) return alert("Enter a valid amount");
            if (amountUsed > parseFloat(selectedCard.current_amount)) return alert("Amount exceeds gift card balance");
            if (amountUsed > parseFloat(selectedOrder.total_amount)) return alert("Amount exceeds order total");

            try {
                const resp = await fetch("/api/giftcards/record_usage/", {
                    method: "POST",
                    headers: {
                        "Content-Type": "application/json",
                        "X-CSRFToken": getCookie("csrftoken"),
                    },
                    body: JSON.stringify({
                        giftcard_id: giftcardId,
                        order_id: orderId,
                        amount: amountUsed,
                    }),
                });

                if (!resp.ok) throw new Error(`HTTP ${resp.status}`);
                closeModal();
                await loadCustomer();
            } catch (err) {
                console.error("Failed to record order usage", err);
                alert("Failed to record order usage");
            }
        };
    });

    // --- Initial load ---
    loadCustomer();
})();
