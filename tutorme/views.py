from datetime import datetime, timedelta

from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, reverse, HttpResponseRedirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from tutorme.models import Classes, Person, Post, Session_Request, Notification
from django.contrib import messages
import requests


sis_url = "https://sisuva.admin.virginia.edu/psc/ihprd/UVSS/SA/s/WEBLIB_HCX_CM.H_CLASS_SEARCH.FieldFormula.IScript_ClassSearch?institution=UVA01&term=1238"

#SOURCE:
#https://docs.python.org/3/library/datetime.html
def __get_person(request):
    if (str(request.user) == 'AnonymousUser'):
        return ""
    else:
        email = request.user.email
        return Person.objects.get(email=email)


# /social/signup wont redirect to login page
def signup_redirect(request):
    messages.error(request, "This email is already being used.")
    return HttpResponseRedirect(reverse("tutorme:login_user"))

@login_required(login_url='/login_user')
def start(request):
    # loads landing page
     return render(request, "home/landing_page.html", {})


def login_user(request):
    # lets user log in with both account created on website or google oauth

    # if user is logged in, redirect to choose_user_type page.
    # request.user.is_authenticated == True for successful google oauth login
    if request.user.is_authenticated:
        return redirect(reverse("tutorme:choose_user_type"))

    else:
        if request.method == "POST":
            # user email is username
            username = request.POST["email"]
            password = request.POST["password"]

            # authenticate with username and password
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, "Logged in as " + user.first_name + ".")
                # send user to choose tutor/tutee option which will redirect to correct home page
                return redirect(reverse("tutorme:choose_user_type"))
            else:
                messages.error(
                    request,
                    "Login failed due to incorrect username or password. Please try again.",
                )
                return redirect("tutorme:login_user")
        else:
            return render(request, "login/login.html", {})


def __createClass(c):
    Classes(
        c["subject"] + c["catalog_nbr"] + c["section_type"],
        c["subject"] + " " + c["catalog_nbr"],
        c["descr"],
        c["units"],
        c["section_type"],
    ).save()


def reset():  # cleaning out all classes and adding them all in
    Classes.objects.all().delete()
    depts = "AAS,ACCT,AIRS,ALAR,AM,AMST,ANTH,APMA,ARAB,ARAD,ARAH,ARCH,ARCY,ARH,ARTH,ARTR,ARTS,ASL,ASTR,BENG,BIMS,BIOC,BIOE,BIOL,BIOM,BIOP,BME,BUS,CASS,CE,CELL,CHE,CHEM,CHIN,CHTR,CJ,CLAS,COGS,COLA,COMM,CONC,CPE,CPLT,CREO,CS,DANC,DEM,DH,DRAM,DS,EALC,EAST,ECE,ECON,EDHS,EDIS,EDLF,EDNC,EGMT,ELA,ENAM,ENCR,ENCW,ENEC,ENGL,ENGN,ENGR,ENLS,ENMC,ENMD,ENNC,ENPG,ENPW,ENRN,ENSP,ENTP,ENVH,ENWR,EP,ESL,ETP,EURS,EVAT,EVEC,EVGE,EVHY,EVSC,FORU,FREN,FRLN,FRTR,GBAC,GBUS,GCCS,GCNL,GCOM,GDS,GERM,GETR,GHSS,GNUR,GREE,GSAS,GSCI,GSGS,GSMS,GSSJ,GSVS,HBIO,HEBR,HETR,HHE,HIAF,HIEA,HIEU,HILA,HIME,HIND,HISA,HIST,HIUS,HR,HSCI,HUMS,IHGC,IMP,INST,ISBU,ISCP,ISED,ISHU,ISIN,ISLS,ISSS,IT,ITAL,ITTR,JAPN,JPTR,JWST,KICH,KINE,KLPA,KOR,KRTR,LAR,LASE,LAST,LATI,LAW,LING,LNGS,LPPA,LPPL,LPPP,LPPS,MAE,MATH,MDST,MED,MESA,MEST,MICR,MISC,MSE,MSP,MUBD,MUEN,MUPF,MUSI,NASC,NCAR,NCBM,NCBS,NCCJ,NCCS,NCDS,NCED,NCEN,NCFA,NCFL,NCHP,NCIS,NCLE,NCPD,NCPH,NCPR,NCSS,NCTH,NESC,NMVS,NUCO,NUIP,NURS,PASH,PATH,PAVS,PC,PERS,PETR,PHAR,PHIL,PHS,PHY,PHYS,PLAC,PLAD,PLAN,PLAP,PLCP,PLIR,PLPT,PLSK,PMCC,POL,PORT,POTR,PPL,PSCJ,PSED,PSHM,PSHP,PSLP,PSLS,PSPA,PSPL,PSPM,PSPS,PSSS,PST,PSTS,PSWD,PSYC,RELA,RELB,RELC,RELG,RELH,RELI,RELJ,RELS,RSC,RUSS,RUTR,SANS,SARC,SAST,SATR,SEC,SEMS,SLAV,SLFK,SLTR,SOC,SPAN,SPTR,STAT,STS,SWAH,SYS,TBTN,TURK,UD,UKR,UNST,URDU,USEM,WGS,XHOS,YIDD,YITR,ZFOR"
    deptList = depts.split(",")
    for det in deptList:
        print("Adding " + det)
        __add_classes(det)


