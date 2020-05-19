import pymongo
import time
from pymongo import errors
from django.http import JsonResponse, HttpResponse
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required, group_required
from django.views.decorators.csrf import csrf_exempt
from django.contrib import messages
from datetime import datetime
from bson.objectid import ObjectId

from nurseApp.forms import *
# parameter for custom message
DANGER = 50

# db conexion
clientMongo = pymongo.MongoClient("mongodb+srv://Challenger:sfchallenge123@clusterdepruebas-anz0g.mongodb.net/test?retryWrites=true&w=majority")
db = clientMongo['SF_Challenge']
col_patients = db['nurseApp_patient']
col_records = db['nurseApp_record']
col_base_stats = db['nurseApp_base_stats']


def get_priority_level(systolic, diastolic):
    priority = {'category': 0} # initial category level
    # query all base stats for Blood pressure
    query_base_stats = col_base_stats.find({'parameter': 'bp'},
                                           {'parameter': 0,
                                            'parameter_text': 0,
                                            '_id': 0})
    # for every record found the 2 parameters passed to the function are compared
    for record in query_base_stats:
        if record['category'] == 0 or record['category'] == 1:
            if record['systolic']['min'] <= systolic <= record['systolic']['max'] \
                and record['diastolic']['min'] <= diastolic <= record['diastolic']['max']:

                priority = record
        else:
            if record['systolic']['min'] <= systolic <= record['systolic']['max'] \
                or record['diastolic']['min'] <= diastolic <= record['diastolic']['max']:

                priority = record
    # this parameters are not necessary
    priority.pop('systolic')
    priority.pop('diastolic')

    return priority


