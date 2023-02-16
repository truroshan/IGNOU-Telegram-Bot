
class User:
    def __init__(self, user):
        if user is None:
            user = {}

        self._id = user.get("_id")
        self.name = user.get("name")
        self.course = user.get("action", {}).get("course")
        self.myenrollment = user.get("myenrollment")
        self.following = user.get("following", {})
        self.enrollment = user.get("action", {}).get("enrollment")
        self.last_used_on = user.get("action", {}).get("last_used_on")
        self.is_admin = user.get("role_status", {}).get("is_admin", False)
        self.user = user

    def dict(self):
        return self.user

#
class Student:
    def __init__(self, student):
        if student is None:
            student = {}

        self._id = student.get("_id")
        self.name = student.get("name")
        self.course = student.get("course")
        self.myenrollment = student.get("myenrollment")
        self.followers = student.get("followers", {})
        self.enrollment = student.get("action", {}).get("enrollment")
        self.last_used_on = student.get("action", {}).get("last_used_on")
        self.is_admin = student.get("role_status", {}).get("is_admin", False)

        self.grade = self.Grade(student.get("grade"))
        self.tee = self.Tee(student.get("tee"))

        self.student = student

    def dict(self):
        return self.student

    # grade card
    class Grade:
        def __init__(self, grade):
            self.passed = grade.get("count",{}).get("passed", 0)
            self.failed = grade.get("count",{}).get("failed", 0)
            self.checked = grade.get("checked")

    # tee card
    class Tee:
        def __init__(self, tee):
            self.count = tee.get("count",0)
            self.checked = tee.get("checked")

