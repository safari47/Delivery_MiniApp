from delivery.schemas import OrdersIn


def generate_message(orders: OrdersIn) -> str:
    # Создаем два списка продуктов по категориям
    peeled_products = []
    unpeeled_products = []
    for product in orders.products.values():
        if product.category_id == 1:
            peeled_products.append(f"{product.name} — {product.quantity} кг")
        elif product.category_id == 2:
            unpeeled_products.append(f"{product.name} — {product.quantity} кг")

    # Формируем сообщение
    message_lines = [
        "📦 *Заявка на поставку*",
        "━━━━━━━━━━━━",
        f"*🏢 Организация:* {orders.Organization}",
        f"*📅 Дата поставки:* {orders.DeliveryDate.strftime('%d.%m.%Y')}",
        "━━━━━━━━━━━━",
        "🥗 *Овощи в заказе:*",
    ]

    if peeled_products:
        message_lines.append("━━━━━━━━━━━━")
        message_lines.append("*Очищенные овощи:*")
        message_lines.extend(peeled_products)

    if unpeeled_products:
        message_lines.append("━━━━━━━━━━━━")
        message_lines.append("*Неочищенные овощи:*")
        message_lines.extend(unpeeled_products)

    return "\n".join(message_lines)
