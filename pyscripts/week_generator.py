import random
from models import *
from rich import print
import copy
import concurrent.futures

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
    distances = [
        abs(item - point)
        for item in list_
    ]
    for d in distances:
        if d == 0 or distances.count(d) > 1:
            return d
    
    return min(distances)-1

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

# def get_hours_space_between_prof(week, day, lecture, test_hours=[]):
#     distance_from_same_prof_counter = 0
#     distance_from_same_prof_counter_temp = None

#     for hour in week[day]:
#         for lec in week[day][hour]:
#             if lec["professor"]["id"] == lecture["professor"]["id"] or hour in test_hours:
#                 if distance_from_same_prof_counter_temp is not None:
#                     distance_from_same_prof_counter += distance_from_same_prof_counter_temp

#                 distance_from_same_prof_counter_temp = 0

#                 break
            
#         else:
#             if distance_from_same_prof_counter_temp is not None:
#                 distance_from_same_prof_counter_temp += 1
    
#     return distance_from_same_prof_counter

# def get_hours_space_between_year(week, day, year, test_hours=[]):
#     distance_from_same_year_counter = 0
#     distance_from_same_year_counter_temp = None

#     for hour in week[day]:
#         for lec in week[day][hour]:
#             if lec["year"] == year or hour in test_hours:
#                 if distance_from_same_year_counter_temp is not None:
#                     distance_from_same_year_counter += distance_from_same_year_counter_temp

#                 distance_from_same_year_counter_temp = 0

#                 break
            
#         else:
#             if distance_from_same_year_counter_temp is not None:
#                 distance_from_same_year_counter_temp += 1
    
#     return distance_from_same_year_counter

# def score_hours(week, day, lecture, hours):
#     if get_items_difference_sum(hours) != len(hours) - 1:
#         return None
    
#     distance_from_same_prof_counter = get_hours_space_between_prof(week, day, lecture, hours)
#     distance_from_same_year_counter = get_hours_space_between_year(week, day, lecture["year"], hours)

#     distance_from_point = get_items_distance_from_point(hours, 12) - 1
#     # distance_from_point_8 = get_items_distance_from_point_sum(hours[:1], 8) / (len(hours) * 2)

#     return - distance_from_point - distance_from_same_prof_counter - distance_from_same_year_counter# + distance_from_point_8
#     # return - diff

# def get_best_hours(week, day, lecture, hours_list):
#     max_score = None
#     max_score_hours = None

#     for hours in hours_list:
#         score = score_hours(week, day, lecture, hours)
        
#         if score is not None and (max_score is None or score > max_score):
#             max_score = score
#             max_score_hours = hours
    
#     return max_score_hours, max_score

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
        if best_score is not None:
            break
        
        day_score = get_day_score(week, day, lecture)
        for lec_hall in lecture_halls:
            if best_score is not None:
                break

            lec_hall_score = get_lecture_hall_score(lec_hall, lecture)
            
            empty_hours = get_lecture_day_available_hours(lecture, week, day, lec_hall)

            hours_list = get_sequence_subset(empty_hours, lecture["hours"])

            # hours, score = get_best_hours(week, day, lecture, hours_list)
            if len(hours_list):
                hours, score = hours_list[0], 0
            else:
                continue

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

def flatten_week(week):
    return [
        {
            "day": day,
            "hour": hour,
            "lecCode": lec["code"],
            "profId": lec["professor"]["id"],
            "year": lec["year"],
            "lec": lec,
        }
        for day in week
        for hour in week[day]
        for lec in week[day][hour]
    ]

def unflatten_json(json_data, keys: list[str] = []):
    if not len(keys):
        return json_data
    
    unflattened_data = {}

    for item in json_data:
        d = unflattened_data
        for k, key in enumerate(keys):
            if item[key] not in d:
                if k < len(keys) - 1:
                    d[item[key]] = {}
                else:
                    d[item[key]] = []
            d = d[item[key]]

        d.append(item)

    return unflattened_data

def get_week_score(week):
    DAY_DISTANCE_PANELTY = 3
    HOUR_DISTANCE_PANELTY = 1
    HALL_CHAIR_PANELTY = 1

    score = 0

    flatten_week_list = flatten_week(week)

    prof_day_hour_group = unflatten_json(flatten_week_list, ["profId", "day", "hour"])
    for profId in prof_day_hour_group:
        score -= DAY_DISTANCE_PANELTY * (len(prof_day_hour_group[profId]) - 1)
        for day in prof_day_hour_group[profId]:
            score -= HOUR_DISTANCE_PANELTY * (get_items_difference_sum(list(prof_day_hour_group[profId][day].keys())) - len(prof_day_hour_group[profId][day]) + 1) 

    lec_day_hour_group = unflatten_json(flatten_week_list, ["lecCode", "day", "hour"])
    for lecCode in lec_day_hour_group:
        score -= DAY_DISTANCE_PANELTY * (len(lec_day_hour_group[lecCode]) - 1)
        for day in lec_day_hour_group[lecCode]:
            hours = list(lec_day_hour_group[lecCode][day].keys())
            score -= HOUR_DISTANCE_PANELTY * (get_items_difference_sum(hours) - len(hours) + 1)
            score -= HOUR_DISTANCE_PANELTY * (get_items_distance_from_point(hours, 12))
    
    year_day_hour_group = unflatten_json(flatten_week_list, ["year", "day", "hour"])
    for year in year_day_hour_group:
        score -= DAY_DISTANCE_PANELTY * (len(year_day_hour_group[year]) - 1)
        for day in year_day_hour_group[year]:
            score -= HOUR_DISTANCE_PANELTY * (get_items_difference_sum(list(year_day_hour_group[year][day].keys())) - len(year_day_hour_group[year][day]) + 1) 
    
    lec_group = unflatten_json(flatten_week_list, ["lecCode"])
    for lecCode in lec_group:
        score -= HALL_CHAIR_PANELTY * abs(lec_group[lecCode][0]["lec"]["lectureHall"]["capacity"] - len(lec_group[lecCode][0]["lec"]["studentIds"]))

        
    return score

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

    for k, v in lec_groups.items():
        lec_groups[k].sort(key=lambda x: x["year"], reverse=True)

    count = 1

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
    for group in list(lec_groups.values())[:2]:
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