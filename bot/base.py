import asyncpg


class Database:
    def __init__(self, dsn):
        self.dsn = dsn
        self.pool = None

    async def create_pool(self):
        self.pool = await asyncpg.create_pool(self.dsn)
        if self.pool:
            print("Successfully created pool!")
        else:
            print("Failed to create pool.")
            
async def create_user_table(self):
        async with self.pool.acquire() as conn:
            await conn.execute(
              'CREATE TABLE IF NOT EXISTS users('
              'id SERIAL PRIMARY KEY, '
              'user_id INTEGER UNIQUE, '
              'name VARCHAR(30), '
              'last_name VARCHAR(30),'
              'tel_number VARCHAR(40),'
              'date_created TIMESTAMP DEFAULT CURRENT_TIMESTAMP, '
              'agreed BOOLEAN DEFAULT FALSE,'
              'Blocked BOOLEAN DEFAULT FALSE)'
            )

async def create_sub_user_table(self):
        async with self.pool.acquire() as conn:
            await conn.execute(
                  'CREATE TABLE IF NOT EXISTS users_sub('
                  'id SERIAL PRIMARY KEY, '
                  'user_id INTEGER UNIQUE ,'
                  'Психолог BOOLEAN DEFAULT FALSE,'
                  'Стилист BOOLEAN DEFAULT FALSE,'
                  'Юрист BOOLEAN DEFAULT FALSE,'
                  'Нутрициолог BOOLEAN DEFAULT FALSE,'
                  'Косметолог  BOOLEAN DEFAULT FALSE,'
                  'Врач BOOLEAN DEFAULT FALSE,'
                  'Тренер BOOLEAN DEFAULT FALSE,'
                  'Дизайнер BOOLEAN DEFAULT FALSE,'
                  'Финансист BOOLEAN DEFAULT FALSE,'
                  'Маркетолог BOOLEAN DEFAULT FALSE,'
                  'Астролог BOOLEAN DEFAULT FALSE)'
            )

async def get_user_id(self, chat_id):
        async with self.pool.acquire() as conn:
            user_id = await conn.fetchval(f"SELECT id FROM users WHERE user_id = '{chat_id}'")
            return user_id

async def set_user_id(self, user_id):
        async with self.pool.acquire() as conn:
            await conn.execute(f"INSERT INTO users (user_id, agreed) VALUES ('{user_id}', TRUE)")

async def set_user_info(self, i_user_id, i_name, i_last_name, i_tel):
        async with self.pool.acquire() as conn:
            await conn.execute(
              f"UPDATE users SET "
              f"name = '{i_name}', "
              f"last_name = '{i_last_name}', "
              f"tel_number = '{i_tel}' "
              f"where user_id = '{i_user_id}' ")

async def set_categories(self, categories, id_user):
        async with self.pool.acquire() as conn:
            categories = list(categories)
            values = [id_user] + [True] * len(categories)
            placeholders = ','.join([f'${i+1}' for i in range(len(values))])
            columns = ','.join([f'{category}=TRUE' for category in categories])
            query = f"""
                  INSERT INTO users_sub(user_id, {','.join(categories)})
                  VALUES ({placeholders})
                  ON CONFLICT (user_id)
                  DO UPDATE SET {columns}
              """
            await conn.execute(query, *values)

async def get_users_list_to_distribute_by_category(self, category):
        async with self.pool.acquire() as conn:
            rows = await conn.fetch(f"SELECT user_id FROM users_sub "
                                    f"WHERE {category} = TRUE;"
                                    )
            return [row[0] for row in rows]

async def get_users_list_to_distribute_for_all(self):
        async with self.pool.acquire() as conn:
            rows = await conn.fetch(f"SELECT user_id FROM users_sub ")
            return [row[0] for row in rows]

async def user_info_response(self, user):
        async with self.pool.acquire() as conn:
            elems = await conn.fetchrow(f"SELECT name, last_name, tel_number, Blocked FROM users WHERE user_id = '{user}' ")
            return elems

