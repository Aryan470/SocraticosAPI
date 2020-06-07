import uuid

class User(object):
    def __init__(self, name:str, email:str, desc:str, userID:str, enrollments:list):
        self.name = name
        self.email = email
        self.desc = desc
        self.userID = userID
        self.enrollments = enrollments
    
    @staticmethod
    def from_dict(source:dict) -> User:
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

class Group(object):
    def __init__(self, name:str, desc:str, groupID:str, mentors:list, students:list, chatHistory:list, pinnedHistory:list):
        self.name = name
        self.desc = desc
        self.groupID = groupID
        self.mentors = mentors
        self.students = students
        self.chatHistory = chatHistory
        self.pinnedHistory = pinnedHistory
    
    @staticmethod
    def from_dict(source:dict) -> Group:
        return User(source["name"], source["desc"], source["groupID"], source["mentors"], source["students"], source["chatHistory"], source["pinnedHistory"])
    
    def to_dict(self) -> dict:
        response = {
            "name": self.name,
            "desc": self.desc,
            "groupID": self.groupID,
            "mentors": self.mentors,
            "students": self.students,
            "chatHistory": self.chatHistory,
            "pinnedHistory": self.pinnedHistory
        }
        return response

class Message(object):
    def __init__(self, messageID:str, content:str, authorID:str, timestamp:str):
        self.messageID = messageID
        self.content = content
        self.authorID = authorID
        self.timestamp = timestamp
    
    @staticmethod
    def from_dict(source) -> User:
        return User(source["messageID"], source["content"], source["authorID"], source["timestamp"])
    
    def to_dict(self) -> dict:
        response = {
            "messageID": self.messageID,
            "content": self.content,
            "authorID": self.authorID,
            "timestamp": self.timestamp
        }
        return response