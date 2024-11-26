
document.addEventListener("DOMContentLoaded", () => {
    // Получаем данные пользователя из initDataUnsafe
    const userData = tg.initDataUnsafe.user;

    if (userData) {
        // Заполняем поля формы
        document.getElementById("name").value = `${userData.first_name} ${userData.last_name}` || "";
        document.getElementById("tg_username").value = userData.username || "";
        document.getElementById("user-id").textContent = userData.id || "";
    } else {
        console.error("Данные пользователя недоступны.");
    }
});

async function sendData() {
    const form = document.getElementById('registrationForm');
    const formData = new FormData(form);

    // Добавляем ID пользователя из initData (если доступно)
    const userId = tg.initDataUnsafe.user?.id;
    
    if (userId) {
        formData.append('telegram_id', userId);
    }

    try {
        // Отправляем данные на сервер
        const response = await fetch('/register_user/', {
            method: 'POST',
            body: formData,
        });

        const result = await response.json();

        if (result.success) {
            tg.showAlert(`✅ Регистрация успешна, ${result.name}!`);
            window.location.href = '/';
        } else {
            console.log('result', result)
            tg.showAlert(`⛔️ Ошибка: ${result.errors}`);
        }
    } catch (error) {
        tg.showAlert(`Ошибка отправки данных: ${error.message}`);
    }
};