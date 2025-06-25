"""
Тест параллельности LiteLLM с DeepSeek
"""

import asyncio
import time
import os
from litellm import acompletion
from dotenv import load_dotenv

load_dotenv()

# Получаем API ключи из .env
API_KEYS = [
    os.getenv("DEEPSEEK_API_KEY_1"),
    os.getenv("DEEPSEEK_API_KEY_2"),
    os.getenv("DEEPSEEK_API_KEY_3")
]

async def test():
    print("=" * 60)
    print("ТЕСТ ПАРАЛЛЕЛЬНОСТИ DEEPSEEK API")
    print("=" * 60)
    
    # Проверяем наличие ключей
    valid_keys = [k for k in API_KEYS if k and k.startswith("sk-")]
    print(f"\nНайдено активных ключей: {len(valid_keys)}")
    
    if not valid_keys:
        print("❌ Нет настроенных API ключей!")
        return
    
    print(f"Отправляем {len(valid_keys)} запросов ОДНОВРЕМЕННО...\n")
    
    start = time.time()
    
    # Создаем задачи с разными ключами
    tasks = []
    for i, key in enumerate(valid_keys, 1):
        task = acompletion(
            model="deepseek/deepseek-chat",
            messages=[
                {"role": "system", "content": "You are a helpful assistant. Respond with exactly 'pong' to any message containing 'ping'."},
                {"role": "user", "content": "ping"}
            ],
            api_key=key,
            max_tokens=10
        )
        tasks.append(task)
        print(f"✅ Запрос {i} отправлен! (время: {time.time() - start:.2f}s)")
    
    # Ждем ВСЕ ответы
    print("\nЖдем ответы...")
    try:
        responses = await asyncio.gather(*tasks, return_exceptions=True)
    except Exception as e:
        print(f"❌ Общая ошибка: {e}")
        return
    
    end = time.time()
    
    # Показываем результаты
    print("\nПолучены ответы:")
    for i, resp in enumerate(responses, 1):
        if isinstance(resp, Exception):
            print(f"❌ Ответ {i}: ОШИБКА - {resp}")
        else:
            try:
                content = resp.choices[0].message.content.strip()
                print(f"✅ Ответ {i}: {content}")
            except:
                print(f"❌ Ответ {i}: Ошибка парсинга")
    
    total_time = end - start
    print(f"\n⏱️  Общее время: {total_time:.2f} секунд")
    print(f"📊 Среднее время на запрос: {total_time/len(valid_keys):.2f} секунд")
    
    # Анализ результата
    if len(valid_keys) >= 2:
        if total_time < 3:
            print("✅ Запросы выполнялись ПАРАЛЛЕЛЬНО!")
        elif total_time < 5:
            print("🟡 Запросы частично параллельны")
        else:
            print("❌ Запросы выполнялись ПОСЛЕДОВАТЕЛЬНО!")
    
    print("=" * 60)

# Дополнительный тест с явным логированием времени
async def detailed_test():
    print("\n\nДЕТАЛЬНЫЙ ТЕСТ С ЛОГИРОВАНИЕМ ВРЕМЕНИ")
    print("=" * 60)
    
    valid_keys = [k for k in API_KEYS if k and k.startswith("sk-")][:3]
    
    async def single_request(key, index):
        start = time.time()
        print(f"[{start:.2f}] Запрос {index} НАЧАТ")
        
        try:
            response = await acompletion(
                model="deepseek/deepseek-chat",
                messages=[{"role": "user", "content": f"Say only: test{index}"}],
                api_key=key,
                max_tokens=10
            )
            end = time.time()
            print(f"[{end:.2f}] Запрос {index} ЗАВЕРШЕН за {end-start:.2f}s")
            return response.choices[0].message.content.strip()
        except Exception as e:
            end = time.time()
            print(f"[{end:.2f}] Запрос {index} ОШИБКА за {end-start:.2f}s: {e}")
            return f"Error: {e}"
    
    # Запускаем все одновременно
    start_all = time.time()
    results = await asyncio.gather(*[
        single_request(key, i) for i, key in enumerate(valid_keys, 1)
    ])
    end_all = time.time()
    
    print(f"\nВСЕ запросы завершены за {end_all - start_all:.2f} секунд")
    print("Результаты:", results)

# Запускаем тесты
if __name__ == "__main__":
    print("Запуск базового теста...")
    asyncio.run(test())
    
    print("\n\n")
    
    print("Запуск детального теста...")
    asyncio.run(detailed_test())