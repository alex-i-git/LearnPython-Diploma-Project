
from sqlalchemy import create_engine
from sqlalchemy import Column, Integer, String, Date, Boolean, DateTime, ForeignKey, Float
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.ext.declarative import declarative_base


engine = create_engine('sqlite:///botdb.sqlite')

db_session = scoped_session(sessionmaker(bind=engine))

Base = declarative_base()
Base.query = db_session.query_property()

class User(Base):
	__tablename__ = 'users' # имя таблицы
	id = Column(Integer, primary_key=True)
	chat_id = Column(Integer)
	#birthdate = Column(Date, required=False)
	birthdate = Column(Date)
	username = Column(String(50))
	is_admin = Column(Boolean) # админ чата или нет
	#gender = Column(String(1), required=False) # 0 - male, 1 - female
	gender = Column(String(1))
	phone = Column(String(20))
	profile_photo = Column(String(20)) # имя файла user_id.jpg
	sn = Column(String(100))	# линк на аккаунт юзера в соцсети





	def __init__(self,id=None, chat_id=None, birthdate=None, username=None, is_admin=None, gender=None, phone=None,profile_photo=None,sn=None):
		self.id = id
		self.chat_id = chat_id
		self.birthdate = birthdate
		self.username = username
		self.is_admin = is_admin
		self.gender = gender
		self.phone = phone
		self.profile_photo = profile_photo
		self.sn = sn


	def __repr__(self):
		return '<User {} {} {} {} {} {} {} {}>'.format(self.chat_id,self.birthdate,self.username,self.is_admin,self.gender,self.phone,self.profile_photo,self.sn)



class Question(Base):
	__tablename__ = 'questions'
	id = Column(Integer, primary_key=True)
	question_text = Column(String(100))
	#question_creation_date = Column(DateTime)
	#question_to_send_date = Column(DateTime)
	#question_type = Column(String(50))


	def __init__(self,question_id = None, question_text = None):
		self.question_id = question_id
		self.question_text = question_text
		#self.question_creation_date = question_creation_date
		#self.question_to_send_date = question_to_send_date
		#self.question_type = question_type


	def __repr__(self):
		return '<User {} {}>'.format(self.question_id,self.question_text)

class Survey(Base):
	__tablename__ = 'survey'
	id = Column(Integer, primary_key=True)
	answer_date = Column(DateTime)
	#feel_today = Column(String(20))
	#where_are_you = Column(String(20))
	#are_you_happy_now = Column(String(20))
	#fresh_selfy = Column(String(100))
	#first_app = Column(String(20))
	#smart_screenshot = Column(String(100))
	#color_you_like = Column(String(5))
	question_id = Column(Integer, ForeignKey('questions.id'))
	user_id = Column(Integer, ForeignKey('users.id'))
	answer_text = Column(String(100))
	answer_photo = Column(String(100))
	latitude = Column(Float)
	longitude = Column(Float)
	

	def __init__(self, id = None, answer_date = None, answer_text = None, \
		user_id = None, answer_photo = None, latitude = None, longitude = None):

		self.id = id
		self.answer_date = answer_date
		#self.feel_today = feel_today
		#self.where_are_you = where_are_you
		#self.are_you_happy_now = are_you_happy_now
		#self.fresh_selfy = fresh_selfy
		#self.first_app = first_app
		self.answer_text = answer_text
		self.user_id = user_id
		self.answer_photo = answer_photo
		self.latitude = latitude
		self.longitude = longitude

	def __repr__(self):
		return '<User {} {} {} {} {} {} {}>'.format(self.id, self.answer_date, \
			self.answer_text, self.user_id, self.answer_photo, self.latitude, self.longitude)
		
class Answer(Base):
	__tablename__ = 'answers'
	id = Column(Integer, primary_key=True)
	answer_variant_text = Column(String(50))
	answer_variant_picture = Column(String(200))


	def __init__(self,id = None, answer_variant_text = None, answer_variant_picture = None):
		self.id = id
		self.answer_variant_text = answer_variant_text
		self.answer_variant_picture = answer_variant_picture


	def __repr__(self):
		return '<User {} {} {} >'.format(self.id, self.answer_variant_text, self.answer_variant_picture)



if __name__ == "__main__":
	Base.metadata.create_all(bind=engine)

