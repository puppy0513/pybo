from datetime import datetime
from datetime import timedelta
from datetime import time
from django.shortcuts import get_object_or_404, render,get_list_or_404, redirect,HttpResponse
from django.contrib import messages
from django.db.models import Q
from numpy import datetime64, datetime_as_string
from .models import Question ,Finance, Kospi,Kosdaq,Risk
from .forms import QuestionForm, AnswerForm 
from django.core.paginator import Paginator
import FinanceDataReader as fdr
from bokeh.resources import CDN
from bokeh.embed import file_html
from bokeh.plotting import figure, output_file, show 
from bokeh.embed import components
from bokeh.layouts import gridplot
from bokeh.io import curdoc
import jinja2
import pandas as pd
from pandas._libs.tslibs.timestamps import Timestamp
from math import pi
import string
import json
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import RobustScaler
import investpy
from sklearn.neighbors import KNeighborsClassifier
from sklearn.model_selection import KFold
from sklearn.metrics import accuracy_score


def index(request):
    curdoc().theme = 'dark_minimal'

    df1 = fdr.DataReader('KS11','2021-08-01')
    df2 = fdr.DataReader('KQ11','2021-08-01')
    
    df1 = df1.rename_axis('Date').reset_index()
    df2 = df2.rename_axis('Date').reset_index()


    #PLOT_OPTIONS = dict(plot_width=800, plot_height=300)
    #SCATTER_OPTIONS = dict(size=12, alpha=0.5)

    red = figure(title = 'KOSPI 종합주가지수',x_axis_type='datetime',width=650,height =400, tools='pan')
    red.line(df1['Date'], df1['Close'], color="red",line_width = 3)
    blue = figure(title = 'KOSDAQ 종합주가지수',x_axis_type='datetime',width=650,height =400, tools='pan')
    blue.line(df2['Date'], df2['Close'], color="blue",line_width = 3)

    script1, div1 = components(red)
    script2, div2 = components(blue)

    context = {'script1':script1,'div1':div1,'script2':script2,'div2':div2}
    return render(request,'pybo/home.html',context=context)


"""
def index(request):
    
    #pybo 목록 출력
    
    # 입력 파라미터
    page = request.GET.get('page', '1')  # 페이지

    question_list = Question.objects.order_by('-create_date')
    # 페이징처리
    paginator = Paginator(question_list, 10)  # 페이지당 10개씩 보여주기
    page_obj = paginator.get_page(page)

    context = {'question_list': page_obj}
    return render(request, 'pybo/question_list.html', context)
"""
def detail(request, question_id):
    
    #pybo 내용 출력
    question = Question.objects.get(id=question_id)
    context = {'question': question}
    return render(request, 'pybo/question_detail.html', context)


def answer_create(request, question_id):
    """
    pybo 답변등록
    """
    question = get_object_or_404(Question, pk=question_id)
    if request.method == "POST":
        form = AnswerForm(request.POST)
        if form.is_valid():
            answer = form.save(commit=False)
            answer.create_date = timezone.now()
            answer.question = question
            answer.save()
            return redirect('pybo:detail', question_id=question.id)
    else:
        form = AnswerForm()
    context = {'question': question, 'form': form}
    return render(request, 'pybo/question_detail.html', context)  
    
def question_create(request):
    if request.method == 'POST':
        form = QuestionForm(request.POST)
        if form.is_valid():
            question = form.save(commit=False)
            question.create_date = timezone.now()
            question.save()
            return redirect('pybo:index')
    else:
        form= QuestionForm()
    context = {'form':form}
    return render(request, 'pybo/question_form.html', context)

def finance(request):
    
    page = request.GET.get('page', '1') 

    finance_list = Finance.objects.order_by('-Date')
    paginator = Paginator(finance_list, 10)  # 페이지당 10개씩 보여주기
    page_obj = paginator.get_page(page)

    context = {'finance_list': page_obj}
    return render(request,'pybo/finance_list.html',context)         #pybo/finance_list.html에 context 변수를 적용해서 넘겨줘라 
