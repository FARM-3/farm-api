import django
django.setup()
from django.db import connection

sqls = [
    "ALTER TABLE taskmanagement_task ADD COLUMN IF NOT EXISTS assigned_to jsonb DEFAULT '[]'::jsonb;",
    "UPDATE taskmanagement_task SET assigned_to = to_jsonb(ARRAY[assigned_to_id]) WHERE assigned_to_id IS NOT NULL;",
]
cur = connection.cursor()
# find FK constraints referencing assigned_to_id
cur.execute("SELECT pc.conname FROM pg_constraint pc JOIN pg_class cl ON pc.conrelid = cl.oid JOIN unnest(pc.conkey) WITH ORDINALITY AS cols(attnum, idx) ON true JOIN pg_attribute a ON a.attrelid = cl.oid AND a.attnum = cols.attnum WHERE cl.relname = 'taskmanagement_task' AND a.attname = 'assigned_to_id' AND pc.contype = 'f'")
rows = cur.fetchall()
for row in rows:
    name = row[0]
    print('Dropping constraint', name)
    cur.execute(f"ALTER TABLE taskmanagement_task DROP CONSTRAINT {name}")

for s in sqls:
    print('Executing:', s)
    cur.execute(s)

# finally drop the old column if exists
cur.execute("SELECT column_name FROM information_schema.columns WHERE table_name='taskmanagement_task' AND column_name='assigned_to_id'")
if cur.fetchone():
    print('Dropping column assigned_to_id')
    cur.execute("ALTER TABLE taskmanagement_task DROP COLUMN assigned_to_id")
else:
    print('assigned_to_id not present')

print('Done')
