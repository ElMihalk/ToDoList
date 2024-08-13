from sqlalchemy import String, Column, create_engine, Date, Table, Integer
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime, timedelta
import sys

def display_query(query, with_date=True):
    list_index: int = 1
    for item in query:
        if with_date:
            print(f"{list_index}. {item.task}. {item.deadline.strftime('%d %b')}")
        else:
            print(f"{list_index}. {item.task}.")
        list_index += 1
    print()

def display_todays_tasks(session):
    query_all_today = session.query(ToDo).filter(ToDo.deadline == datetime.today().date()).all()
    print(f"Today {datetime.today().day} {datetime.today().strftime('%b')}:")
    if len(query_all_today) == 0:
        print("Nothing to do!\n")
    else:
        display_query(query_all_today, with_date=False)

def display_weeks_tasks(session):
    date_today = datetime.today()
    for delta_t in range(7):
        reference_date = date_today + timedelta(days=delta_t)
        query_all_on_day = session.query(ToDo).filter(ToDo.deadline == reference_date.date()).all()
        print(f"{reference_date.strftime('%A %d %b')}:")
        if len(query_all_on_day) == 0:
            print("Nothing to do!\n")
        else:
            display_query(query_all_on_day, with_date=False)
def display_all_tasks(session):
    query_all_by_date = session.query(ToDo).order_by(ToDo.deadline).all()
    print(f"All tasks:")
    if len(query_all_by_date) == 0:
        print("Nothing to do!\n")
    else:
        display_query(query_all_by_date)

def display_missed_tasks(session):
    query_missed = session.query(ToDo).filter(ToDo.deadline < datetime.today().date()).order_by(ToDo.deadline).all()
    print(f"Missed tasks:")
    if len(query_missed) == 0:
        print("All tasks have been completed!\n")
    else:
        display_query(query_missed)

#definition of database
Base = declarative_base()
class ToDo(Base):
    __tablename__ = "task"

    id = Column(Integer, primary_key=True)
    task = Column(String)
    deadline = Column(Date, default=datetime.today())

    def __repr__(self):
        return self.task

engine = create_engine('sqlite:///todo.db?check_same_thread=False', echo=False)

Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)
session = Session()

#input and output
while True:
    option = int(input("1) Today's tasks\n2) Week's tasks\n3) All tasks\n4) Missed tasks\n5) Add a task\n"
                       "6) Delete a task\n0) Exit\n"))

    #Today's tasks
    if option == 1:
        display_todays_tasks(session=session)

    #Week's tasks
    if option == 2:
        display_weeks_tasks(session=session)

    #All tasks
    if option == 3:
        display_all_tasks(session=session)

    #Missed tasks
    elif option == 4:
        display_missed_tasks(session=session)

    #Adding new tasks
    elif option == 5:
        query_all = session.query(ToDo).all()
        try:
            idx = query_all[-1].id + 1
        except IndexError:
            idx = 1
        new_task = input("Enter a task\n")
        new_deadline = input("Enter a deadline\n")
        new_row = ToDo(
            id=idx,
            task=new_task,
            deadline=datetime.strptime(new_deadline, "%Y-%m-%d"),
        )
        session.add(new_row)
        session.commit()
        del query_all
        print("The task has been added!\n")

    #Delete a task
    elif option == 6:
        query_all_by_date = session.query(ToDo).order_by(ToDo.deadline).all()
        if len(query_all_by_date) == 0:
            print("Nothing to delete\n")
        else:
            print("Choose the number of the task you want to delete:")
            display_query(query_all_by_date)
            id_to_delete = int(input())
            session.delete(query_all_by_date[id_to_delete-1])
            session.commit()
            del query_all_by_date
            print("The task has been deleted!")

    #Exit program
    elif option == 0:
        sys.exit()
