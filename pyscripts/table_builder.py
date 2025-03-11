import openpyxl
from openpyxl.styles import PatternFill, Alignment, Border, Side
from rich import print

def combine_sequenced_lectures(week):
    for day in week:
        for hour in week[day]:
            for l, lec in enumerate(week[day][hour]):
                week[day][hour][l]["count"] = 1

    for day in week:
        reversed_hours = list(week[day].keys())[::-1]
        for h, hour in enumerate(reversed_hours[:-1]):
            for l in range(len(week[day][hour])-1, -1, -1):
                lec = week[day][hour][l]
                for l2, lec2 in enumerate(week[day][reversed_hours[h+1]]):
                    # if lec["code"] == lec2["code"] and lec["professorNumber"] == lec2["professorNumber"]:
                    if lec["code"] == lec2["code"] and lec["professor"]["number"] == lec2["professor"]["number"]:
                        week[day][reversed_hours[h+1]][l2]["count"] += week[day][hour][l]["count"]
                        week[day][hour].pop(l)
                        break
    
    return week

def tableize_combined_week_by_year(combined_week, remove_unnecessary_nones = False):
    cols_availibility_counter = {}
    table = {
        "rows": {},
        "cols": {},
    }
    global_row_pointer = 0

    for day in combined_week:
        table["rows"][day] = {}

        for hour in combined_week[day]:
            table["rows"][day][hour] = {}

            if not remove_unnecessary_nones:
                for year in cols_availibility_counter:
                    for i, item in enumerate(cols_availibility_counter[year]):
                        if item != 0:
                            table["cols"][year][i].append(None)

            lectures = combined_week[day][hour][::-1]

            for l in range(len(lectures)-1, -1, -1):
                lec = lectures[l]

                if lec["year"] not in cols_availibility_counter:
                    cols_availibility_counter[lec["year"]] = []
                    table["cols"][lec["year"]] = []

                for year in cols_availibility_counter:

                    if lec["year"] != year:
                        continue

                    for i, item in enumerate(cols_availibility_counter[year]):
                        if item == 0:
                            table["cols"][year][i].append(lec)
                            cols_availibility_counter[year][i] = lec["count"]
                            lectures.pop(l)
                            break
                    else:
                        table["cols"][year].append([{} for _ in range(global_row_pointer)] + [lec])
                        cols_availibility_counter[year].append(lec["count"])


            for year in cols_availibility_counter:
                for i, item in enumerate(cols_availibility_counter[year]):
                    if item == 0:
                        table["cols"][year][i].append({})
                    else:
                        cols_availibility_counter[year][i] -= 1

            global_row_pointer += 1

    table["cols"] = dict(sorted(table["cols"].items())) # to sort keys

    return table

def build_week_html_content(tableized_week):
    style = """<style>
    th, tr {
        border: 1px solid black;
    }
    td, th {
        padding: 5px;
    }
    .bordered_cell {
        border: 1px solid black;
        text-align: center;
        vertical-align: middle;
    }
    .vertical_writing {
        transform: rotate(-90deg);
    }
    table {
        border-collapse: collapse;
    }
    .header_cell {
        /* background-color: rgb(255, 89, 89); */
        background-color: aqua;
    }
    .lec_cell {
        background-color: rgb(224, 224, 224);
    }
    </style>"""

    table_content = style + "<table>"

    header_content = """<tr>
    <th class="bordered_cell header_cell">Day</th>
    <th class="bordered_cell header_cell">Time</th>""" + "".join(
        f"""
        <th class="bordered_cell header_cell" colspan="{len(tableized_week["cols"][year])}">Year {year}</th>
        """
        for year in tableized_week["cols"]
    ) + """
</tr>"""
    

    global_table_row_pointer = 0

    for day in tableized_week["rows"]:
        table_content += header_content
        
        days_content = f"""<td class="bordered_cell vertical_writing" rowspan="{len(tableized_week["rows"][day])+1}">{day}</td>"""
        
        rows_content = []
        for hour in tableized_week["rows"][day]:
            rows_content.append(f"""<tr><td class="bordered_cell">{hour}:00 ~ {hour}:50</td>""")
        
        for year in tableized_week["cols"]:
            for col in tableized_week["cols"][year]:
                for l, lec in enumerate(col[global_table_row_pointer : global_table_row_pointer + len(rows_content)]):
                    if lec is None:
                        continue

                    if lec == {}:
                        rows_content[l] += "<td></td>"
                        continue

                    span = lec["count"]

                    rows_content[l] += f"""<td rowspan="{span}" class="bordered_cell lec_cell">{lec["name"]}<br>{lec["professor"]["name"]}<br>{lec["lectureHall"]["name"]}</td>"""
                    # rows_content[l] += f"""<td rowspan="{span}" class="bordered_cell lec_cell">{lec["name"]}<br>{lec["professorName"]}</td>"""
        
        global_table_row_pointer += len(rows_content)

        for i in range(len(rows_content)):
            rows_content[i] += "</tr>"
        
        days_content += "".join(rows_content)

        table_content += days_content

    table_content += "</table>"

    return table_content

