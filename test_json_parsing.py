#!/usr/bin/env python3
"""Test JSON parsing with markdown formatting."""

import json

def clean_json_response(ai_response: str) -> str:
    """Clean AI response from markdown formatting."""
    cleaned_response = ai_response.strip()

    # Remove markdown code blocks (```json ... ```)
    if cleaned_response.startswith('```json'):
        cleaned_response = cleaned_response[7:]  # Remove ```json
    if cleaned_response.startswith('```'):
        cleaned_response = cleaned_response[3:]  # Remove ```
    if cleaned_response.endswith('```'):
        cleaned_response = cleaned_response[:-3]  # Remove trailing ```

    return cleaned_response.strip()

# Test cases
test_responses = [
    # Case 1: With ```json
    '''```json
{ "summary": "Канал Top Fin Companies представил список проверенных поставщиков финансовых реквизитов с подробными условиями по разным странам и валютам. Основная цель диалога — знакомство с потенциальным клиентом и проверка его перед предоставлением контактов поставщиков. Были запрошены информация о позиции клиента в компании и интересующих его реквизитах, конкретно упомянуты Германия и Казахстан. Общение носит деловой характер с элементами процедуры безопасности.", "key_points": [ "Представлены 4 поставщика реквизитов с детальными ставками и минимальными суммами для разных стран (Узбекистан, Таджикистан, Европа и др.)", "Требуется проведение интервью и озвучивание своей позиции в компании перед предоставлением контактов", "Запрос информации о наличии реквизитов для Германии и Казахстана", "Акцент на безопасности: поставщики работают только после подтверждения от канала" ], "sentiment": "neutral" }
```''',

    # Case 2: With just ```
    '''```
{ "summary": "Test summary", "key_points": ["point 1"], "sentiment": "neutral" }
```''',

    # Case 3: Clean JSON
    '{ "summary": "Clean JSON test", "key_points": ["point 1"], "sentiment": "neutral" }'
]

for i, response in enumerate(test_responses, 1):
    print(f"\n=== Test Case {i} ===")
    print(f"Original: {response[:100]}...")

    cleaned = clean_json_response(response)
    print(f"Cleaned: {cleaned[:100]}...")

    try:
        parsed = json.loads(cleaned)
        print("✅ JSON parsed successfully")
        print(f"Summary: {parsed.get('summary', 'N/A')[:50]}...")
        print(f"Key points: {len(parsed.get('key_points', []))}")
        print(f"Sentiment: {parsed.get('sentiment', 'N/A')}")
    except json.JSONDecodeError as e:
        print(f"❌ JSON parsing failed: {e}")
