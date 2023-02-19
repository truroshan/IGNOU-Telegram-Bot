from collections import OrderedDict
from collections.abc import Mapping

import httpx
from bs4 import BeautifulSoup
from prettytable import PrettyTable


class DotDict(OrderedDict):
    """
    Quick and dirty implementation of a dot-able dict, which allows access and
    assignment via object properties rather than dict indexing.
    """

    def __init__(self, *args, **kwargs):
        # we could just call super(DotDict, self).__init__(*args, **kwargs)
        # but that won't get us nested dotdict objects
        od = OrderedDict(*args, **kwargs)
        for key, val in od.items():
            if isinstance(val, Mapping):
                value = DotDict(val)
            else:
                value = val
            self[key] = value

    def __getattr__(self, k):
        return self.get(k, "-")

    __setattr__ = OrderedDict.__setitem__


class ResultNotFoundError(Exception):
    pass


class IgnouResult:
    def __init__(self) -> None:
        transport = httpx.AsyncHTTPTransport(verify=False)
        self.session: httpx.AsyncClient = httpx.AsyncClient(transport=transport)

    async def get_grade_result(self, program_id: str, enrollment_no: int):

        program_id = program_id.upper()

        params = {
            "prog": program_id,
            "eno": enrollment_no,
        }

        if program_id in [
            "BCA",
            "MCA",
            "MP",
            "MBP",
            "PGDHRM",
            "PGDFM",
            "PGDOM",
            "PGDMM",
            "PGDFMP",
        ]:
            params["type"] = 1
        elif program_id in ["ASSSO", "BA", "BCOM", "BDP", "BSC"]:
            params["type"] = 2
        elif program_id in [
            "BAEGH",
            "BAG",
            "BAHDH",
            "BAHIH",
            "BAPAH",
            "BAPCH",
            "BAPSH",
            "BASOH",
            "BAVTM",
            "BCOMG",
            "BSCANH",
            "BSCBCH",
            "BSCG",
            "BSWG",
        ]:
            params["type"] = 4
        else:
            params["type"] = 3

        grade_card_page = "https://gradecard.ignou.ac.in/gradecard/view_gradecard.aspx"

        response = await self.session.get(grade_card_page, params=params)

        soup = BeautifulSoup(response.text, "lxml")

        name = soup.find(id="ctl00_ContentPlaceHolder1_lblDispname").string

        try:
            trs = soup.find(string="COURSE").findParent("table")
        except AttributeError:
            raise ResultNotFoundError

        trs = soup.find(string="COURSE").findParent("table").find_all("tr")

        data = DotDict()
        data.enrollment_no = enrollment_no
        data.program_id = program_id
        data.name = name

        courses = []
        data.courses = courses

        total = DotDict()
        data.total = total
        total.total_passed = 0
        total.total_failed = 0
        total.total_marks = 0
        total.total_obtained_marks = 0

        column_index = {}
        # get index of coulmn by name

        cols_list = [data.get_text() for data in trs[0].find_all("th")]
        for index, col in enumerate(cols_list):
            if "COURSE" in col:
                column_index["COURSE"] = index
            elif "ASG" in col.upper():
                column_index["ASIGN"] = index
            elif "THEORY" in col:
                column_index["THEORY"] = index
            elif "PRACTICAL" in col:
                column_index["PRACTICAL"] = index
            elif "STATUS" in col:
                column_index["STATUS"] = index

        for tr in trs[1:-1]:
            course = DotDict()
            course.max_marks = 100
            total.total_marks += course.max_marks

            td = tr.find_all("td")

            # course name
            course.name = td[column_index["COURSE"]].string.strip()

            # assignments marks
            if assign := td[column_index["ASIGN"]].string.strip():
                if assign.isnumeric():
                    course.assignment_marks = int(assign)
                    total.total_obtained_marks += course.assignment_marks

            # theory marks
            try:
                if theory := td[column_index["THEORY"]].string.strip():
                    if theory.isnumeric():
                        course.theory_marks = int(theory)
                        total.total_obtained_marks += course.theory_marks
            except Exception:
                course.theory_marks = "-"

            # lab marks
            try:
                if lab := td[column_index["PRACTICAL"]].string.strip():
                    if lab.isnumeric():
                        course.lab_marks = int(lab)
                        total.total_obtained_marks += course.lab_marks
            except Exception:
                course.lab_marks = "-"

            # Status # ✅ ❌
            if "NOT" not in td[column_index["STATUS"]].string.strip():
                course.status = True
                total.total_passed += 1

            else:
                course.status = False
                total.total_failed += 1

            courses.append(course)

        total.total_courses = len(courses)

        return {
            "name": name,
            "enrollment_no": enrollment_no,
            "program_id": program_id,
            "courses": courses,
            **total,
        }

    async def gradeResultData(
        self,
        program_id: str,
        enrollment_no: int,
    ):

        data = DotDict(await self.get_grade_result(program_id, enrollment_no))

        x = PrettyTable()
        x.padding_width = 0
        x.field_names = ["Course", "Asign", "Lab", "Term", "Status"]

        header = "Name : {}\nProg : {} [{}]\n".format(
            data.name, data.program_id, data.enrollment_no
        )

        for course in data.courses:
            tick = "✅" if course.status else "❌"

            x.add_row(
                [
                    course.name,
                    course.assignment_marks,
                    course.lab_marks,
                    course.theory_marks,
                    tick,
                ]
            )

        x.add_row(
            [
                "Total",
                "T:{}".format(data.total_courses),
                "-",  # data.total_obtained_marks,
                "-",  # data.total_marks,
                f"[{data.total_passed}/{data.total_failed}]",
            ]
        )

        return {"header": header, "table": x.get_string()}
