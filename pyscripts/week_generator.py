import random
# from unittest import result
from models import *
from rich import print
import copy
# import concurrent.futures
# import itertools

# def get_lecture_id_by_code(code):
#     lecture_id = None
#     for row2 in lectures:
#         if row2[1] == code:
#             lecture_id = row2[0]
#             break
    
#     return lecture_id

# def is_professor_available(lecture, hour, day):
# # def is_professor_available(professor_id, hour, day):
#     # professor_time = TimeProfessor.query.filter_by(professor_id=professor_id, hour=hour, day=day).first()

#     # if professor_time is None:
#     #     return False

#     return hour in lecture["professor"]["freeTime"][day]:
#         return False
    
#     return True

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
    # result = 0
    # for item in list_:
    #     result += abs(item - point)
    # return result

def get_items_distance_from_point(list_, point):
    return min([
        abs(item - point)
        for item in list_
    ])

def get_shared_items_between_lists(list1, list2):
    shared_items = []

    for item1 in list1:
        for item2 in list2:
            if item1 == item2:
                shared_items.append(item1)
                break
    
    return shared_items

def get_lecture_day_available_hours(lecture, week, day, lecture_hall):
    empty_hours = []
    for hour in week[day]:
        # if not is_professor_available(lecture, hour, day):
        if hour not in lecture["professor"]["freeTime"][day]:
        # if not is_professor_available(lecture["professor"]["id"], hour, day):
            continue

        for lec_ in week[day][hour]:
            if lec_["professor"]["id"] == lecture["professor"]["id"]:
                break

            if lec_["year"] == lecture["year"] and get_shared_items_between_lists(
                    lec_["studentIds"],
                    lecture["studentIds"]
                ):
                    break
            # if get_shared_items_between_lists(
            #         lec_["studentIds"],
            #         lecture["studentIds"]
            #     ):
            #         break

            if lec_["lectureHall"]['id'] == lecture_hall['id']:
                break

            if lecture_hall['capacity'] < len(lecture["studentIds"]):
                break
        else:
            empty_hours.append(hour)
    
    return empty_hours

def get_hours_space_between_prof(week, day, lecture, test_hours=[]):
    distance_from_same_prof_counter = 0
    distance_from_same_prof_counter_temp = None

    for hour in week[day]:
        for lec in week[day][hour]:
            if lec["professor"]["id"] == lecture["professor"]["id"] or hour in test_hours:
                if distance_from_same_prof_counter_temp is not None:
                    distance_from_same_prof_counter += distance_from_same_prof_counter_temp

                distance_from_same_prof_counter_temp = 0

                break
            
        else:
            if distance_from_same_prof_counter_temp is not None:
                distance_from_same_prof_counter_temp += 1
    
    return distance_from_same_prof_counter

def get_hours_space_between_year(week, day, year, test_hours=[]):
    distance_from_same_year_counter = 0
    distance_from_same_year_counter_temp = None

    for hour in week[day]:
        for lec in week[day][hour]:
            if lec["year"] == year or hour in test_hours:
                if distance_from_same_year_counter_temp is not None:
                    distance_from_same_year_counter += distance_from_same_year_counter_temp

                distance_from_same_year_counter_temp = 0

                break
            
        else:
            if distance_from_same_year_counter_temp is not None:
                distance_from_same_year_counter_temp += 1
    
    return distance_from_same_year_counter

def score_hours(week, day, lecture, hours):
    if get_items_difference_sum(hours) != len(hours) - 1:
        return None
    
    distance_from_same_prof_counter = get_hours_space_between_prof(week, day, lecture, hours)
    distance_from_same_year_counter = get_hours_space_between_year(week, day, lecture["year"], hours)

    distance_from_point = get_items_distance_from_point(hours, 12) - 1
    # distance_from_point_8 = get_items_distance_from_point_sum(hours[:1], 8) / (len(hours) * 2)

    return - distance_from_point - distance_from_same_prof_counter - distance_from_same_year_counter# + distance_from_point_8
    # return - diff

def get_best_hours(week, day, lecture, hours_list):
    max_score = None
    max_score_hours = None

    for hours in hours_list:
        score = score_hours(week, day, lecture, hours)
        
        if score is not None and (max_score is None or score > max_score):
            max_score = score
            max_score_hours = hours
    
    return max_score_hours, max_score