def __add_classes(dept, cat_num):
    exact = []
    page = 1
    while True:
        searched = requests.get(
            sis_url + "&page=" + str(page) + "&subject=" + dept
        ).json()
        if len(searched) == 0:
            break
        exact += searched
        page += 1
    for c in exact:
        __createClass(c)

    exact = []
    page = 1
    while True:
        searched = requests.get(
            sis_url + "&page=" + str(page) + "&catalog_nbr=" + cat_num
        ).json()
        if len(searched) == 0:
            break
        exact += searched
        page += 1
    for c in exact:
        __createClass(c)


def __search_classes(dept, cat_num, course_name):
    # return list of classes objects if exists in database
    # else, create list of classes objects and return it
    # adds classes to database if not already in database

    if course_name:
        classes = Classes.objects.filter(title__icontains=course_name)
        name_list = course_name.split(" ")
        

        if len(classes) == 0: # check for stored classes with titles that are pieces of the searched
                for word in name_list:
                    classes = classes | (Classes.objects.filter(title__icontains=word))
                
        if len(classes) == 0:  # check sis
            exact = []
            page = 1
            searched_name = name_list[0]
            for i in range(1, len(name_list)):
                searched_name = searched_name + "_" + name_list[i]
            while True:
                searched = requests.get(
                        sis_url + "&page=" + str(page) + "&keyword=" + searched_name
                        ).json()
                if len(searched) == 0:
                    break
                exact += searched
                page += 1
            for c in exact:
                __createClass(c)
                classes = Classes.objects.filter(title=course_name)

        if len(classes) ==0:  # query api with pieces of the searched
            exact = []
            page = 1
            for word in name_list:
                while len(searched) == 0:
                    searched = requests.get(
                        sis_url + "&page=" + str(page) + "&keyword=" + word
                        ).json()
                    print("querying ", word)
                    print("searcged is ", len(searched), " items long")
                    if len(searched) == 0:
                        break
                    exact += searched
                    page += 1
                for c in exact:
                    __createClass(c)
                    classes = classes | Classes.objects.filter(title__icontains=word)

                        

    else:
        classes = Classes.objects.filter(class_id__icontains=dept + cat_num).order_by(
            "class_id"
        )
        print("there are ", len(classes), " with the dept ", dept)
        if len(classes) == 0:  # class not found --> Check API
            __add_classes(dept, cat_num)
            classes = (
                Classes.objects.filter(class_id__icontains=dept + cat_num).order_by(
                    "class_id"
                )
                | Classes.objects.filter(class_id__icontains=dept).order_by("class_id")
                | Classes.objects.filter(class_id__icontains=cat_num).order_by(
                    "class_id"
                )
            )

    return classes[:500]


