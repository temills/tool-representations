from . import db


class Subject(db.Model):
    __tablename__ = 'subjects'
    
    subject_id = db.Column(db.String, primary_key=True)
    completion_code = db.Column(db.String)
    age = db.Column(db.String)
    gender = db.Column(db.String)
    nationality = db.Column(db.String)
    country = db.Column(db.String)
    student = db.Column(db.String)
    language = db.Column(db.String)
    education = db.Column(db.String)
    comments = db.Column(db.String)
    comments_rt = db.Column(db.String)
    prog_bg = db.Column(db.String)
    math_bg = db.Column(db.String)
    bg_comments = db.Column(db.String)

    def __repr__(self):
        return '<Subject %r>' % self.id


class Trial(db.Model):
    __tablename__ = 'trials'
    row_id = db.Column(db.String, primary_key=True)
    complexity = db.Column(db.String)
    complexity_rt = db.Column(db.String)
    confidence = db.Column(db.String)
    confidence_rt = db.Column(db.String)
    true_x = db.Column(db.String)
    true_y = db.Column(db.String)
    response_x = db.Column(db.String)
    response_y = db.Column(db.String)
    rts = db.Column(db.String)
    func = db.Column(db.String)
    func_idx = db.Column(db.String)

    
    def __repr__(self):
        return '<Subject %r>' % self.id