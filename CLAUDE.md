# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview
This is a Streamlit-based admin panel for monitoring a cryptocurrency analytics system that collects data from social networks (Telegram, Twitter, Discord, Reddit, YouTube) and tracks API usage costs.

## Key Commands
```bash
# Install dependencies
pip install -r requirements.txt

# Run the application
streamlit run app.py

# Run with specific port
streamlit run app.py --server.port 8080

# Check database connection
python -m database.connection
```

## Architecture

### Core Components
1. **Multi-page Streamlit App**: Main entry point is `app.py`, with pages in `pages/` directory
2. **PostgreSQL Database**: Existing database with tables for messages, API usage, processing queue
3. **API Monitoring**: Critical feature for tracking costs across OpenAI, Twitter API, YouTube API, etc.
4. **Caching Layer**: Using Streamlit's native caching for performance

### Critical Features
- **API Cost Monitoring**: Track balances, usage, and limits for all paid services (OpenAI, Twitter, YouTube)
- **Real-time Dashboard**: Show system health, processing speed, top tickers
- **Processing Queue**: Monitor task queue, errors, and performance
- **Ticker Analytics**: Search and analyze cryptocurrency mentions with sentiment

### Database Schema (Key Tables)
- `messages`: Social media posts with platform, ticker, sentiment
- `api_usage`: Track API calls, tokens, and costs
- `processing_queue`: Task queue with status tracking
- `api_keys`: API service configurations and limits

## Development Guidelines

### When Adding New Features
1. Check existing utility modules in `utils/` before creating new ones
2. Use Streamlit's caching decorators (`@st.cache_data`) for expensive queries
3. Follow the existing page naming convention: `{number}_{emoji}_{Name}.py`
4. **IMPORTANT**: When using new libraries, ALWAYS add them to `requirements.txt` immediately

### API Monitoring Priority
The API monitoring page is CRITICAL - ensure accurate cost tracking:
- Always update `api_usage` table after API calls
- Implement balance checks before expensive operations
- Add alerts when approaching limits

### Performance Considerations
- Use database indexes on frequently queried columns (ticker, created_at)
- Implement pagination for large data tables
- Cache aggregated statistics with appropriate TTL

### Error Handling
- Log all API errors to `processing_queue` with error details
- Show user-friendly error messages in the UI
- Implement retry logic for transient API failures

## Development Approach

### Incremental Development
- Implement features step-by-step, allowing testing after each step
- Each commit should result in a working application (even if limited)
- Start with minimal functionality and expand gradually
- Always ensure the app can run with `streamlit run app.py` after each change

### Testing Points
After each implementation step:
1. User can run the application and see the new feature
2. Previous functionality remains working
3. Clear feedback on what was added/changed
4. No broken imports or missing dependencies

### Implementation Order
1. **Step 1**: Basic app structure + empty pages → User can see navigation
2. **Step 2**: Database connection → User can verify DB connectivity
3. **Step 3**: One working metric → User sees real data
4. **Step 4**: Add more features incrementally → User tests each addition

This approach ensures the user can always see progress and catch issues early.

## Work Rules

### Communication Language

- ВСЕ РАЗМЫШЛЕНИЯ И ОБЩЕНИЕ НА РУССКОМ ЯЗЫКЕ!!!
- Technical terms - English!!! 
- Code comments - English!!!


### КРИТИЧЕСКОЕ ПРАВИЛО - УТОЧНЯЮЩИЕ ВОПРОСЫ ПЕРЕД ВЫПОЛНЕНИЕМ

[!] **ОБЯЗАТЕЛЬНОЕ ПРАВИЛО**: Перед выполнением любой сложной задачи или при малейших сомнениях:
- **ВСЕГДА задавай четкие уточняющие вопросы**
- Структурируй вопросы по пунктам с номерами
- Выделяй ключевые моменты жирным шрифтом
- Приводи примеры для ясности
- Показывай текущее состояние и предлагаемые изменения
- Жди явного подтверждения перед действиями

**ФОРМАТ ВОПРОСОВ**:
1. **Тема вопроса**: Конкретное описание
   - Текущее состояние: ...
   - Предлагаемое решение: ...
   - **Вопрос**: Правильно ли я понимаю...?

**КОГДА ОБЯЗАТЕЛЬНО СПРАШИВАТЬ**:
- Изменение структуры данных
- Удаление или перемещение файлов
- Изменение логики работы
- Неоднозначность в требованиях
- Потенциальная потеря данных

### КРИТИЧЕСКОЕ ПРАВИЛО - АНАЛИЗ БЕЗ ИЗМЕНЕНИЙ

