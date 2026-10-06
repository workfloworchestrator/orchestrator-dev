# Postgres init files

All `.sql` files in this directory are mounted into the postgres container and executed on startup.


### Update snapshot

To create or udpate a snapshot, perform the following steps.
The `pg_dump` utility is required.

1. Destroy your local docker compose volume (or temporarily use a new docker compose project name)
2. Set the database snapshot to empty:
```sh
echo "CREATE DATABASE <name>;" > 01-<name>.sql
```
3. Start docker compose as normal and wait for relevant migrations to complete
4. Generate a new database snapshot:
```sh
pg_dump -d postgresql://nwa:nwa@127.0.0.1:5432/<name> --create -f 01-<namne>.sql
```
