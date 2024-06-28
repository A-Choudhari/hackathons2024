# cal/views.py
from django.shortcuts import render, redirect
from django.http import HttpResponseRedirect, StreamingHttpResponse
from django.views import generic
from django.utils.safestring import mark_safe
from datetime import timedelta, datetime, date
import calendar
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy, reverse
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from openai import OpenAI
from transformers import pipeline
import pyttsx3
import keyboard
from setuptools import distutils
import json
import google.generativeai as genai
from datetime import timedelta, datetime, date
from calendarapp.models import EventMember, Event
from calendarapp.utils import Calendar
from calendarapp.forms import EventForm, AddMemberForm
from accounts.models.user import Journaling
import speech_recognition as sr


def get_date(req_day):
    if req_day:
        year, month = (int(x) for x in req_day.split("-"))
        return date(year, month, day=1)
    return datetime.today()


def prev_month(d):
    first = d.replace(day=1)
    prev_month = first - timedelta(days=1)
    month = "month=" + str(prev_month.year) + "-" + str(prev_month.month)
    return month


def next_month(d):
    days_in_month = calendar.monthrange(d.year, d.month)[1]
    last = d.replace(day=days_in_month)
    next_month = last + timedelta(days=1)
    month = "month=" + str(next_month.year) + "-" + str(next_month.month)
    return month


class CalendarView(LoginRequiredMixin, generic.ListView):
    login_url = "accounts:signin"
    model = Event
    template_name = "calendar.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        d = get_date(self.request.GET.get("month", None))
        cal = Calendar(d.year, d.month)
        html_cal = cal.formatmonth(withyear=True)
        context["calendar"] = mark_safe(html_cal)
        context["prev_month"] = prev_month(d)
        context["next_month"] = next_month(d)
        return context


@login_required(login_url="signup")
def create_event(request):
    form = EventForm(request.POST or None)
    if request.POST and form.is_valid():
        title = form.cleaned_data["title"]
        description = form.cleaned_data["description"]
        start_time = form.cleaned_data["start_time"]
        end_time = form.cleaned_data["end_time"]
        Event.objects.get_or_create(
            user=request.user,
            title=title,
            description=description,
            difficulty=start_time,
            end_time=end_time,
        )
        return HttpResponseRedirect(reverse("calendarapp:calendar"))
    return render(request, "event.html", {"form": form})


class EventEdit(generic.UpdateView):
    model = Event
    fields = ["title", "description", "difficulty", "end_time"]
    template_name = "event.html"


@login_required(login_url="signup")
def event_details(request, event_id):
    event = Event.objects.get(id=event_id)
    eventmember = EventMember.objects.filter(event=event)
    context = {"event": event, "eventmember": eventmember}
    return render(request, "event-details.html", context)


def add_eventmember(request, event_id):
    forms = AddMemberForm()
    if request.method == "POST":
        forms = AddMemberForm(request.POST)
        if forms.is_valid():
            member = EventMember.objects.filter(event=event_id)
            event = Event.objects.get(id=event_id)
            if member.count() <= 9:
                user = forms.cleaned_data["user"]
                EventMember.objects.create(event=event, user=user)
                return redirect("calendarapp:calendar")
            else:
                print("--------------User limit exceed!-----------------")
    context = {"form": forms}
    return render(request, "add_member.html", context)


class EventMemberDeleteView(generic.DeleteView):
    model = EventMember
    template_name = "event_delete.html"
    success_url = reverse_lazy("calendarapp:calendar")


