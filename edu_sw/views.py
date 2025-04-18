from django.shortcuts import redirect, render, get_object_or_404
from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.contrib import messages
from django.contrib.auth import authenticate,login,logout
from .models import testJava,testPython,testSQL,PythonVideo,SQLVideo,JavaVideo
from .models import PythonScore, SQLScore, JavaScore,announc,Occupation
import os
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.contrib.sites.shortcuts import get_current_site
from django.utils.encoding import force_str
from django.utils.http import urlsafe_base64_decode

def home(request):
    return render(request,'home.html',{})

def signup(request):
    if request.method == 'POST':
        try:
            # Getting the form data
            username = request.POST.get('username', '').strip()
            first_name = request.POST.get('firstName', '').strip()
            last_name = request.POST.get('lastName', '').strip()
            email = request.POST.get('email', '').strip()
            password1 = request.POST.get('password1', '')
            password2 = request.POST.get('password2', '')
            user_type = request.POST.get('type', '').strip()

            # Validate the form data (check for username, email, passwords, etc.)
            if password1 != password2:
                messages.error(request, "Passwords don't match!")
                return redirect('signup')

            if password1.isdigit():
                messages.error(request, "Your password can’t be entirely numeric.")
                return redirect('signup')

            # Check if the user already exists
            if User.objects.filter(username=username).exists():
                messages.error(request, "Username already exists.")
                return redirect('signup')

            if User.objects.filter(email=email).exists():
                messages.error(request, "Email already exists.")
                return redirect('signup')

            # Create the user with 'is_active=False' so it can only be activated via email
            user = User.objects.create_user(username=username, email=email, password=password1)
            user.first_name = first_name
            user.last_name = last_name
            user.is_active = False  # User is not active until they confirm the email
            user.save()

             # Create the Occupation instance after user creation
            occupation = Occupation(user=user, type=user_type)
            occupation.save()

            # Generate the activation link
            uid = urlsafe_base64_encode(force_bytes(user.pk))  # Use the user's ID, not username
            token = default_token_generator.make_token(user)
            activation_link = f"http://{get_current_site(request).domain}/activate/{uid}/{token}/"

            # Send the confirmation email with the activation link
            subject = "Activate Your Account"
            message = f"""
<html>
  <head>
    <style>
      body {{
        font-family: Arial, sans-serif;
        background-color: #f4f4f4;
        color: #333;
        padding: 20px;
      }}
      .container {{
        max-width: 600px;
        margin: 0 auto;
        background-color: #fff;
        padding: 30px;
        border-radius: 8px;
        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
      }}
      h2 {{
        text-align: center;
        color: #D94F2F;
      }}
      .btn {{
        background-color: #D94F2F;
        color: white;
        padding: 10px 20px;
        text-decoration: none;
        border-radius: 5px;
        display: block;
        text-align: center;
        margin: 20px 0;
      }}
      p {{
        font-size: 16px;
      }}
    </style>
  </head>
  <body>
    <div class="container">
      <h2>Welcome to SW|EDU</h2>
      <p>Hi {first_name},</p>
      <p>Thank you for signing up with <strong>SW|EDU</strong>, the leading platform for coding education. We're excited to have you join our community of learners and innovators.</p>
      <p>To activate your account and begin your coding journey, please click the button below:</p>
      <a style="  color: black; "href="{activation_link}" class="btn">Activate My Account</a>
      <p>If you did not sign up for an account, please disregard this email.</p>
      <p>At <strong>SW|EDU</strong>, we are committed to providing you with the best resources and learning experience. We look forward to supporting you in mastering coding skills and achieving your goals.</p>
      <p>Best regards,<br>The SW|EDU Team</p>
      <p><a href="http://sifiso.pythonanywhere.com" style="color: #D94F2F;">www.swedu.com</a></p>
    </div>
  </body>
</html>
"""


            send_mail(
                'Activate Your Account',
                'This is a plain text fallback for non-HTML email clients.',  # Plain text body
                'noreply@swedu.com',
                [email],
                fail_silently=False,
                html_message=message
                 )


            messages.success(request, "Check your email to confirm your account. You will be able to log in once it's activated.")
            return redirect('signin')

        except Exception as e:
            messages.error(request, f"Something went wrong: {str(e)}")
            return redirect('signup')

    return render(request, 'signup.html')


