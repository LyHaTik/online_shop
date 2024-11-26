let cart = JSON.parse(localStorage.getItem('cart')) || {};

async function loadCart() {
    const cartItems = document.getElementById('cart-items');
    cartItems.innerHTML = '';

    if (!cart['totalSum']) {
        cartItems.innerHTML = '<div>Корзина пуста</div>';
        return;
    }

    document.getElementById(`total`).innerText = cart['totalSum'] + 'р.';

    const processedStores = new Set(); // Набор для отслеживания добавленных магазинов

    for (const storeId of Object.keys(cart)) {
        const productIds = Object.keys(cart[storeId]);
        if (productIds.length === 0) continue;
        
        try {
            const response = await fetch(`/store/${storeId}/filtered_products/?product_ids=${productIds.join(',')}`);
            if (!response.ok) throw new Error(`Ошибка запроса: ${response.status}`);

            const data = await response.json();
            if (!data.products || !Array.isArray(data.products)) {
                throw new Error('Некорректный формат данных от сервера');
            }
            
            const fragment = document.createDocumentFragment();

            data.products.forEach(product => {
                const quantity = cart[product.store_id][product.id];
                if (quantity > 0) {
                    // Добавляем логотип магазина, если он еще не был добавлен
                    if (!processedStores.has(product.store_id)) {
                        const storeItem = document.createElement('li');
                        storeItem.className = 'store-cart';
                        storeItem.innerHTML = `
                            <a href="/store/${product.store_id}/">
                                <img class="logo-product-basket" src="${product.store_image}" alt="${product.store_name}">
                            </a>
                            <a href="/store/${product.store_id}/">
                                ${product.store_name}
                            </a>
                        `;
                        fragment.appendChild(storeItem);
                        processedStores.add(product.store_id);
                    }

                    // Добавляем товар
                    const listItem = document.createElement('li');
                    listItem.className = 'product-item-cart';
                    listItem.innerHTML = `
                            <img class="logo-product-basket" src="${product.image}" alt="${product.name}">
                            ${product.name} ${product.price} ₽
                            <span>
                                <button class="item-button" onclick="updateQuantity(${product.store_id}, ${product.id}, ${product.price}, -1)">-</button>
                                <span class="item-quantity" id="quantity-${product.id}">${quantity}</span>
                                <button class="item-button" onclick="updateQuantity(${product.store_id}, ${product.id}, ${product.price}, 1)">+</button>
                                    
                                <button class="item-button" onclick="removeItem(${product.store_id}, ${product.id}, ${product.price})">x</button>
                            </span>
                    `;
                    fragment.appendChild(listItem);
                }
            });

            cartItems.appendChild(fragment);
        } catch (error) {
            console.error('Ошибка при загрузке товаров:', error);
            cartItems.innerHTML = '<li>Ошибка при загрузке товаров</li>';
        }
    }
}

function removeItem(storeId, productId, productPrice) {
    // Рассчитываем изменение общей суммы
    const quantityDifference = cart[storeId][productId] * productPrice;
    cart['totalSum'] = cart['totalSum'] - quantityDifference;

    delete cart[storeId][productId];
    if (Object.keys(cart[storeId]).length === 0) delete cart[storeId];

    document.getElementById(`total`).innerText = cart['totalSum'] + 'р.';
    // Сохраняем данные корзины в localStorage
    localStorage.setItem('cart', JSON.stringify(cart));
    loadCart();
}

document.addEventListener('DOMContentLoaded', loadCart);