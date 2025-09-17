#!/usr/bin/env python3
"""Test JSON parsing for suggestions."""

import json

def clean_json_response(ai_response: str) -> str:
    """Clean AI response from markdown formatting."""
    cleaned_response = ai_response.strip()

    # Remove markdown code blocks
    if cleaned_response.startswith('```json'):
        cleaned_response = cleaned_response[7:]
    if cleaned_response.startswith('```'):
        cleaned_response = cleaned_response[3:]
    if cleaned_response.endswith('```'):
        cleaned_response = cleaned_response[:-3]

    return cleaned_response.strip()

# Test cases
test_responses = [
    # Case 1: With ```json
    '''```json
{
  "suggestions": [
    "Спасибо за информацию! Я ознакомлюсь с вашими предложениями и свяжусь с вами в ближайшее время.",
    "Отлично, благодарю за подробный разбор. Когда можно ожидать готовую презентацию?",
    "Хорошо, учту все ваши пожелания. Давайте договоримся о звонке на следующей неделе.",
    "Спасибо за обратную связь! Внесу необходимые правки и пришлю обновленный вариант."
  ]
}
```''',

    # Case 2: Clean JSON
    '''{
  "suggestions": [
    "Конечно, отправлю вам все необходимые документы сегодня до конца дня.",
    "Спасибо за понимание! Я подготовлю детальное предложение в ближайшие 2 часа.",
    "Хорошо, давайте встретимся завтра в 14:00 для обсуждения деталей проекта."
  ]
}'''
]

for i, response in enumerate(test_responses, 1):
    print(f"\n=== Test Case {i} ===")
    print(f"Original length: {len(response)} chars")

    cleaned = clean_json_response(response)
    print(f"Cleaned length: {len(cleaned)} chars")

    try:
        parsed = json.loads(cleaned)
        suggestions = parsed.get("suggestions", [])
        print(f"✅ JSON parsed successfully")
        print(f"Found {len(suggestions)} suggestions:")
        for j, suggestion in enumerate(suggestions, 1):
            print(f"  {j}. {suggestion[:60]}{'...' if len(suggestion) > 60 else ''}")
    except json.JSONDecodeError as e:
        print(f"❌ JSON parsing failed: {e}")
        print(f"Cleaned response: {cleaned[:200]}...")
