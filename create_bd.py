import psycopg2

conn = psycopg2.connect(database = 'people', user = 'postgres', password = 'green')
with conn.cursor() as cur:
    cur.execute('''
        CREATE TABLE IF NOT EXISTS human(
            profile_id INTEGER, 
            worksheet_id INTEGER, 
            PRIMARY KEY(profile_id, worksheet_id)
        );
        ''')
    conn.commit()

conn.close()