# def get_day_score(week, day, lecture): # best for profs
#     score = 0
#     for hour in week[day]:
#         if len(week[day][hour]) == 0:
#             score -= 2
#         for lec_ in week[day][hour]:
#             if lec_["code"] == lecture["code"]:
#                 score += 1
#             if lec_["professor"]["id"] != lecture["professor"]["id"]:
#                 score -= 1
    
#     return score

def get_day_score(week, day, lecture):
    score = 0
    for hour in week[day]:
        if len(week[day][hour]) == 0:
            score -= 1
        for lec_ in week[day][hour]:
            # if lec_["code"] != lecture["code"]:
            #     score -= 1
            if lec_["code"] == lecture["code"]:
                score += 1
            # if lec_["professor"]["id"] != lecture["professor"]["id"] and lec_["year"] == lecture["year"]:
            #     score -= 1
            # if not (lec_["professor"]["id"] != lecture["professor"]["id"] and lec_["year"] == lecture["year"]):
            #     score += .5
    
    return score

def get_lecture_hall_score(lecture_hall, lecture):
    return - abs(lecture_hall["capacity"] - len(lecture["studentIds"]))

def place_lecture_in_week(lecture, week, lecture_halls):
    best_hours, best_score, best_day, best_lecture_hall = None, None, None, None
    for day in week:
        day_score = get_day_score(week, day, lecture)
        for lec_hall in lecture_halls:
            lec_hall_score = get_lecture_hall_score(lec_hall, lecture)
            
            empty_hours = get_lecture_day_available_hours(lecture, week, day, lec_hall)

            hours_list = get_sequence_subset(empty_hours, lecture["hours"])

            hours, score = get_best_hours(week, day, lecture, hours_list)

            if score is None:
                continue

            score += day_score + lec_hall_score

            if best_score is None or score > best_score: # or (hours[0] < best_hours[0] and score >= best_score):
                best_score = score
                best_hours = hours
                best_day = day
                best_lecture_hall = lec_hall

    if best_hours is None:
        if lecture["hours"] == 1:
            # raise Exception("Could not place lecture " + lecture["code"])
            # print("Could not place lecture " + lecture["code"])
        
            return None, None
            
        splitted_lectures = split_lecture_time(lecture)

        best_score = 0

        for splitted_lecture in splitted_lectures:
            week_, score = place_lecture_in_week(splitted_lecture, week, lecture_halls)

            if score is None:
                continue

            week = week_

            best_score += score
        
        return week, best_score

    lecture["lectureHall"] = best_lecture_hall

    for hour in best_hours:
        week[best_day][hour].append(lecture.copy())

    return week, best_score

def split_lecture_time(lecture):
    hours = lecture["hours"]
    lec1 = lecture.copy()
    lec1["hours"] = hours // 2
    lec2 = lecture.copy()
    lec2["hours"] = hours - lec1["hours"]

    return [lec1, lec2]

def get_detailed_lectures():
    return [
        {
            'code': lec.code,
            'name': lec.name,
            'professor': {
                'id': lec_prof.professor_id,
                # 'name': lec_prof.professor.name,
                # 'number': lec_prof.professor.number,
                'freeTime': {
                    day: [
                        time_slot.hour
                        for time_slot in TimeProfessor.query.filter_by(professor_id=lec_prof.professor_id, day=day).all()
                    ]
                    # for day in WEEK
                    for day in [
                        "Monday",
                        "Tuesday",
                        "Wednesday",
                        "Thursday",
                        "Friday",
                    ]
                    # for time_slot in TimeProfessor.query.filter_by(professor_id=lec_prof.professor_id).group_by(TimeProfessor.day).all()
                }
            },
            'lectureHall': {
                'id': None,
                'name': None,
                'capacity': None
            },
            'studentIds': [
                lec_student.student_id
                for lec_student in LectureStudent.query.filter(LectureStudent.lecture_professor_id == lec_prof.id).all()
            ],
            'hours': lec.hours,
            'year': lec.year}
        for lec, lec_prof in db.session.query(Lecture, LectureProfessor).join(LectureProfessor).filter(Lecture.id == LectureProfessor.lecture_id).all()
    ]

