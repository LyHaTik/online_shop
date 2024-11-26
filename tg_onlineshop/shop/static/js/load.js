let tg = Telegram.WebApp;
tg.expand();


window.onload = async () => {
    // ПРОВЕРКА ПОЛЬЗОВАТЕЛЯ
    const initDataUnsafe = tg.initDataUnsafe;
    
    // Получаем ID пользователя из initData
    const userId = initDataUnsafe.user?.id;  

    if (!userId) {
        alert("Ошибка: Не удалось получить ID пользователя.");
        return;
    }

    // Записываем ID в память браузера клиента
    let user = JSON.parse(localStorage.getItem('user')) || {};
    user['user_id'] = userId;
    localStorage.setItem('user', JSON.stringify(user));

    // Отправляем запрос на сервер Django для проверки пользователя
    const response = await fetch(`/check_user/?user_id=${userId}`);
    const data = await response.json();
    if (data.is_registered) {
        // Пользователь найден, показываем контент
        window.location.href = '/store_list/';
    } else {
        // Пользователь не найден, перенаправляем на страницу регистрации
        window.location.href = '/register/';
    }
};