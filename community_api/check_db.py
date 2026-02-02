from app.storage import db
from app.models.orm import File, Post

def check():
    session = db.get_db_session()
    try:
        file_count = session.query(File).count()
        post_count = session.query(Post).count()
        print(f"File count: {file_count}")
        print(f"Post count: {post_count}")
        
        if file_count > 0:
            f = session.query(File).first()
            print(f"First file ID: {f.id}")
            print(f"First file Size: {len(f.data)} bytes")
            print(f"First file Mime: {f.mime_type}")
    finally:
        session.close()

if __name__ == "__main__":
    check()
