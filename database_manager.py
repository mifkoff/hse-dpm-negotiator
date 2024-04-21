from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
from datetime import datetime

# Database connection and collections setup
class DatabaseManager:
    def __init__(self, db_url, db_name):
        self.client = MongoClient(db_url, server_api=ServerApi('1'))
        try:
            self.client.admin.command('ping')
            print("Pinged deployment. Successfully connected to MongoDB!")
        except Exception as e:
            print(e)
        self.db = self.client[db_name]
        self.users = self.db['users']
        self.cases = self.db['cases']
        self.messages = self.db['messages']

    # User-related operations
    def add_user(self, user_id, name, cases_id=[]):
        user = {
            "id": user_id,
            "name": name,
            "cases_id": cases_id,
            "is_admin": False,
            "_created_at": datetime.now(),
            "_updated_at": datetime.now()
        }
        return self.users.insert_one(user).inserted_id

    def get_user(self, user_id):
        return self.users.find_one({"id": user_id})

    def update_user(self, user_id, update_data):
        update_data['_updated_at'] = datetime.now()
        return self.users.update_one({"id": user_id}, {"$set": update_data})

    def list_users(self):
        return list(self.users.find({}))

    def update_user_cases(self, user_id, case_id):
        # Fetch and update the user document with new case ID
        self.users.update_one({"id": user_id}, {"$push": {"cases_id": case_id}})
    
    # Case-related operations
    def add_case(self, title, user_id, case_type, counterparty_name, budget, starting_price, target_price, incoming_offer, messages_id=[]):
        case = {
            "title": title,
            "user_id": user_id,
            "messages_id": messages_id,
            "case_type": case_type,
            "counterparty_name": counterparty_name,
            "budget": budget,
            "starting_price": starting_price,
            "target_price": target_price,
            "incoming_offer": incoming_offer,
            "_created_at": datetime.now(),
            "_updated_at": datetime.now()
        }
        case_id = self.cases.insert_one(case).inserted_id
        self.update_user_cases(user_id, case_id)
        return case_id

    def get_case(self, case_id):
        return self.cases.find_one({"_id": case_id})
    
    def get_user_cases(self, user_id):
        user = self.get_user(user_id)
        if not user:
            return []  # No user found
        case_ids = user.get('cases_id', [])
        return list(self.cases.find({"id": {"$in": case_ids}}))

    def update_case(self, case_id, update_data):
        update_data['_updated_at'] = datetime.now()
        return self.cases.update_one({"id": case_id}, {"$set": update_data})

    def list_cases(self):
        return list(self.cases.find({}))

    # Message-related operations
    def add_message(self, case_id, role, content):
        message = {
            "case_id": case_id,
            "role": role,
            "content": content,
            "_created_at": datetime.now(),
            "_updated_at": datetime.now()
        }
        inserted_id = self.messages.insert_one(message).inserted_id

        # Update the corresponding case to include this message ID in messages_id list
        self.cases.update_one(
            {"_id": case_id},
            {"$push": {"messages_id": inserted_id}}
        )

        return inserted_id

    def get_user_cases(self, user_id):
        """
        Retrieves all cases for a given user ID.

        Parameters:
            user_id (str): The user ID to query cases for.

        Returns:
            list: A list of case dictionaries that belong to the user.
        """
        return list(self.cases.find({"user_id": user_id}))
    
    def get_case_by_user_and_title(self, user_id, title):
        """
        Retrieves a specific case for a given user ID and title.

        Parameters:
            user_id (str): The user ID to query cases for.
            title (str): The title of the case to find.

        Returns:
            dict or None: The found case document or None if no case matches.
        """
        return self.cases.find_one({"user_id": user_id, "title": title})
    
    def get_messages_by_case_id(self, case_id):
        return list(self.messages.find({"case_id": case_id}))

# Example usage
if __name__ == "__main__":
    print("[Loaded] database_manager")