from django.test import TestCase, RequestFactory, Client
from django.contrib.auth.models import User
from .models import Person, Classes, Post
from .views import create_post, book_tutoring_session

class PassingTest(TestCase):
    def passingTest(self):
        self.assertEqual(True, True)

class PostTest(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.user = User.objects.create(username="testUsername", email="testEmail@gmail.com", password="testPassword")
        self.tutor = Person.objects.create(user=self.user, email="testEmail@gmail.com", first_name="fN", last_name="lN",
                                           about_me="aM", person_type="Tutor")
        self.dummyClass = Classes.objects.create(class_id="testID", name="testName", title="testTitle",
                                                 units="testUnits", section_type="testSec")
    def createSuccessfulTestPost(self):
        test_list = []
        test_classID = self.dummyClass.class_id
        # start = '2023-05-05 12:00:00+00:00'
        # end = '2023-05-05 14:00:00+00:00'
        request = self.factory.post("/create_post", {"class_id":test_classID, "hourly_fee":10,
                                                             "location":"testLoc", "online":test_list,
                                                             "contact_info":"testInfo", "comments":"testComment",
                                                             "start_time":'2023-05-05 12:00:00+00:00',
                                                             "end_time":'2023-05-05 14:00:00+00:00', "group_size":1})
        request.user = self.tutor
        response = create_post(request)
        self.assertEqual(response.status_code, 200)
    def createFailingTestPost(self): # for when times do not follow logic --> need to stay on modal
        test_list = []
        test_classID = self.dummyClass.class_id
        # start = '2023-05-05 12:00:00+00:00'
        # end = '2023-05-05 12:00:00+00:00'
        request = self.factory.post("/create_post", {"class_id":test_classID, "hourly_fee":10.00,
                                                     "location": "testLoc", "online":test_list,
                                                     "contact_info": "testInfo", "comments": "testComment",
                                                     "start-time": '2023-05-05 12:00:00+00:00',
                                                     "end-time": '2023-05-05 12:00:00+00:00', "group-size":1})
        request.user = self.tutor
        response = create_post(request)
        self.assertEqual(response.status_code, 200)

class SessionRequestTest(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.user1 = User.objects.create(username="testUsername1", email="testEmail1@gmail.com", password="testPassword1")
        self.tutor = Person.objects.create(user=self.user1, email="testEmail1@gmail.com", first_name="tutorFN",
                                           last_name="tutorLN", about_me="tutorAM", person_type="Tutor")
        self.dummyClass = Classes.objects.create(class_id="testID", name="testName", title="testTitle",
                                                 units="testUnits", section_type="testSec")
        self.user2 = User.objects.create(username="testUsername2", email="testEmail2@gmail.com",
                                         password="testPassword2")
        self.tutee = Person.objects.create(user=self.user2, email="testEmail2@gmail.com", first_name="tuteeFN", last_name="tuteeLN",
                                           about_me="tuteeAM", person_type="Tutee")
        self.dummyPost = Post.objects.create(classes=self.dummyClass, creatorEmail=self.tutor.email, creatorName=self.tutor.first_name,
                                             hash="someHash", hourly_fee=10.00, location="testLoc",
                                             online=False, contact_info="testInfo", comments="testComment", displayPost=True,
                                             max_capacity=1, current_capacity=0,
                                             sessionRangeStart='2023-05-05 12:00:00+00:00',
                                             sessionRangeEnd='2023-05-05 14:00:00+00:00')
    def createSuccessfulRequestTest(self):
        cEmail = self.dummyPost.creatorEmail
        pID = self.dummyPost.hash
        classTitle = self.dummyClass.title
        request = self.factory.post('/book_tutoring_session', {"creator-email":cEmail, "isGroup":True,
                                                               "isGroup":"false", "post-id":pID, "by_name":"True",
                                                               "searched":classTitle})
        request.user = self.tutee
        response = book_tutoring_session(request)
        self.assertEqual(response.status_code, 200)

class LoginLogoutTest(TestCase):
    def setUp(self):
        self.client = Client()
    def loginSuccessfulTest(self):
        response = self.client.post('/login_user', {"email":"testEmail@gmail.com", "password":"testPassword"})
        self.assertEqual(response.status_code, 302)
    def logoutSuccessfulTest(self):
        response = self.client.get('/logout_user')
        self.assertEqual(response.status_code, 302)
    def createAccountSuccessfulTest(self):
        response = self.client.post('/create_user', {"username":"testUN", "first_name":"testFN", "last_name":"testLN",
                                                     "email":"testEmail@gmail.com", "password":"testPassword",
                                                     "confirm_password":"testPassword"})
        self.assertEqual(response.status_code, 302)
