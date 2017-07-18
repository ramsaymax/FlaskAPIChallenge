#!flask/bin/python
from flask import Flask, jsonify, make_response, abort
from database import employee_data
from itertools import *

app = Flask(__name__)

#404 Endpoint
@app.errorhandler(404)
def not_found(error):
    return make_response(jsonify({'error': 'Not found'}), 404)

#Head Count Over Time Endpoint
@app.route('/headcount_over_time', methods=['GET'])
def headcount():
    unique_dates = sorted(list(set([item['date'].split('-')[0]+ "-" +item['date'].split('-')[1] for item in employee_data])))
    new_employees_month = dict()
    seen_employees = dict()
    previous_month_headcount = 0
    for date in unique_dates:
        new_employees_month[date] = previous_month_headcount
        for position in employee_data:
            if date in position['date'] and position['employee'] not in seen_employees:
                new_employees_month[date] += 1
                seen_employees[position['employee']] = True
        previous_month_headcount = new_employees_month[date]
    data_for_api = []
    for key in sorted(new_employees_month):
        apiDict = { "month": key , "headcount" : new_employees_month[key] }
        data_for_api.append(apiDict)
        apiDict = {}
    return jsonify({'data': sorted(data_for_api)})

@app.route('/headcount_over_time/<string:department>', methods=['GET'])
def headcount_dpt(department):
    department = department[0].upper() + department[1:]
    if department not in list(set([x['dept'] for x in employee_data])):
        abort(404)
    unique_dates = sorted(list(set([item['date'].split('-')[0]+ "-" +item['date'].split('-')[1] for item in employee_data])))
    new_employees_month = dict()
    seen_employees = dict()
    data_for_api = []
    previous_month_headcount = 0
    for date in unique_dates:
        new_employees_month[date] = previous_month_headcount
        for position in employee_data:
            if date in position['date'] and position['employee'] not in seen_employees and position['dept'] == department:
                new_employees_month[date] += 1
                seen_employees[position['employee']] = True
        previous_month_headcount = new_employees_month[date]
    for key in sorted(new_employees_month):
        apiDict = {"month":key,"headcount":new_employees_month[key]}
        data_for_api.append(apiDict)
        apiDict = {}
    return jsonify({'data': sorted(data_for_api)})

#AVERAGES END POINT
@app.route('/averages', methods=['GET'])
def get_department_averages():
    unique_ids = list(set([employee_item['employee'] for employee_item in employee_data]))
    individual_employee_positions = {}
    for employee_id in unique_ids:
        individual_employee_positions[employee_id] = []
        for employee_object in employee_data:
            if employee_object['employee'] == employee_id:
                individual_employee_positions[employee_id].append(employee_object)
    current_emp_positions = list()
    for employee_id , array_of_jobs in individual_employee_positions.iteritems():
        if len(array_of_jobs)>1:
            multiple_dates_array = [x['date'] for x in array_of_jobs]
            highest_date = max(multiple_dates_array)
            most_recent_position = [item for item in array_of_jobs if item['date'] == highest_date][0]
            current_emp_positions.append(most_recent_position)
        else:
            if array_of_jobs:
                current_emp_positions.append(array_of_jobs[0])
    department_list = list(set([employee_item['dept'] for employee_item in current_emp_positions]))
    api_data = dict()
    for department in department_list:
        averages = [x['salary'] for x in current_emp_positions if x['dept'] == department]
        api_data[department] = int(sum(averages) / float(len(averages)))

    return jsonify({'averages': api_data})

if __name__ == '__main__':
    app.run(debug=True)
