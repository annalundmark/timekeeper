#!/usr/bin/env python

import Tkinter
import tkMessageBox

import sys
import datetime

import MySQLdb as mdb

import csv

def main():
    
    con = mdb.connect('localhost', 'testuser', 'test623', 'testdb_timekeeper')
    
    with con:
        cur = con.cursor()
        
        try:
            cur.execute("SELECT 1 FROM Timeschedule LIMIT 1;")
        except: 
            cur.execute("CREATE TABLE IF NOT EXISTS Timeschedule (Id INT NOT NULL PRIMARY KEY AUTO_INCREMENT,Date VARCHAR(20),AbsTimeArrive VARCHAR(30),TimeArrive VARCHAR(20),Weekday VARCHAR(20),AbsTimeLeave VARCHAR(30),TimeLeave VARCHAR(20),TotalWorkTime VARCHAR(20)); ")
        
        working = False
        
        try: 
            cur.execute("SELECT MAX(Id) AS Id FROM Timeschedule")
            most_recent = cur.fetchone()[0]
            cur.execute("SELECT AbsTimeLeave FROM Timeschedule WHERE Id=(%s);", (most_recent))
            time_leave = cur.fetchone()[0]
            if time_leave:
                working = False
            else:
                working = True
            con.commit()
        except:
            con.rollback()
        
    
        top = Tkinter.Tk()
        top.geometry("250x150+300+300")
    
        startButton = Tkinter.Button(top, text ="Start", state="disabled" if working else "normal" )
        leaveButton = Tkinter.Button(top, text ="Leave", state="normal" if working else "disabled")
        
        startButton.config(command = lambda: startWork(cur, con, startButton, leaveButton))
        leaveButton.config(command = lambda: leaveWork(cur,con, startButton, leaveButton))
        
        exportButton = Tkinter.Button(top, text ="Export data", command = lambda: exportData(cur, con))
   

        startButton.place(x=40, y=40)
        leaveButton.place(x=120, y=40)
        exportButton.place(x=40, y=80)
    
        top.mainloop()



def startWork(cur, con, startButton, leaveButton):
    now, date, hour, minute, weekday = getDateAndTime()
    
    startButton.config(state="disabled")
    leaveButton.config(state="normal")

    in_time = str(hour) + ":" + str(minute)
    
    try: 
        cur.execute("INSERT INTO Timeschedule (Date, AbsTimeArrive, TimeArrive, Weekday) VALUES (%s, %s, %s, %s);", (date, now, in_time, weekday))
        con.commit()
    except:
        con.rollback()
    
    tkMessageBox.showinfo( "Start work", "Welcome to work! You started working at: " + in_time)

def leaveWork(cur, con, startButton, leaveButton):
    now, date, hour, minute, weekday = getDateAndTime()
    
    startButton.config(state="normal")
    leaveButton.config(state="disabled")
        
    out_time = str(hour) + ":" + str(minute)

    try: 
        cur.execute("SELECT MAX(Id) AS Id FROM Timeschedule")
        most_recent = cur.fetchone()[0]
        cur.execute("SELECT AbsTimeArrive FROM Timeschedule WHERE Id=(%s);", (most_recent))
        time_arrive = cur.fetchone()[0]
        abs_work_time = getDiffTime(time_arrive, now)
        cur.execute("UPDATE Timeschedule SET AbsTimeLeave=(%s), TimeLeave=(%s), TotalWorkTime=(%s) WHERE Id=(%s);", (now, out_time, abs_work_time, most_recent))
        con.commit()
    except:
        con.rollback()
        
    tkMessageBox.showinfo( "Leaving", "Goodbye! Your total work time today is: " + abs_work_time)
    
def exportData(cur, con):
    
    now, date, hour, minute, weekday = getDateAndTime()
    
    cur.execute("SELECT * FROM Timeschedule;")
    rows = cur.fetchall()
    with open("export" + date + ".csv", "wb") as csvfile:
        writer = csv.writer(csvfile, delimiter = ";")
        writer.writerow(("Date", "Weekday", "Start work", "Leave work", "Total time"))
        for row in rows:
            writer.writerow((str(row[1]), str(row[4]), str(row[3]), str(row[6]), str(row[7])))
    
    tkMessageBox.showinfo( "Export", "Your data has been exported")

def getDateAndTime():
    now = datetime.datetime.now()
    date = datetime.date.today().isoformat()
    weekday = now.strftime("%A")
    
    if now.minute < 10:
        minute = "0" + now.minute
    else:
        minute = now.minute
    
    return now, date, now.hour, minute, weekday

def getDiffTime(in_time, out_time):
    in_time_object = datetime.datetime.strptime(in_time[0:16], '%Y-%m-%d %H:%M')
    diff = out_time - in_time_object
    total_seconds = diff.seconds
    total_mins = total_seconds/60
    total_hours = total_mins/60
    total_mins = total_mins%60
    
    if total_mins<10:
        total_mins = "0" + str(total_mins)
    
    abs_work_time = str(total_hours) + ":" + str(total_mins)
    
    return abs_work_time


if __name__ == "__main__":
    main()