def __search_posts(dept, cat_num, course_name, filter_by_date):
    classes = __search_classes(dept, cat_num, course_name)
    posts = set()
    for cl in classes:
        if not filter_by_date:
            for p in Post.objects.filter(classes=cl):
                posts.add(p)

        if filter_by_date:
            utc_time = datetime.utcnow()
            local_time = utc_time - timedelta(hours=4)
            for p in Post.objects.filter(
                classes=cl, sessionRangeEnd__gte=local_time
            ):
                posts.add(p)
    return list(posts)


def search(request):
    # search for classes using __search_classes()
    # and render it to search_class page if Tutor
    # or render it to search_post page if Tutee
    print("this is user", request.user)
    if (str(request.user) == 'AnonymousUser'):
        print("entered if")
        return HttpResponseRedirect(reverse("tutorme:login_user"))
    else:
        email=request.user.email
        unread_notifications = Notification.objects.filter(
            recipientEmail=email, is_read=False
        )

        if request.method == "POST":
            by_name = False
            course_name = request.POST["course_name_searched"]
            dept, cat_num = request.POST["dept_searched"], request.POST["catalog_searched"]
            if course_name:
                searched = course_name
                by_name = True  # search was based on course_name, refer to this value rather than dept and cat_num
            else:
                searched = dept + " " + cat_num

            already_requested_posts = set()
            registered_person = __get_person(request)
            if registered_person.person_type == "Tutor":
                classes = __search_classes(dept, cat_num, course_name)
                return render(
                    request,
                    "home/search_classes.html",
                    {
                        "searched": searched,
                        "classes": classes,
                        "by_name": by_name,
                        "already_requested_posts": already_requested_posts,
                        "unread_notifications": unread_notifications,
                    },
                )
            elif registered_person.person_type == "Tutee":
                filter_by_date = True
                posts = __search_posts(dept, cat_num, course_name, filter_by_date)
                booked_posts = (
                    registered_person.post_set.all()
                )  # posts booked by this tutee specifically, not overall
                print("booked posts: ", booked_posts)
                for p in posts:
                    if (
                        len(Session_Request.objects.filter(post=p, tutee=registered_person))
                        != 0
                    ):
                        already_requested_posts.add(p)

                return render(
                    request,
                    "home/search_posts.html",
                    {
                        "searched": searched,
                        "posts": posts,
                        "by_name": by_name,
                        "already_requested_posts": already_requested_posts,
                        "booked_posts": booked_posts,
                        "unread_notifications": unread_notifications,
                    },
                )

        else:
            return redirect(reverse("tutorme:home"))


