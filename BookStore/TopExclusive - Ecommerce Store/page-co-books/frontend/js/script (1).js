function readCookie(name) {
    var prefix = name + "=";
    var cookies = document.cookie.split(";");
    for (var i = 0; i < cookies.length; i++) {
        var cookie = cookies[i].trim();
        if (cookie.indexOf(prefix) === 0) {
            return decodeURIComponent(cookie.substring(prefix.length));
        }
    }
    return "";
}

async function api(url, options) {
    var requestOptions = options || {};
    var headers = Object.assign({}, requestOptions.headers || {});
    if (requestOptions.body) {
        headers["Content-Type"] = "application/json";
    }
    if (requestOptions.method && requestOptions.method !== "GET") {
        headers["X-CSRFToken"] = readCookie("csrftoken");
    }

    var response = await fetch(url, Object.assign({}, requestOptions, {
        headers: headers,
        credentials: "same-origin"
    }));
    var data;
    try {
        data = await response.json();
    } catch (error) {
        throw new Error("The server returned an unreadable response (" + response.status + ").");
    }
    if (!response.ok) {
        var requestError = new Error(data.error || "The request failed.");
        requestError.status = response.status;
        throw requestError;
    }
    return data;
}

function showMessage(message, isError) {
    var element = document.getElementById("message");
    if (!element) {
        element = document.createElement("p");
        element.id = "store-message";
        element.setAttribute("role", "status");
        element.setAttribute("aria-live", "polite");
        document.body.prepend(element);
    }
    element.textContent = message;
    element.className = "message" + (isError ? " error" : " success");
}

function formatPrice(value) {
    return "R" + Number(value).toFixed(2);
}

async function refreshCartCount() {
    var badge = document.getElementById("cart-count");
    if (!badge) {
        return;
    }
    var cart = await api("/api/cart/");
    var quantity = cart.items.reduce(function (count, item) {
        return count + item.quantity;
    }, 0);
    badge.textContent = quantity;
}

async function addBookToCart(button) {
    var quantityInput = document.getElementById("detail-quantity");
    var quantity = quantityInput ? Number(quantityInput.value) : 1;
    try {
        await api("/api/cart/add/", {
            method: "POST",
            body: JSON.stringify({
                product_id: Number(button.dataset.addToCart),
                quantity: quantity
            })
        });
        showMessage("The book was added to your cart.", false);
        await refreshCartCount();
    } catch (error) {
        showMessage(error.message, true);
    }
}

function makeCartRow(item) {
    var row = document.createElement("tr");
    var imageCell = document.createElement("td");
    var image = document.createElement("img");
    image.src = item.image_url;
    image.alt = item.title;
    imageCell.appendChild(image);

    var titleCell = document.createElement("td");
    titleCell.textContent = item.title;
    var priceCell = document.createElement("td");
    priceCell.textContent = formatPrice(item.price);

    var quantityCell = document.createElement("td");
    var quantityInput = document.createElement("input");
    quantityInput.type = "number";
    quantityInput.min = "1";
    quantityInput.max = String(item.stock);
    quantityInput.value = item.quantity;
    quantityInput.setAttribute("aria-label", "Quantity for " + item.title);
    quantityInput.addEventListener("change", async function () {
        try {
            await api("/api/cart/update/", {
                method: "POST",
                body: JSON.stringify({
                    product_id: item.id,
                    quantity: Number(quantityInput.value)
                })
            });
            await renderCart();
        } catch (error) {
            showMessage(error.message, true);
            await renderCart();
        }
    });
    quantityCell.appendChild(quantityInput);

    var subtotalCell = document.createElement("td");
    subtotalCell.textContent = formatPrice(item.subtotal);
    var removeCell = document.createElement("td");
    var removeButton = document.createElement("button");
    removeButton.type = "button";
    removeButton.className = "btn";
    removeButton.textContent = "Remove";
    removeButton.addEventListener("click", async function () {
        try {
            await api("/api/cart/remove/", {
                method: "POST",
                body: JSON.stringify({ product_id: item.id })
            });
            await renderCart();
            showMessage("The book was removed from your cart.", false);
        } catch (error) {
            showMessage(error.message, true);
        }
    });
    removeCell.appendChild(removeButton);

    row.appendChild(imageCell);
    row.appendChild(titleCell);
    row.appendChild(priceCell);
    row.appendChild(quantityCell);
    row.appendChild(subtotalCell);
    row.appendChild(removeCell);
    return row;
}

async function renderCart() {
    var body = document.getElementById("cart-items");
    if (!body) {
        return;
    }
    var cart = await api("/api/cart/");
    body.replaceChildren();
    if (cart.items.length === 0) {
        var emptyRow = document.createElement("tr");
        var emptyCell = document.createElement("td");
        emptyCell.colSpan = 6;
        emptyCell.textContent = "Your cart is empty.";
        emptyRow.appendChild(emptyCell);
        body.appendChild(emptyRow);
    } else {
        cart.items.forEach(function (item) {
            body.appendChild(makeCartRow(item));
        });
    }
    document.getElementById("cart-total").textContent = formatPrice(cart.total);
    await refreshCartCount();
}

