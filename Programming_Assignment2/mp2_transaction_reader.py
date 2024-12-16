import configparser
import psycopg2
from config import read_config

def read_config(filename='database.cfg', section='postgresql'):
    parser = configparser.ConfigParser()
    parser.read(filename)

    db_params = {}
    if parser.has_section(section):
        params = parser.items(section)
        for param in params:
            db_params[param[0]] = param[1]
    else:
        raise Exception(f'Section {section} not found in the {filename} file')

    return db_params



def read_plans(isolation_level, config_filename):
    db_params = read_config(filename=config_filename)
    with psycopg2.connect(**db_params) as conn:
        conn.set_isolation_level(isolation_level)
        with conn.cursor() as cursor:
            cursor.execute("SELECT * FROM plans")
            plans_before = cursor.fetchall()
            print(f"Plans before commit (Isolation Level: {isolation_level}):")
            for plan in plans_before:
                print(plan)
            
            input("Hit enter to continue...\n") 

            cursor.execute("SELECT * FROM plans")
            plans_after = cursor.fetchall()
            print(f"Plans after commit (Isolation Level: {isolation_level}):")
            for plan in plans_after:
                print(plan)

            input("Hit enter to continue...") 

if __name__ == "__main__":
    config_filename = 'database.cfg'
    isolation_levels = [
        psycopg2.extensions.ISOLATION_LEVEL_READ_COMMITTED,
        psycopg2.extensions.ISOLATION_LEVEL_REPEATABLE_READ,
        psycopg2.extensions.ISOLATION_LEVEL_SERIALIZABLE
    ]
    for level in isolation_levels:
        print(f"\nTesting Isolation Level: {level}")
        read_plans(level, config_filename)