def activate_account(request, uidb64, token):
    try:
        # Decode the UID
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user is not None and default_token_generator.check_token(user, token):
        # Token is valid, activate the user
        user.is_active = True
        user.save()
        messages.success(request, "Your account has been activated! You can now log in.")
        return redirect('signin')
    else:
        # Token is invalid or expired
        messages.error(request, "The activation link is invalid or has expired.")
        return redirect('signup')



def signin(request):
    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password1', '').strip()

        # Authenticate the user
        user = authenticate(request, username=username, password=password)

        if user is not None:
            try:
                # Log the user in
                login(request, user)

                # Fetch the user's type from Occupation
                occupation = Occupation.objects.get(user=user)

                if occupation.type == 'admin':
                    return render(request, 'admin_dash/admin_dash.html', {'user': user})
                elif occupation.type == 'user':
                    # Fetch announcements and scores
                    countA = announc.objects.count()
                    announcements = announc.objects.all()
                    python_score = PythonScore.objects.filter(user=user).first()
                    java_score = JavaScore.objects.filter(user=user).first()
                    SQL_score = SQLScore.objects.filter(user=user).first()

                    return render(request, 'user_dash/user_dash.html', {
                        'python_score': python_score,
                        'java_score': java_score,
                        'SQL_score': SQL_score,
                        'countA': countA,
                        'announcements': announcements,
                    })
            except Occupation.DoesNotExist:
                logger.error(f"Occupation entry not found for user: {user.username}")
                messages.error(request, "User type not configured. Please contact support.")
                return redirect('signin')
            except Exception as e:
                logger.critical(f"Unexpected error during signin: {e}", exc_info=True)
                messages.error(request, "An error occurred. Please try again later.")
                return redirect('signin')
        else:
            messages.error(request, 'Invalid username or password.')
            return redirect('signin')

    return render(request, 'signin.html', {})




