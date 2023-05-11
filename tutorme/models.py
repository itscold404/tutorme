from django.contrib import admin
from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MaxValueValidator
from django.contrib.postgres.fields import ArrayField

# Philosophy is to have two user types so that tutors can post hourly rates and courses they can tutor

# We use the default user object to tutorme, so making tutor/tutee objects will then pass the user object in
# as a parameter (using one-to-one methodology in Django)
# need variables for hourly rate and courses (diff hourly rates for diff courses?
# need variable for available time frames

#sources:
#https://docs.djangoproject.com/en/4.2/ref/models/fields/
#https://docs.djangoproject.com/en/4.2/topics/db/examples/many_to_many/
#https://docs.djangoproject.com/en/4.2/topics/db/examples/one_to_one/

class Person(models.Model):
    # username and password stored in User model by default
    TUTOR = 'Tutor'
    TUTEE = 'Tutee'
    NOT_DECIDED = 'Not_Decided'

    PERSON_TYPE_CHOICES = [
        (TUTOR, 'Tutor'),
        (TUTEE, 'Tutee'),
        (NOT_DECIDED, 'Not Decided'),
    ]

    person_type = models.CharField(
        max_length=11,
        choices=PERSON_TYPE_CHOICES,
        default=NOT_DECIDED,
    )

    user = models.OneToOneField(User, null=True, on_delete=models.CASCADE)
    first_name = models.CharField(max_length=30, blank=False, null=False)
    last_name = models.CharField(max_length=30, blank=False, null=False)
    email = models.EmailField(blank=False, null=False)
    about_me = models.CharField(max_length=500, default='')

    # TUTOR ONLY VALUES

    # TUTEE ONLY VALUES
    # booked_sessions stores the session in some form. maybe store post id or something similar
    # currently place holder. dont know to store string or max_length of string
    # should default value be [] or None? change to None if error occures

    @admin.display(
        ordering='email',
    )
    def __str__(self):
        person_info = "first name: " + self.first_name + "\n" + \
            "last name: " + self.last_name + "\n" + "email: " + self.email

        return person_info


class Classes(models.Model):
    class_id = models.CharField(max_length=50, primary_key=True)
    name = models.CharField(max_length=50)
    title = models.CharField(max_length=100)
    units = models.CharField(max_length=10)
    section_type = models.CharField(max_length=50)

    def __str__(self) -> str:
        return self.class_id + ": " + self.title


class Post(models.Model):
    # RETRIEVE SET OF TUTEES FROM POST: post.enrolled_tutee.all()
    # RETRIEVE SET OF POSTS FROM TUTEE: tutee.post_set.all()
    enrolled_tutee = models.ManyToManyField(Person)
    classes = models.ForeignKey(Classes, on_delete=models.CASCADE)

    # tutor/creator email is main link to tutor that created post
    creatorEmail = models.EmailField(blank=False, null=True)
    creatorName = models.CharField(max_length=500, default="")


    # concatinate sessionRangeStart and sessionRangeEnd (separated by one space) to make some kind of unique identifier for
    # posts tutors make(need condition to make it so that tutors cannot create tutoring sessions)
    # within same time range
    hash = models.CharField(max_length=100)

    # keep track of which tutees booked this session. Posts has a record of tutee and tutee has record of post

    hourly_fee = models.DecimalField(decimal_places=2, max_digits=5)
    location = models.CharField(max_length=150)

    # not sure how to deal with same person want to be both tutor and tutee yet
    online = models.BooleanField(default=False)

    # contact_info for any contact details (phone number, email, discord, etc.)
    contact_info = models.CharField(max_length=150)

    # create field for timeframe (is there a models.TimeField?)
    # comments for anything else that the poster wants to let the reader know
    comments = models.CharField(max_length=500)

    # post initally on display. when fully booked, display_post = False
    display_post = models.BooleanField(default=True)

    # default tutor session is one-on-one(capacity = 1). max capacity is 5 tutee per session
    max_capacity = models.IntegerField(
        default=1, validators=[MaxValueValidator(5)])
    current_capacity = models.IntegerField(default=0)

    # store range (start and end of session)
    sessionRangeStart = models.DateTimeField(null=True)
    sessionRangeEnd = models.DateTimeField(null=True)

    def __str__(self) -> str:
        tutor = Person.objects.get(email=self.creatorEmail)
        return tutor.first_name + tutor.last_name + ": " + self.classes.name + \
            "\n $" + str(self.hourly_fee) + "/hr " + self.location + " --- " + str(self.online) + \
            " " + self.contact_info + "\n"


class Session_Request(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    tutee = models.ForeignKey(Person, on_delete=models.CASCADE)
    creator_email = models.EmailField(blank=False, null=True)
    # pending or declined. accepted goes into scheduled sessions
    status = models.CharField(default="pending", max_length=10)
    tutor_message = models.CharField(default="", max_length=500)
    sessionStart = models.DateTimeField(null=True)
    sessionEnd = models.DateTimeField(null=True)


class Notification(models.Model):
    is_read = models.BooleanField(default=False)
    message = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    creatorEmail = models.EmailField(blank=False, null=True)
    recipientEmail = models.EmailField(blank=False, null=True)
    id = models.AutoField(primary_key=True)