async def update_name(self, i_user_id, i_name):
        async with self.pool.acquire() as conn:
            await conn.execute(
              f"UPDATE users SET "
              f"name = '{i_name}' "
              f"where user_id = '{i_user_id}' ")

async def update_surname(self, i_user_id, i_surname):
        async with self.pool.acquire() as conn:
            await conn.execute(
              f"UPDATE users SET "
              f"last_name = '{i_surname}' "
              f"where user_id = '{i_user_id}' ")

async def update_tel_number(self, i_user_id, number):
        async with self.pool.acquire() as conn:
            await conn.execute(
              f"UPDATE users SET "
              f"tel_number = '{number}' "
              f"where user_id = '{i_user_id}' ")

async def update_sub_false(self, i_user_id):
        async with self.pool.acquire() as conn:
            await conn.execute(
              f"UPDATE users_sub SET "
              f"Астролог = false,"
              f"Психолог = false,"
              f"Стилист = false,"
              f"Юрист = false,"
              f"Нутрициолог = false,"
              f"Косметолог = false,"
              f"Врач = false,"
              f"Тренер = false,"
              f"Дизайнер = false,"
              f"Маркетолог = false,"
              f'Финансист = false'
              f" where user_id = '{i_user_id}' ;")

async def update_sub_true(self, i_user_id):
        async with self.pool.acquire() as conn:
            update_query = \
              f"Астролог = TRUE,"\
              f"Психолог = TRUE,"\
              f"Стилист = TRUE,"\
              f"Юрист = TRUE,"\
              f"Нутрициолог = TRUE,"\
              f"Косметолог = TRUE,"\
              f"Врач = TRUE,"\
              f"Тренер = TRUE,"\
              f"Дизайнер = TRUE,"\
              f"Маркетолог = TRUE,"\
              f"Финансист = TRUE "

            insert_query = f"user_id, Астролог, Психолог, Стилист, Юрист, Нутрициолог, "\
                           f"Косметолог, Врач, Тренер, Дизайнер, Маркетолог, Финансист"

            val = f"'{i_user_id}', TRUE, TRUE, TRUE, TRUE, TRUE, TRUE, TRUE,TRUE, TRUE, TRUE, TRUE"

            query = f"INSERT INTO users_sub ({insert_query}) VALUES ({val})" \
                    f" ON CONFLICT (user_id) DO UPDATE SET {update_query}"
            await conn.execute(query)

async def block_user(self, i_user_id):
        async with self.pool.acquire() as conn:
            await conn.execute(
              f"UPDATE users SET "
              f"Blocked = TRUE "
              f"where user_id = '{i_user_id}' ")
            row = await conn.fetchrow(
              f"SELECT COUNT(*) FROM users WHERE user_id = '{i_user_id}'"
            )
            return row[0] > 0

async def unblock_user(self, i_user_id):
        async with self.pool.acquire() as conn:
            await conn.execute(
              f"UPDATE users SET "
              f"Blocked = FALSE "
              f"where user_id = '{i_user_id}' ")
            row = await conn.fetchrow(
              f"SELECT COUNT(*) FROM users WHERE user_id = '{i_user_id}'"
            )
            return row[0] > 0

async def get_status(self, i_user_id):
        async with self.pool.acquire() as conn:
            elem = await conn.fetchrow(f"SELECT Blocked FROM users WHERE user_id = '{i_user_id}' ")
            if elem is not None:
                return elem[0]
            else:
                return elem

async def delete(self, i_user_id):
        async with self.pool.acquire() as conn:
            await conn.execute(f"DELETE FROM users_sub WHERE user_id ='{i_user_id}' ")

async def cout_all(self):
        async with self.pool.acquire() as conn:
            elem = await conn.fetchrow(f"SELECT COUNT(*) FROM users_sub")
            return elem[0]

async def cout_category(self, category):
        async with self.pool.acquire() as conn:
            elem = await conn.fetchrow(f"SELECT COUNT(*) FROM users_sub WHERE {category} = true;")
            return elem[0]
