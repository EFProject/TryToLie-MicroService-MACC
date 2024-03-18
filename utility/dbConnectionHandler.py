import json


def connection_handler(request):
    try:
        with open('postgres_credentials.json', 'r') as f:
            postgres_credentials = json.load(f)
            database = f"dbname={postgres_credentials.get('dbname')} user={postgres_credentials.get('user')} host={postgres_credentials.get('host')} password={postgres_credentials.get('password')}"
            token = request.headers.get('Authorization')
            return database, token == postgres_credentials.get('token')
    except FileNotFoundError:
        print("File containing credentials not found.")
        return None
    except json.JSONDecodeError:
        print("Error decoding JSON in credentials")
        return None