def go_home(request):
    # goes to home page depending on role of user (tutor/tutee)
    print("this is user", request.user)
    if (str(request.user) == 'AnonymousUser'):
        print("entered if")
        return HttpResponseRedirect(reverse("tutorme:login_user"))
    else:
        
        email = request.user.email
        registered_person = Person.objects.get(email=email)
        utc_time = datetime.utcnow()
        local_time = utc_time - timedelta(hours=4)

    # if already selected Tutor/Tutee redirect to home page else go to login page
        if registered_person.person_type == "Tutor":
        # display only pending requests on the tutor page
            all_posts = Post.objects.filter(creatorEmail=email, sessionRangeEnd__gte = local_time)
        
            for p in all_posts:
                print(p.sessionRangeEnd)
            session_request_list = Session_Request.objects.filter(
                creator_email=email, status="pending"
            )

        # create a list nested in another list. inner list will contain tutee objects for individual posts. outer list
        # contains lists of all tutee objects of all posts
        # example: [ [bob, joe], [kenny, joe], [billy] ]
        # list_of_lists_tutee_in_each_post = []

        # for each_post in all_posts:
        #     tutee_list_for_each_post = each_post.enrolled_tutee.all()
        #     list_of_lists_tutee_in_each_post.append(tutee_list_for_each_post)

            unread_notifications = Notification.objects.filter(
                recipientEmail=email, is_read=False
            )

            return render(
                request,
                "home/tutor_homepage.html",
                {"posts": all_posts, "session_request_list": session_request_list, "unread_notifications": unread_notifications,},
            )

        elif registered_person.person_type == "Tutee":
            tutee = Person.objects.get(email=email)
            declined_sessions_list = Session_Request.objects.filter(
                tutee=tutee, status="declined"
            )
            pending_sessions_list = Session_Request.objects.filter(
                tutee=tutee, status="pending"
            )
            approved_sessions_list = tutee.post_set.all()
        
            approved_sessions_filtered = approved_sessions_list.filter(sessionRangeEnd__gte=local_time)

            unread_notifications = Notification.objects.filter(
                recipientEmail=email, is_read=False
            )

            return render(
                request,
                "home/tutee_homepage.html",
                {
                    "declined_sessions_list": declined_sessions_list,
                    "approved_sessions_list": approved_sessions_filtered,
                    "pending_sessions_list": pending_sessions_list,
                    "unread_notifications": unread_notifications,
                },
            )

        else:
            return redirect(reverse("tutorme:login"))


def create_post(request):
    print("this is user", request.user)
    if (str(request.user) == 'AnonymousUser'):
        print("entered if")
        return HttpResponseRedirect(reverse("tutorme:login_user"))
    else:
        if request.method == "POST":
            email = request.user.email
            # TODO: not sure how to pass in the class_id from the modal
            classes = Classes.objects.get(class_id=request.POST["class_id"])
            hourly_fee = request.POST["hourly_fee"]
            print("this is da hourly_fee inputted ", hourly_fee)
            location = request.POST["location"]
            online = len(request.POST.getlist("online")) == 1
            contact_info = request.POST["contact_info"]
            comments = request.POST["comments"]
            creatorName = (
                Person.objects.get(email=email).first_name
                + " "
                + Person.objects.get(email=email).last_name
            )
            start = request.POST["start-time"]
            end = request.POST["end-time"]
            group_size = request.POST["group-size"]
            hash = str(start) + " " + str(end)

            if (
                Post.objects.filter(
                    creatorEmail=email, sessionRangeStart=start, sessionRangeEnd=end
                ).exists()
                == False
            ):
                post = Post(
                    creatorEmail=email,
                    creatorName=creatorName,
                    hash=hash,
                    max_capacity=group_size,
                    classes=classes,
                    hourly_fee=hourly_fee,
                    online=online,
                    contact_info=contact_info,
                    comments=comments,
                    sessionRangeStart=start,
                    sessionRangeEnd=end,
                    location=location,
                )
                post.save()
                print("this is da hourly_fee saved ", post.hourly_fee)
                messages.success(request, "Post successfully created.")
                
            elif(Post.objects.filter(
                    creatorEmail=email, sessionRangeStart=start, sessionRangeEnd=end
                ).exists()
                == True):
                messages.error(
                    request,
                    "Failed to create post: post with same start and end session time already exists.",
                )

        return go_home(request)


