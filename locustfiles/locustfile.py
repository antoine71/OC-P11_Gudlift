from locust import HttpUser, task, between


class QuickstartUser(HttpUser):

    wait_time = between(1, 2.5)

    @task
    def show_summary(self):
        # display tourament list
        self.client.get("/show_summary")

    @task
    def book_get(self):
        # display booking page a booking
        self.client.get("/book/Spring%2520Festival/Simply%2520Lift")

    @task
    def book_post(self):
        # performs a booking
        self.client.post("/book/Spring%2520Festival/Simply%2520Lift", data={'places': 1})

    @task
    def points(self):
        # display clubs list and updated points
        self.client.get("/points")

    def on_start(self):
        self.client.post("/", data={"email": "john@simplylift.co"})
