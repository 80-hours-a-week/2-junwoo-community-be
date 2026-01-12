from app.utils.responses import ok, err
from app.storage import memory_store as db

def _author_payload(user_id: int):
    u = db.get_user(user_id)
    if not u:
        return {"userId": user_id, "nickname": "unknown", "profileImageUrl": None}
    return {"userId": u.userId, "nickname": u.nickname, "profileImageUrl": u.profileImageUrl}

def list_posts(offset: int, limit: int):
    # 엑셀: /v1/posts?offset=0&limit=0 (무한스크롤)
    items = list(db._posts.values())
    # 최신순
    items.sort(key=lambda p: p.createdAt, reverse=True)

    sliced = items[offset: offset + limit] if limit > 0 else items[offset:]
    data = []
    for p in sliced:
        comment_count = sum(1 for c in db._comments.values() if c.postId == p.postId)
        data.append({
            "postId": p.postId,
            "title": p.title,  # FE에서 26자 자르지만, BE는 전체 전달
            "likeCount": len(p.likes),
            "commentCount": comment_count,
            "hits": p.hits,
            "author": _author_payload(p.authorUserId),
            "createdAt": p.createdAt,
        })
    return ok("POSTS_RETRIEVED", data)

def get_post(post_id: int):
    p = db._posts.get(post_id)
    if not p:
        err(404, "POST_NOT_FOUND")

    # 조회수 증가
    p.hits += 1
    db._posts[post_id] = p

    comment_count = sum(1 for c in db._comments.values() if c.postId == p.postId)

    file_obj = None
    if p.fileId or p.fileUrl:
        file_obj = {
            "fileId": p.fileId or 1,
            "fileUrl": p.fileUrl
        }

    return ok("POST_RETRIEVED", {
        "postId": p.postId,
        "title": p.title,
        "content": p.content,
        "likeCount": len(p.likes),
        "commentCount": comment_count,
        "hits": p.hits,
        "author": _author_payload(p.authorUserId),
        "file": file_obj,
        "createdAt": p.createdAt,
    })

def create_post(token_user, title: str, content: str, fileUrl: str | None):
    if not title or len(title) > 26:
        err(400, "INVALID_POST_TITLE")
    if not content:
        err(400, "INVALID_POST_CONTENT")

    p = db.create_post(title, content, token_user.userId, fileUrl)
    return ok("POST_CREATED", {"post_id": p.postId})

def update_post(token_user, post_id: int, title: str, content: str, fileUrl: str | None):
    p = db._posts.get(post_id)
    if not p:
        err(404, "POST_NOT_FOUND")
    if p.authorUserId != token_user.userId:
        err(403, "FORBIDDEN")

    if not title or len(title) > 26:
        err(400, "INVALID_POST_TITLE")
    if not content:
        err(400, "INVALID_POST_CONTENT")

    p.title = title
    p.content = content
    p.fileUrl = fileUrl
    p.updatedAt = db.now_iso()
    db._posts[post_id] = p
    return ok("POST_UPDATED", None)

def delete_post(token_user, post_id: int):
    p = db._posts.get(post_id)
    if not p:
        err(404, "POST_NOT_FOUND")
    if p.authorUserId != token_user.userId:
        err(403, "FORBIDDEN")

    # 댓글도 삭제
    cids = [cid for cid, c in db._comments.items() if c.postId == post_id]
    for cid in cids:
        del db._comments[cid]

    del db._posts[post_id]
    return ok("POST_DELETED", None)

def upload_post_image(postFile_bytes: bytes, mime: str):
    if not postFile_bytes:
        err(400, "INVALID_FILE")

    fid = db.new_id()
    db.files[fid] = postFile_bytes
    db.file_mimes[fid] = mime or "application/octet-stream"
    url = f"/public/image/post/{fid}"
    db.file_urls[fid] = url

    return ok("POST_FILE_UPLOADED", {"postFileId": fid, "postFileUrl": url})

def like_post(token_user, post_id: int):
    p = db._posts.get(post_id)
    if not p:
        err(404, "POST_NOT_FOUND")

    p.likes.add(token_user.userId)
    db._posts[post_id] = p
    return ok("POST_LIKE_CREATED", {"likeCount": len(p.likes)})

def unlike_post(token_user, post_id: int):
    p = db._posts.get(post_id)
    if not p:
        err(404, "POST_NOT_FOUND")

    p.likes.discard(token_user.userId)
    db._posts[post_id] = p
    return ok("POST_LIKE_DELETED", {"likeCount": len(p.likes)})

def list_comments(post_id: int):
    if post_id not in db._posts:
        err(404, "POST_NOT_FOUND")

    items = [c for c in db._comments.values() if c.postId == post_id]
    items.sort(key=lambda c: c.createdAt)

    data = []
    for c in items:
        data.append({
            "commentId": c.commentId,
            "content": c.content,
            "postId": c.postId,
            "author": _author_payload(c.authorUserId),
            "createdAt": c.createdAt,
        })
    return ok("COMMENTS_RETRIEVED", data)

def create_comment(token_user, post_id: int, content: str):
    if post_id not in db._posts:
        err(404, "POST_NOT_FOUND")
    if not content:
        err(400, "INVALID_COMMENT_CONTENT")

    c = db.create_comment(post_id, content, token_user.userId)
    return ok("COMMENT_CREATED", {"commentId": c.commentId})

def update_comment(token_user, post_id: int, comment_id: int, content: str):
    c = db._comments.get(comment_id)
    if not c or c.postId != post_id:
        err(404, "COMMENT_NOT_FOUND")
    if c.authorUserId != token_user.userId:
        err(403, "FORBIDDEN")
    if not content:
        err(400, "INVALID_COMMENT_CONTENT")

    c.content = content
    c.updatedAt = db.now_iso()
    db._comments[comment_id] = c
    return ok("COMMENT_UPDATED", None)

def delete_comment(token_user, post_id: int, comment_id: int):
    c = db._comments.get(comment_id)
    if not c or c.postId != post_id:
        err(404, "COMMENT_NOT_FOUND")
    if c.authorUserId != token_user.userId:
        err(403, "FORBIDDEN")

    del db._comments[comment_id]
    return ok("COMMENT_DELETED", None)