def get_patients_datatable(request):
    data=[]

    query_patients = col_patients.find()

    for patient in query_patients:
         # query the last record saved - None if no record found
        last_record = col_records.find_one({'id_patient': ObjectId(patient['_id'])}, sort=[('ts', pymongo.DESCENDING)], limit=1)
        # if the patient's status is active, the tasks button must be prepare
        if patient['status'] == 'active':
            if last_record is not None:
                priority = "<i class=\"fas fa-exclamation-circle fa-2x\" " \
                           "data-tooltip=\"tooltip\" " \
                           "data-placement=\"top\" " \
                           "title=\"" + last_record['bp_info']['category_text']+ "\"" \
                           "style=\"color:" + last_record['bp_info']['category_color']+ "\"></i>" \
                           "<span hidden>" + str(last_record['bp_info']['category']) + "</span>"
                ts = str(datetime.strftime(last_record['ts'], '%d/%m/%Y - %H:%M'))
                bp = str(last_record['bp_systolic']) + '/'+ str(last_record['bp_diastolic'])
                hr = str(last_record['heart_rate']) + ' (bpm)'
            else:
                priority = "<i class=\"fas fa-question-circle fa-2x text-dark\"" \
                           "data-tooltip=\"tooltip\" " \
                           "data-placement=\"top\" " \
                           "title=\"No record found\"></i>" \
                           "<span hidden> 5 no record found</span>"
                ts = bp = hr = ' - '

            btn_view_data = "<a href=\"../history/" + str(patient['_id']) + "/\"" \
                                      " data-tooltip=\"tooltip\" " \
                                      " data-placement=\"top\" " \
                                      " title=\"View Historical data\">" \
                                      " <i class=\"fas fa-notes-medical fa-2x text-dark\"></i></a>"
            btn_add_signals = "<a href=\"#\" data-patient_id=\"" + str(patient['_id']) + "\"" \
                                           " data-patient_custom_id=\"" + str(patient['custom_id']) + "\"" \
                                           " data-patient_name=\"" + str(patient['name']) + "\"" \
                                           " data-tasks = \"addVitalSings\"" \
                                           " data-toggle=\"modal\"" \
                                           " data-target=\"#modalAddVitalSigns\"" \
                                           " data-tooltip=\"tooltip\" " \
                                           " data-placement=\"top\" " \
                                           " title=\"Add vital signs\"" \
                                           " id=\"btnModalAddVitalSigns\"><i class=\"fas fa-file-medical-alt fa-2x text-dark\"></i></a>"
            btn_edit_data = "<a href=\"../patient/" + str(patient['_id']) + "/\"" \
                                          " data-tooltip=\"tooltip\" " \
                                          " data-placement=\"top\" " \
                                          " title=\"Edit profile\"><i class=\"fas fa-user-edit fa-2x text-dark\"></i></a>"
            btn_patient_delete = "<a href=\"#\" data-patient_id=\"" + str(patient['_id']) + "\"" \
                                              " data-patient_custom_id=\"" + str(patient['custom_id']) + "\"" \
                                              " data-patient_name=\"" + str(patient['name']) + "\"" \
                                              " data-toggle=\"modal\"" \
                                              " data-target=\"#modalDeleteProfile\"" \
                                              " data-tooltip=\"tooltip\" " \
                                              " data-placement=\"top\" " \
                                              " title=\"Delete profile\"" \
                                              " id=\"btnModalDeleteProfile\"><i class=\"fas fa-user-times fa-2x text-dark\"></i></a>"
            btn_patient_status = "<a href=\"#\" data-tooltip=\"tooltip\"" \
                                              " data-placement=\"top\" " \
                                              " title=\"Change status\"" \
                                              " data-patient_id=\"" + str(patient['_id']) + "\"" \
                                              " data-patient_custom_id=\"" + str(patient['custom_id']) + "\"" \
                                              " data-patient_name=\"" + str(patient['name']) + "\"" \
                                              " data-patient_status=\"" + str(patient['status']) + "\"" \
                                              " data-toggle=\"modal\"" \
                                              " data-target=\"#modalChangeStatus\"" \
                                              " id=\"btnModalChangeStatus\"><i class=\"fas fa-toggle-on fa-2x text-dark\"></i></a>"
        else:
            priority = "<i class=\"fas fa-user-slash fa-2x text-muted\"" \
                       "data-tooltip=\"tooltip\" " \
                       "data-placement=\"top\" " \
                       "title=\"Patient's profile currently inactivated\"></i>" \
                       "<span hidden> 100 inactive </span>"

            btn_view_data = "<i class=\"fas fa-notes-medical fa-2x text-muted\"></i>"
            btn_add_signals = "<i class=\"fas fa-file-medical-alt fa-2x text-muted\"></i>"
            btn_edit_data = "<i class=\"fas fa-user-edit fa-2x text-muted\"></i>"
            btn_patient_delete = "<i class=\"fas fa-user-times fa-2x text-muted\"></i>"
            btn_patient_status = "<a href=\"#\" data-tooltip=\"tooltip\"" \
                                              " data-placement=\"top\" " \
                                              " title=\"Change status\"" \
                                              " data-patient_id=\"" + str(patient['_id']) + "\"" \
                                              " data-patient_custom_id=\"" + str(patient['custom_id']) + "\"" \
                                              " data-patient_name=\"" + str(patient['name']) + "\"" \
                                              " data-patient_status=\"" + str(patient['status']) + "\"" \
                                              " data-toggle=\"modal\"" \
                                              " data-target=\"#modalChangeStatus\"" \
                                              " id=\"btnModalChangeStatus\"><i class=\"fas fa-toggle-off fa-2x text-dark\"></i></a>"
            ts = str(datetime.strftime(last_record['ts'], '%d/%m/%Y - %H:%M'))
            bp = str(last_record['bp_systolic']) + '/'+ str(last_record['bp_diastolic'])
            hr = str(last_record['heart_rate']) + ' (bpm)'

        data.append({
            "DT_RowId": str(patient['_id']),
            "priority": priority,
            "name": patient['name'],
            "age": patient['age'],
            "custom_id": patient['custom_id'],
            "date": ts,
            "blood_pressure": bp,
            "heart_rate": hr,
            "tasks": btn_add_signals + btn_view_data + btn_edit_data + btn_patient_delete,
            "status": btn_patient_status
        })

    return JsonResponse({'data': data})

