import uuid

class User(object):
    def __init__(self, name, email, desc="", userID=uuid.uuid4(), enrollments=[]):
        self.name = name
        self.email = email
        self.desc = desc
        self.userID = userID
        self.enrollments = enrollments
    
    @staticmethod
    def from_dict(source) -> User:
        return User(source["name"], source["email"], source["desc"], source["userID"], source["enrollments"])
    
    def to_dict(self) -> dict:
        response = {
            "name": self.name,
            "email": self.email,
            "desc": self.desc,
            "userID": self.userID,
            "enrollments": self.enrollments
        }
        return response