[!] **АБСОЛЮТНОЕ ПРАВИЛО**: Если в запросе есть слова "проанализируй", "сделай анализ", "analyze", "анализ" или любые их формы:
- **СТОП! НЕ ВНОСИ НИКАКИХ ИЗМЕНЕНИЙ В КОД!**
- **НЕ СОЗДАВАЙ НОВЫХ ФАЙЛОВ!**
- **НЕ РЕДАКТИРУЙ СУЩЕСТВУЮЩИЕ ФАЙЛЫ!**
- Только размышляй, исследуй и предлагай варианты решения
- Используй инструменты Read, Grep, Glob ТОЛЬКО для чтения и анализа
- Предоставь детальный анализ с вариантами решения
- Жди явного запроса на реализацию ("реализуй", "сделай", "внеси изменения")

### Step-by-Step Execution

- Ask questions when unclear
- NO assumptions
- Request sudo/admin permissions explicitly

### Write Maximally Concise and Laconic Code

- Less code is better
- Minimal logs (only if user explicitly requests logs)
- If you created a test for verification, delete it after use

### КРИТИЧЕСКОЕ ПРАВИЛО - НЕ СОЗДАВАТЬ ИНСТРУКЦИИ БЕЗ ЗАПРОСА

[!] **АБСОЛЮТНОЕ ПРАВИЛО**: НЕ создавай инструкции по использованию, README файлы или документацию, если пользователь явно не просит!
- **ЗАПРЕЩЕНО**: Автоматически создавать файлы типа USAGE.md, INSTRUCTIONS.md, HOW_TO_USE.md
- **ЗАПРЕЩЕНО**: Добавлять длинные инструкции в конце ответа
- **РАЗРЕШЕНО**: Краткий комментарий о том, как запустить (1-2 строки максимум)
- **ИСКЛЮЧЕНИЕ**: Только если пользователь явно просит "создай инструкцию", "напиши документацию", "объясни как использовать"

**ПОЧЕМУ ЭТО ВАЖНО**:
- Избегаем засорения проекта ненужной документацией
- Пользователь знает свой проект лучше
- Экономим время на ненужные действия

### КРИТИЧЕСКОЕ ПРАВИЛО - НЕ СОЗДАВАТЬ ВЕРСИИ ФАЙЛОВ

[!] **АБСОЛЮТНОЕ ПРАВИЛО**: НИКОГДА не создавай версии файлов!
- **ЗАПРЕЩЕНО**: file_v2.py, file_new.py, file_updated.py, file_old.py
- **ПРАВИЛЬНО**: Всегда обновляй существующий файл
- **ПРИНЦИП**: Одна задача - один файл
- **НЕ СОЗДАВАЙ**: backup файлы, версии, копии
- **ИСКЛЮЧЕНИЕ**: Только если пользователь явно просит создать новый файл с конкретным именем

**ПОЧЕМУ ЭТО ВАЖНО**:
- Версии файлов создают путаницу
- Непонятно какой файл использовать
- Усложняется поддержка кода
- Git уже хранит историю изменений

### Code Minimalism

- NO unnecessary functionality
- Priority: reliability > performance > beauty
- Follow YAGNI principle


### WSL/Windows Environment

- On start determine: `uname -a | grep -i microsoft`
- Use path.posix for paths
- Remember: localhost WSL ≠ localhost Windows

### User Uses Poetry

### Do Only What User Requested, Write Code Safely

## Additional Safety Rules

### Project Context
- ВСЕ РАЗМЫШЛЕНИЯ И ОБЩЕНИЕ НА РУССКОМ ЯЗЫКЕ!!!
- Technical terms - English!!! 
- Code comments - English!!!

- ALWAYS ask project structure before changes
- Request current git branch: `git branch --show-current`
- Check status: `git status` before changes
- DON'T touch files outside task scope

### Before Code Changes

- Show which files will be modified
- Ask confirmation for critical files (.env, config, migrations)
- Make backup: `cp file.py file.py.bak` for important files

### Database

- NEVER execute DROP/DELETE without explicit confirmation
- Always use transactions for changes
- Show SQL before execution

### Testing Changes

- First show changes as diff
- Suggest running on test data
- DON'T run on production without explicit instruction

### State Tracking

- At session start ask: "What stage is the project at?"
- Keep brief action log in comments
- On error - rollback changes

### Environment Variables

- ALL secrets only through .env
- Check required variables on startup
- Default values for non-secret parameters


- ВСЕ РАЗМЫШЛЕНИЯ И ОБЩЕНИЕ НА РУССКОМ ЯЗЫКЕ!!!
- Technical terms - English!!! 
- Code comments - English!!!- ВСЕ РАЗМЫШЛЕНИЯ И ОБЩЕНИЕ НА РУССКОМ ЯЗЫКЕ!!!
- Technical terms - English!!! 
- Code comments - English!!!- ВСЕ РАЗМЫШЛЕНИЯ И ОБЩЕНИЕ НА РУССКОМ ЯЗЫКЕ!!!
- Technical terms - English!!! 
- Code comments - English!!!