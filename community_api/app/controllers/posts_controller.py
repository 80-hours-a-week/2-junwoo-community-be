from app.storage import memory_store as db
from app.utils.responses import ok, err

def list_posts(offset: int, limit: int):
    items = db.list_posts(offset, limit)
    return ok("POSTS_RETRIEVED", {"items": items})

def get_post(post_id: int):
    p = db.get_post(post_id, increase_hits=True)
    if not p:
        err(404, "NOT_FOUND")
    return ok("POST_RETRIEVED", p)

def create_post(u, payload: dict):
    title = payload.get("title")
    content = payload.get("content")
    file_url = payload.get("fileUrl")

    if not title:
        err(400, "TITLE_REQUIRED")
    if len(title) > 26:
        err(400, "TITLE_TOO_LONG")
    if not content:
        err(400, "CONTENT_REQUIRED")

    p = db.create_post(title=title, content=content, author_user_id=u["userId"], file_url=file_url)
    return ok("POST_CREATED", {"postId": p["postId"]})

def update_post(u, post_id: int, payload: dict):
    title = payload.get("title")
    content = payload.get("content")
    file_url = payload.get("fileUrl")

    p = db.get_post(post_id, increase_hits=False)
    if not p:
        err(404, "NOT_FOUND")
    if p["authorUserId"] != u["userId"]:
        err(403, "FORBIDDEN")

    if not title:
        err(400, "TITLE_REQUIRED")
    if len(title) > 26:
        err(400, "TITLE_TOO_LONG")
    if not content:
        err(400, "CONTENT_REQUIRED")

    db.update_post(post_id, title, content, file_url)
    return ok("POST_UPDATED", None)

def delete_post(u, post_id: int):
    p = db.get_post(post_id, increase_hits=False)
    if not p:
        err(404, "NOT_FOUND")
    if p["authorUserId"] != u["userId"]:
        err(403, "FORBIDDEN")

    db.delete_post(post_id)
    return ok("POST_DELETED", None)

def like_post(u, post_id: int):
    if not db.get_post(post_id, increase_hits=False):
        err(404, "NOT_FOUND")
    cnt = db.like_post(post_id, u["userId"])
    return ok("POST_LIKED", {"likeCount": cnt})

def unlike_post(u, post_id: int):
    if not db.get_post(post_id, increase_hits=False):
        err(404, "NOT_FOUND")
    cnt = db.unlike_post(post_id, u["userId"])
    return ok("POST_UNLIKED", {"likeCount": cnt})

def list_comments(post_id: int):
    if not db.get_post(post_id, increase_hits=False):
        err(404, "NOT_FOUND")
    items = db.list_comments(post_id)
    return ok("COMMENTS_RETRIEVED", {"items": items})

def create_comment(u, post_id: int, payload: dict):
    content = payload.get("content")
    if not content:
        err(400, "COMMENT_REQUIRED")
    if not db.get_post(post_id, increase_hits=False):
        err(404, "NOT_FOUND")
    c = db.create_comment(post_id, content, u["userId"])
    return ok("COMMENT_CREATED", {"commentId": c["commentId"]})

def update_comment(u, post_id: int, comment_id: int, payload: dict):
    content = payload.get("content")
    if not content:
        err(400, "COMMENT_REQUIRED")
    c = db.get_comment(comment_id)
    if not c or c["postId"] != post_id:
        err(404, "NOT_FOUND")
    if c["authorUserId"] != u["userId"]:
        err(403, "FORBIDDEN")
    db.update_comment(comment_id, content)
    return ok("COMMENT_UPDATED", None)

def delete_comment(u, post_id: int, comment_id: int):
    c = db.get_comment(comment_id)
    if not c or c["postId"] != post_id:
        err(404, "NOT_FOUND")
    if c["authorUserId"] != u["userId"]:
        err(403, "FORBIDDEN")
    db.delete_comment(comment_id)
    return ok("COMMENT_DELETED", None)
