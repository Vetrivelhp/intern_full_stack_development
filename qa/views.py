from django.shortcuts import render
from django.contrib.auth.models import User
from .models import Question
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
import google.generativeai as genai
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout
import markdown
import os
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("GEMINI_API_KEY")


def login_view(request):

    if request.method == "POST":

        username = request.POST.get("user")
        password = request.POST.get("pass")

        user = authenticate(
            request,
            username=username,
            password=password
        )

        if user is not None:
            login(request, user)
            return redirect("dashboard")

    return render(request, "login.html")

def signup_view(request):

    if request.method == "POST":

        username = request.POST.get("user")
        password1 = request.POST.get("pass1")
        password2 = request.POST.get("pass2")

        if password1 == password2:

            if not User.objects.filter(username=username).exists():

                User.objects.create_user(
                    username=username,
                    password=password1
                )

                return redirect("login")

    return render(request, "sign.html")

def get_answer(question):
    genai.configure(api_key=API_KEY)
    model = genai.GenerativeModel("gemini-2.5-flash-lite")
    response = ""
    
    try:
        response = model.generate_content(question)
        answer = response.text
        return answer
    
    except Exception as e:
        print(e)
        answer = f"Error: {e}"
        return answer


@login_required
def dashboard_view(request):

    questions = Question.objects.filter(
        user=request.user
    ).order_by("created_at")
    
    answer = ""
    
    if request.method == "POST":
        question = request.POST.get("question")
        prompt = f"""
        You are an Electrical Engineering Assistant.

        Answer questions related to:

        - Electrical machines
        - Motors
        - Transformers
        - Generators
        - Power systems
        - Electrical engineering
        - Electrical measurements
        - Electrical units
        - Electrical circuits
        - Power generation
        - Power transmission
        - Power distribution

        Examples of valid questions:

        - What is kWh?
        - What is voltage?
        - What is current?
        - What is power factor?
        - What is a transformer?
        - What is slip in induction motors?
        - What is a circuit breaker?
        
        Answer using markdown.
        Use:
        # headings
        ## subheadings
        - bullet points
        **bold**

        If the question is completely unrelated to electrical engineering, reply exactly:

        This application only supports electrical engineering related questions.

        Question:
        {question}
        """
        
        answer = get_answer(prompt)
        answer_html = markdown.markdown(answer)
        
        Question.objects.create(
            user=request.user,
            question=question,
            answer=answer_html
        )
        
        return redirect("dashboard")
        
    return render(
    request,
    "dashboard.html",
    {
        "answer": answer,
        "questions": questions
    }
)

def logout_view(request):
    logout(request)
    return redirect("login")