from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from sqlalchemy import func, desc, asc
from datetime import datetime, timedelta
from typing import List, Optional
from database import engine, get_db, Base
from models import User, Poll, Option, Vote
from schemas import (
    UserCreate, UserResponse, Token, PollCreate, PollResponse,
    VoteCreate, VoteResponse, OptionResponse
)
from auth import (
    create_access_token, get_password_hash, authenticate_user,
    get_current_user, ACCESS_TOKEN_EXPIRE_MINUTES
)

Base.metadata.create_all(bind=engine)

app = FastAPI(title="在线投票系统")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.post("/register", response_model=UserResponse)
def register(user: UserCreate, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.username == user.username).first()
    if db_user:
        raise HTTPException(status_code=400, detail="用户名已存在")
    db_email = db.query(User).filter(User.email == user.email).first()
    if db_email:
        raise HTTPException(status_code=400, detail="邮箱已被注册")
    hashed_password = get_password_hash(user.password)
    db_user = User(
        username=user.username,
        email=user.email,
        hashed_password=hashed_password
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


@app.post("/token", response_model=Token)
def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户名或密码错误",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}


@app.get("/users/me", response_model=UserResponse)
def read_users_me(current_user: User = Depends(get_current_user)):
    return current_user


@app.post("/polls", response_model=PollResponse)
def create_poll(
    poll: PollCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    db_poll = Poll(
        title=poll.title,
        description=poll.description,
        deadline=poll.deadline,
        creator_id=current_user.id
    )
    db.add(db_poll)
    db.flush()
    for option in poll.options:
        db_option = Option(text=option.text, poll_id=db_poll.id)
        db.add(db_option)
    db.commit()
    db.refresh(db_poll)
    return db_poll


def get_poll_with_stats(db: Session, poll_id: int, user_id: Optional[int] = None):
    poll = db.query(Poll).filter(Poll.id == poll_id).first()
    if not poll:
        return None
    
    total_votes = db.query(func.count(Vote.id)).filter(Vote.poll_id == poll_id).scalar() or 0
    
    options = []
    user_vote = None
    if user_id:
        user_vote = db.query(Vote).filter(
            Vote.poll_id == poll_id,
            Vote.user_id == user_id
        ).first()
    
    for option in poll.options:
        vote_count = db.query(func.count(Vote.id)).filter(
            Vote.option_id == option.id
        ).scalar() or 0
        
        percentage = 0.0
        if total_votes > 0:
            percentage = round((vote_count / total_votes) * 100, 1)
        
        option_response = OptionResponse(
            id=option.id,
            text=option.text,
            vote_count=vote_count,
            percentage=percentage
        )
        options.append(option_response)
    
    now = datetime.utcnow()
    is_expired = now > poll.deadline
    
    poll_response = PollResponse(
        id=poll.id,
        title=poll.title,
        description=poll.description,
        deadline=poll.deadline,
        created_at=poll.created_at,
        creator_id=poll.creator_id,
        options=options,
        total_votes=total_votes,
        is_expired=is_expired,
        has_voted=user_vote is not None,
        voted_option_id=user_vote.option_id if user_vote else None
    )
    
    return poll_response


@app.get("/polls", response_model=List[PollResponse])
def get_polls(
    sort_by: str = "created_at",
    order: str = "desc",
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user)
):
    if sort_by == "votes":
        polls = db.query(Poll).outerjoin(Vote).group_by(Poll.id)
        if order == "desc":
            polls = polls.order_by(desc(func.count(Vote.id)))
        else:
            polls = polls.order_by(asc(func.count(Vote.id)))
    else:
        if order == "desc":
            polls = db.query(Poll).order_by(desc(Poll.created_at))
        else:
            polls = db.query(Poll).order_by(asc(Poll.created_at))
    
    polls = polls.all()
    
    result = []
    for poll in polls:
        poll_response = get_poll_with_stats(db, poll.id, current_user.id if current_user else None)
        if poll_response:
            result.append(poll_response)
    
    return result


@app.get("/polls/{poll_id}", response_model=PollResponse)
def get_poll(
    poll_id: int,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user)
):
    poll_response = get_poll_with_stats(db, poll_id, current_user.id if current_user else None)
    if not poll_response:
        raise HTTPException(status_code=404, detail="投票不存在")
    return poll_response


@app.post("/polls/{poll_id}/vote", response_model=VoteResponse)
def vote(
    poll_id: int,
    vote_data: VoteCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    poll = db.query(Poll).filter(Poll.id == poll_id).first()
    if not poll:
        raise HTTPException(status_code=404, detail="投票不存在")
    
    now = datetime.utcnow()
    if now > poll.deadline:
        raise HTTPException(status_code=400, detail="投票已截止")
    
    existing_vote = db.query(Vote).filter(
        Vote.poll_id == poll_id,
        Vote.user_id == current_user.id
    ).first()
    if existing_vote:
        raise HTTPException(status_code=400, detail="您已经投过票了")
    
    option = db.query(Option).filter(
        Option.id == vote_data.option_id,
        Option.poll_id == poll_id
    ).first()
    if not option:
        raise HTTPException(status_code=404, detail="选项不存在")
    
    db_vote = Vote(
        user_id=current_user.id,
        poll_id=poll_id,
        option_id=vote_data.option_id
    )
    db.add(db_vote)
    db.commit()
    db.refresh(db_vote)
    return db_vote


@app.delete("/polls/{poll_id}")
def delete_poll(
    poll_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    poll = db.query(Poll).filter(Poll.id == poll_id).first()
    if not poll:
        raise HTTPException(status_code=404, detail="投票不存在")
    if poll.creator_id != current_user.id:
        raise HTTPException(status_code=403, detail="无权删除此投票")
    db.delete(poll)
    db.commit()
    return {"message": "删除成功"}
