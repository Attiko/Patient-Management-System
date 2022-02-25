import unittest
from main import app


class MyTestCase(unittest.TestCase):
    def test_Nurse_login(self):
        self.client = app.test_client()
        response = self.client.post(
            "/Dashboard",
            data=dict(id="9718", password="Donald123"),
            follow_redirects=True
        )
        self.assertIn(b'Welcome Nurse. Donald Nelson', response.data)

    def test_Doctor_login(self):
        self.client = app.test_client()
        response = self.client.post(
            "/Dashboard",
            data=dict(id="5562", password="Paul123"),  # Login details provided are correct
            follow_redirects=True
        )
        self.assertIn(b'Welcome Dr. Paul Simon', response.data)  # response page should contain a welcome message
        # if login is successful

    def test_incorrect_login(self):
        self.client = app.test_client()
        response = self.client.post(  # Attempt Login
            "/Dashboard",
            data=dict(id="9718", password="Donald234"),  # Login details provided are wrong
            follow_redirects=True
        )
        self.assertIn(b'Login failed, Incorrect ID or password!', response.data)  # statement should be found in
        # response data should include

    def test_Add_Staff(self):
        self.client = app.test_client()
        self.client.post(
            "/Dashboard",
            data=dict(id="9718", password="Donald123"),
            follow_redirects=True
        )
        response = self.client.post("/staffregisteration",

                                    data=dict(firstname="Jacob", lastname="Zuma", password="Jacob123",
                                              confirmpassword="Jacob123", date="24-1-1977", specialty="GP",
                                              stafftype="Doctor", gender="Male", number="07065567372",
                                              email="Teamkakapo5@gmial.com"),  # Login details provided are wrong
                                    # follow_redirects=True
                                    )
        self.assertIn(b'Login to your account', response.data)  # statement should be found in
        # response data should include

    def test_password_do_not_match(self):
        self.client = app.test_client()
        self.client.post(
            "/Dashboard",
            data=dict(id="9718", password="Donald123"),
            follow_redirects=True
        )
        response = self.client.post("/staffregisteration",

                                    data=dict(firstname="Jacob", lastname="Zuma", password="Jacob123",
                                              confirmpassword="Jacob122", date="24-1-1977",
                                              specialty="GP", stafftype="Doctor", gender="Male", number="07065567372",
                                              email="Teamkakapo5@gmial.com"),  # passwords provided do not match
                                    follow_redirects=True
                                    )
        self.assertIn(b'passwords do not match', response.data)  # statement should be found in
        # response data should include

    def test_Add_Patient(self):
        self.client = app.test_client()
        self.client.post(
            "/Dashboard",
            data=dict(id="9718", password="Donald123"),
            # Login
            follow_redirects=True
        )

        self.client.post(
            "/addPatient",
            data=dict(firstname="Jonathan", lastname="Miller", date="24-1-1977", gender="Male", ethnicity="White",
                      email="teamkakapo@gmail.com",
                      number="07065567372", address="England", symptoms="Leg pain", GP="Greg Thompson"),
            # Register Patient
            follow_redirects=True
        )

        response = self.client.get("/Patients")  # get all patients

        self.assertIn(b'Jonathan Miller', response.data)
        # patient should be found in the list of all patients if test works

    def test_logout(self):
        self.client = app.test_client()
        self.client.post(
            "/Dashboard",
            data=dict(id="9718", password="Donald123"),
            # Login
            follow_redirects=True
        )
        self.client.get('/logout')  # Then log out
        response = self.client.get("/doctor-dashboard")  # Attempt to route to the new admin page

        self.assertIn(b"You are not logged in. Log in to access this page", response.data)  # access is denied since
        # user is logged out


if __name__ == '__main__':
    unittest.main()