def auto_adjust_column_width(ws):
    for col in ws.columns:
        max_length = 0
        col_letter = col[0].column_letter  # Get column letter (A, B, C, etc.)
        
        for cell in col:
            if cell.value:
                max_length = max(max_length, len(str(cell.value)))
        
        ws.column_dimensions[col_letter].width = max_length

def auto_adjust_row_height(ws):
    for row in ws.iter_rows():
        max_height = 15  # Default row height
        for cell in row:
            if cell.value:
                lines = str(cell.value).count("\n") + 1  # Count line breaks
                max_height = max(max_height, lines * 15)  # Adjust for multiline text
        
        ws.row_dimensions[row[0].row].height = max_height

def get_max_dimentions(tableized_week):
    rows_num = 0
    for day in tableized_week["rows"]:
        rows_num += len(tableized_week["rows"][day]) + 1 # fore headers

    cols_num = 2
    for year in tableized_week["cols"]:
        years_columns_num = len(tableized_week["cols"][year])
        cols_num += years_columns_num
    
    return rows_num, cols_num

def build_week_excel_file(tableized_week):
    header_fill = PatternFill(start_color="00FFFF", end_color="00FFFF", fill_type="solid")
    cell_fill = PatternFill(start_color="E0E0E0", end_color="E0E0E0", fill_type="solid")
    alignment = Alignment(wrap_text=True, horizontal="center", vertical="center")  # Center alignment
    day_alignment = Alignment(textRotation=90, horizontal="center", vertical="center")  # Center alignment
    border = Border(
        left=Side(style="thin"),
        right=Side(style="thin"),
        top=Side(style="thin"),
        bottom=Side(style="thin"),
    )

    wb = openpyxl.Workbook()
    ws = wb.active

    def add_header(ws, row, col):
        cell = ws.cell(row=1+row, column=1+col, value=f"Day")
        cell.fill = header_fill
        cell.alignment = alignment
        cell.border = border

        cell = ws.cell(row=1+row, column=1+col+1, value=f"Time")
        cell.fill = header_fill
        cell.alignment = alignment
        cell.border = border

        col += 2

        for year in tableized_week["cols"]:
            years_columns_num = len(tableized_week["cols"][year])
            
            cell = ws.cell(row=1+row, column=1+col, value=f"Year {year}")
            cell.fill = header_fill
            cell.alignment = alignment
            cell.border = border

            ws.merge_cells(
                start_row=1+row,
                start_column=1+col,
                end_row=1+row,
                end_column=1+col+years_columns_num -1
            )

            col += years_columns_num

    global_row_pointer = 0
    global_table_row_pointer = 0
    global_col_pointer = 0


    for day in tableized_week["rows"]:
        add_header(ws, global_row_pointer, global_col_pointer)
        global_row_pointer += 1

        cell = ws.cell(row=1+global_row_pointer, column=1+global_col_pointer, value=day)
        # cell.fill = cell_fill
        cell.alignment = day_alignment
        cell.border = border

        ws.merge_cells(
            start_row=1+global_row_pointer,
            start_column=1+global_col_pointer,
            end_row=1+global_row_pointer+len(tableized_week["rows"][day]) -1,
            end_column=1+global_col_pointer
        )

        local_row_pointer = global_row_pointer
        for hour in tableized_week["rows"][day]:
            cell = ws.cell(row=1+local_row_pointer, column=1+global_col_pointer+1, value=f"{hour}:00 ~ {hour}:50")
            # cell.fill = cell_fill
            cell.alignment = alignment
            cell.border = border
            local_row_pointer += 1
        
        hours_num = len(tableized_week["rows"][day])

        local_col_pointer = global_col_pointer
        for year in tableized_week["cols"]:
            # to_skip = 0
            for col in tableized_week["cols"][year]:
                local_row_pointer = global_row_pointer
                for lec in col[global_table_row_pointer : global_table_row_pointer + hours_num]:
                    local_row_pointer += 1


                    # if to_skip > 0:
                    #     to_skip -= 1
                    #     continue

                    if lec is None:
                        continue

                    if lec == {}:
                        continue

                    to_skip = lec["count"] -1
                    
                    cell = ws.cell(
                        row=local_row_pointer,
                        column=1+local_col_pointer+2,
                        value=lec["name"] + "\n" + lec["professor"]["name"] + "\n" + lec["lectureHall"]["name"]
                        # value=lec["name"] + "\n" + lec["professorName"]
                    )
                    cell.fill = cell_fill
                    cell.alignment = alignment
                    cell.border = border
                    ws.merge_cells(
                        start_row=local_row_pointer,
                        start_column=1+local_col_pointer+2,
                        end_row=local_row_pointer+to_skip,
                        end_column=1+local_col_pointer+2
                    )

                    # local_row_pointer += to_skip
                
                local_col_pointer += 1
        
        global_row_pointer += hours_num
        global_table_row_pointer += hours_num

    rows_num, cols_num = get_max_dimentions(tableized_week)

    for i in range(rows_num):
        cell = ws.cell(row=1+i, column=cols_num)
        b = cell.border
        cell.border = Border(left=b.left, top=b.top, right=Side(style="thin"), bottom=b.bottom)

    for i in range(cols_num):
        cell = ws.cell(row=rows_num, column=1+i)
        b = cell.border
        cell.border = Border(left=b.left, top=b.top, right=b.right, bottom=Side(style="thin"))

    auto_adjust_column_width(ws)
    # auto_adjust_row_height(ws)

    # wb.save("merged_cells.xlsx")
    return wb

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


