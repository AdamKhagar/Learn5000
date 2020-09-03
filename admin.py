import json

class Admin:
    @staticmethod
    def isAdmin(user_id):
        with open('users_data/admins.json') as f:
            admin_id = json.load(f)['id']
        
        return admin_id == user_id

    @staticmethod
    def get_id():
        with open('users_data/admins.json') as f:
            return json.load(f)['id']     
            
    @staticmethod
    def get_state():
        with open('users_data/admins.json') as f:
            return json.load(f)['state']

    @staticmethod
    def set_state(state='await'):
        with open('users_data/admins.json') as f:
            admin_data = json.load(f)
        admin_data['state'] = state
        with open('users_data/admins.json', 'w', encoding='utf-8') as f:
            json.dump(admin_data, f, ensure_ascii=False, indent=4)