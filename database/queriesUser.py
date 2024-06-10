import psycopg2
from psycopg2 import sql
from model.user import User

def get_user_db(id, database):
    print(f'Requested user with id {id}')
    connection = psycopg2.connect(database)
    with connection.cursor() as cur:
        # cur.execute(f'''
        #             SELECT name, email, email_verified, 
        #                     profile_picture_url, provider, 
        #                     COUNT(DISTINCT M.id) AS matches_played, 
        #                     SUM(CASE WHEN M.winner_id = U.id THEN 1 ELSE 0 END) AS matches_won,
        #                     country, 
        #                     TO_CHAR(signup_date:: DATE, 'dd Mon yyyy') AS signup_date
        #             FROM 
        #                 user_info AS U
        #             LEFT JOIN
        #                 matches_info AS M ON U.id IN ( M.user_one_id, M.user_two_id, M.user_three_id) 
        #             WHERE 
        #                 U.id = '{id}'
        #             GROUP BY U.id;
        #             ''')
        cur.execute(f'''
                    SELECT id, name, email, emailverified, 
                            provider, matchesplayed, matcheswon, signupdate
                    FROM 
                        user_info AS U
                    WHERE 
                        U.id = '{id}'
                    GROUP BY U.id;
                    ''')
        ret = cur.fetchone()
        if ret:
            return User(*ret)
        else:
            return None


def insert_user_db(user_info, database):
    print(f'Inserting {user_info}')
    connection = psycopg2.connect(database)

    with connection.cursor() as cur:
        fields = list(user_info.keys())
        values = list(user_info.values())
        print(fields, values)
        try:
            cur.execute(""" 
                INSERT INTO user_info ({}) VALUES ({}) RETURNING id; """.format(', '.join(fields), ', '.join(['%s'] * len(fields))), values)
            connection.commit()
            # Fetch the ID of the newly inserted user
            inserted_id = cur.fetchone()[0]
            cur.close()
            
            return {'msg': "User inserted into the database", 'id': inserted_id}, 200
        except (Exception, psycopg2.Error) as err:
            return {'msg': "Error while interacting with PostgreSQL...\n", 'err': str(err)}, 400


def update_user_db(id, user_info, database):
    print(f'Updating user with id {id} to {user_info}')
    connection = psycopg2.connect(database)

    with connection.cursor() as cur:
        fields = list(user_info.keys())
        values = list(user_info.values())
        print(fields, values)
        try:
            cur.execute("""
                UPDATE user_info SET {} WHERE id = %s;""".format(', '.join(['{}=%s'.format(field) for field in fields])), values + [id])
            connection.commit()
            if cur.rowcount > 0:
                return {'msg': f"User with id {id} updated successfully"}, 200
            else:
                return {'error': f"User with id {id} does not exist"}, 404
        except (Exception, psycopg2.Error) as err:
            return {'msg': "Error while updating user in PostgreSQL...\n", 'err': str(err)}, 400


def delete_user_db(id, database):
    print(f'Deleting user with id {id}')
    connection = psycopg2.connect(database)
    with connection.cursor() as cur:
        try:
            cur.execute("DELETE FROM user_info WHERE id = %s;", (id,))
            connection.commit()
            return {'msg': f"User deleted successfully"}, 200
        except (Exception, psycopg2.Error) as err:
            return {'msg': "Error while deleting user in PostgreSQL...\n", 'err': str(err)}, 400

