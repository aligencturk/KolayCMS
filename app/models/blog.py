from datetime import datetime

class BlogPost:
    def __init__(self, title, content, author=None, created_at=None, updated_at=None):
        self.title = title
        self.content = content
        self.author = author
        self.created_at = created_at or datetime.now().isoformat()
        self.updated_at = updated_at or datetime.now().isoformat()
    
    def to_dict(self):
        return {
            'title': self.title,
            'content': self.content,
            'author': self.author,
            'created_at': self.created_at,
            'updated_at': self.updated_at
        }
    
    @staticmethod
    def from_dict(source):
        return BlogPost(
            title=source.get('title'),
            content=source.get('content'),
            author=source.get('author'),
            created_at=source.get('created_at'),
            updated_at=source.get('updated_at')
        ) 