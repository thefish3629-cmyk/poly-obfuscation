# Project Templates

Templates for documenting projects.

## New Project Template

```markdown
# Project Name

Brief description.

## Purpose

Why this project exists.

## Tech Stack

| Component | Technology |
|-----------|-----------|
| Language | Python |
| Database | PostgreSQL |
| APIs | X, Y |

## Setup

```bash
# Install
pip install -r requirements.txt

# Configure
cp .env.example .env

# Run
python main.py
```

## Features

- Feature 1
- Feature 2

## Status

- Status: Active/Paused/Complete
- Last updated: YYYY-MM-DD

## Links

- [GitHub]()
- [Live]()

## See Also

- [Related]()
```

## API Project Template

```markdown
# API Integration

## Endpoint

```
GET/POST https://api.example.com/v1/...
```

## Auth

- Header: `X-API-Key: ...`

## Usage

```python
import requests

response = requests.get(
    "https://api.example.com/v1/...",
    headers={"X-API-Key": API_KEY}
)
```

## Response

```json
{
  "data": []
}
```
```

## See Also

- [Current Project](current-project.md)