def iterate_over_keys_and_values_recursively(json_data, keys=[]):
    result = []

    for k, v in json_data.items():
        if isinstance(v, dict):
            result.extend(iterate_over_keys_and_values_recursively(v, keys.copy() + [k]))
        else:
            result.append((keys.copy() + [k], v))

    return result

def tableize_json(
    unflatten_json_data, col_keys: list[str] = [],
    row_keys: list[str] = [],
    combine_condition = lambda x, y: False # x == y
):
    if not len(col_keys) and not len(row_keys):
        return json_data

    cols = unflatten_json(unflatten_json_data, col_keys)
    rows = unflatten_json(unflatten_json_data, row_keys)
        
    table_data = {
        "col_labels": col_keys,
        "row_labels": row_keys,
        "col_leaf_count": calc_leaf_num_for_all_keys(cols),
        "row_leaf_count": calc_leaf_num_for_all_keys(rows),
        "cols": cols,
        "rows": rows,
        "data": []
    }

    for y, (row_ks, row_v) in enumerate(list(iterate_over_keys_and_values_recursively(rows))):
        table_data["data"].append([])
        for x, (col_ks, col_v) in enumerate(list(iterate_over_keys_and_values_recursively(cols))):
            table_data["data"][y].append([])

            for r_v in row_v:
                for c_v in col_v:
                    if c_v == r_v:
                        table_data["data"][y][x].append(r_v)

    def complete_condition(x, y):
        return x != [] and y != [] and x != None and y != None and combine_condition(x, y)

    for y, row in enumerate(table_data["data"]):
        for x, col in enumerate(row):
            if col is None:
                continue

            i = 0
            while y+i+1 < len(table_data["data"]) and complete_condition(table_data["data"][y+i+1][x], col):
                i += 1
            
            for j in range(i):
                table_data["data"][y+j+1][x] = None
            
            w = None
            for j in range(i+1):
                w_ = 0
                while x+w_+1 < len(table_data["data"][y+j]) and complete_condition(table_data["data"][y+j][x+w_+1], col):
                    w_ += 1
                
                w = w_ if w is None else min(w, w_)
            
            for k in range(w):
                table_data["data"][y][x+k+1] = None


    return table_data

