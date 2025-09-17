#!/usr/bin/env python3
"""Test chat message formatting for AI."""

# Simulate message objects
class MockMessage:
    def __init__(self, text, is_outgoing, sender_first_name=None, sender_last_name=None, sender_username=None):
        self.text = text
        self.is_outgoing = is_outgoing
        self.sender_first_name = sender_first_name
        self.sender_last_name = sender_last_name
        self.sender_username = sender_username

# Test messages
messages = [
    MockMessage("Здравствуйте! Интересуют ваши финансовые услуги.", False, "Иван", "Петров"),
    MockMessage("Здравствуйте! Да, мы предоставляем различные финансовые услуги. Расскажите подробнее, что вас интересует?", True),
    MockMessage("Нужны реквизиты для Германии и Казахстана.", False, "Иван", "Петров"),
    MockMessage("Отлично! У нас есть проверенные партнеры в этих странах. Перед тем как предоставить контакты, мне нужно задать несколько вопросов для безопасности.", True),
    MockMessage("Конечно, спрашивайте.", False, "Иван", "Петров"),
    MockMessage("Какова ваша позиция в компании?", True),
]

# Format messages as AI would see them
formatted_messages = []
for msg in messages:
    if msg.is_outgoing:
        # Исходящее сообщение от бизнес-аккаунта
        sender_label = "Вы (бизнес-аккаунт)"
    else:
        # Входящее сообщение от клиента
        sender_name = f"{msg.sender_first_name or ''} {msg.sender_last_name or ''}".strip()
        if not sender_name and msg.sender_username:
            sender_name = f"@{msg.sender_username}"
        if not sender_name:
            sender_name = "Клиент"
        sender_label = sender_name

    formatted_messages.append(f"{sender_label}: {msg.text}")

chat_history = "\n".join(formatted_messages)

print("История чата для AI:")
print("=" * 50)
print(chat_history)
print("=" * 50)
print("\nТеперь AI четко понимает, какие сообщения от бизнес-аккаунта, а какие от клиента!")
