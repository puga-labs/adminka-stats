# Database Integration Guide

Этот файл содержит полную логику для интеграции новых баз данных в страницу Database Statistics (Processing).

## Текущее состояние

### Реализованная БД
- **twitter_data** - подключена через MCP сервер `postgres-telegram`
- Канал: `0xMert_` 
- Дата: `2023-08-22`
- Статус: работает

### Файл реализации
`pages/3_⚙️_Processing.py` - полностью переписан с нуля

## Архитектура решения

### 1. Структура функций

```python
@st.cache_data(ttl=300)
def get_[DATABASE]_db_stats() -> Dict:
    """Get [DATABASE] database statistics via MCP"""
    # Возвращает стандартную структуру данных
```

### 2. Стандартная структура данных

```python
{
    "database_name": "название_бд",
    "status": "connected|connection_error|data_error", 
    "channels": {
        "имя_канала": {
            "dates": ["2023-08-22", "2023-08-23"],
            "total_entries": 5
        }
    },
    "total_channels": 1,
    "total_dates": 2,
    "last_updated": "2025-06-24 17:42:08"
}
```

### 3. Статусы ошибок
- `connected` - все работает
- `connection_error` - нет подключения к БД
- `data_error` - ошибка валидации данных

## Инструкции для добавления новой БД

### Шаг 1: Добавить функцию получения данных

```python
@st.cache_data(ttl=300)
def get_telegram_db_stats() -> Dict:
    """Get Telegram database statistics via MCP"""
    try:
        # SQL запрос для получения каналов и дат
        channels_query = """
        SELECT 
            channel_name as channel,
            DATE(message_date) as date,
            COUNT(*) as entries
        FROM telegram_messages 
        GROUP BY channel_name, DATE(message_date)
        ORDER BY channel_name, date
        """
        
        # Пока используем заглушку - позже заменить на реальный MCP запрос
        channels_data = {
            "durov_channel": {
                "dates": ["2023-08-20", "2023-08-21"],
                "total_entries": 3
            }
        }
        
        # Валидация данных
        if not isinstance(channels_data, dict):
            raise ValueError("Invalid channels data format")
        
        total_channels = len(channels_data)
        total_dates = 0
        
        for channel_name, channel_data in channels_data.items():
            if not isinstance(channel_data, dict) or "dates" not in channel_data:
                raise ValueError(f"Invalid data format for channel: {channel_name}")
            total_dates += len(channel_data["dates"])
        
        return {
            "database_name": "telegram_data",
            "status": "connected",
            "channels": channels_data,
            "total_channels": total_channels,
            "total_dates": total_dates,
            "last_updated": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        
    except ValueError as ve:
        return {
            "database_name": "telegram_data", 
            "status": "data_error",
            "error": f"Data validation failed: {str(ve)}",
            "channels": {},
            "total_channels": 0,
            "total_dates": 0
        }
    except Exception as e:
        return {
            "database_name": "telegram_data", 
            "status": "connection_error",
            "error": f"Connection failed: {str(e)}",
            "channels": {},
            "total_channels": 0,
            "total_dates": 0
        }
```

### Шаг 2: Добавить вызов в render_database_stats()

```python
def render_database_stats():
    """Render database statistics in hierarchical format"""
    
    # Получаем данные всех БД
    databases = [
        get_twitter_db_stats(),
        get_telegram_db_stats(),  # <- ДОБАВИТЬ ЭТУ СТРОКУ
        # get_discord_db_stats(),  # <- ДОБАВИТЬ БУДУЩИЕ БД
    ]
    
    # Отображаем каждую БД
    for db_stats in databases:
        render_single_database(db_stats)
        st.markdown("---")
```

### Шаг 3: Создать универсальную функцию отображения