def calc_leaf_num_for_all_keys(json_data):
    json_data_temp = {
        "leaf_count": 0
    }

    for col_ks, col_v in iterate_over_keys_and_values_recursively(json_data):
        d = json_data_temp

        d["leaf_count"] += 1
        
        for k in list(col_ks): # .values()
            if k not in d:
                d[k] = {
                    "leaf_count": 1
                }
            else:
                d[k]["leaf_count"] += 1
            d = d[k]
    
    return json_data_temp

def tableized_json_to_html_table(
    tableize_json_data,
    cell_filling_function=lambda i, value: f"<td>{value}</td>",
    cols_filling_function=lambda i, value, span: f"<th colspan={span}>{value}</th>",
    rows_filling_function=lambda i, value, span: f"<th rowspan={span}>{value}</th>",
    foot_filling_function=None,
):
    cols = []
    cols_html = []

    # cols_leaf_counts = calc_leaf_num_for_all_keys(tableize_json_data["cols"])

    # for col_ks, col_v in iterate_over_keys_and_values_recursively(tableize_json_data["cols"]):
    for col_ks, col_v in iterate_over_keys_and_values_recursively(tableize_json_data["cols"]):
        # d = cols_leaf_counts
        d = tableize_json_data["col_leaf_count"]
        for index, col_k in enumerate(col_ks):
            d = d[col_k]
            # while len(cols) < index+1:
            if len(cols) < index+1:
                cols.append(None)
                cols_html.append([])
                
            if cols[index] is None or cols[index] != col_k:
                cols[index] = col_k
                for i in range(index+1, len(cols)):
                    cols[i] = None
                # cols_html[index].append(f"<th colspan={d['leaf_count']}>{col_k}</th>")
                cols_html[index].append(cols_filling_function(index, col_k, d['leaf_count']))


    rows = []
    rows_html = [""]

    # rows_leaf_counts = calc_leaf_num_for_all_keys(tableize_json_data["rows"])

    for i, (row_ks, row_v) in enumerate(
        iterate_over_keys_and_values_recursively(tableize_json_data["rows"])
    ):
        # d = rows_leaf_counts
        d = tableize_json_data["row_leaf_count"]

        for index, row_k in enumerate(row_ks):
            d = d[row_k]
            # while len(rows) < index+1:
            if len(rows) < index+1:
                rows.append(None)
                
            if rows[index] is None or rows[index] != row_k:
                rows[index] = row_k
                for j in range(index+1, len(rows)):
                    rows[j] = None
                # rows_html[-1] += f"<th rowspan={d['leaf_count']}>{row_k}</th>"
                rows_html[-1] += rows_filling_function(i, row_k, d['leaf_count'])
        
        for c, cell in enumerate(tableize_json_data["data"][i]):
            if cell is None:
                continue

            # rows_html[-1] += f"<td>{cell}</td>"
            rows_html[-1] += cell_filling_function(i, cell)

        rows_html.append("")


    html_string = "<table>"
    
    row_cols = "".join(
        f"<th rowspan={len(tableize_json_data['col_labels'])}>{label}</th>"
        for label in tableize_json_data["row_labels"]
    )
    html_string += "<thead>" + "".join(map(
        lambda i, x: "<tr>" + (row_cols if i == 0 else "") + "".join(x) + "</tr>",
        range(len(cols_html)), cols_html
    )) + "</thead>"

    html_string += "<tr>" + "</tr><tr>".join(rows_html) + "</tr>"

    if foot_filling_function is not None:
        foot_content = "<tfoot><tr>"

        for d in range(tableize_json_data["col_leaf_count"]["leaf_count"]):
            foot_content += foot_filling_function(d)
        
        foot_content += "</tr></tfoot>"

        print(foot_content)

        html_string += foot_content

