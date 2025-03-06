import sqlite3

def create_database():
    # Create Student Table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS StudentTb (
            Id INTEGER PRIMARY KEY AUTOINCREMENT,
            StudentNumber TEXT UNIQUE NOT NULL,
            Name TEXT NOT NULL
        )
    ''')

    # Create Professor Table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS ProfessorTb (
            Id INTEGER PRIMARY KEY AUTOINCREMENT,
            ProfessorNumber TEXT UNIQUE NOT NULL,
            Name TEXT NOT NULL
        )
    ''')

    # Create Lecture Table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS LectureTb (
            Id INTEGER PRIMARY KEY AUTOINCREMENT,
            LectureCode TEXT UNIQUE NOT NULL,
            Name TEXT NOT NULL,
            Hours INTEGER NOT NULL,
            Year INTEGER NOT NULL
        )
    ''')

    # Create LectureStudent Table (Many-to-Many relationship between Student and Lecture)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS LectureStudentTb (
            Id INTEGER PRIMARY KEY AUTOINCREMENT,
            StudentId INTEGER NOT NULL,
            LectureProfessorId INTEGER NOT NULL,
            FOREIGN KEY (StudentId) REFERENCES StudentTb(Id),
            FOREIGN KEY (LectureProfessorId) REFERENCES LectureProfessorTb(Id)
        )
    ''')

    # Create LectureProfessor Table (Many-to-Many relationship between Professor and Lecture)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS LectureProfessorTb (
            Id INTEGER PRIMARY KEY AUTOINCREMENT,
            ProfessorId INTEGER NOT NULL,
            LectureId INTEGER NOT NULL,
            FOREIGN KEY (ProfessorId) REFERENCES ProfessorTb(Id),
            FOREIGN KEY (LectureId) REFERENCES LectureTb(Id)
        )
    ''')

    # Create TimeProfessor Table (Professor's availability schedule)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS TimeProfessorTb (
            Id INTEGER PRIMARY KEY AUTOINCREMENT,
            ProfessorId INTEGER NOT NULL,
            Hour INTEGER NOT NULL,
            Day TEXT NOT NULL,
            FOREIGN KEY (ProfessorId) REFERENCES ProfessorTb(Id)
        )
    ''')

    conn.commit()
    # conn.close()

def insert_dummy_data():
    # Insert dummy students
    students = [
        ("S001", "Alice"),
        ("S002", "Bob"),
        ("S003", "Charlie")
    ]
    cursor.executemany("INSERT OR IGNORE INTO StudentTb (StudentNumber, Name) VALUES (?, ?)", students)

    # Insert dummy professors
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
    cursor.executemany("INSERT OR IGNORE INTO ProfessorTb (ProfessorNumber, Name) VALUES (?, ?)", professors)

    # Insert dummy lectures
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
    cursor.executemany("INSERT OR IGNORE INTO LectureTb (LectureCode, Name, Hours, Year) VALUES (?, ?, ?, ?)", lectures)

    # Insert dummy lecture-student associations
    lecture_students = [
        (1, 1),
        (2, 1),
        (3, 2),
        (1, 3),
        (2, 3),
        (3, 3),
    ]
    cursor.executemany("INSERT OR IGNORE INTO LectureStudentTb (StudentId, LectureProfessorId) VALUES (?, ?)", lecture_students)

    # Insert dummy lecture-professor associations
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
    cursor.executemany("INSERT OR IGNORE INTO LectureProfessorTb (ProfessorId, LectureId) VALUES (?, ?)", lecture_professors)

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
    time_professors = [(i+1, s[1], d) for i in range(len(professors)) for d in WEEKDAYS for s in sample]
    cursor.executemany("INSERT OR IGNORE INTO TimeProfessorTb (ProfessorId, Hour, Day) VALUES (?, ?, ?)", time_professors)

    conn.commit()
    # conn.close()

if __name__ == "__main__":
    conn = sqlite3.connect("UniversityDb.db")  # Create or connect to the database
    cursor = conn.cursor()

    create_database()
    insert_dummy_data()