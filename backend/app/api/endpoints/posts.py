from fastapi import FastAPI, Response, status, HTTPException, Depends, APIRouter
from sqlalchemy.orm import Session
from typing import Optional, List
from sqlalchemy import func

from ...core.database import get_db
from ...core.security import get_current_user
from ...models.domain import Post, Vote
from ...schemas import PostOut, PostCreate, Post as PostSchema

router = APIRouter(prefix="/posts", tags=['Posts'])

@router.get("/", response_model=List[PostOut])
def get_posts(
    db: Session = Depends(get_db),
    current_user: int = Depends(get_current_user),
    limit: int = 10,
    skip: int = 0,
    search: Optional[str] = ""
):
    posts = db.query(Post, func.count(Vote.post_id).label("votes")).join(
        Vote, Vote.post_id == Post.id, isouter=True).group_by(Post.id)\
        .filter(Post.title.contains(search)).limit(limit).offset(skip).all()
    return posts

@router.post("/", status_code=status.HTTP_201_CREATED, response_model=PostSchema)
def create_posts(
    post: PostCreate,
    db: Session = Depends(get_db),
    current_user: int = Depends(get_current_user)
):
    new_post = Post(owner_id=current_user.id, **post.dict())
    db.add(new_post)
    db.commit()
    db.refresh(new_post)
    return new_post

@router.get("/{id}", response_model=PostOut)
def get_post(
    id: int,
    db: Session = Depends(get_db),
    current_user: int = Depends(get_current_user)
):
    post = db.query(Post, func.count(Vote.post_id).label("votes")).join(
        Vote, Vote.post_id == Post.id, isouter=True).group_by(Post.id)\
        .filter(Post.id == id).first()
    
    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"post with id: {id} was not found"
        )
    return post

@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_post(
    id: int,
    db: Session = Depends(get_db),
    current_user: int = Depends(get_current_user)
):
    post_query = db.query(Post).filter(Post.id == id)
    post = post_query.first()
    
    if post is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"post with id: {id} does not exist"
        )
    
    if post.owner_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to perform requested action"
        )
    
    post_query.delete(synchronize_session=False)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)

@router.put("/{id}", response_model=PostSchema)
def update_post(
    id: int,
    updated_post: PostCreate,
    db: Session = Depends(get_db),
    current_user: int = Depends(get_current_user)
):
    post_query = db.query(Post).filter(Post.id == id)
    post = post_query.first()
    
    if post is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"post with id: {id} does not exist"
        )
    
    if post.owner_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to perform requested action"
        )
        
    post_query.update(updated_post.dict(), synchronize_session=False)
    db.commit()
    return post_query.first()
