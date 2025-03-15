# from rich import print
import copy
import random
from pyscripts.week_generator import *
from models import *

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

def flatten_week2(week):
    return [
        {
            "day": day,
            "hour": hour,
            "lecCode": loc_code,
            "profId": prof_id,
            "year": lec["year"],
            "lec": lec["lec"],
        }
        for prof_id in week
        for loc_code in week[prof_id]
        for day in week[prof_id][loc_code]
        for hour in week[prof_id][loc_code][day]
        for lec in week[prof_id][loc_code][day][hour]
    ]

def unflatten_json(json_data, keys: list[str] = []):
    if not len(keys):
        return json_data
    
    unflattened_data = {}

    for i, item in enumerate(json_data):
        d = unflattened_data
        for k, key in enumerate(keys):
            if item[key] not in d:
                if k < len(keys) - 1:
                    d[item[key]] = {}
                else:
                    d[item[key]] = []
            d = d[item[key]]

        d.append((i, item))

    return unflattened_data

def get_week_score(flatten_week_list): # fitness
    DAY_DISTANCE_PANELTY = 3
    HOUR_DISTANCE_PANELTY = 1
    HALL_CHAIR_PANELTY = 1

    score = 0

    prof_day_hour_group = unflatten_json(flatten_week_list, ["profId", "day", "hour"])
    for profId in prof_day_hour_group:
        if profId is None:
            continue
        score -= DAY_DISTANCE_PANELTY * (len(prof_day_hour_group[profId]) - 1)
        for day in prof_day_hour_group[profId]:
            score -= HOUR_DISTANCE_PANELTY * (get_items_difference_sum(list(prof_day_hour_group[profId][day].keys())) - len(prof_day_hour_group[profId][day]) + 1) 

    lec_day_hour_group = unflatten_json(flatten_week_list, ["lecCode", "day", "hour"])
    for lecCode in lec_day_hour_group:
        if lecCode is None:
            continue
        score -= DAY_DISTANCE_PANELTY * (len(lec_day_hour_group[lecCode]) - 1)
        for day in lec_day_hour_group[lecCode]:
            hours = list(lec_day_hour_group[lecCode][day].keys())
            score -= HOUR_DISTANCE_PANELTY * (get_items_difference_sum(hours) - len(hours) + 1)
            score -= HOUR_DISTANCE_PANELTY * (get_items_distance_from_point(hours, 12))
    
    year_day_hour_group = unflatten_json(flatten_week_list, ["year", "day", "hour"])
    for year in year_day_hour_group:
        if year is None:
            continue
        score -= DAY_DISTANCE_PANELTY * (len(year_day_hour_group[year]) - 1)
        for day in year_day_hour_group[year]:
            score -= HOUR_DISTANCE_PANELTY * (get_items_difference_sum(list(year_day_hour_group[year][day].keys())) - len(year_day_hour_group[year][day]) + 1) 
    
    # lec_group = unflatten_json(flatten_week_list, ["lecCode"])
    # for lecCode in lec_group:
    #     if lecCode is None or lec_group[lecCode][0]["lec"] is None:
    #         continue
    #     score -= HALL_CHAIR_PANELTY * abs(lec_group[lecCode][0]["lec"]["lectureHall"]["capacity"] - len(lec_group[lecCode][0]["lec"]["studentIds"]))

    return score

def get_available_time(flatten_week_list, profs_free_time, detailed_lectures, prof_id, lec_code):
    day_hour_group = unflatten_json(flatten_week_list, ["day", "hour"])
    empty_hours = {}

    def add_hour(day, hour):
        z = copy.deepcopy(flatten_week_list)
        z.append({
            "day": day,
            "hour": hour,
            "lecCode": lec_code,
            "profId": prof_id,
            "year": detailed_lectures[lec_code]["year"],
            "lec": detailed_lectures[lec_code]
        })
        score = get_week_score(z)

        if day not in empty_hours:
            empty_hours[day] = []
        
        empty_hours[day].append((hour, score))

    for day in profs_free_time[prof_id]:
        for hour in profs_free_time[prof_id][day]:
            if day not in day_hour_group or hour not in day_hour_group[day]:
                add_hour(day, hour)
                continue

            for row in day_hour_group[day][hour]:
                lec = row[1]["lec"]
                if lec["professor"]["id"] == prof_id:
                    break

                if lec["year"] == detailed_lectures[lec_code]["year"] and get_shared_items_between_lists(
                        lec["studentIds"],
                        detailed_lectures[lec_code]["studentIds"]
                    ):
                        break
                # if get_shared_items_between_lists(
                #         lec_["studentIds"],
                #         lecture["studentIds"]
                #     ):
                #         break


                # if lec_["lectureHall"]['id'] == lecture_hall['id']:
                #     break

                # if lecture_hall['capacity'] < len(lecture["studentIds"]):
                #     break
            else:
                add_hour(day, hour)
    
    return empty_hours

