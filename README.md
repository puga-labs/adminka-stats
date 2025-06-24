# Crypto Analytics Admin Panel

Streamlit-based admin panel for monitoring cryptocurrency analytics system.

## Quick Start with Poetry

### 1. Install Poetry (if not installed)
```bash
curl -sSL https://install.python-poetry.org | python3 -
```

### 2. Install dependencies
```bash
poetry install
```

### 3. Configure database
```bash
cp .env.example .env
# Edit .env with your database credentials
```

### 4. Run the application
```bash
poetry run streamlit run app.py
```

The app will be available at http://localhost:8501

## Alternative: Run with custom port
```bash
poetry run streamlit run app.py --server.port 8080
```

## Development

### Add new dependency
```bash
poetry add package-name
```

### Run with auto-reload
```bash
poetry run streamlit run app.py --server.runOnSave true
```

### Format code
```bash
poetry run black .
```