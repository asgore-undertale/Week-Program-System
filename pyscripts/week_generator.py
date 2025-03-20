import random
from models import *
from rich import print
import copy

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

def get_hours_score(week, day, lecture, hours):
    if get_items_difference_sum(hours) != len(hours) - 1:
        return None
    
    distance_from_same_prof_counter = get_hours_space_between_prof(week, day, lecture, hours)
    distance_from_same_year_counter = get_hours_space_between_year(week, day, lecture["year"], hours)

    distance_from_point = get_items_distance_from_point(hours, 12) - 1
    # distance_from_point_8 = get_items_distance_from_point_sum(hours[:1], 8) / (len(hours) * 2)

    return - distance_from_point - distance_from_same_prof_counter - distance_from_same_year_counter# + distance_from_point_8
    # return - diff

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

def choose_random_max(list_, func_):
    max_index, list_max = max(enumerate(list_), key=lambda x: func_(x[1]))
    return list_max, max_index
    # list_maxes = [item for item in list_ if func_(item) == func_(list_max)]
    # return random.choice(list_maxes)

def get_week_score(week, lecture, lecture_halls):
    results = []
    
    for day in week:
        day_score = get_day_score(week, day, lecture)
        for lec_hall in lecture_halls:
            lec_hall_score = get_lecture_hall_score(lec_hall, lecture)
            
            empty_hours = get_lecture_day_available_hours(lecture, week, day, lec_hall)

            hours_list = get_sequence_subset(empty_hours, lecture["hours"])

            hours_results = [
                {
                    "hours": hours,
                    "score": score
                }
                for hours in hours_list
                if (score := get_hours_score(week, day, lecture, hours)) is not None
            ]

            if not hours_results:
                continue

            best_hours_ = choose_random_max(hours_results, lambda x: x["score"] or -99999)[0]
            best_hours_["score"] += day_score + lec_hall_score

            results.append({
                "day": day,
                "hours": best_hours_["hours"],
                "score": best_hours_["score"] + day_score + lec_hall_score,
                "lectureHall": lec_hall
            })
    
    return results

def place_lecture_in_week(lecture, week, lecture_halls):
    times = get_week_score(week, lecture, lecture_halls)

    if len(times):
        best_time = choose_random_max(times, lambda x: x["score"] or -99999)[0]
    else:
        best_time = {"hours": None, "score": None}

    if best_time["hours"] is None:
        if lecture["hours"] == 1:
            # raise Exception("Could not place lecture " + lecture["code"])
            # print("Could not place lecture " + lecture["code"])
        
            return None, None
            
        splitted_lectures = split_lecture_time(lecture)

        best_time["score"] = 0

        for splitted_lecture in splitted_lectures:
            week_, score = place_lecture_in_week(splitted_lecture, week, lecture_halls)

            if score is None:
                return None, None

            week = week_

            best_time["score"] += score
        
        return week, best_time["score"]

    lecture["lectureHall"] = best_time["lectureHall"]

    for hour in best_time["hours"]:
        week[best_time["day"]][hour].append(lecture.copy())

    return week, best_time["score"]

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
            'id': i+1,
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
        for i, (lec, lec_prof) in enumerate(db.session.query(Lecture, LectureProfessor).join(LectureProfessor).filter(Lecture.id == LectureProfessor.lecture_id).all())
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
    
    # detailed_lectures.sort(key=lambda x: x["hours"])
    # detailed_lectures.sort(key=lambda x: x["year"])
    # detailed_lectures.sort(key=lambda x: x["professor"]["id"])

    results = [
        result
        for _ in range(POPULATION_SIZE)
        if (result := build_week_(copy.deepcopy(week_program), copy.deepcopy(detailed_lectures), copy.deepcopy(lecture_halls), True))["score"] is not None
    ]

    if not len(results):
        return {
            "week_program": None,
            "score": None
        }

    for _ in range(GENERATIONS_NUM):
        best_result, best_index = choose_random_max(results, lambda x: x["score"] or -99999)
        print("Generation:", _, "Score:", best_result["score"])

        for r, result in enumerate(results):
            if r == best_index:
                continue

            results[r] = build_week_(
                copy.deepcopy(week_program),
                follow_leader(result["detailed_lectures"], best_result["detailed_lectures"]),
                copy.deepcopy(lecture_halls),
                True
            )

    best_result = choose_random_max(results, lambda x: x["score"] or -99999)[0]

    print(best_result["score"])

    for day in best_result["week_program"]:
        for hour in best_result["week_program"][day]:
            for l, lec in enumerate(best_result["week_program"][day][hour]):
                best_result["week_program"][day][hour][l] = get_fully_detailed_lecture(lec)

    return {
        "week_program": best_result["week_program"],
        "score": best_result["score"]
    }

def build_week_(week_program, detailed_lectures, lecture_halls, is_random = True):
    if is_random:
        random.shuffle(detailed_lectures)
    
    total_score = 0

    for lec in detailed_lectures:
        if not lec["studentIds"]:
            # print(f"Lecture: {lec["code"]}, for Professor: {lec["professor"]["id"]} has been dropped!")
            # print("Cause: No students take this lecture.")
            continue

        if not lec["hours"]:
            # print(f"Lecture: {lec["code"]}, for Professor: {lec["professor"]["id"]} has been dropped!")
            # print("Cause: No hours.")
            continue

        week_program, score = place_lecture_in_week(lec, week_program, lecture_halls)

        if score is None:
            return {
                "week_program": None,
                "detailed_lectures": detailed_lectures,
                "score": None
            }

        total_score += score

    # print(total_score)

    return {
        "week_program": week_program,
        "detailed_lectures": detailed_lectures,
        "score": total_score
    }

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

def follow_leader(indivisual, leader):
    i = random.randint(0, len(leader)-1)

    leader_gen = leader[i]

    for j, item in enumerate(indivisual):
        if item["id"] == leader_gen["id"]:
            indivisual_gen = indivisual.pop(j)
            break
    
    indivisual.insert(i, indivisual_gen)

    return indivisual

POPULATION_SIZE       = 100
GENERATIONS_NUM       = 100
SELECTION_RATE        = .5
REPLACE_MUTATION_RATE = 1
SWAP_MUTATION_RATE    = 0
SHUFFLE_RATE          = 0