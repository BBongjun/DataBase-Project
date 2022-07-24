# db_etoos의 모듈을 가지고 import를 하고 시작합니다.
import db_etoos
import pickle


db_etoos.get_link_list()

############################### 시작 ###############################
def init():
    with open("etoos_link.pickle","rb") as fr:
        LINK_LIST = pickle.load(fr)
        db_etoos.get_data(LINK_LIST)

init()