"""
def finance_detail(request,finance_id):
    finance_list = Finance.objects.get(id = finance_id)
    context ={'finance_list':finance_list}
    return render(request,'pybo/finance_detail.html',context)
"""
def kospi(request):
    page = request.GET.get('page', '1') 

    kospi_list = Kospi.objects.order_by('Symbol')
    search_key = request.GET.get('search_key') # 검색어 가져오기
    if search_key: # 만약 검색어가 존재하면
        kospi_list = kospi_list.filter(Name__icontains=search_key) # 해당 검색어를 포함한 queryset 가져오기

    paginator = Paginator(kospi_list, 10)  # 페이지당 10개씩 보여주기
    page_obj = paginator.get_page(page)

    context = {'kospi_list': page_obj}
    return render(request,'pybo/kospi.html',context)

def kosdaq(request):
    page = request.GET.get('page', '1') 
    kosdaq_list = Kosdaq.objects.order_by('Symbol')
    search_key = request.GET.get('search_key') # 검색어 가져오기
    if search_key: # 만약 검색어가 존재하면
        kosdaq_list = kosdaq_list.filter(Name__icontains=search_key) # 해당 검색어를 포함한 queryset 가져오기

    paginator = Paginator(kosdaq_list, 10)  # 페이지당 10개씩 보여주기
    page_obj = paginator.get_page(page)

    context = {'kosdaq_list': page_obj}
    return render(request,'pybo/kosdaq.html',context)


def kospi_detail(request,kospi_id):
    # 종목 정보
    Kospi_list = Kospi.objects.get(Symbol = kospi_id)

    kospi_id =str(kospi_id)
    # 종목 historic data
    if len(kospi_id) != 6:
        kospi_id = kospi_id.zfill(6)

    df = fdr.DataReader(kospi_id,'2021-09-01')
    df = df.sort_index(ascending=False)
    #차트 그리기
    
    #데이터 형 변환
    df.index = df.index.astype(str)
    df['Change'] *= 100
  
    # json 데이터로 변형
    json_records = df.reset_index().to_json(orient ='records')
    data = []
    data = json.loads(json_records)
    
    #페이지 설정
    page = request.GET.get('page', '1') 
    paginator = Paginator(df, 10)  # 페이지당 10개씩 보여주기
    page_obj = paginator.get_page(page)

    context ={'Kospi_list':Kospi_list ,'d': data}
    return render(request,'pybo/kospi_detail.html',context)

def kosdaq_detail(request,kosdaq_id):
   # 종목 정보
    Kosdaq_list = Kosdaq.objects.get(Symbol = kosdaq_id)

    kosdaq_id =str(kosdaq_id)
    # 종목 historic data
    if len(kosdaq_id) != 6:
        kosdaq_id = kosdaq_id.zfill(6)

    df = fdr.DataReader(kosdaq_id,'2021-09-01')
    df = df.sort_index(ascending=False )

    #데이터 형 변환
    df.index = df.index.astype(str)
    df['Change'] *= 100
  
    # json 데이터로 변형
    json_records = df.reset_index().to_json(orient ='records')
    data = []
    data = json.loads(json_records)
    
    #페이지 설정
    page = request.GET.get('page', '1') 
    paginator = Paginator(df, 10)  # 페이지당 10개씩 보여주기
    page_obj = paginator.get_page(page)

    context ={'Kosdaq_list':Kosdaq_list ,'d': data}
    return render(request,'pybo/kosdaq_detail.html',context)

