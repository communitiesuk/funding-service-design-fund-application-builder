## Database
### Schema
The database schema is defined in [app/db/models.py](./app/db/models.py) and is managed by Alembic. The migrations are stored in [app/db/migrations/versions](./app/db/migrations/versions/)

### Entity Relationship Diagram
See [Here](./app/db/database_ERD_9-8-24.png)

### Recreate Local DBs
For both `DATABASE_URL` and `DATABASE_URL_UNIT_TEST`, drops the database if it exists and then recreates it.

### Init migrations
Deletes the [versions](./app/db/migrations/versions/) directory and runs `migrate()` to generate a new intial migration version for the SQLAlchemy models.

### Create Test Data
Inserts a set of seed data comprising one Fund, 2 rounds and the applicaiton/assessment config for one of those rounds. The data created is defined in [test_data.py](./tasks/test_data.py)