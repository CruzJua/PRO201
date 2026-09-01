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

The application should use the shared database instance and can verify the connection during startup or a health check:

```python
from database import get_database

db = get_database()
db.check_connection()  # Raises if configuration or database access is unavailable.
```

`get_database()` creates the Supabase client once per process. It does not make a network request until `check_connection()` or a repository operation is called.

For trusted server-side code, you can use `$env:SUPABASE_SECRET_KEY` instead. Never expose that key to the frontend or commit it to Git. The DAL prefers the secret key when both keys are configured.

## Example

```python
from database import Database

db = Database()

db.users.create(user_id=1, name="Alex")
db.images.create(image_id=1, url="https://example.com/scan.png")
db.predictions.create(
    pred_id=1,
    user_id="3f8b1c2d-4e5f-6a7b-8c9d-0e1f2a3b4c5d",  # Supabase auth UUID
    image_id=1,
    description="Potential tumor detected",
)

predictions = db.predictions.list_with_user_and_image()
```

`Prediction.user_id` is a `text` column holding the **Supabase auth UUID** (the
JWT `sub` claim), not a `Users.user_id`. There is no foreign key from
`Prediction` to `Users`, so a user *name* cannot be embedded in a query.

`list_with_user_and_image()` returns every prediction, shaped like:

```python
{
    "pred_id": 1,
    "user_id": "3f8b1c2d-4e5f-6a7b-8c9d-0e1f2a3b4c5d",
    "url": "https://example.com/scan.png",
    "description": "Potential tumor detected",
}
```

`list_by_user(user_id)` returns just one user's predictions, newest first, in
the shape the `/history` page consumes:

```python
{
    "pred_id": 1,
    "label": "glioma",
    "image_url": "https://example.com/scan.png",
}
```