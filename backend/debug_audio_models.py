#!/usr/bin/env python3
"""
Отладочный скрипт для поиска аудио-моделей в OpenRouter.
"""
import asyncio
import json
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.services.settings_service import SettingsService
from app.services.openrouter_service import OpenRouterModelManager
from app.schemas.settings_schema import KeyTypeEnum

async def debug_audio_models():
    """Отладка поиска аудио-моделей."""
    
    print("🔍 Поиск аудио-моделей в OpenRouter...")
    
    # Получаем сессию базы данных
    db_gen = get_db()
    db: Session = next(db_gen)
    
    try:
        settings_service = SettingsService(db)
        user_id = 1
        openrouter_key = settings_service.get_api_key(user_id, KeyTypeEnum.OPENROUTER, decrypt=True)
        
        if not openrouter_key:
            print("❌ OpenRouter API ключ не найден!")
            return
        
        manager = OpenRouterModelManager(openrouter_key)
        service = await manager.get_service()
        
        # Получаем все модели
        all_models = await service.get_models()
        print(f"📊 Всего моделей: {len(all_models)}")
        
        # Ищем модели с аудио в названии или ID
        audio_keywords = ["audio", "whisper", "speech", "voice", "tts", "transcription", "asr"]
        potential_audio_models = []
        
        print("\n🔍 Поиск моделей с аудио-ключевыми словами...")
        for model in all_models:
            model_text = f"{model.id} {model.name}".lower()
            
            for keyword in audio_keywords:
                if keyword in model_text:
                    potential_audio_models.append({
                        "id": model.id,
                        "name": model.name,
                        "input_modalities": model.input_modalities,
                        "output_modalities": model.output_modalities,
                        "architecture": model.architecture,
                        "keyword_found": keyword,
                        "category": model.get_model_category()
                    })
                    break
        
        if potential_audio_models:
            print(f"🎵 Найдено {len(potential_audio_models)} моделей с аудио-ключевыми словами:")
            for model in potential_audio_models:
                print(f"\n   • {model['name']} ({model['id']})")
                print(f"     Ключевое слово: {model['keyword_found']}")
                print(f"     Input: {model['input_modalities']}")
                print(f"     Output: {model['output_modalities']}")
                print(f"     Architecture: {model['architecture']}")
                print(f"     Category: {model['category']}")
        else:
            print("❌ Модели с аудио-ключевыми словами не найдены")
        
        # Проверяем, есть ли модели с input_modalities или output_modalities содержащими audio
        print("\n🔍 Поиск моделей с аудио в модальностях...")
        audio_modality_models = []
        
        for model in all_models:
            if ("audio" in model.input_modalities or 
                "audio" in model.output_modalities or
                any("audio" in str(mod).lower() for mod in model.input_modalities) or
                any("audio" in str(mod).lower() for mod in model.output_modalities)):
                audio_modality_models.append({
                    "id": model.id,
                    "name": model.name,
                    "input_modalities": model.input_modalities,
                    "output_modalities": model.output_modalities,
                    "category": model.get_model_category()
                })
        
        if audio_modality_models:
            print(f"🎵 Найдено {len(audio_modality_models)} моделей с аудио в модальностях:")
            for model in audio_modality_models:
                print(f"\n   • {model['name']} ({model['id']})")
                print(f"     Input: {model['input_modalities']}")
                print(f"     Output: {model['output_modalities']}")
                print(f"     Category: {model['category']}")
        else:
            print("❌ Модели с аудио в модальностях не найдены")
        
        # Проверяем архитектуру моделей
        print("\n🔍 Анализ архитектур моделей...")
        architecture_stats = {}
        
        for model in all_models:
            arch_modality = model.architecture.get("modality", "unknown")
            architecture_stats[arch_modality] = architecture_stats.get(arch_modality, 0) + 1
        
        print("📊 Статистика архитектур:")
        for arch, count in sorted(architecture_stats.items(), key=lambda x: x[1], reverse=True):
            print(f"   {arch}: {count} моделей")
            if "audio" in arch.lower():
                print(f"      ⭐ Содержит 'audio'!")
        
        # Сохраняем результаты отладки
        debug_results = {
            "total_models": len(all_models),
            "potential_audio_models": potential_audio_models,
            "audio_modality_models": audio_modality_models,
            "architecture_stats": architecture_stats,
            "audio_keywords_searched": audio_keywords
        }
        
        with open("audio_models_debug.json", "w", encoding="utf-8") as f:
            json.dump(debug_results, f, indent=2, ensure_ascii=False)
        
        print(f"\n💾 Результаты отладки сохранены в audio_models_debug.json")
        
        await manager.close()
        
        # Выводы
        print("\n📋 Выводы:")
        if potential_audio_models or audio_modality_models:
            print("✅ Найдены потенциальные аудио-модели")
            print("💡 Возможно, нужно обновить логику определения аудио-моделей")
        else:
            print("❌ Аудио-модели не найдены в текущем плане OpenRouter")
            print("💡 Рекомендации:")
            print("   1. Проверьте, поддерживает ли ваш план OpenRouter аудио-модели")
            print("   2. Обратитесь к документации OpenRouter для актуального списка моделей")
            print("   3. Возможно, аудио-модели доступны только в платных планах")
        
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        import traceback
        traceback.print_exc()
        
    finally:
        db.close()

if __name__ == "__main__":
    print("🚀 Debug Audio Models in OpenRouter")
    print("=" * 50)
    asyncio.run(debug_audio_models())
