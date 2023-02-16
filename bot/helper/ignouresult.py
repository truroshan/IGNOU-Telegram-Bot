import requests
from bs4 import BeautifulSoup
from prettytable import PrettyTable
import re
from bot.database import  Database

db = Database()

class IgnouResult:

    def __init__(self,text='Bca 197940316') -> None:
        self.text = text.upper().strip()
        self.enrollmentNo = ''
        self.courseId = ''
        self.extractCourseIDandEnrollmentNo()
        self.sem = 'Dec20'

        self.session = requests.Session()
        self.session.headers.update({
            'Connection': 'keep-alive',
            'Cache-Control': 'max-age=0',
            'Upgrade-Insecure-Requests': '1',
            'Content-Type': 'application/x-www-form-urlencoded',
            'User-Agent': 'Mozilla/5.0 (Linux; Android 6.0.1; Moto G (4)) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.96 Mobile Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
            'Sec-GPC': '1',
            'Sec-Fetch-Site': 'same-origin',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-User': '?1',
            'Sec-Fetch-Dest': 'document',
            'Accept-Language': 'en-US,en;q=0.9,ru;q=0.8',
        }

        )
    def extractCourseIDandEnrollmentNo(self):

        self.courseId = re.findall("\D+", self.text)[0].strip()
        self.enrollmentNo = re.findall('\d+', self.text)[0].strip()
        return self.courseId,self.enrollmentNo

    def teeResultJson(self):

        data = {
        'eno': self.enrollmentNo,
        'myhide': 'OK'
        }
        teeUrl = f'https://termendresult.ignou.ac.in/TermEnd{self.sem}/TermEnd{self.sem}.asp'
        response = self.session.post(teeUrl, data=data)
        
        if 'Not found' in response.text:
            return {'status':'notok'} # result not found

        soup = BeautifulSoup(response.text,'lxml')

        trs = soup.find_all('tr')[1:]
        resultJson = list()

        for tr in trs:
            info = tr.find_all("td")
            data = list()
            for index,col in enumerate(info):
                if index == len(info) - 1:
                    break
                data.append(info[index].text.strip())
            resultJson.append(data)
        
        return {'result' : resultJson,'count' : len(trs),'html':response.text, 'status':'ok'}




    def gradeResultJson(self):

        data = {
        'Program': self.courseId,
        'eno': self.enrollmentNo,
        'submit': 'Submit',
        'hidden_submit': 'OK'
        }

        if self.courseId in ['BCA', 'MCA', 'MP', 'MBP', 'PGDHRM', 'PGDFM', 'PGDOM', 'PGDMM', 'PGDFMP']:
            url = 'https://gradecard.ignou.ac.in/gradecardM/Result.asp'
        elif self.courseId in ['ASSSO', 'BA', 'BCOM', 'BDP', 'BSC']:
            url = 'https://gradecard.ignou.ac.in/gradecardB/Result.asp'
        else:
            url = 'https://gradecard.ignou.ac.in/gradecardR/Result.asp'

        response = self.session.post(url, data=data)

        soup = BeautifulSoup(response.text,'lxml')

        if 'Not found' in response.text or response.status_code != 200:
            return {'status':'notok'} # result not found

        trs = soup.find_all("tr")[1:]
        
        resultJson = list()
        student = dict()
        btags = soup.find_all('b')[3:6]

        for n,ba in enumerate(btags,1):
            if n == 1:
                student['enrollment'] = ba.text.split(":")[1].strip()
            elif n == 2:
                student['name'] = ba.text.split(":")[1].strip()
            else:
                student['course'] = ba.text.split(":")[1].strip()

        count = dict()
        count['passed'] = 0
        count['failed'] = 0
        count['total'] = 0
        for tr in trs:
            data = list()

            td = tr.find_all("td")

            data.append(td[0].string.strip())
            data.append(td[1].string.strip())
            data.append(td[2].string.strip())
            data.append(td[6].string.strip())

            status = True if 'Not' not in td[7].string.strip() else False # ✅ ❌
            data.append(status)

            if status:
                count['passed'] += 1
            else:
                count['failed'] += 1
            count['total'] += 1
            
            resultJson.append(data)
        
        return {'result' :  resultJson,'student' : student,'count' : count,'html':response.text,'status':'ok'}
    
    def gradeResultString(self):
        x = PrettyTable()
        x.field_names = ["Course","Asign","Lab","Term","Status"]
        
        gradeJson = self.gradeResultJson()

        if gradeJson['status'] != 'ok':
            return False
        header = 'Name : {}\n -> {} -> {}\n'.format(gradeJson['student']['name'],self.courseId,self.enrollmentNo)

        for sub in gradeJson['result']:
            tick = '✅' if sub[-1] else '❌'
            sub[-1] =  tick
            x.add_row(sub)

        footer = ['count','T:{}'.format(gradeJson['count']['total']),
                'P:{}'.format(gradeJson['count']['passed']),
                'F:{}'.format(gradeJson['count']['failed']),
                'L:{}'.format(gradeJson['count']['total']-gradeJson['count']['passed'])]
        x.add_row(footer)
        
        return {
            'enrollmentno' : self.enrollmentNo,
            'course' : self.courseId,
            'result' : '<pre>' + header + x.get_string() + '</pre>',
            'json' : gradeJson
        }

    def teeResultString(self):
        x = PrettyTable()
        header = 'Enrollment no : {} ({})\n'.format(self.enrollmentNo,self.sem)
        x.field_names = ["Course","Marks","Max","Month","Updation"]

        teeJson = self.teeResultJson()

        if teeJson['status'] != 'ok':
            return False

        for sub in teeJson['result']:
            x.add_row(sub)

        return {
            'enrollmentno' : self.enrollmentNo,
            'course' : self.courseId,
            'count' : teeJson['count'],
            'result' : '<pre>' + header + x.get_string() + '</pre>',
            'json' : teeJson
        }

    async def gradeCardUpdated(self):
        
        response = self.gradeResultJson()

        if response['status'] != 'ok':
            return False

        updated = re.findall('([\w]+ ?[\d]+, ?[\d]+)',response['html'])[0]

        last_updateed = await db.get_site_update("ignou")

        if updated != last_updateed.get("grade",''):
            return {"date" : updated,"updated" : True}
        return {"date" : updated,"updated" : False}


    async def teeCardUpdated(self):

        teeUrl = f'https://termendresult.ignou.ac.in/TermEnd{self.sem}/TermEnd{self.sem}.asp'

        response = self.session.post(teeUrl)

        if response.status_code != 200:
            return False

        updated = re.findall('([\w]+ ?[\d]+, ?[\d]+)',response.text)[0]

        # todayDate = datetime.datetime.today().strftime('%B %d, %Y')

        last_updateed = await db.get_site_update("ignou")

        if updated != last_updateed.get("tee",''):
            return {"date" : updated,"updated" : True}
        return {"date" : updated,"updated" : False}
