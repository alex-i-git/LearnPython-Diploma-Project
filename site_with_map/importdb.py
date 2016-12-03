from db import Survey
	s = Survey
	class 'db.Survey'
	u.query.all()	
	return render_template("index.html")
	print(s)

u.query.filter(Survey.latitude=='Маша').first()
u.query.filter(Survey.longitude.like('М%')).all()