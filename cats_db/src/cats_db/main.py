from pymongo import MongoClient
from pymongo.server_api import ServerApi
from pymongo.errors import WriteError, BulkWriteError
from pprint import pprint

password = '9K3G4xwyH57qP8Nh'
client = MongoClient(
    f"mongodb+srv://vovchik357:{password}@cluster0.imbqfnj.mongodb.net/Cluster0?retryWrites=true&w=majority",
    server_api=ServerApi('1')
)
db = client.cats


cat_schema = {
    "bsonType": "object",
    "required": ["name", "age", "features"],
    "properties": {
        "name": {
            "bsonType": "string",
            "description": "Ім'я кота має бути рядком (string)"
        },
        "age": {
            "bsonType": "int",
            "minimum": 0,
            "description": "Вік має бути цілим числом (int) не менше 0"
        },
        "features": {
            "bsonType": "array",
            "items": { "bsonType": "string" },
            "description": "Особливості мають бути списком рядків"
        }
    }
}


def create_db():
    '''Creating database or add validator'''
    try:
        db.create_collection("cats", validator={"$jsonSchema": cat_schema})
    except Exception as e:
        db.command("collMod", "cats", validator={"$jsonSchema": cat_schema})
        print(e)
        print("Правила валідації оновлено для існуючої колекції")


create_db()

def create(data: dict[str, str | int | list[str]] | list[dict[str, str | int | list[str]]]) -> str | list[str]:
    '''Add new dict or dicts to database'''
    if isinstance(data, dict):
        try:
            result = db.cats.insert_one(data)
            return result.inserted_id
        except (WriteError, BulkWriteError) as e:
            print(e)
    elif isinstance(data, list):
        try:
            result = db.cats.insert_many(data)
            return result.inserted_ids
        except (WriteError, BulkWriteError) as e:
            print(e)


one_cat = {
        "name": "barsik",
        "age": 3,
        "features": ["ходить в капці", "дає себе гладити", "рудий"],
    }

# print(create(one_cat))

two_cats = [
        {
            "name": "Lama",
            "age": 2,
            "features": ["ходить в лоток", "не дає себе гладити", "сірий"],
        },
        {
            "name": "Liza",
            "age": 4,
            "features": ["ходить в лоток", "дає себе гладити", "білий"],
        },
    ]

# print(create(two_cats))


def read_all() -> list[dict[str, str | int | list[str]]]:
    '''Return all cats from database'''
    result = db.cats.find({})
    if result:
        return [el for el in result]

# pprint(read_all())

def read_one(name: str) -> dict[str, str | int | list[str]]:
    '''Return one cat by name'''
    result = db.cats.find_one({'name': name})
    return result

# pprint(read_one('barsik'))


def update_age_by_name(name: str, age: int) -> dict[str, str | int | list[str]]:
    '''Change age for cat by name'''
    try:
        db.cats.update_one({"name": name}, {"$set": {"age": age}})
    except (WriteError, BulkWriteError) as e:
        print(e)
    return read_one(name)

# pprint(update_age_by_name('barsik', 4))


def add_features_by_name(name: str, feature: str) -> dict[str, str | int | list[str]]:
    '''Append new feature to cat by name'''
    cat = read_one(name)
    if cat:
        cat['features'].append(feature)
        try:
            db.cats.update_one({"name": name}, {"$set": cat})
        except (WriteError, BulkWriteError) as e:
            print(e)
    return read_one(name)

# pprint(add_features_by_name('barsik', 'хропить'))


def delete_by_name(name: str):
    '''Remove cat by name'''
    db.cats.delete_one({"name": name})
    return read_one(name)

# print(delete_by_name('barsik'))


def delete_all():
    '''Remove all cats'''
    db.cats.delete_many({})
    return read_all()

# print(delete_all())
