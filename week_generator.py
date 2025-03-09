import random
from models import *

# def get_lecture_id_by_code(code):
#     lecture_id = None
#     for row2 in lectures:
#         if row2[1] == code:
#             lecture_id = row2[0]
#             break
    
#     return lecture_id

def is_professor_available(professor_id, hour, day):
    time = TimeProfessor.query.filter_by(professor_id=professor_id, hour=hour, day=day).first()

    if time is None:
        return False
    
    return True

    # for row in professors_time:
    #     if row[1] == professor_id and row[2] == hour and row[3] == day:
    #         return True
    # return False

# def get_professor_conflicts_num(lectures, hour, day):
#     conflicts_num = 0
#     professors_ids = []

#     for lec in lectures:
#         lec_id = get_lecture_id_by_code(lec[0])
                
#         for row2 in lectures_professores:
#             if row2[2] == lec_id:
#                 if row2[1] in professors_ids:
#                     conflicts_num += 1
#                 else:
#                     if not is_professor_available(row2[1], hour, day):
#                         conflicts_num += 1
#                     professors_ids.append(row2[1])
    
#     return conflicts_num

# def get_student_conflicts_num(lectures):
#     conflicts_num = 0
#     students_ids = []

#     for lec in lectures:
#         lec_id = get_lecture_id_by_code(lec[0])
                
#         for row2 in lectures_students:
#             if row2[2] == lec_id:
#                 if row2[1] in students_ids:
#                     conflicts_num += 1
#                 else:
#                     students_ids.append(row2[1])
    
#     return conflicts_num

def get_sequence_subset(list_, subset_size):
    return [
        list_[i: i + subset_size]
        for i in range(len(list_) - subset_size + 1)
    ]

def get_items_difference_sum(list_):
    result = 0
    for i in range(1, len(list_)):
        result += abs(list_[i] - list_[i-1])
    return result

# def get_items_distance_from_point_sum(list_, point):
#     result = 0
#     for item in list_:
#         result += abs(item - point)
#     return result

def get_shared_items_between_lists(list1, list2):
    shared_items = []

    for item1 in list1:
        for item2 in list2:
            if item1 == item2:
                shared_items.append(item1)
                break
    
    return shared_items

def get_lecture_day_available_hours(lecture, week, day):
    empty_hours = []
    for hour in week[day]:
        if not is_professor_available(lecture["professorId"], hour, day):
            continue

        for lec_ in week[day][hour]:
            # there can only be one professor for a lecture hour
            if lec_["professorId"] == lecture["professorId"]:
                break
            # we check for conflicts only for lectures with the same year
            if lec_["year"] == lecture["year"] and get_shared_items_between_lists(
                lec_["studentIds"],
                lecture["studentIds"]
            ):
                break
        else:
            empty_hours.append(hour)
    
    return empty_hours

def score_hours(hours):
    diff = get_items_difference_sum(hours) - len(hours) + 1
    # distance_from_point = 0#get_items_distance_from_point_sum(hours, 12) / (len(hours) * 2)

    # return - diff - distance_from_point
    return - diff

def get_best_hours(hours_list, acceptable_threshold = None):
    max_score = None
    max_score_hours = None

    for hours in hours_list:
        score = score_hours(hours)

        if acceptable_threshold is not None and score >= acceptable_threshold:
            return hours, score
        
        if max_score is None or score > max_score:
            max_score = score
            max_score_hours = hours
    
    return max_score_hours, max_score

def place_lecture_in_week(lecture, week):
    best_hours, best_score, best_day = None, None, None
    for day in week:
        empty_hours = get_lecture_day_available_hours(lecture, week, day)

        hours_list = get_sequence_subset(empty_hours, lecture["hours"])

        hours, score = get_best_hours(hours_list)

        if score is None:
            continue

        if best_score is None or score > best_score:
            best_score = score
            best_hours = hours
            best_day = day

    if best_hours is None:
        if lecture["hours"] == 1:
            raise Exception("Could not place lecture " + lecture["code"])
            
        splitted_lectures = split_lecture_time(lecture)

        for splitted_lecture in splitted_lectures:
            week = place_lecture_in_week(splitted_lecture, week, professors_time)
        
        return week

    for hour in best_hours:
        week[best_day][hour].append(lecture.copy())
    
    return week

def split_lecture_time(lecture):
    hours = lecture["hours"]
    lec1 = lecture.copy()
    lec1["hours"] = hours // 2
    lec2 = lecture.copy()
    lec2["hours"] = hours - lec1["hours"]

    return [lec1, lec2]

def build_week(is_random = False):
    WEEK = dict(
        (day, 
            dict([
                (hour, [])
                for hour in [
                    8, 9, 10, 11, 13, 14, 15, 16, 17
                ]
            ])
        )
        for day in [
            "Monday",
            "Tuesday",
            "Wednesday",
            "Thursday",
            "Friday",
        ]
    )

    detailed_lectures = [
        {
            'code': lec.code,
            'professorId': lec_prof.professor_id,
            'studentIds': [
                lec_student.student_id
                for lec_student in LectureStudent.query.filter(LectureStudent.lecture_professor_id == lec_prof.id).all()
            ],
            'hours': lec.hours,
            'year': lec.year}
        for lec, lec_prof in db.session.query(Lecture, LectureProfessor).join(LectureProfessor).filter(Lecture.id == LectureProfessor.lecture_id).all()
    ]


    if is_random:
        random.shuffle(detailed_lectures)
    else:
        detailed_lectures.sort(key=lambda x: -x["hours"])

    for lec in detailed_lectures:
        if not lec["studentIds"]:
            print(f"Lecture: {lec["code"]}, for Professor: {lec["professorId"]} has been dropped!")
            print("Cause: No students take this lecture.")
            continue

        week = place_lecture_in_week(lec, WEEK)

    for day in week:
        for hour in week[day]:
            for l, lec in enumerate(week[day][hour]):
                week[day][hour][l] = get_fully_detailed_lecture(lec)

    return week

def get_fully_detailed_lecture(detailed_lecture):
    lecture = Lecture.query.filter(Lecture.code == detailed_lecture["code"]).first()
    detailed_lecture["name"] = lecture.name

    professor = Professor.query.filter(Professor.id == detailed_lecture["professorId"]).first()
    detailed_lecture["professorName"] = professor.name
    detailed_lecture["professorNumber"] = professor.number
    del detailed_lecture["professorId"] # it is safer to remove any database info

    students = Student.query.filter(Student.id.in_(detailed_lecture["studentIds"])).all()
    detailed_lecture["studentNumbers"] = [
        student.number
        for student in students
    ]
    del detailed_lecture["studentIds"]

    return detailed_lecture