def book_tutoring_session(request):
    # create session_request object to be approved by tutor when tutee books session
    print("this is user", request.user)
    if (str(request.user) == 'AnonymousUser'):
        print("entered if")
        return HttpResponseRedirect(reverse("tutorme:login_user"))
    else:
        if request.method == "POST":
            tutor_email = request.POST["creator-email"]
            tutee = __get_person(request)
            tutee_email = request.user.email
            isGroup = request.POST["isGroup"]
            hash = request.POST["post-id"]
            by_name = request.POST["by_name"]
            print("hash is", hash)
            print("tutor email is", tutor_email)

            # getting information to reload page
            searched = request.POST["searched"]

            if (
                by_name == "True"
            ):  # give course_name a value only if posts were searched by name (passed thru html it becomes a str not bool)
                course_name = searched
                dep = ""
                cat_num = ""
            # if a tutee tries to book the same session twice, then no posts will show up after reload, not sure how to fix
            # but we probably shouldnt show posts tutees have already tried to book
            else:
                course_name = ""
                loc = searched.find(" ")
                dep = searched[0:loc]
                cat_num = searched[loc + 1 : len(searched) - 1]
                by_name = False

            # only show posts that have end date/time later than curret date/time
            posts = __search_posts(dep, cat_num, course_name, True)

            currentTime = (
                (datetime.utcnow()) - (timedelta(hours=4))
            ).strftime("%m/%d/%Y, %I:%M:%S %p")
            #source: https://stackoverflow.com/questions/11710469/how-to-get-python-to-display-current-time-eastern
            booked_session_post = Post.objects.get(creatorEmail=tutor_email, hash=hash)
            Notification.objects.create(
                message=tutee_email
                + " has requested a session with you! "
                + ((datetime.utcnow()) - (timedelta(hours=4))).strftime(
                    "%m/%d/%Y, %I:%M:%S %p"
                ),
                creatorEmail=tutee_email,
                recipientEmail=tutor_email,
            )

            if isGroup == "false":
                print("nope not group")
                requested_start_time = request.POST["session-start-time"]
                print("-----------------------------time", requested_start_time)
                requested_end_time = request.POST["session-end-time"]
                print("-----------------------------time", requested_end_time)

                if (
                    Session_Request.objects.filter(
                        post=booked_session_post, tutee=tutee, creator_email=tutor_email
                    ).exists()
                    == False
                ):
                    session_request = Session_Request(
                        post=booked_session_post,
                        tutee=tutee,
                        creator_email=tutor_email,
                        sessionStart=requested_start_time,
                        sessionEnd=requested_end_time,
                    )
                    session_request.save()
                    messages.success(request, "Session request sent.")

                    print(
                        "session request created for tutee with email of",
                        session_request.tutee.email,
                    )

            if isGroup == "true":
                print("yup is group")
                if (
                    Session_Request.objects.filter(
                        post=booked_session_post, tutee=tutee, creator_email=tutor_email
                    ).exists()
                    == False
                ):
                    session_request = Session_Request(
                        post=booked_session_post,
                        tutee=tutee,
                        creator_email=tutor_email,
                        sessionStart=booked_session_post.sessionRangeStart,
                        sessionEnd=booked_session_post.sessionRangeEnd,
                    )
                    session_request.save()
                    messages.success(request, "Session request sent.")

                    print(
                        "session request created for tutee with email of",
                        session_request.tutee.email,
                    )

            # create already_requested_posts again because when its passed from html it becomes a string
            already_requested_posts = set()
            booked_posts = tutee.post_set.all()
            for p in posts:
                if len(Session_Request.objects.filter(post=p, tutee=tutee)) != 0:
                    already_requested_posts.add(p)
            return render(
                request,
                "home/search_posts.html",
                {
                    "searched": searched,
                    "posts": posts,
                    "already_requested_posts": already_requested_posts,
                    "booked_posts": booked_posts,
                },
            )

        return go_home(request)