def build_week(week_program = None, detailed_lectures = None, lecture_halls = None, is_random = True):
    if week_program is None:
        week_program = {
            day: {
                hour: []
                for hour in [
                    8, 9, 10, 11, 13, 14, 15, 16, 17
                ]
            }
            for day in [
                "Monday",
                "Tuesday",
                "Wednesday",
                "Thursday",
                "Friday",
            ]
        }

    if detailed_lectures is None:
        detailed_lectures = get_detailed_lectures()

    if lecture_halls is None:
        lecture_halls = [
            {
                'id': lec_hall.id,
                'name': lec_hall.name,
                'capacity': lec_hall.capacity
            }
            for lec_hall in db.session.query(LectureHall).all()
        ]


    lecs = {}
    for lec in detailed_lectures:
        if lec["professor"]["id"] in lecs:
            lecs[lec["professor"]["id"]].append(lec)
        else:
            lecs[lec["professor"]["id"]] = [lec]
    
    lec_groups = dict(sorted(lecs.items(), key=lambda item: sum(v["hours"] for v in item[1]), reverse=True))
    lec_groups = dict(sorted(lec_groups.items(), key=lambda item: sum(v["year"] for v in item[1]), reverse=True))

    count = 100

    results = [
        build_week_(copy.deepcopy(week_program), copy.deepcopy(lec_groups), copy.deepcopy(lecture_halls), is_random)
        for _ in range(count)
    ]


    # with concurrent.futures.ProcessPoolExecutor() as executor:
    #     results = list(executor.map(build_week_, (copy.deepcopy(week_program) for _ in range(count)), (copy.deepcopy(lec_groups) for _ in range(count)), (copy.deepcopy(lecture_halls) for _ in range(count)), (is_random for _ in range(count))))
        # results = list(executor.map(build_week_, (copy.deepcopy(week_program) for _ in range(count)), lec_groups_permutations, (copy.deepcopy(lecture_halls) for _ in range(count)), (is_random for _ in range(count))))

    # print(len(lec_groups))
    # lec_groups_permutations = list(itertools.permutations(lec_groups))
    # print(1)
    # i = len(lec_groups_permutations)
    # print(i)
    # input()
        
    best_week_program = None
    best_score = None

    for test_week_program, score in results:
        if best_score is None or best_score < score:
            best_score = score
            best_week_program = test_week_program

    for day in best_week_program:
        for hour in best_week_program[day]:
            for l, lec in enumerate(best_week_program[day][hour]):
                best_week_program[day][hour][l] = get_fully_detailed_lecture(lec)

    return best_week_program, best_score

def build_week_(week_program, lec_groups, lecture_halls, is_random):
    detailed_lectures = []
    for group in list(lec_groups.values()):
        if is_random:
            random.shuffle(group)
        detailed_lectures.extend(group)
    
    total_score = 0

    for lec in detailed_lectures:
        if not lec["studentIds"]:
            print(f"Lecture: {lec["code"]}, for Professor: {lec["professor"]["id"]} has been dropped!")
            print("Cause: No students take this lecture.")
            continue

        if not lec["hours"]:
            # print(f"Lecture: {lec["code"]}, for Professor: {lec["professor"]["id"]} has been dropped!")
            # print("Cause: No hours.")
            continue

        week_program_, score = place_lecture_in_week(lec, week_program, lecture_halls)

        if score is None:
            continue

        week_program = week_program_

        total_score += score

    # print(total_score)

    return week_program, total_score

def get_fully_detailed_lecture(detailed_lecture):
    # lecture = Lecture.query.filter(Lecture.code == detailed_lecture["code"]).first()
    # detailed_lecture["name"] = lecture.name

    professor = Professor.query.filter(Professor.id == detailed_lecture["professor"]["id"]).first()
    detailed_lecture["professor"]["name"] = professor.name
    detailed_lecture["professor"]["number"] = professor.number
    
    # detailed_lecture["professor"] = {
    #     "name": professor.name,
    #     "number": professor.number
    # }

    # del detailed_lecture["professor"]["id"] # it is safer to remove any database info
    # del detailed_lecture["professor"]["freeTime"]
    # del detailed_lecture["professor"]

    students = Student.query.filter(Student.id.in_(detailed_lecture["studentIds"])).all()
    detailed_lecture["studentNumbers"] = [
        student.number
        for student in students
    ]
    # del detailed_lecture["studentIds"]

    return detailed_lecture