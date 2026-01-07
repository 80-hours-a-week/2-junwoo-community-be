from typing import List, Dict

# 임시 데이터 저장소 (DB 대체)
posts: List[Dict] = []
post_id_counter = 1


def get_posts():
    return posts


def create_post(title: str, content: str):
    global post_id_counter

    post = {
        "id": post_id_counter,
        "title": title,
        "content": content
    }
    posts.append(post)
    post_id_counter += 1
    return post


def get_post(post_id: int):
    for post in posts:
        if post["id"] == post_id:
            return post
    return None


def delete_post(post_id: int):
    global posts
    posts = [post for post in posts if post["id"] != post_id]
    return {"message": "게시글 삭제 완료"}