def approve_session_request(request):
    print("approving sessions now")
    if request.method == "POST":
        tutee_email = request.POST["tutee-email"]
        tutor_email = request.POST["tutor-email"]
        hash = request.POST["post-id"]
        tutee = Person.objects.get(email=tutee_email)
        post = Post.objects.filter(creatorEmail=tutor_email, hash=hash).first()
        session = Session_Request.objects.get(tutee=tutee, post=post)
        currentTime = (
            (datetime.utcnow()) - (timedelta(hours=4))
        ).strftime("%m/%d/%Y, %I:%M:%S %p")
        if "approve" in request.POST:
            print("session was approved")

            # #tutee now able to access all their posts using post_set.all()
            post.enrolled_tutee.add(tutee)

            # #updating the Post object's capacity and tutees enrolled
            post.current_capacity = len(post.enrolled_tutee.all())

            if post.max_capacity == 1:
                post.sessionRangeStart = session.sessionStart
                post.sessionRangeEnd = session.sessionEnd

            post.save()
            session.delete()

            Notification.objects.create(
                message=tutor_email
                + " has approved your session request! "
                + (
                    (datetime.utcnow()) - (timedelta(hours=4))
                ).strftime("%m/%d/%Y, %I:%M:%S %p"),
                creatorEmail=tutor_email,
                recipientEmail=tutee_email,
            )
            messages.success(request, "Session approved.")
            print(post.enrolled_tutee.all())

        elif "deny" in request.POST:
            messages.success(request, "Session declined.")
            post.display_post = False
            session.status = "declined"
            # declined_session.tutor_message = rejection_explanation

            Notification.objects.create(
                message=tutor_email
                + " has denied your session request. "
                + (
                    (datetime.utcnow()) - (timedelta(hours=4))
                ).strftime("%m/%d/%Y, %I:%M:%S %p"),
                creatorEmail=tutor_email,
                recipientEmail=tutee_email,
            )
            session.save()
            post.save()
            print("reason was", session.tutor_message)

    return go_home(request)


def delete_session_request(request):
    print("delete button pressed")
    if request.method == "POST":
        print("method is a post")
        if "delete" in request.POST:
            print("delete button recognized")
            tutee_email = request.POST["tutee-email"]
            print("tutee email:", tutee_email)
            tutor_email = request.POST["tutor-email"]
            print("tutor email:", tutor_email)
            hash = request.POST["post-id"]
            tutee = Person.objects.get(email=tutee_email)
            currentTime = (
                (datetime.utcnow()) - (timedelta(hours=4))
            ).strftime("%m/%d/%Y, %I:%M:%S %p")
            post = Post.objects.filter(creatorEmail=tutor_email, hash=hash).first()
            if post.display_post == True:
                Notification.objects.create(
                    message=tutee_email
                    + " has deleted their session request. "
                    + (
                        (datetime.utcnow()) - (timedelta(hours=4))
                    ).strftime("%m/%d/%Y, %I:%M:%S %p"),
                    creatorEmail=tutee_email,
                    recipientEmail=tutor_email,
                )

            session_to_delete = Session_Request.objects.get(tutee=tutee, post=post)
            # print("session with", session_to_delete.creator_email, "is being deleted")
            session_to_delete.delete()
            # print("session deleted")
            messages.success(request, "Session request deleted.")

    return go_home(request)


def choose_user_type(request):
    # calls create_person_object() to create a new Person object if the object does not exist
    # else, let the user select the role(tutor/tutee) they want to be if their role is Not_Decided
    # redirect to tutor/tutee home page

    # keep create_person_object code seperate from choose_user_type
    # error of not being able to find newly created person if create_person_object
    # code is put here

    if str(request.user) == 'AnonymousUser':
        return redirect(reverse("tutorme:login_user"))
    
    else:
        create_person_object(request)
        registered_person = __get_person(request)

        # if already selected Tutor/Tutee redirect to home page
        # messages.success(
        #     request, 'Successfully logged in as ' + request.user.first_name + '!')
        if registered_person.person_type in ["Tutor", "Tutee"]:
            return redirect(reverse("tutorme:home"))

        # assign person as tutor/tutee upon submission of role they want to be
        if request.method == "POST":
            user_type = request.POST["user_type"]
            registered_person = __get_person(request)

            if user_type == "tutee":
                registered_person.person_type = "Tutee"
                registered_person.save()
            else:
                registered_person.person_type = "Tutor"
                registered_person.save()

            return redirect(reverse("tutorme:home"))

        # if person has not decided or their role is Not_decided,
        # show them the choose_user_type page and let them select role
        else:
            return render(request, "login/choose_user_type.html", {})


