// Фильтр категории магазинов
document.getElementById('store-category-select').addEventListener('change', async function () {
    const categoryId = this.value;
    const response = await fetch(`/filtered_stores/?category=${categoryId}`);
    const data = await response.json();

    const storesList = document.getElementById('stores-list');
    storesList.innerHTML = '';

    data.stores.forEach(store => {
        const listItem = document.createElement(`div`);
        listItem.setAttribute('class', 'item-shop'); // Добавляем класс
        listItem.setAttribute('data-id', store.id); // Устанавливаем data-id
        if (store.openClose && store.onMain) {
            listItem.innerHTML = `
                <a href="/store/${store.id}/">
                    <img class="item-img" src="${store.image}" alt="${store.name}">
                </a>
                <a href="/store/${store.id}/">
                    <div class="item-shop-title">${store.name} | ${store.category} ${store.openingTime}-${store.closingTime}</div>
                </a>`
        } else {
            listItem.innerHTML = `
                <img class="item-img" src="/static/img/close.avif" alt="Закрыто">
                <div class="item-shop-title">${store.name} | ${store.category}
                    <span class="close-text">Закрыто</span>
                </div>`
        }
        storesList.appendChild(listItem);
    });
});

document.addEventListener('DOMContentLoaded', () => {
    updateBasketImage();
});