from app.storage import memory_store as db
from app.utils.responses import ok, err

def list_posts(offset: int, limit: int):
    items = list(db._posts.values())  # noqa: 내부 접근(과제용)
    items.sort(key=lambda p: p.postId, reverse=True)

    if limit and limit > 0:
        items = items[offset:offset+limit]
    else:
        items = items[offset:]

    out = []
    for p in items:
        out.append({
            "postId": p.postId,
            "title": p.title[:26],
            "authorUserId": p.authorUserId,
            "fileUrl": p.fileUrl,
            "hits": p.hits,
            "likeCount": len(p.likes),
            "commentCount": sum(1 for c in db._comments.values() if c.postId == p.postId),  # noqa
            "createdAt": p.createdAt,
            "updatedAt": p.updatedAt,
        })
    return ok("POSTS_RETRIEVED", {"items": out})

def get_post(post_id: int):
    p = db._posts.get(post_id)  # noqa
    if not p:
        err(404, "NOT_FOUND")
    p.hits += 1
    p.updatedAt = db.now_iso()

    return ok("POST_RETRIEVED", {
        "postId": p.postId,
        "title": p.title,
        "content": p.content,
        "authorUserId": p.authorUserId,
        "fileUrl": p.fileUrl,
        "hits": p.hits,
        "likeCount": len(p.likes),
        "commentCount": sum(1 for c in db._comments.values() if c.postId == p.postId),  # noqa
        "createdAt": p.createdAt,
        "updatedAt": p.updatedAt,
    })

def create_post(u, title: str, content: str, file_url: str | None):
    if not title:
        err(400, "TITLE_REQUIRED")
    if len(title) > 26:
        err(400, "TITLE_TOO_LONG")
    if not content:
        err(400, "CONTENT_REQUIRED")
    p = db.create_post(title, content, u.userId, file_url)
    return ok("POST_CREATED", {"postId": p.postId})

def update_post(u, post_id: int, title: str | None, content: str | None, file_url: str | None):
    p = db._posts.get(post_id)  # noqa
    if not p:
        err(404, "NOT_FOUND")
    if p.authorUserId != u.userId:
        err(403, "FORBIDDEN")

    if title is not None:
        if not title:
            err(400, "TITLE_REQUIRED")
        if len(title) > 26:
            err(400, "TITLE_TOO_LONG")
        p.title = title
    if content is not None:
        if not content:
            err(400, "CONTENT_REQUIRED")
        p.content = content

    p.fileUrl = file_url
    p.updatedAt = db.now_iso()
    return ok("POST_UPDATED", None)

def delete_post(u, post_id: int):
    p = db._posts.get(post_id)  # noqa
    if not p:
        err(404, "NOT_FOUND")
    if p.authorUserId != u.userId:
        err(403, "FORBIDDEN")

    db._posts.pop(post_id, None)  # noqa
    # 연관 댓글 삭제(과제용)
    for cid in list(db._comments.keys()):  # noqa
        if db._comments[cid].postId == post_id:  # noqa
            db._comments.pop(cid, None)  # noqa
    return ok("POST_DELETED", None)

def like_post(u, post_id: int):
    p = db._posts.get(post_id)  # noqa
    if not p:
        err(404, "NOT_FOUND")
    p.likes.add(u.userId)
    return ok("POST_LIKED", {"likeCount": len(p.likes)})

def unlike_post(u, post_id: int):
    p = db._posts.get(post_id)  # noqa
    if not p:
        err(404, "NOT_FOUND")
    p.likes.discard(u.userId)
    return ok("POST_UNLIKED", {"likeCount": len(p.likes)})

def list_comments(post_id: int):
    p = db._posts.get(post_id)  # noqa
    if not p:
        err(404, "NOT_FOUND")
    items = [c for c in db._comments.values() if c.postId == post_id]  # noqa
    items.sort(key=lambda c: c.commentId)

    out = []
    for c in items:
        out.append({
            "commentId": c.commentId,
            "postId": c.postId,
            "content": c.content,
            "authorUserId": c.authorUserId,
            "createdAt": c.createdAt,
            "updatedAt": c.updatedAt,
        })
    return ok("COMMENTS_RETRIEVED", {"items": out})

def create_comment(u, post_id: int, content: str):
    if not content:
        err(400, "COMMENT_REQUIRED")
    p = db._posts.get(post_id)  # noqa
    if not p:
        err(404, "NOT_FOUND")
    c = db.create_comment(post_id, content, u.userId)
    return ok("COMMENT_CREATED", {"commentId": c.commentId})

def update_comment(u, post_id: int, comment_id: int, content: str):
    if not content:
        err(400, "COMMENT_REQUIRED")
    c = db._comments.get(comment_id)  # noqa
    if not c or c.postId != post_id:
        err(404, "NOT_FOUND")
    if c.authorUserId != u.userId:
        err(403, "FORBIDDEN")

    c.content = content
    c.updatedAt = db.now_iso()
    return ok("COMMENT_UPDATED", None)

def delete_comment(u, post_id: int, comment_id: int):
    c = db._comments.get(comment_id)  # noqa
    if not c or c.postId != post_id:
        err(404, "NOT_FOUND")
    if c.authorUserId != u.userId:
        err(403, "FORBIDDEN")
    db._comments.pop(comment_id, None)  # noqa
    return ok("COMMENT_DELETED", None)

def save_file(raw: bytes, mime: str):
    file_id = db.new_id()
    db.files[file_id] = raw
    db.file_mimes[file_id] = mime
    url = f"/public/files/{file_id}"
    db.file_urls[file_id] = url
    return ok("FILE_UPLOADED", {"fileId": file_id, "fileUrl": url})