class CalendarViewNew(LoginRequiredMixin, generic.View):
    login_url = "accounts:signin"
    template_name = "calendarapp/calendar2.html"
    form_class = EventForm

    def get(self, request, *args, **kwargs):
        forms = self.form_class()
        events = Event.objects.filter(user=request.user, is_active=True)
        events_month = Event.objects.get_running_events(user=request.user)
        event_list = []
        # start: '2020-09-16T16:00:00'
        for event in events:
            event_list.append(
                {"id": event.id,
                 "title": event.title,
                 "difficulty": event.difficulty,
                 "start": event.end_time.strftime("%Y-%m-%dT%H:%M:%S"),
                 "end": event.end_time.strftime("%Y-%m-%dT%H:%M:%S"),
                 "description": event.description,
                 }
            )

        context = {"form": forms, "events": event_list,
                   "events_month": events_month}
        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        forms = self.form_class(request.POST)
        if forms.is_valid():
            form = forms.save(commit=False)
            form.user = request.user
            form.save()
            return redirect("calendarapp:calendar")
        context = {"form": forms}
        return render(request, self.template_name, context)


def delete_event(request, event_id):
    event = get_object_or_404(Event, id=event_id)
    if request.method == 'POST':
        next = event
        next.is_active = False
        next.save()
        return JsonResponse({'message': 'Event success delete.'})
    else:
        return JsonResponse({'message': 'Error!'}, status=400)


def next_week(request, event_id):
    event = get_object_or_404(Event, id=event_id)
    if request.method == 'POST':
        next = event
        next.id = None
        next.end_time += timedelta(days=7)
        next.save()
        return JsonResponse({'message': 'Sucess!'})
    else:
        return JsonResponse({'message': 'Error!'}, status=400)


def daily_check(request):
    if request.method == "POST":
        summarizer = pipeline("summarization")
        data = json.loads(request.body)
        if data.get("journal") is not None:
            text = data.get("journal")
            # Generate summary
            summary = summarizer(text, max_length=500, min_length=50, do_sample=False)
            new_journal = Journaling(user=request.user, text_summary=summary[0]['summary_text'])
            new_journal.save()
        return HttpResponseRedirect(reverse("calendar"))
    else:
        return render(request, "daily-check.html")


def to_do_list(request):
    return render(request, "to_do_list.html")


def next_day(request, event_id):
    event = get_object_or_404(Event, id=event_id)
    if request.method == 'POST':
        next = event
        next.id = None
        next.end_time += timedelta(days=1)
        next.save()
        return JsonResponse({'message': 'Sucess!'})
    else:
        return JsonResponse({'message': 'Error!'}, status=400)


class StopFunction(Exception):
    pass


def journals(request):
    user_journals = Journaling.objects.filter(user=request.user)
    return render(request, "journal.html", {"user_journals": user_journals})


request_for_task = ""


def user_transcript(request):
    global request_for_task
    if request.method == "POST":
        data = json.loads(request.body)
        if data.get("user_transcript") is not None:
            transcript = data.get("user_transcript")
            todo_list = Event.objects.filter(user=request.user, is_active=True)
            final_list = []
            for item in todo_list:
                format = '%m/%d/%Y %I:%M %p'
                date_time = datetime.strftime(item.end_time, format)
                item_str = f"{item.pk}, {item.title}, {date_time}, {item.difficulty}, {item.description}"
                final_list.append(item_str)
            request_for_task = request
            print(transcript)
            genAI_todo(transcript, final_list)
            return HttpResponseRedirect(reverse("dashboard"))


