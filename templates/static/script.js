// Константы Telegram API
const tg = window.Telegram.WebApp;
const MainButton = tg.MainButton;
Telegram.WebApp.expand();
MainButton.setParams({ color: '#4CAF50', text: 'Оформить заказ', has_shine_effect: true }); // Устанавливаем параметры кнопки
const userFirstName = tg.initDataUnsafe.user.first_name; // Имя пользователя
const userID = tg.initDataUnsafe.user.id; // ID пользователя
const userAvatar = tg.initDataUnsafe.user.photo_url; // Аватар пользователя

// Элементы DOM
const modal = document.getElementById('cartModal'); // Модальное окно корзины
const historyModal = document.getElementById('historyModal'); // Модальное окно истории
const checkoutButton = document.getElementById('checkoutButton'); // Кнопка оформления заказа
const modalsucess = document.getElementById('successMdl'); // Модальное окно успешного оформления
const orderNumberSpan = document.getElementById('orderNumber'); // Элемент для отображения номера заказа
const organizationInput = document.getElementById('organization_name'); // Поле ввода названия организации

// Другие переменные
let cart = {}; // Корзина
let items = []; // Список организаций

// Функция для заполнения информации о пользователе
function fillUserInfo() {
    const userNameElement = document.getElementById('userName'); // Элемент для имени пользователя
    const userAvatarElement = document.querySelector('.user-avatar'); // Элемент для аватара пользователя
    userNameElement.textContent = userFirstName; // Устанавливаем имя пользователя
    userAvatarElement.src = userAvatar; // Устанавливаем аватар пользователя
}

// Обработчик нажатия на основную кнопку
MainButton.onClick(function () {
    updateCartModal(); // Обновляем модальное окно корзины
    modal.style.display = "block"; // Показываем модальное окно
    MainButton.hide(); // Скрываем основную кнопку
});

// Вызываем функцию загрузки данных при загрузке страницы
window.addEventListener('load', initializePage);

// Основная функция инициализации страницы
async function initializePage() {
    try {
        // Скрываем прелоадер и показываем контент
        const preloader = document.getElementById('preloader');
        const content = document.getElementById('content');
        preloader.style.display = 'none';
        content.style.display = 'block';

        // Заполняем информацию о пользователе
        fillUserInfo();

        // Загружаем данные из API
        
        const response = await fetch(`/products/${encodeURIComponent(userID)}`);
        if (!response.ok) throw new Error('Network response was not ok');
        const products = await response.json();

        // Создаем карточки товаров
        createProductCards(products);

        // Устанавливаем значение организации в поле ввода если ранее было сохранено
        organizationInput.value = products.organization || ''; // Устанавливаем значение организации из данных

        // Загружаем список организаций из файла
        await loadOrganizations();
    } catch (error) {
        console.error('Ошибка при инициализации страницы:', error);
    }
}

// Функция для загрузки списка организаций из файла
async function loadOrganizations() {
    try {
        const response = await fetch('/static/Organization/name.json');
        if (!response.ok) throw new Error('Не удалось загрузить список организаций');
        items = await response.json(); // Записываем данные в глобальную переменную
        console.log('Список организаций загружен:', items);
    } catch (error) {
        console.error('Ошибка при загрузке списка организаций:', error);
    }
}


// Функция для создания карточек товаров из JSON
function createProductCards(products) {
    const peeledGrid = document.getElementById('peeledGrid'); // Сетка очищенных товаров
    const unpeeledGrid = document.getElementById('unpeeledGrid'); // Сетка неочищенных товаров

    products.products.forEach(product => {
        const productCard = document.createElement('div'); // Создаем карточку товара
        productCard.className = 'product-card'; // Устанавливаем класс
        productCard.dataset.category = product.category_id; // Добавляем категорию в data-атрибут
        productCard.innerHTML = `
            <img src="${product.image}" alt="${product.description}" class="product-image">
            <div class="product-info">
                <div class="product-name" id=${product.id}>${product.name}</div>
                <span class="product-description">${product.description} кг</span>
                <button class="add-to-cart">В корзину</button>
            </div>
        `;

        const addToCartButton = productCard.querySelector('.add-to-cart'); // Кнопка "В корзину"
        addToCartButton.addEventListener('click', (event) => handleAddToCart(event, product)); // Добавляем обработчик

        if (product.category_id === 1) {
            peeledGrid.appendChild(productCard); // Добавляем в сетку очищенных товаров
        } else {
            unpeeledGrid.appendChild(productCard); // Добавляем в сетку неочищенных товаров
        }
    });
}