def signout(request):
    logout(request)
    response = redirect('home')
    response['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    response['Pragma'] = 'no-cache'
    response['Expires'] = '0'
    return response







def back_admin(request):
    return render(request, 'admin_dash/admin_dash.html' )

def back_user(request):
    announcements = announc.objects.all()
    countA = announcements.count()


    python_score = PythonScore.objects.filter(user=request.user).first()
    java_score = JavaScore.objects.filter(user=request.user).first()
    SQL_score = SQLScore.objects.filter(user=request.user).first()


    return render(request, 'user_dash/user_dash.html', {
        'python_score': python_score,
        'java_score': java_score,
        'SQL_score': SQL_score,
        'countA': countA,
        'announcements': announcements,
    })


def add_tests(request):
    role = None
    count = 0

    if request.method == 'POST':
        role = request.POST.get('role', '').strip()


        role_model_map = {
            'java': testJava,
            'SQL': testSQL,
            'python': testPython,
        }


        model = role_model_map.get(role)
        if model:
            count = model.objects.count()
        else:
            count = None

    return render(request, 'admin_dash/test_database.html', {
        'role': role,
        'count': count,
    })






def test_database(request):
    if request.method == 'POST':

        role = request.POST.get('role', '').strip()
        question = request.POST.get('question', '').strip()
        option1 = request.POST.get('option1', '').strip()
        option2 = request.POST.get('option2', '').strip()
        option3 = request.POST.get('option3', '').strip()
        option4 = request.POST.get('option4', '').strip()
        correct_option = request.POST.get('correct-option', '').strip()


        role_model_map = {
            'python': testPython,
            'SQL': testSQL,
            'java': testJava,
        }

        model = role_model_map.get(role)
        if model:

            model.objects.create(
                Question=question,
                Option1=option1,
                Option2=option2,
                Option3=option3,
                Option4=option4,
                CorrectOption=correct_option
            )
            count = model.objects.count()
            return render(request, 'admin_dash/test_database.html', {
                'role': role,
                'count': count,
            })


        return render(request, 'admin_dash/test_database.html', {
            'error': 'Invalid role specified.',
        })

    return render(request, 'admin_dash/test_database.html')



def   add_videos(request):
     if request.method == 'POST':
        role = request.POST['role']
        return render(request,'admin_dash/add_videos.html',{'role':role})






def upload_videos(request):
    if request.method == 'POST':

        role = request.POST.get('role', '').strip()
        title = request.POST.get('title', '').strip()
        video_file = request.FILES.get('video_file')


        if not title or not video_file:
            message = "Title and video file are required."
            return render(request, 'admin_dash/add_videos.html', {'message': message})


        role_model_map = {
            'python': PythonVideo,
            'SQL': SQLVideo,
            'java': JavaVideo,
        }


        model = role_model_map.get(role)
        if model:

            new_video = model(title=title, video_file=video_file)
            new_video.save()
            message = 'Your video has been uploaded successfully.'
        else:

            message = "Invalid role. Please choose a valid option."

        return render(request, 'admin_dash/add_videos.html', {'role': role, 'message': message})

    return render(request, 'admin_dash/admin_dash.html')



def deleteView_videos(request):
    if request.method == 'POST':

        role = request.POST.get('role', '').strip()


        role_model_map = {
            'python': PythonVideo,
            'SQL': SQLVideo,
            'java': JavaVideo,
        }


        model = role_model_map.get(role)
        if model:
            videos = model.objects.all()
            return render(request, 'admin_dash/delete_videos.html', {'role': role, 'videos': videos})
        else:
            message = "Invalid role. Please select a valid option."
            return render(request, 'admin_dash/delete_videos.html', {'message': message})


    return render(request, 'admin_dash/delete_videos.html')






def delete_videos(request):
    if request.method == 'POST':
        role = request.POST.get('role')
        video_id = request.POST.get('id')


        if not role or not video_id:
            return render(request, 'admin_dash/delete_videos.html', {'error': 'Role or ID is missing'})

        try:
            video_id = int(video_id)
        except ValueError:
            return render(request, 'admin_dash/delete_videos.html', {'error': 'Invalid ID format'})


        if role == 'java':
            video = get_object_or_404(JavaVideo, id=video_id)
        elif role == 'SQL':
            video = get_object_or_404(SQLVideo, id=video_id)
        elif role == 'python':
            video = get_object_or_404(PythonVideo, id=video_id)
        else:
            return render(request, 'admin_dash/delete_videos.html', {'error': 'Invalid role specified'})


        if video:
            file_field = getattr(video, 'video_file', None)

            if file_field and os.path.isfile(file_field.path):
                os.remove(file_field.path)

            video.delete()


        if role == 'java':
            videos = JavaVideo.objects.all()
        elif role == 'SQL':
            videos = SQLVideo.objects.all()
        elif role == 'python':
            videos = PythonVideo.objects.all()

        return render(request, 'admin_dash/delete_videos.html', {'role': role, 'videos': videos})

    return render(request, 'admin_dash/delete_videos.html')  # Handle GET requests






def view_grade(request):
    python_scores = PythonScore.objects.all()
    java_scores = JavaScore.objects.all()
    SQL_scores = SQLScore.objects.all()

    student_grades = {}

    for python_score in python_scores:
        user = python_score.user
        student_grades[user] = {
            'user': user,
            'python_score': f"{python_score.score}%",
            'SQL_score': None,
            'java_score': None,
        }

    for SQL_score in SQL_scores:
        user = SQL_score.user
        if user in student_grades:
            student_grades[user]['SQL_score'] = f"{SQL_score.score}%"
        else:
            student_grades[user] = {
                'user': user,
                'python_score': None,
                'SQL_score': f"{SQL_score.score}%",
                'java_score': None,
            }

    for java_score in java_scores:
        user = java_score.user
        if user in student_grades:
            student_grades[user]['java_score'] = f"{java_score.score}%"  # Add '%' to the score
        else:
            student_grades[user] = {
                'user': user,
                'python_score': None,
                'SQL_score': None,
                'java_score': f"{java_score.score}%",  # Add '%' to the score
            }

    student_grades_list = list(student_grades.values())

    return render(request, 'admin_dash/grades.html', {'student_grades': student_grades_list})

def   view_announcement(request):

    announcements = announc.objects.all()
    return render(request,'admin_dash/add_anouc.html',{'announcements':announcements})

def   add_Announcement(request):
    if request.method == 'POST':
        Content= request.POST['content']
        message = announc(contect=Content)
        message.save()
        announcements = announc.objects.all()
    return render(request,'admin_dash/add_anouc.html',{'announcements':announcements})

def   view_adminTest(request):
    if request.method == 'POST':
        role = request.POST['role']

        if role =='python':
            try:
               tests = testPython.objects.all()
               return render(request, 'admin_dash/adminTest_crud.html', {'role': role,'tests':tests})
            except testPython.DoesNotExist:
                return render(request, 'admin_dash/adminTest_crud.html', {'role': role,'tests':None})


        elif role =='SQL':
            try:
               tests = testSQL.objects.all()
               return render(request, 'admin_dash/adminTest_crud.html', {'role': role,'tests':tests})
            except  testSQL.DoesNotExist:
                return render(request, 'admin_dash/adminTest_crud.html', {'role': role,'tests':None})


        elif role =='java':
            try:
               tests = testJava.objects.all()
               return render(request, 'admin_dash/adminTest_crud.html', {'role': role,'tests':tests})
            except testJava.DoesNotExist:
                return render(request, 'admin_dash/adminTest_crud.html', {'role': role,'tests':None})


        else:
            return render(request,'admin_dash/admin_dash.html')
    return render(request,'admin_dash/admin_dash.html')



def delete_Announcement(request):
    if request.method == 'POST':
        id = request.POST.get('id')

        if not id:
            return render(request, 'admin_dash/add_anouc.html', {'error': 'Announcement ID is missing'})

        try:
            id = int(id)
        except ValueError:
            return render(request, 'admin_dash/add_anouc.html', {'error': 'Invalid ID format'})


        announcement = get_object_or_404(announc, id=id)
        announcement.delete()


        announcements = announc.objects.all()

        return render(request, 'admin_dash/add_anouc.html', {'announcements': announcements})


    announcements = announc.objects.all()
    return render(request, 'admin_dash/add_anouc.html', {'announcements': announcements})






def test_delete(request):
    if request.method == 'POST':
        role = request.POST.get('role')
        video_id = request.POST.get('id')

        if not role or not video_id:
            return render(request, 'admin_dash/adminTest_crud.html', {'error': 'Role or ID is missing'})

        try:
            video_id = int(video_id)
        except ValueError:
            return render(request, 'admin_dash/adminTest_crud.html', {'error': 'Invalid ID'})


        if role == 'java':
            test_to_delete = get_object_or_404(testJava, id=video_id)
            test_to_delete.delete()
            tests = testJava.objects.all()
        elif role == 'SQL':
            test_to_delete = get_object_or_404(testSQL, id=video_id)
            test_to_delete.delete()
            tests = testSQL.objects.all()
        elif role == 'python':
            test_to_delete = get_object_or_404(testPython, id=video_id)
            test_to_delete.delete()
            tests = testPython.objects.all()
        else:
            return render(request, 'admin_dash/adminTest_crud.html', {'error': 'Invalid role'})

        return render(request, 'admin_dash/adminTest_crud.html', {'role': role, 'tests': tests})


    return render(request, 'admin_dash/adminTest_crud.html', {'role': role})


def update_test(request):
    if request.method == 'POST':
        role = request.POST['role']
        id = request.POST.get('id')


        if role =='python':
            return render(request,'admin_dash/update_test.html',{'role': role,'id':id})

        elif role =='SQL':
            return render(request,'admin_dash/update_test.html',{'role': role,'id':id})

        elif role =='java':
            return render(request,'admin_dash/update_test.html',{'role': role,'id':id})

        else:
            return render(request,'admin_dash/admin_dash.html')
    return render(request, 'admin_dash/update_test.html',{'role': role} )




def update(request):
    role = None
    if request.method == 'POST':
        role = request.POST.get('role')
        id = request.POST.get('id')

    id = int(id)

    question = request.POST['question']
    option1 = request.POST['option1']
    option2 = request.POST['option2']
    option3 = request.POST['option3']
    option4 = request.POST['option4']
    correct_option = request.POST['correct-option']

    if role =='python':
        up = testPython.objects.get(id=id)
        up.Question = question
        up.Option1 = option1
        up.Option2 = option2
        up.Option3 = option3
        up.Option4 = option4
        up.CorrectOption = correct_option
        up.save()

        try:
            tests = testPython.objects.all()
        except testPython.DoesNotExist:
            return redirect('view_adminTest')
        return render(request, 'admin_dash/adminTest_crud.html', {'role': role,'tests':tests })

    elif role =='SQL':
        up = testSQL.objects.get(id=id)
        up.Question = question
        up.Option1 = option1
        up.Option2 = option2
        up.Option3 = option3
        up.Option4 = option4
        up.CorrectOption = correct_option
        up.save()

        try:
            tests = testSQL.objects.all()
        except testSQL.DoesNotExist:
            return redirect('view_adminTest')
        return render(request, 'admin_dash/adminTest_crud.html', {'role': role,'tests':tests })

    elif role =='java':
        up = testJava.objects.get(id=id)
        up.Question = question
        up.Option1 = option1
        up.Option2 = option2
        up.Option3 = option3
        up.Option4 = option4
        up.CorrectOption = correct_option
        up.save()

        try:
            tests = testJava.objects.all()
        except testJava.DoesNotExist:
            return redirect('view_adminTest')
        return render(request, 'admin_dash/adminTest_crud.html', {'role': role,'tests':tests })


    return render(request, 'admin_dash/adminTest_crud.html',{'role': role} )





#this is the user codes



def view_test(request):
    role = None
    if request.method == 'POST':
        role = request.POST.get('role')


    if role == 'java':
        tests = testJava.objects.all()
        return render(request, 'user_dash/view_test.html', {'role': role,'tests':tests})
    elif role == 'SQL':
        tests = testSQL.objects.all()
        return render(request, 'user_dash/view_test.html', {'role': role,'tests':tests})
    elif role == 'python':
        tests = testPython.objects.all()
        return render(request, 'user_dash/view_test.html', {'role': role,'tests':tests})


    return render(request, 'user_dash/view_test.html', {'role': role})

def view_score(request):
    role = None


    if request.method == 'POST':
        score = 0
        role = request.POST.get('role')

    if role == 'java':
        total_questions = testJava.objects.count()

        for test in testJava.objects.all():
            selected_answer = request.POST.get(str(test.id))
            if  int(selected_answer) == int(test.CorrectOption):
                score += 1

            percentage = (score / total_questions) * 100
            percentage =round(percentage,1)

        python_score, created  = JavaScore.objects.get_or_create(user=request.user)

        python_score.score =percentage
        python_score.save()

        return render(request, 'user_dash/view_score.html', {'role': role,'percentage':percentage,'score':score,'total_questions':total_questions})
    elif role == 'SQL':
        total_questions = testSQL.objects.count()
        for test in testSQL.objects.all():
            selected_answer = request.POST.get(str(test.id))
            if  int(selected_answer) == int(test.CorrectOption):
                score += 1

            percentage = (score / total_questions) * 100
            percentage =round(percentage,1)

        python_score, created  = SQLScore.objects.get_or_create(user=request.user)

        python_score.score =percentage
        python_score.save()
        return render(request, 'user_dash/view_score.html', {'role': role,'percentage':percentage,'score':score,'total_questions':total_questions})
    elif role == 'python':
        total_questions = testPython.objects.count()
        for test in testPython.objects.all():
            selected_answer = request.POST.get(str(test.id))
            if  int(selected_answer) == int(test.CorrectOption):
                score += 1

            percentage = (score / total_questions) * 100
            percentage =round(percentage,1)

        python_score, created  = PythonScore.objects.get_or_create(user=request.user)

        python_score.score =percentage
        python_score.save()
        return render(request, 'user_dash/view_score.html', {'role': role,'percentage':percentage,'score':score,'total_questions':total_questions})
    return render(request, 'user_dash/view_test.html')

def   view_videos(request):
     if request.method == 'POST':
        role = request.POST['role']

        if role=='java':
            videos = JavaVideo.objects.all()
            return render(request,'user_dash/view_videos.html',{'role':role,'videos':videos})
        elif role =='SQL':
            videos = SQLVideo.objects.all()
            return render(request,'user_dash/view_videos.html',{'role':role,'videos':videos})
        elif role == 'python':
            videos = PythonVideo.objects.all()
            return render(request,'user_dash/view_videos.html',{'role':role,'videos':videos})
        else:
            return render(request,'user_dash/view_videos.html',{'role':role})

def python_home(request):
    return render(request,'home/python.html')


def java_home(request):
    return render(request,'home/java.html')


def SQL_home(request):
    return render(request,'home/SQL.html')

def privacy_policy(request):
    return render(request, 'privacy_policy.html')

def about(request):
    return render(request, 'about.html')

def contact(request):
    return render(request, 'contact.html')








