#!/bin/python3

from datetime import datetime
from datetime import timedelta

import sys

def read(path):
    f = open(path, "r");
    f.seek(0);
    lines = f.readlines();
    f.close();
    return lines;

def minutes_to_h_m(m):
    h = m // 60;
    m = m % 60
    
    if h < 10:
        h = '0'+str(h);
    if m < 10:
        m = '0'+str(m);

    return str(h)+"h"+str(m);

# return True if the date_str (11/11/2023) is in the current period (day, week, month, year, all)
# else return false

def is_in_current_period(date_str, period):
   
    current_date = datetime.now().date()
    
    date_format = "%d/%m/%Y"
    date_to_check = datetime.strptime(date_str, date_format).date()
    
    if (period == "day"):
        current_date = datetime.today().date()
        date_format = "%d/%m/%Y"
        target_date = datetime.strptime(date_str, date_format).date()
        return current_date == target_date;
    elif (period == "week"):
        start_of_week = current_date - timedelta(days=current_date.weekday())
        end_of_week = start_of_week + timedelta(days=6)

        return start_of_week <= date_to_check <= end_of_week
    elif (period == "month"):

        start_of_month = current_date.replace(day=1)
        next_month = current_date.replace(month=current_date.month + 1, day=1)
        end_of_month = next_month - timedelta(days=1)

        return start_of_month <= date_to_check <= end_of_month
    elif (period == "year"):
        start_of_year = current_date.replace(month=1, day=1)
        end_of_year = current_date.replace(month=12, day=31)
        
        return start_of_year <= date_to_check <= end_of_year;
    elif (period == "all"):
        return True;
    else:
        print("[ERROR] is_in_current_period: period not allowd: "+period)
    
def parse_date(line):
    #clean
    line = line.split("**")[1];
    line = line.split("**")[0];

    #parse data
    data = line.split("/");
    day = data[0];
    month = data[1];
    year = data[2];

    return {'day': day, 'month': month, 'year': year};

def parse_time(line):
    #clean
    line = line.split("*")[1];
    line = line.split("*")[0];
    #parse data
    data1 = line.split(" - ")[0];
    if len(line.split(" - ")) == 1: #one hour case -> cancel
        data2 = line;
    else:
        data2 = line.split(" - ")[1];

    if "?" in data2: #? not finished hours -> cancel 
        data2 = data1;

    time_start = {};
    time_end = {};

    if "h" in data1:
        h1 = int(data1.split('h')[0]);
        m1 = int(data1.split('h')[1]);    
        h2 = int(data2.split('h')[0]);
        m2 = int(data2.split('h')[1]);    
    elif ":" in data1:
        h1 = int(data1.split(':')[0]);
        m1 = int(data1.split(':')[1]);    
        h2 = int(data2.split(':')[0]);
        m2 = int(data2.split(':')[1]);    
    else:
        print("[ERROR] parse time line:'"+str(line)+"'");
        return {};
    
    if h1 > h2: #midnight work session betwwen 2 day case
        h2 += 24; # add 24 hours will cause problem when need to put dates 

    time_start = {'h': h1, 'm': m1};    
    time_end = {'h': h2, 'm': m2};    
    
    #process duration in minutes
    dh = (time_end['h'] - time_start['h']) * 60;
    dm = time_end['m'] - time_start['m'];
    duration = dh + dm;

    return {'time_start': time_start, 'time_end': time_end, 'duration': duration};

def parse_data(line):
    #parse data

    project = "";
    activity = "";
    comment = "";
    tags = [];

    if "[[" in line: #new version
        project = line.split("[[")[1].split("]]")[0];
        activity = line.split("[[")[0];
    elif "[" in line: #old version
        project = line.split("[")[1].split("]")[0];
        activity = line.split("[")[0];

    while "#" in line:
        tag = line.split("#")[1].split(' ')[0];
        tags.append(tag);
        line = line.split("#")[1];
        if ' ' in line:
            line = line.split(' ')[1];

    comment = line;
    
    #clean
    activity = activity.replace(" ", "");
    activity = activity.replace("\t", "");

    return {'project': project, 'activity': activity, 'comment': comment, 'tags': tags};


# get hour minutes for each project as: return a preformated list of projects

#[[project18]]
#   activity1   12h03  
#   activity2   10h02
#   total       22h05
#

#[[project02]]
#   activity1   12h03  
#   activity2   10h02
#   total       22h05
#

# @todo add an argument, period: all/week/month/years, period is the current period and determine which period to keep to display stats