#     foot_content = """<tfoot>
#     <tr>
#         <td>
#             <button onclick="saveFreeTime()">Save</button>
#         </td>""" + "".join(
#         f"""<td>
#     <button onclick="eraseDay({d+1})">Erase</button>
#     <button onclick="toggleDay({d+1})">Toggle</button>
# </td>"""
#         for d in range(tableize_json_data["col_leaf_count"]["leaf_count"])
#     ) + """</tr>
# </tfoot>"""

    html_string += "</table>"

    return html_string

def build_time_table_html_content(times_list):
    unflattened_times_list = unflatten_json(times_list, ["day", "hour"])

    tableize_json_data = tableize_json(
        # times_list, ["day", "hour"], ["day", "hour"],
        times_list, ["day"], ["hour"],
        # lambda x, y: x[0]["hour"] == y[0]["hour"]
        # lambda x, y: x[0]["day"] == y[0]["day"]
    )

    tableize_json_data["row_labels"] = ["Time"]
    # tableize_json_data["row_leaf_count"] = {
    #     f"{k}:00 ~ {k}:50": v
    #     for k, v in tableize_json_data["row_leaf_count"].items()
    # }
    # tableize_json_data["rows"] = {
    #     f"{k}:00 ~ {k}:50": v
    #     for k, v in tableize_json_data["rows"].items()
    # }

    html_string = tableized_json_to_html_table(
        tableize_json_data,
        cell_filling_function=lambda i, value: f"<td{" class='selected'" * (len(value) == 1)}></td>",
        # cols_filling_function=lambda i, value, span: f"<th colspan={span}>{value}</th>",
        rows_filling_function=lambda i, value, span: f"<td rowspan={span}>{value}:00 ~ {value}:50</td>",
        foot_filling_function=lambda i: f"""<td>""" + ("""<button onclick="saveFreeTime()">Save</button></td><td>""" if i == 0 else "") + """
    <button onclick="eraseDay({i+1})">Erase</button>
    <button onclick="toggleDay({i+1})">Toggle</button>
</td>""",
    )

    style = """<style>
table {
    border-collapse: collapse;
}
td, th {
    border: 1px solid black;
    padding: 5px;
    text-align: center;
    vertical-align: middle;
}
tr th {
    background-color: aqua;
}
button {
    margin: 2px;
}
.selected {
    background-color: green;
}</style>"""

    return style + html_string

# split
# is col/row empty
# multiple values in cell?

#     return style + unflatten_json_to_html_table(
#         unflattened_times_list,
#         is_cols=False,
#         # row_keys = ["day"],
#         # col_keys = ["hour"],
#         cell_func = lambda x: '<td class="selected" onclick="this.classList.toggle("selected");"></td>'
#     )

    days = [
        "Monday",
        "Tuesday",
        "Wednesday",
        "Thursday",
        "Friday",
    ]

    hours = [
        8, 9, 10, 11, 13, 14, 15, 16, 17
    ]

    table_content = style + "<table id='schedule-table'>"

    header_content = """<thead>
<tr>
    <th>Time</th>""" + "".join(f"""
    <th value="{day}">{day}</th>
    """
    for day in days
) + """
</tr>
</thead>"""

    body_content = """<tbody>""" + "".join(
"<tr>" + f"""<td value="{hour}">{hour}:00 ~ {hour}:50</td>""" + "".join(
        f"""<td class="{(hour in unflattened_times_list[day]) * "selected"}" onclick="this.classList.toggle('selected');"></td>"""
        for day in days
    ) + "</tr>"
    for hour in hours
) + """
</tbody>"""
        # if hour == 12
        #         <td class="break"></td>
        #     else
        # f"""<td class="{is_in_list(day, hour) * "selected"}" onclick="this.classList.toggle('selected');"></td>"""
    
    foot_content = """<tfoot>
    <tr>
        <td>
            <button onclick="saveFreeTime()">Save</button>
        </td>""" + "".join(
        f"""<td>
    <button onclick="eraseDay({d+1})">Erase</button>
    <button onclick="toggleDay({d+1})">Toggle</button>
</td>"""
        for d in range(len(days))
    ) + """</tr>
</tfoot>"""

    table_content += header_content + body_content + foot_content

    table_content += "</table>"

    return table_content