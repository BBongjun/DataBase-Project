# 이 파이썬 파일은 이투스에 있는 자료들을 추출하기 위해서 코딩한것입니다.
# 추출한 데이터들을 엑셀에 저장하는 과정까지 포함되어있습니다.


import requests
from bs4 import BeautifulSoup
import openpyxl
import os
import pickle
import re

################################### 과목 리스트 ###################################
SUBJECTS_LIST = [
    { "subject": "국어", "value": "0001" },
    { "subject": "영어", "value": "0002" },
    { "subject": "수학", "value": "0003" },
]

################################### 각 수강후기의 링크를 가져오는 함수 ###################################
def get_link_list():
    
    LINK_LIST = []
    
    
    for subject_obj in SUBJECTS_LIST:
        
        print(subject_obj["subject"] + " 시작합니다!!!")

        
        URL = 'https://go3.etoos.com/teacher/evaluate/default.asp?AREA_CD=' + subject_obj["value"]
        html = requests.get(URL)
        soup = BeautifulSoup(html.content.decode('euc-kr','replace'))

        
        print(subject_obj["subject"] + " 가져오는 것에 성공했습니다!!!")

        POPUP_BASE_URL = "https://go3.etoos.com"

        last_page = soup.find_all(attrs={'class': 'link_page'})[-1].text

        
        print(subject_obj["subject"] + f"의 마지막 페이지는 {last_page}입니다.")

       
        print(subject_obj["subject"] + " 페이지 반복 시작하겠습니다!")

        
        for i in range(int(last_page)):
            
            print(str(i+1) + "번째 페이지입니다!!")

            PAGE_URL = f"{URL}&page={i+1}"
            page_html = requests.get(PAGE_URL)
            page_soup = BeautifulSoup(page_html.content.decode('euc-kr','replace'))
            
            tbody = page_soup.find('tbody')
            trs = tbody.find_all('tr')


            escape = False
            for tr in trs:
              
                date = tr.find_all('td')[-1].text
                
                if int(date[:4]) < 2021:
                    escape = True
                    print("날짜가 2021년보다 전입니다!!!!")
                    break
                
                wr_tit = tr.find(attrs={'class': 'wr_tit'})
                a = wr_tit.find(attrs={'class': 'link'})
                href = a["href"][32:-11]
                link = f"{POPUP_BASE_URL}{href}"
    
                LINK_LIST.append(link)
                
            if escape:
                print("날짜가 2021년보다 전이라서 반복문에서 탈출!")
                break
    with open("etoos_link.pickle","wb") as fw:
        pickle.dump(LINK_LIST, fw)


def get_data(LINK_LIST):
    
    current_path = os.getcwd()
    wb = openpyxl.Workbook()
    sheet = wb.active
    sheet.append(["과목", "선생님이름", "학생이름", "학생학년", "문이과", "별점", "키워드(해쉬태그)"])
    print("엑셀로 변환 시작하겠습니다!!!")
    print("총 " + str(len(LINK_LIST)) + "개의 데이터가 삽입될 예정입니다.")
    count = 1

   
    for link in LINK_LIST:
        print(f"{count}번째 데이터 삽입 시작합니다.")
        html = requests.get(link)
        soup = BeautifulSoup(html.content.decode('euc-kr','replace'))

        ######################### 과목, 선생님이름 ###############################
        lect_name = soup.find(attrs={'class': 'lect_name'}).text
        lect_and_teacher = lect_name.split(" ")[0].replace(u'\xa0', u' ')
        
        # 과목
        try:
            lecture = lect_and_teacher.split(" ")[0]
        except:
            lecture = "null"

        # 선생님이름
        try:
            teacher = lect_and_teacher.split(" ")[1]
        except:
            teacher = "null"
        ##########################################################################

        ################################## 학생이름, 학생학년, 문이과 ####################
        head_info = soup.find(attrs={'class': 'head_info'}).text
        grade_and_major = re.findall('\(([^)]+)', head_info)[0].split(",")
        
        # 학생 이름
        try:
            student = head_info.split(" ")[0].replace(u'\xa0', u' ').split(" ")[0]
        except:
            student = "null"
        
        # 학생 학년
        try:
            if grade_and_major[0].strip():
                grade = grade_and_major[0].strip()
            else:
                grade = "null"
        except:
            grade = "null"
        
        # 학생 문이과
        try:
            if grade_and_major[1].strip():
                if grade_and_major[1].strip()[:2] == "계열":
                    major = grade_and_major[1].strip() + ")"
                else:
                    major = grade_and_major[1].strip()
            else:
                major = "null"
        except:
            major = "null"
        ######################################################################################
        

        ######################################## 별점 ########################################
        try:
            star = int(int(soup.find(attrs={'class': 'star_on'})["style"][6:-1]) / 20)
        except:
            star = "null"
        ######################################################################################
        
        ################################## 키워드(해시태그) ##################################
        try:
            keyword_list = []
            cont_keyword = soup.find(attrs={'class': 'cont_keyword'})
            keyword_spans = cont_keyword.find_all('span')[1:]
            
            for keyword_span in keyword_spans:
                keyword_list.append(keyword_span.text)
            
            keyword = ','.join(keyword_list)
        except:
            keyword = "null"
            
        ######################################################################################
        sheet.append([lecture, teacher, student, grade, major, star, keyword])
        count = count + 1
    
    print("모든 데이터의 삽입이 완료되었습니다.")
    print("저장하겠습니다.")
    wb.save(f"{current_path}/etoos_pickle.xlsx")
    print("엑셀 저장을 완료했습니다.")