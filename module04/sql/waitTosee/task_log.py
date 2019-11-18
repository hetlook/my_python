from  datetime import datetime
from celery import Celery
from chaping import ItemCommentSpider
from save_get_value import PageCounter
from time_master import TimeMaster


app = Celery("task_log", broker="amqp://", backend="redis://:py8888@localhost")
app.config_from_object('config')


@app.task
def worker(name):
    url = "http://sentence.iciba.com/index.php?&c=dailysentence&m=getdetail&title=2019-11-15&_=1573811833104"
    scraw = ItemCommentSpider()
    result = scraw.get_comment(url)
    # time = TimeMaster().change_datetime(str(datetime.now()))
    time = f'{datetime.now():%Y-%m-%d %H:%M}'
    pc = PageCounter()
    content = {"en":result[0], "ch":result[1], "time":time}
   # print(content, type(content)) 
    print(time, type(time))
    pc.set_content(time, content)

    return f"{time}-15s-ok"
