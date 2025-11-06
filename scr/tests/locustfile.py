from locust import HttpUser, task, between

class APIUser(HttpUser):
    wait_time = between(1, 3)

    @task(5)
    def predict(self):
        self.client.post("/predict", json={"features": [1,2,3]})