def logout_user(request):
    logout(request)
    return redirect(reverse("tutorme:login_user"))


def create_person_object(request):
    # if the PERSON object is not registered in the database, create
    # a new PERSON object using the USER object and store in database
    print("this is user", request.user)
    if (str(request.user) == 'AnonymousUser'):
        print("entered if")
        return HttpResponseRedirect(reverse("tutorme:login_user"))
    else:
        email = request.user.email
        first_name = request.user.first_name
        last_name = request.user.last_name

        if Person.objects.filter(email=email).exists() == False:
            new_person = Person(first_name=first_name, last_name=last_name, email=email)
            new_person.save()


def change_user_type(request):
    theUser = __get_person(request)
    
    if str(request.user) == 'AnonymousUser':
        return redirect(reverse("tutorme:login_user"))
    else:
        if theUser.person_type == "Tutee":
            theUser.person_type = "Tutor"
            theUser.save()
            messages.success(request, "You are now a tutor.")
        else:
            theUser.person_type = "Tutee"
            theUser.save()
            messages.success(request, "You are now a tutee.")
        return redirect(reverse("tutorme:profile"))


def get_user_type(request):
    if str(request.user) == 'AnonymousUser':
        return redirect(reverse("tutorme:login_user"))
    else:
        if request.method == "POST":
            registered_person = __get_person(request)
            if registered_person == "":
                return redirect(reverse("tutorme:login_user"))
            else:
                user_type = registered_person.person_type
                return render(request, "home/home.html", {"user_type": user_type})

        else:
            return go_home(request)


def go_profile(request):
    theUser = __get_person(request)
    if str(request.user) == 'AnonymousUser':
        return redirect(reverse("tutorme:login_user"))
    else:

        user_type = theUser.person_type
        first_name = theUser.first_name
        last_name = theUser.last_name
        about_me = theUser.about_me
        email = theUser.email
        unread_notifications = Notification.objects.filter(
            recipientEmail=email, is_read=False
        )

        if user_type == "Tutor":
            posts = set()
            utc_time = datetime.utcnow()
            local_time = utc_time - timedelta(hours=4)
            for p in Post.objects.filter(
                creatorEmail = email, sessionRangeEnd__gte=local_time
                ):
                posts.add(p)
        
            print("the posts ", posts)
            return render(
                request,
                "profile/tutor_profile.html",
                {
                    "user_type": user_type,
                    "first_name": first_name,
                    "last_name": last_name,
                    "about_me": about_me,
                    "email": email,
                    "posts": posts,
                    "unread_notifications": unread_notifications,
                },
            )

        else:
            return render(
                request,
                "profile/profile.html",
                {
                    "user_type": user_type,
                    "first_name": first_name,
                    "last_name": last_name,
                    "about_me": about_me,
                    "email": email,
                    "unread_notifications": unread_notifications,
                },
            )


def getPosts(request):
    theUser = __get_person(request)
    if str(request.user) == 'AnonymousUser':
        return redirect(reverse("tutorme:login_user"))
    else:

        posts = Post.objects.filter(creatorEmail=theUser.email)
        return render(request, "profile/tutor_profile.html", {"posts": posts})


def edit_posts(request):
    # need to add checks for max attribute size
    theUser = __get_person(request)
    if str(request.user) == 'AnonymousUser':
        return redirect(reverse("tutorme:login_user"))
    else:
        if request.method == "POST":
            if request.POST["hash"]:
                post = Post.objects.get(hash=request.POST["hash"])
                if request.POST["hourly_fee"]:
                    post.hourly_fee = request.POST["hourly_fee"]
                if request.POST["location"]:
                    post.location = request.POST["location"]
                online = len(request.POST.getlist("online")) == 1
                post.online = online
                if request.POST["contact_info"]:
                    post.contact_info = request.POST["contact_info"]
                if request.POST["comments"]:
                    post.comments = request.POST["comments"]
                if request.POST["group-size"]:
                    post.max_capacity = request.POST["group-size"]

                post.save()
                messages.success(request, "Post changes successfully saved.")

        return go_profile(request)


