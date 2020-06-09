# Academic Staff class
class Academic_Staff:
    academic_staff = None

    def __init__(self, name):
        self.name = name

    @staticmethod
    def search(name):
        for i in range(len(Professor.professors)):
            if Professor.professors[i].name == name:
                return i
        return -1

    def __repr__(self):
        return "Academic Staff: " + self.name


# Presentation class
class Presentation:
    presentation = None

    def __init__(self, name, staff):
        self.name = name
        self.staff = staff

    @staticmethod
    def searchPreset(name):
        for i in range(len(Presentation.presentation)):
            if Presentation.presentation[i].name == name:
                return i
        return -1

    @staticmethod
    def searchStaff(name):
        for i in range(len(Presentation.presentation)):
            if name in Presentation.presentation[i].staff:
                return i
        return -1

    def __repr__(self):
        return "Presentation: {} by Staff1: {}, Staff2: {}, Staff3: {}".format(self.name, self.staff[0], self.staff[1], self.staff[2])


# Venue class
class Venue:
    venue = None

    def __init__(self, name):
        self.name = name

    @staticmethod
    def search(name):
        for i in range(len(Venue.venue)):
            if Venue.venue[i].name == name:
                return i
        return -1

    def __repr__(self):
        return "Venue: " + self.name


# Slot class
class Slot:
    slot = None

    def __init__(self, name):
        self.name = name

    def __repr__(self):
        return "Slot: " + self.name