from locust import HttpUser, task, between


class QuickstartUser(HttpUser):

    wait_time = between(1, 2.5)

    @task
    def hello_world(self):
        self.client.get("/hello")

    @task
    def show_summary(self):
        self.client.get("/show_summary")

    @task
    def book(self):
        self.client.get("/book/Spring%2520Festival/Simply%2520Lift")

    @task
    def points(self):
        self.client.get("/points")

    def on_start(self):
        self.client.post("/", data={"email": "john@simplylift.co"})