// Функция для получения упаковочной единицы
function getPackingUnit(description) {
    if (description) {
        const raw = description.replace(',', '.'); // Заменяем запятую на точку
        const parsed = parseFloat(raw); // Парсим число
        return !isNaN(parsed) && parsed > 0 ? parsed : 1; // Возвращаем значение или 1
    }
    return 1;
}

// Обработчик добавления товара в корзину
function handleAddToCart(event, product) {
    const productCard = event.target.closest('.product-card'); // Карточка товара
    const productName = product.name; // Название товара
    const productCategory = product.category_id; // Категория товара
    const productKey = `${productName}-${productCategory}`; // Уникальный ключ товара

    const packingUnit = getPackingUnit(product.description); // Упаковочная единица

    const inputWrapper = document.createElement('div'); // Обертка для поля ввода
    inputWrapper.className = 'quantity-input-wrapper';

    const input = document.createElement('input'); // Поле ввода количества
    input.type = 'text';
    input.value = `${packingUnit} кг`;
    input.className = 'quantity-input';

    inputWrapper.appendChild(input); // Добавляем поле ввода в обертку
    event.target.replaceWith(inputWrapper); // Заменяем кнопку на поле ввода

    // Функция округления до упаковочной единицы
    function roundToPackingUnit(value) {
        const val = parseFloat(value);
        if (isNaN(val) || val <= 0) return 0;
        const factor = 1 / packingUnit;
        return Math.ceil(val * factor) / factor;
    }

    // Функция обновления корзины
    function updateCart() {
        const raw = input.value.replace(/[^\d.,]/g, '').replace(',', '.'); // Убираем лишние символы
        const quantity = roundToPackingUnit(raw); // Округляем значение
        input.value = quantity > 0 ? `${quantity} кг` : ''; // Устанавливаем значение

        if (quantity > 0) {
            cart[productKey] = {
                id: product.id,
                name: product.name,
                category_id: product.category_id,
                quantity,
                image: product.image,
                description: product.description
            };
            updateProductCard(productKey, quantity); // Обновляем карточку товара
        } else {
            delete cart[productKey]; // Удаляем товар из корзины
        }

        updateCartMainButton(); // Обновляем основную кнопку
    }

    // Обработчик ввода в поле
    input.addEventListener('input', () => {
        const cursorPosition = input.selectionStart; // Сохраняем позицию курсора
        const raw = input.value.replace(/[^\d.,]/g, '').replace(',', '.'); // Убираем лишние символы
        input.value = raw ? `${raw} кг` : ''; // Устанавливаем новое значение
        const newCursorPosition = raw.length; // Рассчитываем новую позицию курсора
        input.setSelectionRange(newCursorPosition, newCursorPosition); // Восстанавливаем позицию курсора
    });

    // Обработчик нажатия Enter
    input.addEventListener('keydown', (e) => {
        if (e.key === 'Enter') {
            e.preventDefault(); // Предотвращаем стандартное поведение
            input.blur(); // Убираем фокус с поля ввода
            updateCart(); // Обновляем корзину
        }
    });

    // Обработчик потери фокуса
    input.addEventListener('blur', () => {
        const raw = input.value.replace(/[^\d.,]/g, '').replace(',', '.');
        if (raw === '' || parseFloat(raw) === 0) {
            const newButton = document.createElement('button'); // Создаем новую кнопку
            newButton.textContent = 'В корзину';
            newButton.className = 'add-to-cart';
            inputWrapper.replaceWith(newButton); // Заменяем поле ввода на кнопку
            newButton.addEventListener('click', (event) => handleAddToCart(event, product)); // Добавляем обработчик
            delete cart[productKey]; // Удаляем товар из корзины
        } else {
            updateCart(); // Обновляем корзину
        }
    });

    updateCart(); // Обновляем корзину
    updateCartMainButton(); // Обновляем основную кнопку
}

// Добавляем обработчики на все кнопки "В корзину"
document.querySelectorAll('.add-to-cart').forEach(button => {
    button.addEventListener('click', handleAddToCart);
});

// === Основные функции для работы с корзиной ===