def genAI_todo(transcript, todo_list, fail_count=0):
    genai.configure(api_key='AIzaSyDBq8NMvrMKxdBjwfKXW_amq0W8QDnAYZ4')
    model = genai.GenerativeModel(
        "models/gemini-1.5-pro-latest",
        generation_config=genai.GenerationConfig(
            max_output_tokens=1000,
            temperature=0.4
        ),
        system_instruction="""Your job is to understand user's requests for tasks on their todo list and update it accordingly.
                            Based on the user's request and the existing to-do list, you should add the user's tasks to the to-do list,
                            update existing tasks, and/or remove completed or unwanted tasks in the to-do list.
                            To add a task, output ADD_TASK (Task Name) (Task Description) (Task Priority) (Task Due Date)
                            To update a task, output UPDATE_TASK (Index) (Task Name) (Task Description) (Task Priority) (Task Due Date)
                            To remove a task or mark it complete, output REMOVE_TASK (Index)
                            When outputting this, include the parentheses around each parameter.
                            Leave task description empty if the user does not specify anything about the task.
                            Task priority should be 'low', 'medium', or 'high'. Use medium as the default priority.
                            Give the due date in the format MM/DD/YYYY HH:MM AM/PM. If the user does not give a specific time, use 11:59 PM. 
                            Output these to-do list actions only as much as necessary and seperate the functions with new lines.

                            Example 1: if the date is January 1st, 2024 and the user asks to add math homework to their to-do list, you would output:
                            ADD_TASK (Math Homework) () (medium) (01/01/2024 11:59 PM)

                            Example 2: if the date is January 1st, 2024, there is a task called English report in the existing todo list (with the index 35, description 'symbolism', is due tomorrow, and has medium priority),
                            and the user asks to make the English report due today, you would output:
                            UPDATE_TASK (35) (English report) (symbolism) (medium) (01/01/2024 11:59 PM)

                            Example 3: if there is a task called feed the dog with index 29 in the existing todo list, and the user says they have completed it, you would output:
                            REMOVE_TASK (29)
                            """
    )
    chat = model.start_chat()

    current_time = datetime.now()
    time_prompt = "The current date and time is " + current_time.strftime("%A, %B %d, %Y at %I:%M %p.")

    prompt = time_prompt + "\nCurrent to-do list tasks: " + ''.join(todo_list) + "\n\nUSER: " + transcript
    print(prompt, "\n\nASSISTANT:")
    #  try:

    response = chat.send_message(prompt)
    text = response.text
    print(text)

    commands = text.split("\n")
    # print(commands)
    commands = list(set(commands))
    for command in commands:
        command_type = command.split(" ")[0]
        # print(command)
        command = command.replace(command_type + " ", "")
        elements_list = command.split(") (")
        elements_list[0] = elements_list[0].replace("(", "")
        elements_list[-1] = elements_list[-1].replace(")", "")
        elements_list[-1] = elements_list[-1].strip()

        print(elements_list)
        if command_type == "ADD_TASK":
            add_task(elements_list[0], elements_list[1], elements_list[2], elements_list[3])
        elif command_type == "UPDATE_TASK":
            # print(elements_list[0])
            elements_list[0] = int(elements_list[0])
            update_task(elements_list[0], elements_list[1], elements_list[2], elements_list[3], elements_list[4])
        elif command_type == "REMOVE_TASK":
            elements_list[0] = int(elements_list[0])
            remove_task(elements_list[0])
        else:
            continue


#  except:
#       print("There was an error.")
#       fail_count += 1
#       if fail_count <= 1:
#           time.sleep(30)
#           genAI_todo(transcript, todo_list, fail_count)


def add_task(task_title: str, task_description: str, task_priority: str, task_due_date: str):
    """Adds a new task to the to-do list
    task_priority: string that is 'low', 'medium', or 'high'"""
    # Format of task_due_date: m/d/Y H:M AM/PM
    format = '%m/%d/%Y %I:%M %p'
    due_date_datetime_obj = datetime.strptime(task_due_date, format)
    task_priority= task_priority[0].upper() + task_priority[1:]
    new_event = Event(user=request_for_task.user, title=task_title, description=task_description,
                      difficulty=task_priority, end_time=due_date_datetime_obj, is_active=True)
    new_event.save()
    print("ADD", task_title, task_description, task_priority, task_due_date)


def update_task(index_number: int, task_title: str, task_description: str, task_priority: str, task_due_date: str):
    """Updates the task in the list that matches the inputted index number
    task_priority: string that is 'low', 'medium', or 'high'"""
    # Format of task_due_date: m/d/Y H:M AM/PM
    format = '%m/%d/%Y %I:%M %p'
    due_date_datetime_obj = datetime.strptime(task_due_date, format)
    print(due_date_datetime_obj)
    task_priority = task_priority[0].upper() + task_priority[1:]
    event_item = Event.objects.get(id=index_number)
    event_item.title = task_title
    event_item.description = task_description
    event_item.difficulty = task_priority
    event_item.end_time = due_date_datetime_obj
    event_item.save()
    print("UPDATE", index_number, task_title, task_due_date, task_priority, task_description)


