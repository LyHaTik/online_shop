let tg = Telegram.WebApp;
tg.expand();

// ЧАСЫ
function updateClock() {
    const clockElement = document.getElementById("header-clock");
    const now = new Date();
    // Получаем часы, минуты
    const hours = String(now.getHours()).padStart(2,0);
    const minutes = String(now.getMinutes()).padStart(2,0);
    // Форматируем время
    const timeString = `${hours}:${minutes}`;

    clockElement.textContent = timeString;
}
// Обновляем каждую секунду
setInterval(updateClock, 1000);


// ЗАКРЫТЬ
function tgClose() {
    tg.close();
}


let isPopupOpen = false; // Флаг состояния всплывающего окна
let cart = JSON.parse(localStorage.getItem('cart')) || {};

async function placeOrder() {
    if (Object.keys(cart).length === 0) {
        if (!isPopupOpen) {
            isPopupOpen = true; // Устанавливаем флаг
            tg.showAlert('⚠️ Корзина пуста!', () => {
                isPopupOpen = false; // Сбрасываем флаг после закрытия
            });
        }
        return;
    }

    try {
        // Подтверждение оформления заказа
        const confirmed = await new Promise((resolve) => {
            if (!isPopupOpen) {
                isPopupOpen = true;
                tg.showConfirm('Сделать заказ?', (result) => {
                    isPopupOpen = false; // Сбрасываем флаг после закрытия
                    resolve(result);
                });
            }
        });

        if (!confirmed) {
            console.log('Заказ отменен.');
            return;
        }

        let user = JSON.parse(localStorage.getItem('user')) || {};
        const userId = user['user_id'];

        // Формируем данные заказа
        const orderData = {
            clientId: userId,
            stores: Object.entries(cart)
                .filter(([storeId]) => !isNaN(parseInt(storeId, 10))) // Фильтруем только числовые storeId
                .map(([storeId, products]) => ({
                    storeId: parseInt(storeId, 10),
                    products: Object.entries(products)
                        .filter(([productId]) => !isNaN(parseInt(productId, 10))) // Фильтруем только числовые productId
                        .map(([productId, quantity]) => ({
                            productId: parseInt(productId, 10),
                            quantity,
                        })),
                })),
        };

        // Отправляем данные на сервер
        const response = await fetch('/create_order/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(orderData),
        });

        if (!response.ok) {
            throw new Error(`Ошибка запроса: ${response.status}`);
        }

        const data = await response.json();

        // Обрабатываем ответ сервера
        if (data.orders) {
            Object.entries(data.orders).forEach(([storeName, orderId]) => {
                if (!isPopupOpen) {
                    isPopupOpen = true;
                    tg.showAlert(
                        `✅ Заказ из магазина "${storeName}" успешно оформлен! Номер заказа: ${orderId}`,
                        () => {
                            isPopupOpen = false; // Сбрасываем флаг после закрытия
                        }
                    );
                }
            });

            // Очищаем корзину и перенаправляем пользователя
            localStorage.removeItem('cart');
            window.location.href = '/store_list/';
        } else {
            if (!isPopupOpen) {
                isPopupOpen = true;
                tg.showAlert('⛔️ Не удалось оформить заказы. Пожалуйста, попробуйте снова.', () => {
                    isPopupOpen = false; // Сбрасываем флаг после закрытия
                });
            }
        }
    } catch (error) {
        console.error('Произошла ошибка:', error);
        if (!isPopupOpen) {
            isPopupOpen = true;
            tg.showAlert('⛔️ Произошла ошибка при оформлении заказа. Пожалуйста, попробуйте позже.', () => {
                isPopupOpen = false; // Сбрасываем флаг после закрытия
            });
        }
    }
}

let user = JSON.parse(localStorage.getItem('user')) || {};
const userId = user['user_id'];
function toCart() {
    window.location.href = `/cart/${userId}`;
}

function updateBasketImage() {
    const buttonBasket = document.getElementById('button-basket');
    //let cart = JSON.parse(localStorage.getItem('cart')) || {};

    if (buttonBasket) {
        buttonBasket.setAttribute('class', 'close-button');
        buttonBasket.setAttribute('onclick', 'toCart()');

        const totalSum = cart['totalSum'] || 0; // Убедимся, что totalSum существует

        if (totalSum > 700 && totalSum <= 1000) {
            buttonBasket.innerHTML = `<img class="img-basket" src="/static/img/basket14.png" alt="Корзина">`;
        } else if (totalSum > 300 && totalSum <= 700) {
            buttonBasket.innerHTML = `<img class="img-basket" src="/static/img/basket23.png" alt="Корзина">`;
        } else if (totalSum > 0 && totalSum <= 300) {
            buttonBasket.innerHTML = `<img class="img-basket" src="/static/img/basket21.png" alt="Корзина">`;
        } else {
            buttonBasket.innerHTML = `<img class="img-basket" src="/static/img/basket20.png" alt="Корзина">`;
        }
    } else {
        console.error('Element with id "button-basket" not found');
    }
}


// Функция для обновления количества товара
function updateQuantity(storeId, productId, productPrice, change) {
    productPrice = parseFloat(productPrice);
    // Инициализация объекта корзины
    if (!cart[storeId]) {
        cart[storeId] = {};
    }

    if (!cart[storeId][productId]) {
        cart[storeId][productId] = 0;
    }

    if (!cart['totalSum']) {
        cart['totalSum'] = 0;
    }

    // Предыдущее количество товара
    const previousQuantity = cart[storeId][productId];

    // Обновляем количество товара
    cart[storeId][productId] = Math.max(0, previousQuantity + change);

    // Рассчитываем изменение общей суммы
    const quantityDifference = cart[storeId][productId] - previousQuantity;

    cart['totalSum'] += quantityDifference * productPrice;

    // Обновляем отображение количества товара
    document.getElementById(`quantity-${productId}`).textContent = cart[storeId][productId];

    // Обновляем общую сумму товаров
    document.getElementById('total').innerText = `${cart['totalSum']}р.`;

    // Удаляем товар из корзины, если его количество стало равно 0
    if (cart[storeId][productId] === 0) {
        delete cart[storeId][productId];
    }

    // Если корзина магазина пуста, удаляем магазин
    if (Object.keys(cart[storeId]).length === 0) {
        delete cart[storeId];
    }

    // Сохраняем данные корзины в localStorage
    localStorage.setItem('cart', JSON.stringify(cart));
    updateBasketImage();
}
