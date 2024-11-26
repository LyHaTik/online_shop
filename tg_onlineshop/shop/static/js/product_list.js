const storeId = document.getElementById('store-name').dataset.storeId;

// Загружаем данные корзины из localStorage
let cart = JSON.parse(localStorage.getItem('cart')) || {};

// Храним выбранные товары и их количество
const selectedProducts = {};
const productPrices = {};


// Инициализация количества товаров на странице
document.addEventListener('DOMContentLoaded', () => {

    // Находим все кнопки с определенным классом
    const buttons = document.querySelectorAll('.item-button-about');

    
    buttons.forEach((button) => {
        // Блокируем стандартное контекстное меню
        button.addEventListener('contextmenu', (event) => {
            event.preventDefault(); // Отключаем меню браузера при долгом нажатии
        });

        // Показываем описание при удержании
        button.addEventListener('touchstart', () => {
            // Достаем описание из атрибута data-description
            const description = button.dataset.description || 'Описание недоступно';
            const name = button.dataset.name || 'Описание товара';

            // Используем Telegram.WebApp.showPopup для отображения
            Telegram.WebApp.showPopup({
                title: name,
                message: description,
                buttons: [{ id: "ok", type: "default", text: "OK" }]
            });
        });
    });



    if (cart['totalSum']) {
        document.getElementById(`total`).innerText = cart['totalSum'] + 'р.';
    }
    if (cart[storeId]) {
        Object.keys(cart[storeId]).forEach(productId => {
            const quantityElement = document.getElementById(`quantity-${productId}`);
            if (quantityElement) {
                quantityElement.textContent = cart[storeId][productId];
            }
    })};

    updateBasketImage();
});


// Функция отслеживает изменение категории товаров и выдает список товаров на странице согласно категории
document.getElementById('product-category-select').addEventListener('change', async function () {
    const categoryId = this.value;
    const response = await fetch(`/store/${storeId}/filtered_products/?category=${categoryId}`);
    const data = await response.json();
    console.log('localStorage', localStorage)
    const productsList = document.getElementById('products-list');
    productsList.innerHTML = '';

    data.products.forEach(product => {
        const listItem = document.createElement('div');
        let productId = product["id"];
        let productQuantity;
        if (Object.keys(cart).length === 0) {
            productQuantity = 0; // Если корзина пуста
        } else {
            productQuantity = cart[storeId]?.[productId] || 0; // Если товар отсутствует в корзине, значение по умолчанию — 0
        }

        listItem.innerHTML = `
        <div class="item" data-id="${product.id}">
            <button class="item-button-about" data-description="${product.description}" data-name="${product.name}">
                <img class="item-img" src="${product.image}" alt="${product.name}">
            </button>
            <div class="item-title">${product.name} ${product.price} p.</div>
            <div class="item-controls">
                <button class="item-button" onclick="updateQuantity(${product.store_id}, ${product.id}, ${product.price}, -1)">-</button>
                <span class="item-quantity" id="quantity-${product.id}">${productQuantity}</span>
                <button class="item-button" onclick="updateQuantity(${product.store_id}, ${product.id}, ${product.price}, 1)">+</button>
            </div>
        </div>`;
        productsList.appendChild(listItem);
    });
});
