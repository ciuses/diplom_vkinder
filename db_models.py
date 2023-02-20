import sqlalchemy as alch
from sqlalchemy.orm import declarative_base, relationship, sessionmaker

data_source_name = f"postgresql://postgres:hanson@192.168.56.101:5432/vkinder"
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

# if __name__ == '__main__':
    # create_tables(engine)
    # Session = sessionmaker(bind=engine)
    # my_session = Session()
    #
    # block_id = Black_List(user_id=47474274257547)
    # block_id2 = Black_List(user_id=47474274247)
    #
    #
    # # requ = Requester(requester_id=3773, f_name='Абр', l_name='Валг')
    # # usr = Users(requ_id=3773, user_id=55555, f_name='Буря', l_name='Буу', city='Зажопинск')
    # # usr2 = Users(requ_id=3773, user_id=77777, f_name='Куя', l_name='Зуу', city='Поджопинск')
    # # phot = Photos(use_id=55555, photo_id=1111111111, likes=7, comments=3, link='http://shtshth.rgrgra/')
    # # phot2 = Photos(use_id=55555, photo_id=2222222222, likes=343, comments=7, link='http://eeeee.cccccc/')
    # # phot3 = Photos(use_id=77777, photo_id=3333333333, likes=2, comments=0, link='http://яяяя.hhh/')
    # #
    # my_session.add(block_id)
    # my_session.add(block_id2)
    # # # my_session.add(requ)
    # # # my_session.add(usr)
    # # # my_session.add(phot)
    # # my_session.add_all([block_id, requ, usr, usr2, phot, phot2, phot3])
    # #
    # print(my_session.commit())

    # requpa = Requester(requester_id=1111111111, f_name='Абр', l_name='Валг')
    # my_session.add(requpa)
    # my_session.commit()
    #
    # user1 = Users(requ_id=requpa.id, user_id=222222222222, f_name='Петя', l_name='Пижон', city='Зажопинск')
    # my_session.add(user1)
    # my_session.commit()
    #
    # photka = Photos(use_id=user1.id, photo_id=10, likes=3, comments=2, link='http://shtshth.rgrgra/')
    # photka2 = Photos(use_id=user1.id, photo_id=11, likes=10, comments=4, link='http://sragragar.rgrgra/')
    # my_session.add_all([photka, photka2])
    # my_session.commit()
    #