@csrf_exempt
def get_patient_historical_data(request):
    table_data = []
    bp_sys = []
    bp_dias = []
    hr = []

    query_records = col_records.find({'id_patient': ObjectId(request.POST['patient_id'])})

    if request.is_ajax():
        if request.POST['petitioner'] == 'graphs':
            for record in query_records:
                ts_point = int(str(int(time.mktime(record['ts'].timetuple()))) + '000')
                bp_sys.append([ts_point, int(record['bp_systolic'])])
                bp_dias.append([ts_point, int(record['bp_diastolic'])])
                hr.append([ts_point, int(record['heart_rate'])])

            graph_data = {'bp_sys': bp_sys,
                          'bp_dias': bp_dias,
                          'hr': hr}
            return JsonResponse(graph_data)

        elif request.POST['petitioner'] == 'table':
            for record in query_records:
                ts = str(datetime.strftime(record['ts'], '%d/%m/%Y - %H:%M'))
                btn_record_delete = "<a href=\"#\" data-record_id=\"" + str(record['_id']) + "\"" \
                                                 " data-record_date=\"" + ts + "\"" \
                                                 " data-tasks = \"deleteVitalSings\"" \
                                                 " data-toggle=\"modal\"" \
                                                 " data-target=\"#modalDeleteVitalSignsRecord\"" \
                                                 " data-tooltip=\"tooltip\" " \
                                                 " data-placement=\"top\" " \
                                                 " title=\"Delete Record\"" \
                                                 " id=\"btnModalDeleteVitalSignsRecord\"><i class=\"fas fa-trash-alt text-dark\"></i></a>"
                btn_record_edit = "<a href=\"#\"   data-record_id=\"" + str(record['_id']) + "\"" \
                                                 " data-record_date=\"" + ts + "\"" \
                                                 " data-tasks = \"editVitalSings\"" \
                                                 " data-toggle=\"modal\"" \
                                                 " data-target=\"#modalEditVitalSigns\"" \
                                                 " data-tooltip=\"tooltip\" " \
                                                 " data-placement=\"top\" " \
                                                 " title=\"Edit Record\"" \
                                                 " id=\"btnEditVitalSigns\"><i class=\"fas fa-edit text-dark\"></i></a>"

                if request.user.is_authenticated:
                    table_data.append({
                        "DT_RowId": str(record['_id']),
                        "date": datetime.strftime(record['ts'], '%d/%m/%Y - %H:%M:%S'),
                        "bp": str(record['bp_systolic']) + '/' + str(record['bp_diastolic']),
                        "bp_category": "<span style=\"color: "
                                           + str(record['bp_info']['category_color']) + "\"><b>"
                                           + str(record['bp_info']['category_text']) + "</b></span>",
                        "hr": str(record['heart_rate']) + ' (bpm)',
                        "hr_info": str(record['hr_info']),
                        "tasks": btn_record_edit + btn_record_delete
                    })
                else:
                    table_data.append({
                        "DT_RowId": str(record['_id']),
                        "date": datetime.strftime(record['ts'], '%d/%m/%Y - %H:%M:%S'),
                        "bp": str(record['bp_systolic']) + '/' + str(record['bp_diastolic']),
                        "bp_category": "<span style=\"color: "
                                           + str(record['bp_info']['category_color']) + "\"><b>"
                                           + str(record['bp_info']['category_text']) + "</b></span>",
                        "hr": str(record['heart_rate']) + ' (bpm)',
                        "hr_info": str(record['hr_info'])
                    })

            return JsonResponse({'data': table_data})

