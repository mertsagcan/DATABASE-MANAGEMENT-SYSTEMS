import configparser
import random
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


def write_plan(isolation_level, config_filename):
    db_params = read_config(filename=config_filename)
    conn = psycopg2.connect(**db_params)
    try:
        conn.set_isolation_level(isolation_level)
        cursor = conn.cursor()
        try:
            # Generate random name and max_parallel_sessions
            plan_name = f"Plan_{random.randint(1000, 9999)}"
            max_parallel_sessions = random.randint(6, 20)
            plan_id = random.randint(1000, 9999)

            cursor.execute(
                "INSERT INTO plans (plan_id, name, max_parallel_sessions) VALUES (%s, %s, %s)",
                (plan_id, plan_name, max_parallel_sessions)
            )
            input("Hit enter to commit a new plan...")  # Wait for reader script to read initial plans
            conn.commit()
            print(f"Commited new plan: {plan_name} with max_parallel_sessions: {max_parallel_sessions}")
            input("Hit enter to continue...")  # Wait for reader script to read updated plans
        except Exception as e:
            print("An error occurred:", e)
        finally:
            cursor.close()
    except Exception as e:
        print("An error occurred:", e)
    finally:
        conn.close()


if __name__ == "__main__":
    config_filename = 'database.cfg'
    isolation_levels = [
        psycopg2.extensions.ISOLATION_LEVEL_READ_COMMITTED,
        psycopg2.extensions.ISOLATION_LEVEL_REPEATABLE_READ,
        psycopg2.extensions.ISOLATION_LEVEL_SERIALIZABLE
    ]
    for level in isolation_levels:
        print(f"\nTesting Isolation Level: {level}")
        write_plan(level, config_filename)
