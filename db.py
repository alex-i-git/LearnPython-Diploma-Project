
from sqlalchemy import create_engine
from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.ext.declarative import declarative_base


engine = create_engine('sqlite:///dbot.sqlite')

db_session = scoped_session(sessionmaker(bind=engine))

Base = declarative_base()
Base.query = db_session.query_property()

class User(Base):
	__tablename__ = 'users'
	id = Column(Integer, primary_key=True)
	first_name = Column(String(50))
	last_name = Column(String(50))
	chat_id = Column(Integer)

	def __init__(self,first_name=None, last_name=None, chat_id=None):
		self.first_name = first_name
		self.last_name = last_name
		self.chat_id = chat_id

	def __repr__(self):
		return '<User {} {} {}>'.format(self.first_name,self.last_name,self.chat_id)

if __name__ == "__main__":
	Base.metadata.create_all(bind=engine)