@csrf_exempt
def add_vital_signs(request):

    if int(request.POST.get('heart_rate')) <= 60:
        hr_info = 'Low (must be more than 60 bpm)'
    elif int(request.POST.get('heart_rate')) > 130:
        hr_info = 'High (must be less than 130 bpm)'
    else:
        hr_info = 'Normal'

    if request.method == 'POST':
        if request.POST.get('task') == 'addVitalSign':
            record = {
                'id_responsible': int(request.user.id),
                'id_patient': ObjectId(request.POST.get('patient_id')),
                'bp_systolic': int(request.POST.get('bp_systolic')),
                'bp_diastolic': int(request.POST.get('bp_diastolic')),
                'bp_info': get_priority_level(int(request.POST.get('bp_systolic')), int(request.POST.get('bp_diastolic'))),
                'heart_rate': int(request.POST.get('heart_rate')),
                'hr_info': hr_info,
                'ts': datetime.now()
            }

            try:
                col_records.insert_one(record)
                message = {'text': 'The data have been successfully saved',
                           'type': 'success'}

            except pymongo.errors.OperationFailure as err:
                message = {'text': 'There was an error with MongoDB! Error #{0}'.format(err),
                           'type': 'danger'}

            return HttpResponse(
                JsonResponse(message),
                content_type="application/json"
            )
        elif request.POST.get('task') == 'editVitalSign':
            record = {
                'bp_systolic': int(request.POST.get('bp_systolic')),
                'bp_diastolic': int(request.POST.get('bp_diastolic')),
                'bp_info': get_priority_level(int(request.POST.get('bp_systolic')), int(request.POST.get('bp_diastolic'))),
                'heart_rate': int(request.POST.get('heart_rate')),
                'hr_info': hr_info
            }

            try:
                col_records.update_one({'_id': ObjectId(request.POST.get('record_id'))}, {'$set': record})
                message = {'text': 'The data have been successfully updated',
                           'type': 'success'}

            except pymongo.errors.OperationFailure as err:
                message = {'text': 'There was an error with MongoDB! Error #{0}'.format(err),
                           'type': 'danger'}

            return HttpResponse(
                JsonResponse(message),
                content_type="application/json"
            )

    else:
        return HttpResponse(
            JsonResponse({"nothing to see": "this isn't happening"}),
            content_type="application/json"
        )

@csrf_exempt
def change_patient_status(request):
    if request.method == 'POST':
        patient_id = ObjectId(request.POST.get('patient_id'))
        patient_current_status = col_patients.find_one({'_id': ObjectId(patient_id)},
                                                       {'status': 1})

        if patient_current_status['status'] == 'active':
            patient_new_status = 'inactive'
        else:
            patient_new_status = 'active'

        try:
            col_patients.update_one({'_id': ObjectId(patient_id)},
                                    {'$set': {'status': patient_new_status}})
            message = {'text': 'The status of the patient has been updated.',
                       'type': 'success'}

        except pymongo.errors.OperationFailure as err:
            message = {'text': 'There was an error with MongoDB! Error #{0}'.format(err),
                       'type': 'danger'}

        return HttpResponse(
            JsonResponse(message),
            content_type="application/json"
        )

    else:
        return HttpResponse(
            JsonResponse({"nothing to see": "this isn't happening"}),
            content_type="application/json"
        )

@csrf_exempt
def delete_patient_profile(request):
    if request.method == 'POST':
        patient_id = ObjectId(request.POST.get('patient_id'))

        try:
            col_patients.delete_one({'_id': patient_id})
            col_records.delete_many({'id_patient': patient_id})
            message = {'text': 'All Patient\'s data has been deleted.' ,
                       'type': 'success'}

        except pymongo.errors.OperationFailure as err:
            message = {'text': 'There was an error with MongoDB! Error #{0}'.format(err),
                       'type': 'danger'}

        return HttpResponse(
            JsonResponse(message),
            content_type="application/json"
        )

    else:
        return HttpResponse(
            JsonResponse({"nothing to see": "this isn't happening"}),
            content_type="application/json"
        )

@csrf_exempt
def delete_vital_signs_record(request):
    if request.method == 'POST':
        record_id = ObjectId(request.POST.get('record_id'))

        try:
            col_records.delete_many({'_id': record_id})
            message = {'text': 'The record has been deleted.' ,
                       'type': 'success'}

        except pymongo.errors.OperationFailure as err:
            message = {'text': 'There was an error with MongoDB! Error #{0}'.format(err),
                       'type': 'danger'}

        return HttpResponse(
            JsonResponse(message),
            content_type="application/json"
        )

    else:
        return HttpResponse(
            JsonResponse({"nothing to see": "this isn't happening"}),
            content_type="application/json"
        )

#============================== TEMPLATE VIEWS ====================================
@login_required
@group_required('Nurses')
def index(request):

    return render(request,
                  'nurseApp/index.html',
                  context={})

