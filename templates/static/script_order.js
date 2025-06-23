async function fetchOrders() {
    const selectedDate = document.getElementById('order-date').value;
    const response = await fetch(`/orders/${encodeURIComponent(selectedDate)}`, {
        method: 'GET',
        headers: {
            'Content-Type': 'application/json',
        },
    });
    
    const ordersContainer = document.getElementById('orders-container');
    const noOrdersElement = document.getElementById('no-orders');
    ordersContainer.innerHTML = '';

    if (response.status === 200) {
        const data = await response.json();
        noOrdersElement.style.display = 'none'; // Прячем элемент "нет заявок"
        ordersContainer.style.display = 'block'; // Отображаем контейнер заказов
        data.orders.forEach(order => {
            const orderBlock = document.createElement('div');
            orderBlock.classList.add('order-block');

            const orderHeader = document.createElement('div');
            orderHeader.classList.add('order-header');
            orderHeader.innerHTML = `<span class="order-number">Заявка №${order.order_id}</span><span class="organization-name">${order.organizationName}</span>`;
            orderBlock.appendChild(orderHeader);

            const orderDetails = document.createElement('div');
            orderDetails.classList.add('order-details');

            Object.keys(order.products).forEach(categoryName => {
                const category = order.products[categoryName];

                const categoryElement = document.createElement('div');
                categoryElement.classList.add('category', categoryName);
                categoryElement.textContent = categoryName;
                orderDetails.appendChild(categoryElement);

                category.forEach(product => {
                    const productInfo = document.createElement('div');
                    productInfo.classList.add('product-info');
                    productInfo.innerHTML = `<span class="product-name">${product.productName}</span><span class="product-quantity">${product.quantity} кг.</span>`;
                    orderDetails.appendChild(productInfo);
                });
            });

            orderBlock.appendChild(orderDetails);
            ordersContainer.appendChild(orderBlock);
        });
    } else if (response.status === 204) {
        noOrdersElement.style.display = 'block'; // Отображаем элемент "нет заявок"
        ordersContainer.style.display = 'none'; // Прячем контейнер заказов
    } else {
        // Дополнительная обработка для других ответов, если необходимо
        console.error('Ошибка при получении данных о заказах');
    }
}
