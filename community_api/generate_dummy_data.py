import os
import sys
import random
from datetime import datetime, timedelta
from faker import Faker
from sqlalchemy.orm import Session
from app.database import SessionLocal, engine, Base
from app.models.orm import User, Post, Comment

# Initialize Faker
fake = Faker('ko_KR')

def init_db():
    Base.metadata.create_all(bind=engine)

def create_dummy_users(db: Session, num_users=50):
    print(f"Creating {num_users} dummy users...")
    
    # Check existing user count to avoid primary key collisions if we were just incrementing
    # But for email/nickname uniqueness, we'll just use a large random range or sequential if empty.
    # To be safe and simple for "adding" 100k users, we can use a timestamp prefix or just rely on fake.unique
    
    users_buffer = []
    batch_size = 5000
    start_time = datetime.now()

    # Get current max id or count to help with uniqueness if needed, 
    # but UUIDs or simple random + check is often used. 
    # Here we will use a deterministic approach for bulk generation to ensure valid uniqueness.
    # generating strictly unique emails/nicknames for 100k entries with Faker alone isn't always guaranteed fast without collisions.
    # We will append a counter.
    
    existing_count = db.query(User).count()
    start_index = existing_count + 1

    for i in range(num_users):
        idx = start_index + i
        user = User(
            email=f"user{idx}_{fake.word()}@example.com",
            password_hash="dummy_hash", 
            nickname=f"user_{idx}_{fake.word()}",
            created_at=fake.date_time_between(start_date='-1y', end_date='now')
        )
        users_buffer.append(user)

        if len(users_buffer) >= batch_size:
            try:
                db.bulk_save_objects(users_buffer)
                db.commit()
                users_buffer = []
                elapsed = datetime.now() - start_time
                print(f"Inserted {i+1}/{num_users} users. (Elapsed: {elapsed})")
            except Exception as e:
                db.rollback()
                print(f"Error creating users batch: {e}")
                return

    if users_buffer:
        try:
            db.bulk_save_objects(users_buffer)
            db.commit()
            print(f"Inserted remaining {len(users_buffer)} users.")
        except Exception as e:
            db.rollback()
            print(f"Error creating remaining users: {e}")

def get_user_ids(db: Session):
    return [user.id for user in db.query(User.id).all()]

def get_post_ids(db: Session):
    # This might be heavy if millions, but acceptable for 100k
    return [post.id for post in db.query(Post.id).all()]

def create_dummy_posts(db: Session, total_posts=100000, batch_size=5000):
    user_ids = get_user_ids(db)
    if not user_ids:
        print("No users found. Creating users first.")
        create_dummy_users(db, num_users=100) # minimal set
        user_ids = get_user_ids(db)

    print(f"Starting generation of {total_posts} posts...")
    
    posts_buffer = []
    start_time = datetime.now()
    
    for i in range(total_posts):
        post = Post(
            title=fake.sentence(nb_words=6),
            content=fake.paragraph(nb_sentences=3),
            author_user_id=random.choice(user_ids),
            hits=random.randint(0, 100),
            created_at=fake.date_time_between(start_date='-1y', end_date='now'),
            updated_at=datetime.utcnow()
        )
        posts_buffer.append(post)
        
        if len(posts_buffer) >= batch_size:
            try:
                db.bulk_save_objects(posts_buffer)
                db.commit()
                posts_buffer = []
                elapsed = datetime.now() - start_time
                print(f"Inserted {i+1}/{total_posts} posts. (Elapsed: {elapsed})")
            except Exception as e:
                db.rollback()
                print(f"Error inserting post batch: {e}")
                return

    if posts_buffer:
         try:
            db.bulk_save_objects(posts_buffer)
            db.commit()
            print(f"Inserted remaining {len(posts_buffer)} posts.")
         except Exception as e:
            db.rollback()
            print(f"Error inserting remaining post batch: {e}")

    print("Post generation done!")

def create_dummy_comments(db: Session, total_comments=100000, batch_size=5000):
    user_ids = get_user_ids(db)
    post_ids = get_post_ids(db)

    if not user_ids or not post_ids:
        print("Users or Posts missing. Cannot create comments.")
        return

    print(f"Starting generation of {total_comments} comments...")
    
    comments_buffer = []
    start_time = datetime.now()

    for i in range(total_comments):
        comment = Comment(
            post_id=random.choice(post_ids),
            author_user_id=random.choice(user_ids),
            content=fake.sentence(),
            created_at=fake.date_time_between(start_date='-1y', end_date='now')
        )
        comments_buffer.append(comment)

        if len(comments_buffer) >= batch_size:
            try:
                db.bulk_save_objects(comments_buffer)
                db.commit()
                comments_buffer = []
                elapsed = datetime.now() - start_time
                print(f"Inserted {i+1}/{total_comments} comments. (Elapsed: {elapsed})")
            except Exception as e:
                db.rollback()
                print(f"Error inserting comment batch: {e}")
                return
    
    if comments_buffer:
        try:
            db.bulk_save_objects(comments_buffer)
            db.commit()
            print(f"Inserted remaining {len(comments_buffer)} comments.")
        except Exception as e:
            db.rollback()
            print(f"Error inserting remaining comment batch: {e}")
            
    print("Comment generation done!")

if __name__ == "__main__":
    db = SessionLocal()
    try:
        print("--- Dummy Data Generator ---")
        # 1. Users (100k)
        if db.query(User).count() < 100000:
             create_dummy_users(db, num_users=100000)
        else:
             print("Users sufficient. Skipping user generation.")

        # 2. Posts (100k)
        create_dummy_posts(db, total_posts=100000, batch_size=5000)

        # 3. Comments (100k)
        create_dummy_comments(db, total_comments=100000, batch_size=5000)
        
    finally:
        db.close()