@login_required
@group_required('Nurses')
def add_patient(request):

    if request.method == 'POST':
        form = PatientForm(request.POST)
        if form.is_valid():
            # in case the name and last name starts with single cases
            form.cleaned_data['name'] = str(form.cleaned_data['name']).title()
            # at the star the patient is flagged as active into the system
            form.cleaned_data['status'] = 'active'

            try:
                col_patients.insert_one(form.cleaned_data)
                messages.success(request, str(form.cleaned_data.get('name')) + ' has been added as a Patient')

            except pymongo.errors.OperationFailure as err:
                # manual check for the custom_id to be unique.
                # if it is not unique, return the form and the message
                if err.code == 11000:
                    messages.warning(request, 'ID: The ID is already in use.')

                    return render(request,
                          'nurseApp/add_patient.html',
                          context={'form': form})

                else:
                    messages.add_message(request, DANGER,
                                         'There was an error with MongoDB! Error #{0}'.format(err), extra_tags='danger')

            return redirect(add_patient)

        else:
            messages.warning(request, 'There was an Error. Please check the fields below.')

            return render(request,
                          'nurseApp/add_patient.html',
                          context={'form': form})
    else:
        form = PatientForm()

    return render(request,
                  'nurseApp/add_patient.html',
                  context={'form': form})

@login_required
@group_required('Nurses')
def edit_patient_profile(request, patient_id):
    responsable = request.user.username

    if request.method == 'POST':
        form = PatientForm(request.POST)

        if form.has_changed():
            if form.is_valid():
                try:
                    col_patients.update_one({'_id': ObjectId(patient_id)}, {'$set': form.cleaned_data})

                    messages.success(request, 'The profile has been successfully modified.')

                except pymongo.errors.OperationFailure as err:
                    # manual check for the custom_id to be unique.
                    # if it is not unique, return the form and the message
                    if err.code == 11000:
                        messages.warning(request, 'ID: The ID is already in use.')

                        return render(request,
                              'nurseApp/add_patient.html',
                              context={'form': form})

                    else:
                        messages.add_message(request, DANGER,
                                             'There was an error with MongoDB! Error #{0}'.format(err), extra_tags='danger')

            else:
                messages.warning(request, 'There was an Error. Please check the fields below.')

                return render(request,
                          'nurseApp/edit_patient_profile.html',
                          context={'form': form})

        query = col_patients.find_one({'_id': ObjectId(patient_id)}, {'_id': 0})
        form = PatientForm(query)

        return render(request,
                  'nurseApp/edit_patient_profile.html',
                  context={'form': form,
                           'patient_name': query['name']})

    else:
        query = col_patients.find_one({'_id': ObjectId(patient_id)}, {'_id': 0})
        form = PatientForm(initial=query)

        return render(request,
                      'nurseApp/edit_patient_profile.html',
                      context={'form': form,
                               'patient_name': query['name']})

@login_required
@group_required('Nurses')
def view_patients(request):

    form = RecordForm()

    return render(request,
                  'nurseApp/view_patients.html',
                  context={'form_records': form})

@csrf_exempt
def view_historical_data(request, patient_id):
    # verification of the patient_id, if is not valid, its a patient's custom_id
    if ObjectId().is_valid(patient_id):

        query_patient = col_patients.find_one({'_id': ObjectId(patient_id)}, {'name': 1, 'custom_id': 1, '_id': 1})
        form = RecordForm()

        return render(request,
                      'nurseApp/view_historical_data.html',
                      context={'patient': query_patient['name'],
                               'patient_id': query_patient['_id'],
                               'patient_custom_id': query_patient['custom_id'],
                               'form_records': form,
                               'notFound': False})
    else:
        query_patient = col_patients.find_one({'custom_id': patient_id}, {'name': 1, 'custom_id': 1, '_id': 1})

        if query_patient is not None:
            return render(request,
                          'nurseApp/view_historical_data.html',
                          context={'patient': query_patient['name'],
                                   'patient_id': query_patient['_id'],
                                   'patient_custom_id': query_patient['custom_id'],
                                   'notFound': False})
        else:
            return render(request,
                          'nurseApp/view_historical_data.html',
                          context={'custom_id': patient_id,
                                   'notFound': True})

