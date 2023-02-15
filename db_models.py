import sqlalchemy as alch
from sqlalchemy.orm import declarative_base, relationship, sessionmaker

Base = declarative_base()
data_source_name = f"postgresql://postgres:hanson@192.168.56.101:5432/vkinder"
engine = alch.create_engine(data_source_name)


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

    requester_id = alch.Column(alch.BIGINT, primary_key=True, nullable=False, unique=True)
    f_name = alch.Column(alch.String(length=60))
    l_name = alch.Column(alch.String(length=80))

    users = relationship("Users", back_populates="requester")


class Users(Base):
    __tablename__ = "users"

    user_id = alch.Column(alch.BIGINT, primary_key=True)
    requ_id = alch.Column(alch.BIGINT, alch.ForeignKey("requester.requester_id"), nullable=False)
    f_name = alch.Column(alch.String(length=60))
    l_name = alch.Column(alch.String(length=80))
    city = alch.Column(alch.String(length=80))

    requester = relationship("Requester", back_populates="users")
    photos = relationship("Photos", back_populates="users")


class Photos(Base):
    __tablename__ = "photos"

    photo_id = alch.Column(alch.BIGINT, primary_key=True)
    use_id = alch.Column(alch.BIGINT, alch.ForeignKey("users.user_id"), nullable=False)
    likes = alch.Column(alch.Integer, nullable=True)
    comments = alch.Column(alch.Integer, nullable=True)
    link = alch.Column(alch.Text, unique=True)

    users = relationship("Users", back_populates="photos")


class Black_List(Base):
    __tablename__ = "black_list"

    id = alch.Column(alch.Integer, primary_key=True)
    user_id = alch.Column(alch.BIGINT, nullable=False, unique=True)


def create_tables(engine):
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)


if __name__ == '__main__':
    create_tables(engine)
    Session = sessionmaker(bind=engine)
    my_session = Session()

    block_id = Black_List(id=1, user_id=47474274257547)
    requ = Requester(requester_id=3773, f_name='Абр', l_name='Валг')
    usr = Users(requ_id=3773, user_id=55555, f_name='Буря', l_name='Буу', city='Зажопинск')
    usr2 = Users(requ_id=3773, user_id=77777, f_name='Куя', l_name='Зуу', city='Поджопинск')
    phot = Photos(use_id=55555, photo_id=1111111111, likes=7, comments=3, link='http://shtshth.rgrgra/')
    phot2 = Photos(use_id=55555, photo_id=2222222222, likes=343, comments=7, link='http://eeeee.cccccc/')
    phot3 = Photos(use_id=77777, photo_id=3333333333, likes=2, comments=0, link='http://яяяя.hhh/')

    # my_session.add(block_id)
    # my_session.add(requ)
    # my_session.add(usr)
    # my_session.add(phot)
    my_session.add_all([block_id, requ, usr, usr2, phot, phot2, phot3])

    my_session.commit()