def get_recap_by_project(datas, period):
    projects = [];
    project_label_list = [];

    for date in datas:

        # if in_period which will compare the date with the dates from the period 
        
        d = date['date'];
        date_str = d['day'] + "/"+ d['month'] + "/" + d['year'];

        # fix end of file
        if (date_str == "00/00/00 eof"):
            break;

        if (is_in_current_period(date_str, period) == True):
            for time in date['times']: # time is time associated to project, activity, duration
                # time {time_start, time_end, duration, data}
                data = time['data']; # {project(label), activity(label), comment, tags}
                project_label = data['project'];
                
                if 'duration' in time: # case no duration
                    
                    if project_label not in project_label_list:
                        activities_total_duration = {}; #activities['work'] = total_duration;
                        activity_label = data['activity'];
                        activities_total_duration[activity_label] = time['duration'];
                        project = {'label': project_label, 'activities': activities_total_duration, 'total': 0};
                        projects.append(project);
                        project_label_list.append(project_label);
                    else: # a project already exist
                        for project in projects: # looking for the existing project
                            label_found = 0;
                            existing_project_label = project['label'];
                            new_project_label = data['project'];
        
                            if existing_project_label == new_project_label:
                                activity_label = data['activity'];
                                for label, duration in project['activities'].items(): # looking for the existing activity
                                    if label == activity_label: # found
                                        label_found = 1;
                                        project['activities'][activity_label] += time['duration'];
        
                                if label_found == 0: #create new activity in the list
                                    project['activities'][activity_label] = time['duration'];
                else:
                    print("[ERROR] no duration in time obejct");
        
#                index_project = projects.index(time['data']['project']);
#                index_activity = time['data']['activity'];
#                projects[index_project][index_activity] += time['duration'];

    # compute total
    
    for project in projects:
        project['total'] = 0;
        for activity_label, duration in project['activities'].items():
            project['total'] += duration;

# @todo debug why the script task is not take in account ?

    return projects;

def print_recap(projects):
    all_period_total = 0;

    for project in projects:
        print('[['+project['label']+']]');
        for label, duration in project['activities'].items():
            all_period_total += duration;
            if (len(label) > 10):
                print('\t'+label+'\t'+minutes_to_h_m(duration)+'');
            else:
                print('\t'+label+'\t\t'+minutes_to_h_m(duration)+'');
        print('\ttotal:\t\t'+minutes_to_h_m(project['total'])+'\n')
                
    print('[[all_projects]]');
    print('\ttotal:\t'+minutes_to_h_m(all_period_total)+'\n')

# main

# read file

path_old_old = "/home/dev/Documents/notes/root/0. tools/qs/olds_log.md" # 2022
path_old = "/home/dev/Documents/notes/root/0. tools/7. logs.md" # fev - april 2023
# @todo on xiaomi maybe i could found a better version of logs

# @todo old_format converter to new_format

path_now = "/home/dev/Documents/notes/root/0. tools/logs_actual.md";

lines = read(path_now);

# parse file

# detect a day
# parse activities of the day
# return an day object with it whithin
# {'date': date, 'times': [{'time_start': time_start, 'time_end': time_end, 'duration': duration}]};

datas = [];
i = 0;

while "**" not in lines[i]: # go to the first date if there is empty lines or something
    line = lines[i];
    print('[ERROR] line below is ignored: "'+line+'"');
    i += 1;

while i < len(lines):
    current_date = {};
    current_time = {};
    times = [];
    line = lines[i];

    # set the new current date
    current_date = parse_date(line);
    i += 1;

    # parse all inside
    while i < len(lines) and "**" not in lines[i]: # while next dates is not detected
        print("[PARSING] line : "+str(i + 1));
        line = lines[i];
        if "*" in line: #new time
            time = parse_time(line);
            current_time = time;
        elif "[[" in line: #new data detected,  
            data = parse_data(line);
            current_time['data'] = data;
            times.append(current_time);
            current_time = {};
        elif (i == (len(lines) - 1)): # save the last line
            data = parse_data(line);
            current_time['data'] = data;
            times.append(current_time);
        else:
            print("[ERROR] parsing line "+str(i));
            print("[ERROR] content line :'"+str(lines[i])+"'");
            print("[ERROR] current time :'"+str(current_time)+"'");
        i += 1;

    if (i < len(lines)):
        line = lines[i];
    if "**" in line: #save dict
        # save the day
        data_date = {'date': current_date, 'times': times};
        datas.append(data_date);
# process datas

print('\n\n\n');

if len(sys.argv) > 1:
    a = sys.argv[1]

    if (a == "--day" or a == "-d"):
        period = "day";
    elif (a == "--week" or a == "-w"):
        period = "week";
    elif (a == "--month" or a == "-m"):
        period = "month";
    elif (a == "--year" or a == "-y"):
        period = "year";
    else:
        period = "all";
else:
    period = "all";
    
projects = get_recap_by_project(datas, period);
print_recap(projects);
