import csv

# just run one section each time!

# switzerland
f = open("switzerland.csv")
csv_f = csv.reader(f)
row_count = 1
patient = ""
print("SWITZERLAND")
with open("switzerland_76.csv", "w", newline="") as file:
    writer = csv.writer(file)
    for row in csv_f:
        row = [r.replace(" ", ", ") for r in row]  # insert commas

        # concatenate cells 1-10 (or 1-12)
        if row_count % 10 == 0:
            # print(row)
            patient += row[0]
            print(patient)
            patientList = patient.split(", ")
            writer.writerow(patientList)
            row_count += 1
            patient = ""
        else:
            # print(row_count)
            str = row[0]
            str += ", "
            # print(str)
            patient += str
            str = ""
            row_count += 1

"""# cleveland
f = open('cleveland.csv')
csv_f = csv.reader(f)
row_count = 1
patient = ""
print("CLEVELAND")
with open("cleveland_76.csv","w",newline="") as file:
    writer = csv.writer(file)
    for row in csv_f:
        row = [r.replace(" ", ", ") for r in row] # insert commas
        
        # concatenate cells 1-10 (or 1-12)
        if(row_count % 10 == 0):
            #print(row)
            patient += row[0]
            print(patient)
            patientList = patient.split(", ")
            writer.writerow(patientList)
            row_count += 1
            patient = ""
        else:
            #print(row_count)
            str = row[0]
            str += ", "
            #print(str)
            patient += str
            str = ""
            row_count += 1

# new
f = open('new.csv')
csv_f = csv.reader(f)
row_count = 1
patient = ""
print("NEW")
with open("new_76.csv","w",newline="") as file:
    writer = csv.writer(file)
    for row in csv_f:
        row = [r.replace(" ", ", ") for r in row] # insert commas
        
        # concatenate cells 1-10 (or 1-12)
        if(row_count % 12 == 0):
            #print(row)
            patient += row[0]
            print(patient)
            patientList = patient.split(", ")
            writer.writerow(patientList)
            row_count += 1
            patient = ""
        else:
            #print(row_count)
            str = row[0]
            str += ", "
            #print(str)
            patient += str
            str = ""
            row_count += 1

# long-beach-va
f = open('long-beach-va.csv')
csv_f = csv.reader(f)
row_count = 1
patient = ""
print("LONG-BEACH-VA")
with open("long-beach-va_76.csv","w",newline="") as file:
    writer = csv.writer(file)
    for row in csv_f:
        row = [r.replace(" ", ", ") for r in row] # insert commas
        
        # concatenate cells 1-10 (or 1-12)
        if(row_count % 10 == 0):
            #print(row)
            patient += row[0]
            print(patient)
            patientList = patient.split(", ")
            writer.writerow(patientList)
            row_count += 1
            patient = ""
        else:
            #print(row_count)
            str = row[0]
            str += ", "
            #print(str)
            patient += str
            str = ""
            row_count += 1 

# hungarian
f = open('hungarian.csv')
csv_f = csv.reader(f)
row_count = 1
patient = ""
print("HUNGARIAN")
with open("hungarian_76.csv","w",newline="") as file:
    writer = csv.writer(file)
    for row in csv_f:
        row = [r.replace(" ", ", ") for r in row] # insert commas
        
        # concatenate cells 1-10 (or 1-12)
        if(row_count % 10 == 0):
            #print(row)
            patient += row[0]
            print(patient)
            patientList = patient.split(", ")
            writer.writerow(patientList)
            row_count += 1
            patient = ""
        else:
            #print(row_count)
            str = row[0]
            str += ", "
            #print(str)
            patient += str
            str = ""
            row_count += 1 """
