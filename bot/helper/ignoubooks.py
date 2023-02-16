import requests
import os

class IgnouBooks:

    def __init__(self,course=None,subject='None') -> None:
        self.headers = {'User-Agent':'Dalvik/2.1.0 (Linux; U; Android 10; Redmi Note 7 Pro Build/QQ3A.200605.001)','b8S3lCfLoGo4DVAzNQnl5OpMyALyq8e2WpWbZTMlwZ5iPHr.UaVNW':'J0lta3zy@19' }
        self.course = course.upper()  # Course Name like BCA or MCA
        self.subject = subject.upper()  # If subject code passed like BCS011 or MCS023
        self.pId = '' # IGNOU course id like BCA 23 and MCA 25
        self.cId = '' # IGNOU Course subject id list
        self.courseList = '' # get all subject of course

    def courseCode(self):
        courses = ['https://egkapp.ignouonline.ac.in/api/programmes/type/Bachelor','https://egkapp.ignouonline.ac.in/api/programmes/type/Master'] 
        for courseurl in courses:
            response = requests.get(courseurl,headers = self.headers).json()
            for res in response:
                if '(' not in res['pCode']:
                    if self.course == res['pCode'].upper():
                        self.pId = res['pId']
                        return
                elif '(' in res['pCode'] and 'English' == res['pMedium']:
                    if self.course == res['pCode'].split("(")[0].upper():
                        self.pId = res['pId']
                        return

    def subjectCode(self):
        self.courseCode()
        subjects = 'https://egkapp.ignouonline.ac.in/api/courses/p/' + str(self.pId)

        response = requests.get(subjects,headers = self.headers).json()

        substring =''  # 〽️
        
        for res in response:
            fullname = res['cCode']
            con = any(map(str.isdigit, fullname))
            if not con:
                con = False
                continue
            if '-' in fullname:
                first = fullname.split('-')[0]
                last = str(int(fullname.split('-')[1])//1)
                finalname = first + last
            
            if finalname == self.subject:
                self.cId = res['cId']
            title = res['cTitle']
            coursename = res['cpId']['pCode']
            substring += f'{title} \n〽️ `/book {coursename} {finalname}`\n\n'
        
        self.courseList =  substring

    def getCourseSubjectlist(self):
        self.courseCode()
        self.subjectCode()
        return self.courseList

    def getDownload(self):
        self.courseCode()
        self.subjectCode()
        downloads = 'https://egkapp.ignouonline.ac.in/api/blocks/c/' + str(self.cId)

        response = requests.get(downloads,headers = self.headers).json()

        namelist = []  
        for res in response:
            downurl = 'https://egkapp.ignouonline.ac.in/api/blocks/download/' + str(res['bId'])

            downloadresponse = requests.get(downurl,headers = self.headers)
            
            open(f"{res['bCode']} [{self.subject}][@IGNOUpyBoT].pdf", 'wb').write(downloadresponse.content)
            namelist.append(f"{res['bCode']} [{self.subject}][@IGNOUpyBoT].pdf")
            print(f"{res['bCode']} [{self.subject}][@IGNOUpyBoT].pdf")

        return namelist
