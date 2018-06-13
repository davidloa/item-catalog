from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from database_setup import Category, Base, CategoryItem, User

engine = create_engine('sqlite:///catalogapp.db')
# Bind the engine to the metadata of the Base class so that the
# declaratives can be accessed through a DBSession instance
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
# A DBSession() instance establishes all conversations with the database
# and represents a "staging zone" for all the objects loaded into the
# database session object. Any change made against the objects in the
# session won't be persisted into the database until you call
# session.commit(). If you're not happy about the changes, you can
# revert all of them back to the last commit by calling
# session.rollback()
session = DBSession()


# Create fake users
User1 = User(name="David Loa",
             email="davidloa@example.com")

session.add(User1)
session.commit()


# Soccer category and its items
category1 = Category(name="Soccer", user_id=1)

session.add(category1)
session.commit()

categoryItem1 = CategoryItem(title="Soccer Cleats",
                             description="The Shoes",
                             category=category1,
                             user_id=1)

session.add(categoryItem1)
session.commit()

categoryItem2 = CategoryItem(title="Jersey",
                             description="The Shirt",
                             category=category1,
                             user_id=1)

session.add(categoryItem2)
session.commit()


# Basketball category and its items
category2 = Category(name="Basketball", user_id=1)

session.add(category2)
session.commit()


# Baseball category and its items
category3 = Category(name="Baseball", user_id=1)

session.add(category3)
session.commit()

categoryItem1 = CategoryItem(title="Bat",
                             description="The Bat",
                             category=category3,
                             user_id=1)

session.add(categoryItem1)
session.commit()


# Frisbee category and its items
category4 = Category(name="Frisbee", user_id=1)

session.add(category4)
session.commit()


# Snowboarding category and its items
category5 = Category(name="Snowboarding", user_id=1)

session.add(category5)
session.commit()

categoryItem1 = CategoryItem(title="Snowboard",
                             description="Best for any terrain and conditions."
                             " All-mountain snowboards perform anywhere "
                             "on a mountain's groomed runs, backcountry, "
                             "even park and pipe. They may be directional "
                             "(meaning downhill only) or twin-tip "
                             "(for riding switch, meaning either direction). "
                             "Most boarders ride all-mountain boards. "
                             "Because of their versatility, "
                             "all-moutain boards are good for beginners "
                             "who are still learning what terrain they like.",
                             category=category5,
                             user_id=1)

session.add(categoryItem1)
session.commit()
