import sqlalchemy as alch
from sqlalchemy.orm import declarative_base, relationship, sessionmaker


Base = declarative_base()


# class Publisher(Base):
#     __tablename__ = "publisher"
#
#     id = alch.Column(alch.Integer, primary_key=True)
#     name = alch.Column(alch.String(length=80), unique=True)
#
#     book = relationship("Book", back_populates="publisher")
#
#     def __str__(self):
#         return f'id={self.id}\nname={self.name}'
#
#
# class Book(Base):
#     __tablename__ = "book"
#
#     id = alch.Column(alch.Integer, primary_key=True)
#     title = alch.Column(alch.String(length=255), unique=True)
#     id_publisher = alch.Column(alch.Integer, alch.ForeignKey("publisher.id"), nullable=False)
#
#     publisher = relationship("Publisher", back_populates="book")
#     stock = relationship("Stock", back_populates="book")
#
#     def __str__(self):
#         return f'id={self.id}\ntitle={self.title}\nid_publisher={self.id_publisher}'



class Requester(Base):
    __tablename__ = "requester"

    id = alch.Column(alch.Integer, primary_key=True)
    user_id = alch.Column(alch.Integer, nullable=False, unique=True)
    f_name = alch.Column(alch.String(length=60))
    l_name = alch.Column(alch.String(length=80))


class Users(Base):
    __tablename__ = "users"

    id = alch.Column(alch.Integer, primary_key=True)
    user_id = alch.Column(alch.Integer, alch.ForeignKey("requester.id"), nullable=False, unique=True)
    f_name = alch.Column(alch.String(length=60))
    l_name = alch.Column(alch.String(length=80))
    city = alch.Column(alch.String(length=80))

    requester = relationship("Requester", back_populates="users")

class Photos(Base):
    __tablename__ = "photos"

    photo_id = alch.Column(alch.Integer, alch.ForeignKey("users.id"), nullable=False, unique=True)
    likes = alch.Column(alch.Integer, nullable=False)
    comments = alch.Column(alch.Integer, nullable=False)
    link = alch.Column(alch.Text, unique=True)

    users = relationship("Users", back_populates="photos")

class Black_List(Base):
    __tablename__ = "black_list"

    id = alch.Column(alch.Integer, primary_key=True)
    user_id = alch.Column(alch.Integer, nullable=False, unique=True)



############################### Строка подключения и создание движка алхимии

# load_dotenv()
# data_source_name = f"postgresql://{os.getenv('USER')}:" \
#                    f"{os.getenv('PASSWORD')}@" \
#                    f"{os.getenv('HOST')}:" \
#                    f"{os.getenv('PORT')}/" \
#                    f"{os.getenv('DB')}"
engine = alch.create_engine(data_source_name)
# create_tables(engine)

############################################# сессия

Session = sessionmaker(bind=engine)
my_session = Session()