```python
def render_single_database(db_stats: Dict):
    """Render single database statistics"""
    
    # Определяем цвет статуса
    if db_stats['status'] == 'connected':
        status_color = "🟢"
        status_text = "Connected"
    elif db_stats['status'] == 'data_error':
        status_color = "🟡"
        status_text = "Data Error"
    else:
        status_color = "🔴"
        status_text = "Connection Error"
    
    # Заголовок БД
    st.subheader(f"{status_color} Database: {db_stats['database_name']}")
    
    # Время обновления
    if 'last_updated' in db_stats:
        st.caption(f"Last updated: {db_stats['last_updated']}")
    
    # Обработка ошибок
    if db_stats['status'] != 'connected':
        if db_stats['status'] == 'data_error':
            st.warning(f"[WARNING] {db_stats.get('error', 'Data validation failed')}")
        else:
            st.error(f"[ERROR] {db_stats.get('error', 'Connection failed')}")
        
        st.info("[INFO] Showing empty state due to connection issues")
        st.markdown("### 📢 Channels Overview")
        st.info("[INFO] No data available - check database connection")
        return
    
    # Метрики
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(label="📊 Total Channels", value=db_stats['total_channels'])
    with col2:
        st.metric(label="📅 Total Dates", value=db_stats['total_dates'])
    with col3:
        st.metric(label="⚡ Status", value=status_text)
    with col4:
        # Определяем тип БД по имени
        db_type = db_stats['database_name'].replace('_data', '').title()
        st.metric(label="🔗 Type", value=db_type)
    
    # Каналы
    if db_stats['channels']:
        st.markdown("### 📢 Channels Overview")
        
        for channel_name, channel_data in db_stats['channels'].items():
            with st.expander(f"📱 **{channel_name}** ({channel_data['total_entries']} entries)", expanded=False):
                
                info_col1, info_col2 = st.columns(2)
                
                with info_col1:
                    st.markdown("**📈 Statistics:**")
                    st.markdown(f"- Total entries: **{channel_data['total_entries']}**")
                    st.markdown(f"- Date range: **{len(channel_data['dates'])} days**")
                
                with info_col2:
                    st.markdown("**📅 Available dates:**")
                    
                    dates = sorted(channel_data['dates'])
                    if len(dates) <= 5:
                        for date in dates:
                            st.markdown(f"- {date}")
                    else:
                        for date in dates[:3]:
                            st.markdown(f"- {date}")
                        st.markdown("- ...")
                        for date in dates[-2:]:
                            st.markdown(f"- {date}")
    else:
        st.info("[INFO] No channels found in database")
```

## Типичные SQL запросы для разных БД

### Telegram
```sql
SELECT 
    channel_name as channel,
    DATE(message_date) as date,
    COUNT(*) as entries
FROM telegram_messages 
GROUP BY channel_name, DATE(message_date)
ORDER BY channel_name, date
```

### Discord
```sql
SELECT 
    server_name as channel,
    DATE(message_timestamp) as date,
    COUNT(*) as entries
FROM discord_messages 
GROUP BY server_name, DATE(message_timestamp)
ORDER BY server_name, date
```

### Reddit
```sql
SELECT 
    subreddit as channel,
    DATE(post_date) as date,
    COUNT(*) as entries
FROM reddit_posts 
GROUP BY subreddit, DATE(post_date)
ORDER BY subreddit, date
```

### YouTube
```sql
SELECT 
    channel_id as channel,
    DATE(video_date) as date,
    COUNT(*) as entries
FROM youtube_videos 
GROUP BY channel_id, DATE(video_date)
ORDER BY channel_id, date
```

## MCP серверы

### Текущие подключения
- `postgres-telegram` - БД `twitter_data`

### Ожидаемые будущие подключения
- `postgres-telegram-messages` - БД `telegram_data`
- `postgres-discord` - БД `discord_data`
- `postgres-reddit` - БД `reddit_data`
- `postgres-youtube` - БД `youtube_data`

## Чек-лист для добавления новой БД

- [ ] 1. Создать функцию `get_[database]_db_stats()`
- [ ] 2. Добавить вызов в `render_database_stats()`
- [ ] 3. Протестировать с заглушкой данных
- [ ] 4. Подключить реальный MCP сервер
- [ ] 5. Заменить заглушку на реальный SQL запрос
- [ ] 6. Протестировать с реальными данными
- [ ] 7. Добавить обработку специфичных ошибок БД

## Важные замечания

### Кэширование
- Все функции `get_*_db_stats()` должны иметь `@st.cache_data(ttl=300)`
- Кнопка "🔄 Refresh" очищает весь кэш

### Обработка ошибок
- Всегда возвращать структуру с полями `database_name`, `status`, `channels`, `total_channels`, `total_dates`
- Использовать `connection_error` для проблем с БД
- Использовать `data_error` для проблем с валидацией

### Валидация данных
- Проверять `isinstance(channels_data, dict)`
- Проверять наличие ключа `"dates"` в каждом канале
- Проверять что `total_entries` - число

### Расширяемость
- Код готов к добавлению неограниченного количества БД
- Каждая БД отображается отдельно с собственными метриками
- Универсальная функция `render_single_database()` работает для всех типов БД

## Текущий статус файла

Файл `pages/3_⚙️_Processing.py` содержит:
- ✅ Полную реализацию для Twitter БД
- ✅ Кэширование и обработку ошибок  
- ✅ Кнопку обновления данных
- ✅ Готовую архитектуру для добавления новых БД
- ✅ Минималистичный дизайн без лишних элементов

**Следующий шаг:** Подключить новую БД и добавить соответствующую функцию по этому гайду.