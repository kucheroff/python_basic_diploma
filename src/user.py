from city import City
from hotel import Hotel
from req import req

class User:
    def __init__(self, cid, step):
        self.cid = cid
        self.step = step
        self.hotel = Hotel()
        self.city = City()

