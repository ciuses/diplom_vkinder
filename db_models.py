import sqlalchemy as alch
from sqlalchemy.orm import declarative_base, relationship, sessionmaker
from token_other import data_source_name

Base = declarative_base()
engine = alch.create_engine(data_source_name)

class Requester(Base):
    __tablename__ = "requester"

    id = alch.Column(alch.Integer, primary_key=True)
    requester_id = alch.Column(alch.BIGINT, nullable=False)
    f_name = alch.Column(alch.String(length=60))
    l_name = alch.Column(alch.String(length=80))

    users = relationship("Users", back_populates="requester")

class Users(Base):
    __tablename__ = "users"

    id = alch.Column(alch.Integer, primary_key=True)
    user_id = alch.Column(alch.BIGINT)
    requ_id = alch.Column(alch.Integer, alch.ForeignKey("requester.id"), nullable=False)
    f_name = alch.Column(alch.String(length=60))
    l_name = alch.Column(alch.String(length=80))
    city = alch.Column(alch.String(length=80))

    requester = relationship("Requester", back_populates="users")
    photos = relationship("Photos", back_populates="users")

class Photos(Base):
    __tablename__ = "photos"

    id = alch.Column(alch.Integer, primary_key=True)
    photo_id = alch.Column(alch.BIGINT)
    use_id = alch.Column(alch.Integer, alch.ForeignKey("users.id"), nullable=False)
    likes = alch.Column(alch.Integer, nullable=True)
    comments = alch.Column(alch.Integer, nullable=True)
    link = alch.Column(alch.Text)

    users = relationship("Users", back_populates="photos")

class Black_List(Base):
    __tablename__ = "black_list"

    id = alch.Column(alch.Integer, primary_key=True)
    user_id = alch.Column(alch.BIGINT, nullable=False)

def create_tables(engine):
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)

create_tables(engine)
Session = sessionmaker(bind=engine)
my_session = Session()