def generate_population(size, week_program = None, detailed_lectures = None, lecture_halls = None, is_random = True):
    return [
        flatten_week(
            build_week(week_program, detailed_lectures, lecture_halls, is_random)
        )
        for _ in range(size)
    ]

def selection(population):
    return sorted(
        population,
        key=lambda week: get_week_score(week),
        reverse=True
    )[
        : len(population) - int(len(population) * SELECTION_RATE)
    ]
    

def move_lecture(flatten_week_list, profs_free_time, detailed_lectures): # move to any available time
    prof_code_day_hour_group = unflatten_json(flatten_week_list, ["profId", "lecCode", "day", "hour"])

    prof_id1 = random.choice(list(prof_code_day_hour_group.keys()))
    lec_code1 = random.choice(list(prof_code_day_hour_group[prof_id1].keys()))

    available_time = get_available_time(flatten_week_list, profs_free_time, detailed_lectures, prof_id1, lec_code1)

    a = prof_code_day_hour_group[prof_id1][lec_code1]

    day1 = random.choice(list(a.keys()))
    # day2 = random.choice(list(available_time.keys()))
    day2 = sorted(available_time.keys(), key=lambda x: sum([h[1] for h in available_time[x]]), reverse=True)[0]

    if day2 not in a:
        a[day2] = {}

    # if len(available_time[day2]) < len(a[day1]):
    #     return flatten_week_list

    width = min(len(a[day1]), len(available_time[day2][0]))

    if len(available_time[day2][0]) < len(a[day1]):
        offset = random.randint(0, len(a[day1]) - len(available_time[day2][0]))
        offset1 = 0
    else:
        offset = 0
        offset1 = random.randint(0, len(available_time[day2][0]) - len(a[day1]))

    if day1 == day2 and offset == 0:
        return flatten_week_list

    for i in range(width-1, -1, -1):
        hour1 = list(a[day1].values())[i+offset]

        flatten_week_list.pop(hour1[0][0])

        lec = hour1[0][1]
        lec["day"] = day2
        lec["hour"] = available_time[day2][0][i+offset1]

        flatten_week_list.append(lec)
        
    return flatten_week_list
        # if profs_free_time[prof_id1][day2][i+offset1] not in hours2:
        #     hours2.append(profs_free_time[prof_id1][day2][i+offset1])
        
        # hour2 = profs_free_time[prof_id1][day2][i+offset1]
        # # hour2 = hours2[i]
        
        # # lec1 = a[day1][i+offset][0]
        # lec1 = hour1[0]
        # del hour1[0]


        # lec1["day"] = day2
        # lec1["hour"] = hour2[0]["hour"]

        # hour2.append(
        #     lec1
        # )

    # return flatten_week2(prof_code_day_hour_group)
    

# def swap_lecture(flatten_week_list, profs_free_time):
#     prof_code_day_hour_group = unflatten_json(flatten_week_list, ["profId", "lecCode", "day", "hour"])

#     prof_id1 = random.choice(list(prof_code_day_hour_group.keys()))
#     lec_code1 = random.choice(list(prof_code_day_hour_group[prof_id1].keys()))
#     day1 = random.choice(list(profs_free_time[prof_id1].keys()))
#     hour1 = random.choice(profs_free_time[prof_id1][day1])
#     lectures1 = prof_code_day_hour_group[prof_id1][lec_code1][day1][hour1]

#     prof_id2 = random.choice(list(prof_code_day_hour_group.keys()))
#     lec_code2 = random.choice(list(prof_code_day_hour_group[prof_id2].keys()))
#     day2 = random.choice(list(prof_code_day_hour_group[prof_id2].keys()))
#     shared_hours = get_shared_items_between_lists(
#         list(prof_code_day_hour_group[prof_id2][day2].keys()),
#         hour1,
#     )

#     if not len(shared_hours):
#         return flatten_week_list

