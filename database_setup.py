from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine


Base = declarative_base()


class User(Base):
    """ Registered user information is stored in db
    Attributes:
    id (int): id created for registered user
    name (str): name of registered user limit to 250 chars
    email (str): email of registered user limit to 250 chars
    picture (str): picture of registered user limit to 250 chars
    """
    __tablename__ = 'user'

    id = Column(Integer, primary_key=True)
    name = Column(String(250), nullable=False)
    email = Column(String(250), nullable=False)
    picture = Column(String(250))


class Category(Base):
    """
    Attributes:
    id (int): The id of category
    name (str): The name of the category
    user_id (int): linked with db user id, differentiate user authorization
    in input or edit category
    user: linked to User class
    """
    __tablename__ = 'category'

    id = Column(Integer, primary_key=True)
    name = Column(String(80), nullable=False)
    user_id = Column(Integer, ForeignKey('user.id'))
    user = relationship(User, backref="category")

    @property
    def serialize(self):
        """Return object data in easily serializeable format"""
        return {
            'name': self.name,
            'id': self.id,
        }


class CategoryItem(Base):
    """
    Attributes:
    id (int): The id of category item
    title (str): The name of the category item limit to 80 chars
    description (str): Describe what the category item is limit to 250 chars
    category_id: based and linked to db category id
    category: has relationship with db category
    user_id (int): linked with db user id, differentiate user authorization
    user: linked to User class
    """
    __tablename__ = 'category_item'

    id = Column(Integer, primary_key=True)
    title = Column(String(80), nullable=False)
    description = Column(String(250))
    category_id = Column(Integer, ForeignKey('category.id'))
    category = relationship(Category, cascade="delete")
    user_id = Column(Integer, ForeignKey('user.id'))
    user = relationship(User, backref="items")

    # Add serialize function to be able to send JSON objects in a
    # serializable format
    @property
    def serialize(self):
        """Return object data in easily serializeable format"""
        return {
            'title': self.title,
            'description': self.description,
            'id': self.id,
        }


engine = create_engine('sqlite:///catalogapp.db')

Base.metadata.create_all(engine)