async function renderOrders() {
    var container = document.getElementById("orders-list");
    if (!container) {
        return;
    }
    try {
        var result = await api("/api/orders/");
        container.replaceChildren();
        if (result.orders.length === 0) {
            container.textContent = "You have not placed any orders yet.";
            return;
        }
        result.orders.forEach(function (order) {
            var card = document.createElement("article");
            card.className = "book-card";
            var heading = document.createElement("h2");
            heading.textContent = "Order #" + order.id + " - " + order.status;
            var date = document.createElement("p");
            date.textContent = new Date(order.created_at).toLocaleString();
            var list = document.createElement("ul");
            order.items.forEach(function (item) {
                var line = document.createElement("li");
                line.textContent = item.quantity + " x " + item.title + " (" +
                    formatPrice(item.price) + " each)";
                list.appendChild(line);
            });
            var total = document.createElement("p");
            total.className = "price";
            total.textContent = "Total: " + formatPrice(order.total);
            card.appendChild(heading);
            card.appendChild(date);
            card.appendChild(list);
            card.appendChild(total);
            container.appendChild(card);
        });
    } catch (error) {
        showMessage(error.message + " Use the Login link above to sign in.", true);
    }
}

async function updateNavigation() {
    var account = await api("/api/me/");
    document.querySelectorAll("[data-login-link], [data-signup-link]").forEach(function (link) {
        link.hidden = account.authenticated;
    });
    document.querySelectorAll("[data-logout-link]").forEach(function (link) {
        link.hidden = !account.authenticated;
    });
}

function connectForms() {
    var loginForm = document.getElementById("login-form");
    if (loginForm) {
        loginForm.addEventListener("submit", async function (event) {
            event.preventDefault();
            try {
                var result = await api("/api/login/", {
                    method: "POST",
                    body: JSON.stringify({
                        email: document.getElementById("email").value,
                        password: document.getElementById("password").value
                    })
                });
                window.location.href = "/books.html";
            } catch (error) {
                showMessage(error.message, true);
            }
        });
    }

    var signupForm = document.getElementById("signup-form");
    if (signupForm) {
        signupForm.addEventListener("submit", async function (event) {
            event.preventDefault();
            var password = document.getElementById("password").value;
            if (password !== document.getElementById("confirm").value) {
                showMessage("The passwords do not match.", true);
                return;
            }
            if (!document.getElementById("terms").checked) {
                showMessage("Please agree to the terms.", true);
                return;
            }
            try {
                await api("/api/register/", {
                    method: "POST",
                    body: JSON.stringify({
                        full_name: document.getElementById("fullname").value,
                        email: document.getElementById("email").value,
                        password: password,
                        terms_accepted: true
                    })
                });
                window.location.href = "/books.html";
            } catch (error) {
                showMessage(error.message, true);
            }
        });
    }

    var checkoutForm = document.getElementById("checkout-form");
    if (checkoutForm) {
        checkoutForm.addEventListener("submit", async function (event) {
            event.preventDefault();
            var values = {
                full_name: document.getElementById("checkout-name").value,
                email: document.getElementById("checkout-email").value,
                phone: document.getElementById("checkout-phone").value,
                address: document.getElementById("checkout-address").value,
                city: document.getElementById("checkout-city").value,
                postal_code: document.getElementById("checkout-postal-code").value
            };
            try {
                var result = await api("/api/orders/create/", {
                    method: "POST",
                    body: JSON.stringify(values)
                });
                checkoutForm.reset();
                await renderCart();
                showMessage("Order #" + result.order_id + " placed successfully.", false);
            } catch (error) {
                showMessage(error.status === 401
                    ? error.message + " Use the Login link above, then return here to order."
                    : error.message, true);
            }
        });
    }

    document.querySelectorAll("[data-add-to-cart]").forEach(function (button) {
        button.addEventListener("click", function () {
            addBookToCart(button);
        });
    });

    document.querySelectorAll("[data-logout-link]").forEach(function (link) {
        link.addEventListener("click", async function (event) {
            event.preventDefault();
            try {
                await api("/api/logout/", { method: "POST" });
                window.location.href = "/";
            } catch (error) {
                showMessage(error.message, true);
            }
        });
    });

    var contactForm = document.querySelector(".contact-form");
    if (contactForm) {
        contactForm.addEventListener("submit", function (event) {
            event.preventDefault();
            showMessage("Thank you! Your message was sent.", false);
        });
    }
}

async function initializeStorefront() {
    try {
        await api("/api/csrf/");
        await updateNavigation();
        connectForms();
        await refreshCartCount();
        await renderCart();
        await renderOrders();
    } catch (error) {
        showMessage("Could not connect to the bookstore server: " + error.message, true);
    }
}

document.addEventListener("DOMContentLoaded", initializeStorefront);
