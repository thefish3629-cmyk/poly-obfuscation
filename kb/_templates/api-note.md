# API Name

Brief description of what this API does.

## Base URL

```
https://api.example.com/v1
```

## Authentication

- Header: `X-API-Key: YOUR_KEY`
- Or: `Authorization: Bearer YOUR_TOKEN`

## Endpoints

### GET /resource

Description.

**Parameters:**
| Name | Type | Required | Description |
|------|------|----------|-------------|
| param1 | string | Yes | Description |

**Response:**
```json
{
  "field": "value"
}
```

### POST /resource

Description.

## Errors

| Code | Meaning |
|------|---------|
| 400 | Bad Request |
| 401 | Unauthorized |
| 429 | Rate Limited |

## Rate Limits

- Requests per minute: X
- Burst: Y

## Example Usage

```python
import requests

response = requests.get(
    "https://api.example.com/v1/resource",
    headers={"X-API-Key": API_KEY}
)
data = response.json()
```

## See Also

- [Related API]()
- [Documentation]()