from datetime import datetime
from firebase_admin import firestore

class User:
    def __init__(self, email=None, password=None, name=None, role='user', created_at=None, id=None, uid=None, username=None):
        self.email = email
        self.password = password  # Şifre hash'lenmiş olarak saklanmalı
        self.name = name
        self.role = role
        self.created_at = created_at if created_at else datetime.now()
        self.id = id
        self.uid = uid
        self.username = username

    @property
    def is_authenticated(self):
        return True

    @property
    def is_active(self):
        return True

    @property
    def is_anonymous(self):
        return False

    def get_id(self):
        return str(self.uid)

    @staticmethod
    def from_dict(source):
        user = User()
        user.email = source.get('email')
        user.password = source.get('password')
        user.name = source.get('name')
        user.role = source.get('role', 'user')
        user.uid = source.get('uid')
        user.username = source.get('username')
        created_at = source.get('created_at')
        if isinstance(created_at, str):
            user.created_at = datetime.fromisoformat(created_at)
        else:
            user.created_at = created_at
        user.id = source.get('id')
        return user

    def to_dict(self):
        return {
            'email': self.email,
            'password': self.password,
            'name': self.name,
            'role': self.role,
            'created_at': self.created_at.isoformat() if isinstance(self.created_at, datetime) else self.created_at,
            'id': self.id,
            'uid': self.uid,
            'username': self.username
        }

    @staticmethod
    def get_by_email(email):
        db = firestore.client()
        users_ref = db.collection('users')
        query = users_ref.where('email', '==', email).limit(1).get()
        for doc in query:
            user_data = doc.to_dict()
            user_data['id'] = doc.id
            return User.from_dict(user_data)
        return None

    @staticmethod
    def create(user_data):
        db = firestore.client()
        users_ref = db.collection('users')
        doc_ref = users_ref.add(user_data)
        return doc_ref[1].id  # Oluşturulan belgenin ID'sini döndür

    @staticmethod
    def get_all():
        db = firestore.client()
        users = []
        for doc in db.collection('users').get():
            user_data = doc.to_dict()
            user_data['id'] = doc.id
            users.append(User.from_dict(user_data))
        return users

    @staticmethod
    def update(user_id, user_data):
        db = firestore.client()
        user_ref = db.collection('users').document(user_id)
        user_ref.update(user_data)

    @staticmethod
    def delete(user_id):
        db = firestore.client()
        user_ref = db.collection('users').document(user_id)
        user_ref.delete() 