def edit_user(request):
    print("USER EDITING")
    theUser = __get_person(request)
    if str(request.user) == 'AnonymousUser':
        return redirect(reverse("tutorme:login_user"))
    else:
        if request.method == "POST":  # form to change user vals submitted
            # only change if somethign was added to the form
            change_fName = False
            change_Lname = False
            if request.POST["first_name"] and len(request.POST["first_name"]) < 31:
                theUser.first_name = request.POST["first_name"]
                change_fName = True
                
            if request.POST["last_name"] and len(request.POST["last_name"]) < 31:
                theUser.last_name = request.POST["last_name"]
                change_Lname = True
            if request.POST["about_me"] and len(request.POST["about_me"]) < 501:
                theUser.about_me = request.POST["about_me"]
            if change_Lname or change_fName:
                for p in Post.objects.filter(creatorEmail = theUser.email):
                    curName = p.creatorName
                    
                    curName = curName.split()
                    
                    
                    fname = curName[0]
                    Lname = curName[1]
                    if change_Lname:
                        Lname = request.POST["last_name"]
                    if change_fName:
                        fname = request.POST["first_name"]
                    p.creatorName = fname + " " + Lname
                    p.save()
                    
            theUser.save()
            messages.success(request, "Account changes successfully saved.")
            return go_profile(request)
        else:
            return go_profile(request)


def create_user(request):
    # creates User object using information in sign up page

    if request.method == "POST":  # form submitted
        username = request.POST["email"]
        first_name = request.POST["first_name"]
        last_name = request.POST["last_name"]
        email = request.POST["email"]

        # passwords match -- attempt to create a new account
        if request.POST["password"] == request.POST["confirm_password"]:
            # need to have unique username and email address
            if User.objects.filter(email=email).count() == 0:
                user = User.objects.create_user(
                    username=username,
                    email=email,
                    password=request.POST["password"],
                    first_name=first_name,
                    last_name=last_name,
                )
                user.save()
                messages.success(request, "Account successfully created.")
                return redirect(reverse("tutorme:login_user"))
            else:
                messages.error(
                    request,
                    "An account already exists with given username and/or email. Please try another!",
                )
                return redirect(reverse("tutorme:create_user"))

        # passwords do not match -- display error message
        else:
            messages.error(request, "Passwords do not match.")
            return redirect(reverse("tutorme:create_user"))
    else:
        return render(request, "login/creation_form.html", {})


def go_mailbox(request):
    print("this is user", request.user)
    if (str(request.user) == 'AnonymousUser'):
        print("entered if")
        return HttpResponseRedirect(reverse("tutorme:login_user"))
    else:
        model = Notification
        email = request.user.email
        unread_notifications = Notification.objects.filter(
            recipientEmail=email, is_read=False
        ).order_by("-timestamp")
        return render(
            request, "home/mailbox.html", {"unread_notifications": unread_notifications}
        )


def read_notification(request, id):
    print("this is user", request.user)
    if (str(request.user) == 'AnonymousUser'):
        print("entered if")
        return HttpResponseRedirect(reverse("tutorme:login_user"))
    else:
        notification = Notification.objects.filter(id=id).first()
        if notification != None:
            notification.is_read = True
            notification.save()
            notification.delete()
        email = request.user.email
        # print(notification.is_read)

        unread_notifications = Notification.objects.filter(
            recipientEmail=email, is_read=False
        ).order_by("-timestamp")
        return render(
            request, "home/mailbox.html", {"unread_notifications": unread_notifications}
        )