// Обновляет содержимое модального окна корзины
function updateCartModal() {
    const cartItems = document.getElementById('cartItems');
    cartItems.innerHTML = '';

    // Категории товаров
    const categories = {
        1: { name: 'Чищенные овощи', items: [] },
        2: { name: 'Нечищенные овощи', items: [] }
    };

    // Распределяем товары по категориям
    for (const [productKey, item] of Object.entries(cart)) {
        categories[item.category_id].items.push(`
            <div class="cart-item">
                <img src="${item.image}" alt="${item.name}">
                <div class="cart-item-info">
                    <div class="cart-item-name">${item.name}</div>
                    <div class="cart-quantity-control">
                        <input type="number" class="cart-quantity-input" value="${item.quantity}" min="0" onchange="updateQuantity('${productKey}', this.value)">
                        <span class="cart-quantity-label">кг.</span>
                    </div>
                </div>
            </div>
        `);
    }

    // Добавляем категории в корзину
    for (const category of Object.values(categories)) {
        if (category.items.length > 0) {
            cartItems.innerHTML += `
                <div class="cart-category">
                    <h3>${category.name}</h3>
                    ${category.items.join('')}
                </div>
            `;
        }
    }

    // Показываем или скрываем кнопку оформления заказа
    checkoutButton.style.display = Object.keys(cart).length > 0 ? 'block' : 'none';
}

// Обновляет количество товара в корзине
function updateQuantity(productKey, newQuantity) {
    const item = cart[productKey];
    const packingUnit = getPackingUnit(item.description);

    const val = parseFloat(newQuantity);
    const factor = 1 / packingUnit;
    const rounded = Math.ceil(val * factor) / factor;

    if (rounded > 0) {
        cart[productKey].quantity = rounded;
        updateProductCard(productKey, rounded);
    } else {
        delete cart[productKey];
        updateProductCard(productKey, 0);
    }

    updateCartModal();
}

// Обновляет карточку товара на странице
function updateProductCard(productKey, quantity) {
    const productCards = document.querySelectorAll('.product-card');
    for (let card of productCards) {
        const cardKey = `${card.querySelector('.product-name').textContent}-${card.dataset.category}`;
        if (cardKey === productKey) {
            const quantityInput = card.querySelector('.quantity-input');
            if (quantityInput) {
                if (quantity > 0) {
                    quantityInput.value = `${quantity} кг`;
                } else {
                    const newButton = document.createElement('button');
                    newButton.textContent = 'В корзину';
                    newButton.className = 'add-to-cart';
                    quantityInput.replaceWith(newButton);
                    newButton.addEventListener('click', (event) => handleAddToCart(event, cart[productKey]));
                }
            } else if (quantity > 0) {
                const addToCartButton = card.querySelector('.add-to-cart');
                if (addToCartButton) {
                    const inputWrapper = document.createElement('div');
                    inputWrapper.className = 'quantity-input-wrapper';

                    const input = document.createElement('input');
                    input.type = 'text';
                    input.value = `${quantity} кг`;
                    input.className = 'quantity-input';

                    inputWrapper.appendChild(input);
                    addToCartButton.replaceWith(inputWrapper);

                    input.addEventListener('input', () => {
                        const raw = input.value.replace(/[^\d.,]/g, '').replace(',', '.');
                        input.value = raw ? `${raw} кг` : '';
                    });

                    input.addEventListener('blur', () => {
                        const raw = input.value.replace(/[^\d.,]/g, '').replace(',', '.');
                        if (raw === '' || parseFloat(raw) === 0) {
                            const newButton = document.createElement('button');
                            newButton.textContent = 'В корзину';
                            newButton.className = 'add-to-cart';
                            inputWrapper.replaceWith(newButton);
                            newButton.addEventListener('click', (event) => handleAddToCart(event, cart[productKey]));
                            delete cart[productKey];
                        } else {
                            updateQuantity(productKey, raw);
                        }
                    });
                }
            }
            break;
        }
    }
}

// Показывает или скрывает основную кнопку корзины
function updateCartMainButton() {
    if (Object.keys(cart).length > 0) {
        MainButton.show();
    } else {
        MainButton.hide();
    }
}

// === Функции для оформления заказа ===

// Показывает модальное окно успешного заказа
function showModal(orderNumber) {
    orderNumberSpan.textContent = orderNumber;
    modal.style.display = "none";
    modalsucess.style.display = 'block';
}