#     hour2 = random.choice(shared_hours)
#     lectures2 = prof_code_day_hour_group[prof_id2][lec_code2][day2][hour2]

#     if len(lectures2) > len(lectures1):
#         prof_id1, prof_id2 = prof_id2, prof_id1
#         lec_code1, lec_code2 = lec_code2, lec_code1
#         day1, day2 = day2, day1
#         hour1, hour2 = hour2, hour1
#         lectures1, lectures2 = lectures2, lectures1

#     if not len(shared_hours):
#         return flatten_week_list

#     hour2 = random.choice(shared_hours)
#     lectures2 = prof_code_day_hour_group[prof_id2][lec_code2][day2][hour2]

#     if len(lectures2) > len(lectures1):
#         prof_id1, prof_id2 = prof_id2, prof_id1
#         lec_code1, lec_code2 = lec_code2, lec_code1
#         day1, day2 = day2, day1
#         hour1, hour2 = hour2, hour1
#         lectures1, lectures2 = lectures2, lectures1

#     width = min(len(lectures1), len(lectures2))
#     offset = random.randint(0, len(lectures1) - len(lectures2))

#     for i in range(width):
#         lec1 = prof_code_day_hour_group[prof_id1][lec_code1][day1][hour1][i+offset]
#         lec2 = prof_code_day_hour_group[prof_id2][lec_code2][day2][hour2][i]

#         lec1["day"] = day2
#         lec1["hour"] = hour2

#         lec2["day"] = day1
#         lec2["hour"] = hour1

#         prof_code_day_hour_group[prof_id1][lec_code1][day1][hour1][i+offset] = lec2
#         prof_code_day_hour_group[prof_id2][lec_code2][day2][hour2][i] = lec1

#     return flatten_week2(prof_code_day_hour_group)

def run_genetic():
    profs_free_time = get_profs_free_time()
    detailed_lectures = get_detailed_lectures()
    # lecture_halls = get_lecture_halls()

    population = generate_population(POPULATION_SIZE)

    for i in range(GENERATIONS_NUM):
        population = list(map(
            lambda week: move_lecture(copy.deepcopy(week), profs_free_time, detailed_lectures) if random.random() < MUTATION_RATE else week,
            population
        ))

        population = selection(population)
        
        print("Generation:", i+1, "score:", get_week_score(population[0]))

    grouped_week = unflatten_json(population[0], ["day", "hour"])
    for day in grouped_week:
        for hour in grouped_week[day]:
            for i in range(len(grouped_week[day][hour])-1, -1, -1):
                if grouped_week[day][hour][i][1]["lec"] is None:
                    grouped_week[day][hour].pop(i)
                else:
                    grouped_week[day][hour][i] = get_fully_detailed_lecture(grouped_week[day][hour][i][1]["lec"])

    return grouped_week

def get_profs_free_time():
    profs_free_time = {
        professor.id: {}
        for professor in Professor.query.all()
    }

    for professor_id in profs_free_time:
        for time_slot in TimeProfessor.query.filter_by(professor_id=professor_id).group_by(TimeProfessor.day, TimeProfessor.hour).all():
            day = time_slot.day
            hour = time_slot.hour

            if day not in profs_free_time[professor_id]:
                profs_free_time[professor_id][day] = []

            profs_free_time[professor_id][day].append(hour)
    
    return profs_free_time

def get_detailed_lectures():
    return {
        lec.code: {
            'code': lec.code,
            'name': lec.name,
            'professorId': lec_prof.professor_id,
            'lectureHallId': None,
            # 'lectureHall': {
            #     'id': None,
            #     'name': None,
            #     'capacity': None
            # },
            'studentIds': [
                lec_student.student_id
                for lec_student in LectureStudent.query.filter(LectureStudent.lecture_professor_id == lec_prof.id).all()
            ],
            'hours': lec.hours,
            'year': lec.year}
        for lec, lec_prof in db.session.query(Lecture, LectureProfessor).join(LectureProfessor).filter(Lecture.id == LectureProfessor.lecture_id).all()
    }

def get_lecture_halls():
    return {
        lec_hall.id: {
            'id': lec_hall.id,
            'name': lec_hall.name,
            'capacity': lec_hall.capacity
        }
        for lec_hall in db.session.query(LectureHall).all()
    }

POPULATION_SIZE = 100
GENERATIONS_NUM = 200
SELECTION_RATE  = .5
MUTATION_RATE   = .5