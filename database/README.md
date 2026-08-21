# Database DAL

This package provides Supabase CRUD repositories for `Users`, `Images`, and `Prediction`.

## Setup

Install the dependency from the repository root:

```powershell
pip install -r database/requirements.txt
```

Set these environment variables before using the DAL:

```powershell
$env:SUPABASE_URL = "https://your-project.supabase.co"
$env:SUPABASE_PUBLISHABLE_KEY = "your-publishable-key"
```

For trusted server-side code, you can use `$env:SUPABASE_SECRET_KEY` instead. Never expose that key to the frontend or commit it to Git. The DAL prefers the secret key when both keys are configured.

## Example

```python
from database import Database

db = Database()

db.users.create(user_id=1, name="Alex")
db.images.create(image_id=1, url="https://example.com/scan.png")
db.predictions.create(
    pred_id=1,
    user_id=1,
    image_id=1,
    description="Potential tumor detected",
)

predictions = db.predictions.list_with_user_and_image()
```

`list_with_user_and_image()` returns rows shaped like:

```python
{
    "pred_id": 1,
    "name": "Alex",
    "url": "https://example.com/scan.png",
    "description": "Potential tumor detected",
}
```