def graph(request, id):

    id =str(id)   

    if len(id) != 6:
        id = id.zfill(6)
    
    df = fdr.DataReader(id,'2021-08-01')
    df = df.rename_axis('Date').reset_index()

    inc = df.Close > df.Open
    dec = df.Open > df.Close
    w = 12*60*60*1000 # half day in ms

    TOOLS = "pan,wheel_zoom,box_zoom,reset,save"
    
    p1 = figure(x_axis_type="datetime", tools=TOOLS, plot_width=1000, plot_height=500, title = "Candlestick with Volume")
    p1.xaxis.major_label_orientation = pi/4  
    p1.grid.grid_line_alpha=0.3
    p1.segment(df.Date, df.High, df.Date, df.Low, color="black")
    p1.vbar(df.Date[inc], w, df.Open[inc], df.Close[inc], fill_color="#F2583E", line_color="black")
    p1.vbar(df.Date[dec], w, df.Open[dec], df.Close[dec], fill_color="#3088f1", line_color="black")
   
    script, div = components(p1)

    return render(request, 'pybo/graph.html', {'script': script, 'div': div})

def risk(request):
    page = request.GET.get('page', '1')

    # 데이터 프레임으로 받기
    risk_list = Risk.objects.order_by('-id')
    risk_list_1 = Risk.objects.order_by('id').values()

    # 시간설정, 스케일러 설정
    td = datetime.today().strftime("%d" + "/" + "%m" + "/" + "%Y")  # 오늘 날짜
    yesterday = datetime.today() - timedelta(2)
    yesterday = yesterday.strftime("%d" + "/" + "%m" + "/" + "%Y")
    scaler = RobustScaler()
    day1 = []
    day1.append((datetime.today() + timedelta(240)).strftime("%Y" + "/" + "%m" + "/" + "%d"))
    day1.append((datetime.today() + timedelta(300)).strftime("%Y" + "/" + "%m" + "/" + "%d"))

    """ 미국 10년 국채 금리 """
    df = investpy.get_bond_historical_data(bond='U.S. 10Y', from_date=yesterday, to_date=td)
    data = pd.DataFrame(df)

    """미국 2년 국채 금리 """
    df1 = investpy.get_bond_historical_data(bond='U.S. 2Y', from_date=yesterday, to_date=td)
    data1 = pd.DataFrame(df1)

    """ 국채 10년물 - 국채 2년물 / 국채 스프레드 """
    spread = data.loc[:, 'Close'] - data1.loc[:, 'Close']

    """달러 인덱스 점수 매기기"""
    search_results = investpy.get_index_historical_data(index='US Dollar Index', country='United States', from_date=yesterday, to_date=td)
    DXY = search_results.loc[:, 'Close']  # 달러 인덱스의 종가

    spread['Date'] = spread.index

    today_ = pd.concat([spread, DXY], axis=1, keys=['spread', 'DXY'])
    today_['Date'] = today_.index

    today_1 = today_.iloc[[1], :]
    today_1['Label'] = 0

    #데이터 읽어 들여서 데이터프레임에 넣고 robustscaler 넣는다.
    data2 =pd.DataFrame(risk_list_1)
    # 합치고
    data2 = pd.concat([data2,today_1])
    # 스케일링진행
    data2[["spread", "DXY"]] = scaler.fit_transform(data2[["spread", "DXY"]])

    #모델설정
    model = KNeighborsClassifier(n_neighbors =3 , weights='distance', metric='euclidean')
    X = data2.iloc[:[len(data2) - 1], 1:3]         # X열
    y = data2.iloc[:[len(data2) - 1], [3]]         # 라벨링
    X_test = data2.iloc[[len(data2) - 1], 1:3]

    kf = KFold(n_splits=5, shuffle=True, random_state=42)

    for train_index, test_index in kf.split(X):
        X_train, X_test = X.iloc[train_index, :], X.iloc[test_index, :]
        y_train, y_test = y.iloc[train_index, :], y.iloc[test_index, :]
        model.fit(X_train, y_train)

    y_pred = model.predict(X_test)

    paginator = Paginator(risk_list, 10)  # 페이지당 10개씩 보여주기
    page_obj = paginator.get_page(page)

    context = {'risk_list': page_obj, 'data':data, 'pred':y_pred,'day': day1}
    return render(request, 'pybo/risk.html',context)