// Отправляет заказ на сервер
async function success_order() {
    const orderButton = document.getElementById('checkoutButton');
    const loadingIndicator = document.getElementById('loading-bar-spinner');

    const order_date = document.getElementById('date_order').value;
    const name_organization = String(document.getElementById('organization_name').value).trim();

    if (!name_organization) {
        alert('Название организации не может быть пустым!');
        return;
    }
    if (!items.includes(name_organization)) {
        alert('Организация не найдена в списке! Пожалуйста, выберите из списка.');
        return;
    }

    if (!order_date) {
        alert('Дата заказа не может быть пустой!');
        return;
    }

    orderButton.style.display = 'none';
    loadingIndicator.style.display = 'block';

    try {
        const response = await fetch('/orders', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                products: cart,
                DeliveryDate: order_date,
                Organization: name_organization,
                CustomerId: userID
            })
        });

        if (response.ok) {
            const responseData = await response.json();
            const orderNumber = responseData.order_id;
            showModal(orderNumber);
        } else {
            alert(`Ошибка: ${response.statusText}`);
        }
    } catch (error) {
        alert(`Ошибка: ${error.message}`);
    } finally {
        orderButton.style.display = 'block';
        loadingIndicator.style.display = 'none';
    }
}

// === Функции для истории заказов ===

// Загружает историю заказов
async function order_history() {
    try {
        const response = await fetch(`/user_orders/${encodeURIComponent(userID)}`, {
            method: 'GET',
            headers: {
                'Content-Type': 'application/json',
            },
        });

        if (response.status === 204) {
            tg.showAlert('История заказов пуста');
        } else if (response.ok) {
            const responseData = await response.json();
            displayHistory(responseData);
        } else {
            console.error('Ошибка загрузки данных истории заказов');
        }
    } catch (error) {
        tg.showAlert('Произошла ошибка при загрузке истории заказов');
    }
}

// Отображает историю заказов
function displayHistory(data) {
    const historyContent = document.getElementById('historyContent');
    historyContent.innerHTML = '';
    data.orders.forEach((order) => {
        const orderBlock = document.createElement('div');
        orderBlock.className = 'order-block';

        const orderHeader = document.createElement('h3');
        orderHeader.textContent = `Заказ № ${order.order_id} от ${order.delivery_date}`;
        orderBlock.appendChild(orderHeader);

        const categoriesList = document.createElement('ul');

        for (const category in order.products) {
            const categoryHeader = document.createElement('li');
            categoryHeader.className = 'category-header';
            categoryHeader.textContent = category;
            const productsList = document.createElement('ul');

            order.products[category].forEach((product) => {
                const productItem = document.createElement('li');
                productItem.className = 'product-item';
                productItem.innerHTML = `<span>${product.name}</span> <span class="product-quantity">${product.quantity} кг.</span>`;
                productsList.appendChild(productItem);
            });

            categoryHeader.appendChild(productsList);
            categoriesList.appendChild(categoryHeader);
        }

        orderBlock.appendChild(categoriesList);
        historyContent.appendChild(orderBlock);
    });

    const historyModal = document.getElementById('historyModal');
    historyModal.style.display = 'block';
    MainButton.hide();
}

// === Функции для модальных окон ===

// Закрывает основное модальное окно
function closeModal() {
    tg.close();
}

// Закрывает модальное окно истории заказов
function closeHistoryModal() {
    historyModal.style.display = "none";
    updateCartMainButton();
}

// Закрывает модальное окно корзины
function closeCartModal() {
    modal.style.display = "none";
    updateCartMainButton();
}

// === Прочие функции ===

// Фильтрует элементы в списке
function filterOrganization() {
    const input = document.getElementById('organization_name');
    const dataList = document.getElementById('organization_list');
    const query = input.value.toLowerCase();

    // Очищаем предыдущие результаты
    dataList.innerHTML = '';

    // Фильтруем элементы и добавляем их в datalist
    const filteredItems = items.filter(item => item.toLowerCase().includes(query));
    filteredItems.forEach(item => {
        const option = document.createElement('option');
        option.value = item; // Сохраняем оригинальный регистр
        dataList.appendChild(option);
    });
}

// Обрабатывает нажатие клавиши Enter
function handleKeyDown(event) {
    if (event.key === 'Enter') {
        event.preventDefault();
        document.activeElement.blur();
    }
}

// Обрабатывает клик вне модальных окон
window.onclick = function (event) {
    if (event.target == modal) {
        modal.style.display = "none";
    }
    if (event.target == historyModal) {
        historyModal.style.display = "none";
    }
}