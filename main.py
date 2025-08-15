from dataclasses import dataclass, asdict
from pymongo import MongoClient
from pymongo.server_api import ServerApi


@dataclass
class Cat:
    name: str
    age: int
    features: list[str]


class CatRepository:
    def __init__(self, db: MongoClient):
        self.db = db
        self.collection = db.cats

    def create(self, cat: Cat):
      res =  self.collection.insert_one(asdict(cat))
      print(res.inserted_id)

    def get_all(self):
        res =  self.collection.find()
        for cat in res:
            print(Cat(name=cat["name"], age=cat["age"], features=cat["features"]))

    def get_by_name(self, name: str):
        res = self.collection.find_one({"name": name})
        if res:
            print(Cat(name=res["name"], age=res["age"], features=res["features"]))
        else:
            print("Cat not found")

    def update_by_name(self, name: str, payload: dict):
        res = self.collection.update_one({"name": name}, {"$set": payload}, upsert=True)
        if res.modified_count > 0:
            print(res.raw_result)
        else:
            print("Cat not found")

    def add_feature(self, name: str, feature: str):
        res = self.collection.update_one({"name": name}, {"$push": {"features": feature}})

    def delete_by_name(self, name: str):
        res = self.collection.delete_one({"name": name})
        if res.deleted_count > 0:
            print(res.raw_result)
        else:
            print("Cat not found")

    def delete_all(self):
        res = self.collection.delete_many({})
        if res.deleted_count > 0:
            print(res.raw_result)
        else:
            print("No cats to delete")


if __name__ == "__main__":
    with MongoClient("mongodb://admin:secret@localhost:27017") as client:
        cat_repository = CatRepository(client.book)
        cat_repository.create(Cat(name="Mia", age=3, features=["ходить в капці", "дає себе гладити", "рудий"]))
        cat_repository.get_all()
        cat_repository.get_by_name("Mia")
        cat_repository.update_by_name("Mia", {"age": 12})
        cat_repository.update_by_name("barsik", {"features": ["ходить в капці", "дає себе гладити", "рудий", "гриматий"], "age": 10})
        cat_repository.add_feature("Mia", "гриматий")
        cat_repository.delete_by_name("Mia")
        cat_repository.delete_all()