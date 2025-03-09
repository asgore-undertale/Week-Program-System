from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin

db = SQLAlchemy()

class Professor(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    number = db.Column(db.String, unique=True, nullable=False)
    name = db.Column(db.String, nullable=False)

class Student(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    number = db.Column(db.String, unique=True, nullable=False)
    name = db.Column(db.String, nullable=False)

class Admin(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    number = db.Column(db.String, unique=True, nullable=False)
    name = db.Column(db.String, nullable=False)

class Lecture(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String, unique=True, nullable=False)
    name = db.Column(db.String, nullable=False)
    hours = db.Column(db.Integer, nullable=False)
    year = db.Column(db.Integer, nullable=False)

class TimeProfessor(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    professor_id = db.Column(db.Integer, db.ForeignKey('professor.id'), nullable=False)
    hour = db.Column(db.Integer, nullable=False)
    day = db.Column(db.Integer, nullable=False)

class LectureProfessor(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    professor_id = db.Column(db.Integer, db.ForeignKey('professor.id'), nullable=False)
    lecture_id = db.Column(db.Integer, db.ForeignKey('lecture.id'), nullable=False)

class LectureStudent(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('student.id'), nullable=False)
    lecture_professor_id = db.Column(db.Integer, db.ForeignKey('lecture_professor.id'), nullable=False)

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    number = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    role = db.Column(db.String(50), nullable=False)  # Admin, User, etc.

# def seed_data():
def seed_data(app):
    with app.app_context():
            
        if not Student.query.first():  # Check if table is empty
            students = [
                ("S1000", "Hülya Kaya"),
                ("S1001", "Hülya Çelik"),
                ("S1002", "Ayşe Acar"),
                ("S1003", "Fatma Eren"),
            ]
            db.session.add_all(map(
                lambda x: Student(
                    number=x[0],
                    name=x[1]
                ),
                students
            ))

        if not Professor.query.first():
            professors = [
                ("P001", "Dr. Öğr. Üyesi Rasim ÇEKİK"),
                ("P002", "Dr. Öğr. Üyesi Adnan KOK"),
                ("P003", "Öğretm Görevls Metn ÇALMAN"),
                ("P004", "Dr. Öğr. Üyesi Dilan ALP"),
                ("P005", "Dr. Öğr. Üyesi Mustafa MIZRAK"),
                ("P006", "Doç. Dr. Bilal ALTAN"),
                ("P007", "Dr. Öğr. Üyesi Mehmet GÜL"),
                ("P008", "Doç. Dr. Mahmut DİRİK"),
                ("P009", "Dr. Öğr. Üyesi Kenan DONUK"),
                ("P010", "Dr. Öğr. Üyesi Emrullah GAZİOĞLU"),
                ("P011", "Doç. Dr. Murat ASLAN"),
                ("P012", "Doç. Dr. Asaf T. ÜLGEN"),
            ]
            db.session.add_all(map(
                lambda x: Professor(
                    number=x[0],
                    name=x[1]
                ),
                professors
            ))

        if not Lecture.query.first():
            lectures = [
                ("L001", "Mühendislk Etğ", 2, 1),
                ("L002", "Algoritma ve Programlama II", 5, 1),
                ("L003", "Makine Öğrenmesi", 3, 2),
                ("L004", "Türk Dili II", 2, 1),
                ("L005", "İngilizce II", 2, 1),
                ("L006", "Fizik II", 4, 1),
                ("L007", "Matematik II", 4, 1),
                ("L008", "Dfferansyel Denklemler", 4, 2),
                ("L009", "Olasılık ve İstatstk", 3, 2),
                ("L010", "Atatürk İlke ve İnkılapları", 2, 2),
                ("L011", "Nesne Tabanlı Programlama", 4, 2),
                ("L012", "İnsan Blgsayar Etkleşm", 2, 2),
                ("L013", "Görsel Programlama Dilleri", 4, 2),
                ("L014", "Mobil Tabanlı Uygulamalar", 2, 3),
                ("L015", "Gömülü Sistemi Programlama", 3, 4),
                ("L016", "Algoritmalar", 3, 2),
                ("L017", "Yapay Zeka", 3, 2),
                ("L018", "Bilişim Hukuku", 2, 2),
                ("L019", "Veri Madenciliğine Giriş", 3, 3),
                ("L020", "Yazılım Mühendislği", 4, 3),
                ("L021", "Bulanık Mantığın Temelleri", 4, 4),
                ("L022", "Bilgisayar Organizasyonu ve Mimarisi", 4, 2),
                ("L023", "Bilgisayar Mühendisliği Uygulamaları", 4, 3),
                ("L024", "Biçimsel Diller ve Otomata Teorisi", 3, 3),
                ("L025", "Algoritma Analizi", 3, 3),
                ("L026", "Veritabanı II", 3, 3),
                ("L027", "Bilgisayar Ağları", 3, 3),
                ("L028", "Optimizasyona Giriş", 3, 4),
                ("L029", "Elektrik Devreleri", 3, 1),
            ]
            db.session.add_all(map(
                lambda x: Lecture(
                    code=x[0],
                    name=x[1],
                    hours=x[2],
                    year=x[3]
                ),
                lectures
            ))

        if not LectureStudent.query.first():
            lecture_students = [
                (1, 1),
                (1, 2),
                (1, 4),
                (1, 5),
                (1, 6),
                (1, 7),
                (1, 29),
                (2, 3),
                (2, 8),
                (2, 9),
                (2, 10),
                (2, 11),
                (2, 12),
                (2, 13),
                (2, 16),
                (2, 17),
                (2, 18),
                (2, 22),
                (3, 14),
                (3, 19),
                (3, 20),
                (3, 23),
                (3, 24),
                (3, 25),
                (3, 26),
                (3, 27),
                (4, 15),
                (4, 21),
                (4, 28),
            ]
            db.session.add_all(map(
                lambda x: LectureStudent(
                    student_id=x[0],
                    lecture_professor_id=x[1],
                ),
                lecture_students
            ))

        if not LectureProfessor.query.first():
            lecture_professors = [
                (1, 1),
                (1, 2),
                (1, 3),
                (2, 4),
                (3, 5),
                (4, 6),
                (5, 7),
                (5, 8),
                (5, 9),
                (6, 10),
                (7, 11),
                (7, 12),
                (7, 13),
                (7, 14),
                (7, 15),
                (8, 16),
                (8, 17),
                (9, 18),
                (9, 19),
                (9, 20),
                (9, 21),
                (10, 22),
                (10, 23),
                (10, 24),
                (10, 25),
                (11, 26),
                (11, 27),
                (11, 28),
                (12, 29),
            ]
            db.session.add_all(map(
                lambda x: LectureProfessor(
                    professor_id=x[0],
                    lecture_id=x[1]
                ),
                lecture_professors
            ))

        if not TimeProfessor.query.first():
            sample = [
                (1, 8, ""),
                (1, 9, ""),
                (1, 10, ""),
                (1, 11, ""),
                (1, 13, ""),
                (1, 14, ""),
                (1, 15, ""),
                (1, 16, ""),
                (1, 17, ""),
            ]

            WEEKDAYS = [
                "Monday",
                "Tuesday",
                "Wednesday",
                "Thursday",
                "Friday",
            ]

            # Insert dummy professor schedule
            time_professors = [
                (i+1, s[1], d)
                for i in range(len(professors)) 
                for d in WEEKDAYS for s in sample
            ]
            db.session.add_all(map(
                lambda x: TimeProfessor(
                    professor_id=x[0],
                    hour=x[1],
                    day=x[2]
                ),
                time_professors
            ))

        db.session.commit()