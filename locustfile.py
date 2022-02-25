from locust import HttpUser, task, between


class WebsiteUser(HttpUser):
    wait_time = between(5, 15)

    def on_start(self):
        self.client.get("/")

    @task
    def nurse(self):
        self.client.post("/Dashboard", {
            "id": "9718",
            "password": "Donald123"
        })

        self.client.get("/Patients")

        self.client.get('/logout')

    @task
    def doctor(self):
        self.client.post("/Dashboard", {
            "id": "5562",
            "password": "Paul123"
        })

        self.client.get("/assignedPatients")

        self.client.get('/logout')