def remove_task(index_number: int):
    """Deletes or marks as complete the task in the list that matches the inputted index number"""
    event_item = Event.objects.get(id=index_number)
    event_item.is_active = False
    event_item.save()
    print("REMOVE", index_number)


# ex_transcript = "ok so I need to finish the English vignette Monday evening and I need to remember to write about Michael in it because he is the goat reference and then I finished the math homework, but there's part 2 for it due tomorrow. Also, make the sink fix thing high priority please and remember that I can buy the tools for it at home depot. Thanks good night"
# ex_todo = """[1, 'Fix the sink', 05/19/2024 9:30 PM, 'medium', 'Use the red wrench'],
#            [2, 'Math homework', 05/17/2024 11:59 PM, 'high', '']
#            [3, 'Schedule appointment with Jack', 05/21/2024 11:59 PM, 'low', '']"""
# print("start")
# genAI_todo(ex_transcript, ex_todo)

# Chatbot conversational application

def stream(request):
    #def event_stream():
    #    ex_text = ["Akshat: Hi", "Chatbot: How are you doing", "Akshat: Bye"]
        #while True:
    response = StreamingHttpResponse(messages([], request), content_type="text/event-stream")
    response['X-Accel-Buffering'] = 'no'  # Disable buffering in nginx
    response['Cache-Control'] = 'no-cache'  # Ensure clients don't cache the data
    return response


def messages(conversation_transcript, request):
    user_name = "USER: "
    chatbot_name = "ECHO: "

    recognizer = sr.Recognizer()
    client = OpenAI(
        api_key="PUT API KEY",
    )
    todo_list = Event.objects.filter(user=request.user, is_active=True)
    final_list = []
    conversation_transcript = ['','']
    for item in todo_list:
        format = '%m/%d/%Y %I:%M %p'
        date_time = datetime.strftime(item.end_time, format)
        item_str = f"{item.pk}, {item.title}, {date_time}, {item.difficulty}, {item.description}"
        final_list.append(item_str)
    system_msg = f"You are a friendly assistant in a todo list app that is doing an end of day check in for the user's tasks.\nExisting to-do list: {''.join(final_list)}"
    engine = pyttsx3.init()
    # engine.setProperty("rate", 200)
    engine.setProperty("volume", 1)

    voices = engine.getProperty("voices")
    engine.setProperty("voice", voices[1].id)

    while True:
        with sr.Microphone() as source:
            print("\ncUSER: ")
            audio = recognizer.listen(source)
            #print(audio)

        # text = ""

        print("converting to text")
        text = recognizer.recognize_whisper(audio, language="en")
        #print(text)
        conversation_transcript[0] = user_name + text

        chat_completion = client.chat.completions.create(
            messages=[
                {
                    "role": "system",
                    "content": system_msg
                },
                {
                    "role": "user",
                    "content": text,
                }
            ],
            model="gpt-3.5-turbo",
        )

        assistant_message = chat_completion.choices[0].message.content
        #print("\nECHO: " + assistant_message)
        conversation_transcript[1] = chatbot_name + assistant_message
        engine.say(assistant_message)
        for item in conversation_transcript:
            print(item)
            #data = json.load(item)
            yield f'data: {item}\n\n'
        engine.runAndWait()
        genAI_todo(conversation_transcript, todo_list)
        if keyboard.is_pressed('q'):
            engine.stop()
            print("Loop terminated by user.")
            summarizer = pipeline("summarization")
            # Summarize the text
            summary = summarizer(text, max_length=50, min_length=25, do_sample=False)
            Journaling(user=request.user, date=datetime.now(), text_summary=summary[0]['summary_text'])
            break


def end_item(request):
    data = json.loads(request.body)
    if data.get("id_item") is not None:
        id = data.get("id_item")
        item = Event.objects.get(pk=id)
        item.is_active = False
        item.save()
    return HttpResponseRedirect(reverse("dashboard"))