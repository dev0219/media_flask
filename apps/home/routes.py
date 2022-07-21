# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""
# from msilib.schema import Error
from flask_login import (
    login_required,
    current_user,
    login_user,
    logout_user
)

import json

from numpy import append

from apps.home import blueprint

from flask import render_template, request

from flask_login import login_required

from jinja2 import TemplateNotFound

import pandas as pd

from apps.authentication.models import Users, ClientData, ClientLogo, ClientImgData

from .preprocessing import (
    calculate_actual_roi,
    calculate_overspend,
    calculate_overspend_revenue,
    get_data_utils,
    get_default_roas_values,
    get_default_start_end_times,
    get_overspend_revenue,
    get_passed_values,
    get_roas_sheets_and_channels,
    load_table_data,
    load_data
)


@blueprint.route('/index', methods=["GET", "POST"])
@login_required
def index():
    us = ""
    user = request.args.get("user")
    if user is None:
        us = "test"
    else:
        username = request.values["user"] 
        us = username

    user = Users.query.filter_by(username=us).first()
    client_data = ClientData.query.filter_by(user_id=user.id).first()
    client_img_arr = ClientImgData.query.filter_by(user_id=user.id)
    clientImg = []
    for imgitem in client_img_arr:
        clientImg.append({'id':imgitem.id,'filename':imgitem.filename})



    StackedPlotContribution = pd.read_excel (client_data.data,sheet_name='Stacked Plot Contribution')
    # sheetnames = pd.ExcelFile(client_data.data).sheet_names
    filtered = ['Display', 'Facebook', 'Google PLA', 'Google Search', 'Microsoft']
    Tags = list(filtered)
    Display = StackedPlotContribution.iloc[:,1].tolist()[::-1]
    Facebook = StackedPlotContribution.iloc[:,2].tolist()[::-1]
    GooglePLA = StackedPlotContribution.iloc[:,3].tolist()[::-1]
    GoogleSearch = StackedPlotContribution.iloc[:,4].tolist()[::-1]
    Microsoft = StackedPlotContribution.iloc[:,5].tolist()[::-1]
    BaseRevenue = StackedPlotContribution.iloc[:,6].tolist()[::-1]
    labels = StackedPlotContribution.iloc[:,7].tolist()

    timeseries = pd.read_excel(client_data.data,sheet_name='Timeseries Plot')
    timeseries = timeseries.fillna('Nan')

    predRevTrain= timeseries.iloc[:,2].tolist()
    actualRev = timeseries.iloc[:,3].tolist()
    predRevTest = timeseries.iloc[:,4].tolist()
    labels2 = timeseries.iloc[:,1].tolist()
    

    columnNames = timeseries.columns.tolist()[2:]
    pieContrib = pd.read_excel(client_data.data,sheet_name='Pie Chart Contribution')
    totalContribution= pieContrib.iloc[:,2].tolist()
    labels3 = pieContrib.iloc[:,0].tolist()
    'Base sale Contribution Chart Data'
    BaseSaleContribution = pd.read_excel (client_data.data,sheet_name='Base Sale Contribution')
    BaseSaleContributionHeaderArr = pd.read_excel (client_data.data,sheet_name='Base Sale Contribution',nrows=0)    
    Alpha = BaseSaleContribution.iloc[:,next((i for i, item in enumerate(BaseSaleContributionHeaderArr.columns) if item == 'alpha'), -1)].tolist()
    Unnamed = BaseSaleContribution.iloc[:,next((i for i, item in enumerate(BaseSaleContributionHeaderArr.columns) if item == 'Unnamed:0'), -1)].tolist()
    MacroGenWOYcos = BaseSaleContribution.iloc[:,next((i for i, item in enumerate(BaseSaleContributionHeaderArr.columns) if item == 'macro_gen_WOY_cos'), -1)].tolist()
    MacroGenWOYsin = BaseSaleContribution.iloc[:,next((i for i, item in enumerate(BaseSaleContributionHeaderArr.columns) if item == 'macro_gen_WOY_sin'), -1)].tolist()
    MacroHolidayThanksg = BaseSaleContribution.iloc[:,next((i for i, item in enumerate(BaseSaleContributionHeaderArr.columns) if item == 'macro_holiday_Thanksgiving'), -1)].tolist()
    MacroGenCovid = BaseSaleContribution.iloc[:,next((i for i, item in enumerate(BaseSaleContributionHeaderArr.columns) if item == 'macro_gen_Covid'), -1)].tolist()
    MacroGenCPI = BaseSaleContribution.iloc[:,next((i for i, item in enumerate(BaseSaleContributionHeaderArr.columns) if item == 'macro_gen_CPI'), -1)].tolist()
    BaseSaleContributionlabels = BaseSaleContribution.iloc[:,next((i for i, item in enumerate(BaseSaleContributionHeaderArr.columns) if item == 'Day'), -1)].tolist()
    
    'Line chart for Revenue'
    return render_template('home/index.html',ClientimageID = clientImg, Tags=Tags,userid=user.id,first=columnNames[0],second =columnNames[1] ,third = columnNames[2], totalContribution=totalContribution, labels3 =labels3, predRevTrain=predRevTrain,actualRev =actualRev,predRevTest =predRevTest, labels2 =labels2, Display=Display , Facebook = Facebook,GooglePLA =GooglePLA,GoogleSearch =GoogleSearch,Microsoft=Microsoft,BaseRevenue = BaseRevenue,labels = labels,
    Baseline_Alpha=Alpha,Baseline_Unnamed=Unnamed,Baseline_MacroWOYcos=MacroGenWOYcos,Baseline_MacroWOYsin=MacroGenWOYsin,Baseline_MacroHoliday=MacroHolidayThanksg,Baseline_MacroGenCovid=MacroGenCovid,Baseline_MacroGenCPI=MacroGenCPI,Baseline_labels=BaseSaleContributionlabels)

@blueprint.route('/validation', methods=["GET", "POST"])
@login_required
def validation():
    us = ""
    user = request.args.get("user")
    if user is None:
        us = "test"
    else:
        username = request.values["user"] 
        us = username

    user = Users.query.filter_by(username=us).first()
    if user.is_admin == 1:
        errormsg = 'The admin have not database.'
        return render_template('home/notfound.html',ErrorMsg = errormsg,userid=user.id,username=us)
    client_data = ClientData.query.filter_by(user_id=user.id).first()
    client_img_arr = ClientImgData.query.filter_by(user_id=user.id)

    excel_Sheet_names = (pd.ExcelFile(client_data.data)).sheet_names
    if not 'Timeseries Plot' in excel_Sheet_names :
        errormsg = 'The Model Validation Database does not exist.'
        return render_template('home/notfound.html',ErrorMsg = errormsg,userid=user.id,username=us)

    clientImg = []
    for imgitem in client_img_arr:
        clientImg.append({'id':imgitem.id,'filename':((imgitem.filename.replace('_',' ')).replace('.png','').replace('.jpg',''))})

    timeseries = pd.read_excel(client_data.data,sheet_name='Timeseries Plot')
    timeseries = timeseries.fillna('Nan')

    predRevTrain= timeseries.iloc[:,2].tolist()
    actualRev = timeseries.iloc[:,3].tolist()
    predRevTest = timeseries.iloc[:,4].tolist()
    labels2 = timeseries.iloc[:,1].tolist()
    

    columnNames = timeseries.columns.tolist()[2:]
    
    return render_template('home/modelvalidation.html',ClientimageID = clientImg,username=us,userid=user.id,first=columnNames[0],second =columnNames[1] ,third = columnNames[2], predRevTrain=predRevTrain,actualRev =actualRev,predRevTest =predRevTest, labels2 =labels2)

@blueprint.route('/recommendation', methods=["GET", "POST"])
@login_required
def recommendation():
    us = ""
    user = request.args.get("user")
    if user is None:
        us = "test"
    else:
        username = request.values["user"] 
        us = username

    user = Users.query.filter_by(username=us).first()
    if user.is_admin == 1:
        errormsg = 'The admin have not database.'
        return render_template('home/notfound.html',ErrorMsg = errormsg,userid=user.id,username=us)
    client_data = ClientData.query.filter_by(user_id=user.id).first()

    excel_Sheet_names = (pd.ExcelFile(client_data.data)).sheet_names

    'Media Channels Color Setting'
    if not 'Media Channels' in excel_Sheet_names:
        errormsg = 'The Media Channels does not exist.'        
        return render_template('home/notfound.html',ErrorMsg = errormsg,userid=user.id,username=us)
    ChannelsData = pd.read_excel (client_data.data,sheet_name='Media Channels')
    ChannelsHeaderArr = pd.read_excel (client_data.data,sheet_name='Media Channels',nrows=0)
    ChannelColorArr = {}
    for index, item_ in enumerate(ChannelsHeaderArr, start=0):
        if index != 0:
            ChannelColorArr[item_] = ChannelsData.iloc[:,next((i for i, item in enumerate(ChannelsHeaderArr.columns) if item == item_), -1)].tolist()[0]

    if not 'Scenario Timeseries' in excel_Sheet_names or not 'Scenario Spend Comparison' in excel_Sheet_names or not 'Media Plan Recommendations' in excel_Sheet_names:
        errormsg = 'The Media Plan Recommendation Database does not exist.'
        return render_template('home/notfound.html',ErrorMsg = errormsg,userid=user.id,username=us)

    'Scenario Timeseries'
    
    ScenarioTimeseriesData = pd.read_excel (client_data.data,sheet_name='Scenario Timeseries')    
    ScenarioTimeseriesHeaderArr = pd.read_excel (client_data.data,sheet_name='Scenario Timeseries',nrows=0) 
    BaseScenario = ScenarioTimeseriesData.iloc[:,next((i for i, item in enumerate(ScenarioTimeseriesHeaderArr.columns) if item == 'Base Scenario'), -1)].tolist()
    ROASOptimized = ScenarioTimeseriesData.iloc[:,next((i for i, item in enumerate(ScenarioTimeseriesHeaderArr.columns) if item == 'ROAS Optimized'), -1)].tolist()
    ScenarioTimeserieslabels = ScenarioTimeseriesData.iloc[:,next((i for i, item in enumerate(ScenarioTimeseriesHeaderArr.columns) if item == 'Day'), -1)].tolist()

    'Scenario Spend Comparison'


    ScenarioComparisonData = pd.read_excel (client_data.data,sheet_name='Scenario Spend Comparison')
    ScenarioComparisonHeaderArr = pd.read_excel (client_data.data,sheet_name='Scenario Spend Comparison',nrows=0) 
    BaseScenarioComparison = ScenarioComparisonData.iloc[:,next((i for i, item in enumerate(ScenarioComparisonHeaderArr.columns) if item == 'Base Scenario'), -1)].tolist()
    ROASOptimizedComparison = ScenarioComparisonData.iloc[:,next((i for i, item in enumerate(ScenarioComparisonHeaderArr.columns) if item == 'ROAS Optimized'), -1)].tolist()
    DifferentComparison = ScenarioComparisonData.iloc[:,next((i for i, item in enumerate(ScenarioComparisonHeaderArr.columns) if item == 'Difference'), -1)].tolist()
    ScenarioComparisonlabel = ScenarioComparisonData.iloc[:,0].tolist()

    'Media Plan Recommendations'

    AllRecommendationsData = pd.read_excel (client_data.data,sheet_name='Media Plan Recommendations')
    RecommendationsDataHeaderArr = pd.read_excel (client_data.data,sheet_name='Media Plan Recommendations',nrows=0)
    ScenarioComparison = AllRecommendationsData.iloc[:,next((i for i, item in enumerate(RecommendationsDataHeaderArr.columns) if item == 'Scenario'), -1)].tolist()
 
    MediaData={}
    MediaHeaderTitle=['Timeline']

    for item_header in RecommendationsDataHeaderArr:
        if 'Day' in item_header:
            MediaData[item_header] = []
            MediaData[item_header] = AllRecommendationsData.iloc[:,next((i for i, item in enumerate(RecommendationsDataHeaderArr.columns) if item == item_header), -1)].tolist()
        if 'macro_notable_' in item_header:
            MediaData[item_header] = []
            MediaHeaderTitle.append((item_header.replace('macro_notable_','')).replace('_', ' '))
            MediaData[item_header] = AllRecommendationsData.iloc[:,next((i for i, item in enumerate(RecommendationsDataHeaderArr.columns) if item == item_header), -1)].tolist()
          
        if 'spend_' in item_header:
            MediaData[item_header] = []
            MediaHeaderTitle.append((item_header.replace('spend_','')).replace('_', ' '))
            MediaData[item_header] = AllRecommendationsData.iloc[:,next((i for i, item in enumerate(RecommendationsDataHeaderArr.columns) if item == item_header), -1)].tolist()
    
    Recommendation_List = {}
    for k,v in MediaData.items():
        Recommendation_List[k] = {'Base':[],'Roas':[]}
        for index, item in enumerate(ScenarioComparison, start=0):
            if item == 'Base Scenario':
                if 'spend_' in k:                   
                    Recommendation_List[k]['Base'].append('$'+str(round(v[index]/1000))+'K')
                else:
                    Recommendation_List[k]['Base'].append(v[index])               
            else:
                if 'spend_' in k:                   
                    Recommendation_List[k]['Roas'].append('$'+str(round(v[index]/1000))+'K')
                else:
                    Recommendation_List[k]['Roas'].append(v[index]) 
 
    return render_template('home/mediarecommendation.html',ChannelColorArr=ChannelColorArr,MediaHeaderTitle=MediaHeaderTitle,Recommendation_List=Recommendation_List,username=us,userid=user.id,ROASOptimized=ROASOptimized,BaseScenario=BaseScenario,ScenarioTimeserieslabels=ScenarioTimeserieslabels,BaseScenarioComparison=BaseScenarioComparison,ROASOptimizedComparison=ROASOptimizedComparison,DifferentComparison=DifferentComparison,ScenarioComparisonlabel=ScenarioComparisonlabel)
@blueprint.route('/modelinput', methods=["GET", "POST"])
@login_required
def modelinput():
    us = ""
    user = request.args.get("user")
    if user is None:
        us = "test"
    else:
        username = request.values["user"] 
        us = username

    user = Users.query.filter_by(username=us).first()
    if user.is_admin == 1:
        errormsg = 'The admin have not database.'
        return render_template('home/notfound.html',ErrorMsg = errormsg,userid=user.id,username=us)
    client_data = ClientData.query.filter_by(user_id=user.id).first()

    excel_Sheet_names = (pd.ExcelFile(client_data.data)).sheet_names

    
    if not 'Raw Data' in excel_Sheet_names:
        errormsg = 'The Model Input Summary Database does not exist.'
        return render_template('home/notfound.html',ErrorMsg = errormsg,userid=user.id,username=us)


    'Media Channels Color'
    if not 'Media Channels' in excel_Sheet_names:
        errormsg = 'The Media Channels does not exist.'        
        return render_template('home/notfound.html',ErrorMsg = errormsg,userid=user.id,username=us)
    ChannelsData = pd.read_excel (client_data.data,sheet_name='Media Channels')
    ChannelsHeaderArr = pd.read_excel (client_data.data,sheet_name='Media Channels',nrows=0)
    ChannelColorArr = {}
    for index, item_ in enumerate(ChannelsHeaderArr, start=0):
        if index != 0:
            ChannelColorArr[item_] = ChannelsData.iloc[:,next((i for i, item in enumerate(ChannelsHeaderArr.columns) if item == item_), -1)].tolist()[0]


    'Raw Data Sheet'
    

    DFDataArr = pd.read_excel (client_data.data,sheet_name='Raw Data')
    DFHeaderArr = pd.read_excel (client_data.data,sheet_name='Raw Data',nrows=0)
 
    DFData={}

    for item_header in DFHeaderArr:
        if item_header == 'Day':
            DFData[item_header] = []
            DFData[item_header] = DFDataArr.iloc[:,next((i for i, item in enumerate(DFHeaderArr.columns) if item == item_header), -1)].tolist()
        if item_header == 'Revenue':
            DFData[item_header] = []
            DFData[item_header] = DFDataArr.iloc[:,next((i for i, item in enumerate(DFHeaderArr.columns) if item == item_header), -1)].tolist()
        if 'impr_' in item_header:
            DFData[item_header] = []
            DFData[item_header] = DFDataArr.iloc[:,next((i for i, item in enumerate(DFHeaderArr.columns) if item == item_header), -1)].tolist()
          
        if 'spend_' in item_header:
            DFData[item_header] = []
            DFData[item_header] = DFDataArr.iloc[:,next((i for i, item in enumerate(DFHeaderArr.columns) if item == item_header), -1)].tolist()
   
 
    return render_template('home/modelinputsummary.html',username=us,userid=user.id,DFData=DFData,ChannelColorArr=ChannelColorArr)

@blueprint.route('/channelintegration', methods=["GET", "POST"])
@login_required
def channelintegration():
    us = ""
    user = request.args.get("user")
    if user is None:
        us = "test"
    else:
        username = request.values["user"] 
        us = username

    user = Users.query.filter_by(username=us).first()
    if user.is_admin == 1:
        errormsg = 'The admin have not database.'
        return render_template('home/notfound.html',ErrorMsg = errormsg,userid=user.id,username=us)
    client_data = ClientData.query.filter_by(user_id=user.id).first()

    excel_Sheet_names = (pd.ExcelFile(client_data.data)).sheet_names

    'Media Channels Color'
    if not 'Media Channels' in excel_Sheet_names:
        errormsg = 'The Media Channels does not exist.'        
        return render_template('home/notfound.html',ErrorMsg = errormsg,userid=user.id,username=us)
    ChannelsData = pd.read_excel (client_data.data,sheet_name='Media Channels')
    ChannelsHeaderArr = pd.read_excel (client_data.data,sheet_name='Media Channels',nrows=0)
    ChannelColorArr = {}
    for index, item_ in enumerate(ChannelsHeaderArr, start=0):
        if index != 0:
            ChannelColorArr[item_] = ChannelsData.iloc[:,next((i for i, item in enumerate(ChannelsHeaderArr.columns) if item == item_), -1)].tolist()[0]

    if not 'Channel Integration' in excel_Sheet_names:
        errormsg = 'The Channel Integration Database does not exist.'
        return render_template('home/notfound.html',ErrorMsg = errormsg,userid=user.id,username=us)

    ChannelIntegrationAllData = pd.read_excel (client_data.data,sheet_name='Channel Integration')
    ChannelIntegrationHeaderArr = pd.read_excel (client_data.data,sheet_name='Channel Integration',nrows=0)
    ChannelIntegrationTitle=[]
    ChannelIntegrationData = {};
    for item_header in ChannelIntegrationHeaderArr:
        if 'spend_' in item_header:
            ChannelIntegrationData[item_header] = [] 
            ChannelIntegrationTitle.append((item_header.replace('spend_','')).replace('_', ' '))
            ChannelIntegrationData[item_header] = ChannelIntegrationAllData.iloc[:,next((i for i, item in enumerate(ChannelIntegrationHeaderArr.columns) if item == item_header), -1)].tolist()
        if 'Day' in item_header:
            ChannelIntegrationData[item_header] = [] 
            ChannelIntegrationTitle.append('Timeline')
            ChannelIntegrationData[item_header] = ChannelIntegrationAllData.iloc[:,next((i for i, item in enumerate(ChannelIntegrationHeaderArr.columns) if item == item_header), -1)].tolist()
    SocialiconLst = ['twitter', 'google', 'linkedin','pinterest','OutBrain','youtube','tiktok','baidu','reddit','adroll','naver','bing','Meta']
    return render_template('home/channelintegration.html',ChannelColorArr=ChannelColorArr,SocialiconLst=SocialiconLst,username=us,userid=user.id,ChannelIntegrationData=ChannelIntegrationData,ChannelIntegrationTitle=ChannelIntegrationTitle) 

@blueprint.route('/output', methods=["GET", "POST"])
@login_required
def output():
    us = ""
    user = request.args.get("user")
    if user is None:
        us = "test"
    else:
        username = request.values["user"] 
        us = username

    user = Users.query.filter_by(username=us).first()
    if user.is_admin == 1:
        errormsg = 'The admin have not database.'
        return render_template('home/notfound.html',ErrorMsg = errormsg,userid=user.id,username=us)
    client_data = ClientData.query.filter_by(user_id=user.id).first()

    excel_Sheet_names = (pd.ExcelFile(client_data.data)).sheet_names
    if not 'Stacked Plot Contribution' in excel_Sheet_names or not 'Pie Chart Contribution' in excel_Sheet_names or not 'Base Sale Contribution' in excel_Sheet_names:
        errormsg = 'The Model Output Database does not exist.'
        return render_template('home/notfound.html',ErrorMsg = errormsg,userid=user.id,username=us)

    'Media Channels Color'
    if not 'Media Channels' in excel_Sheet_names:
        errormsg = 'The Media Channels does not exist.'        
        return render_template('home/notfound.html',ErrorMsg = errormsg,userid=user.id,username=us)
    ChannelsData = pd.read_excel (client_data.data,sheet_name='Media Channels')
    ChannelsHeaderArr = pd.read_excel (client_data.data,sheet_name='Media Channels',nrows=0)
    ChannelColorArr = {}
    for index, item_ in enumerate(ChannelsHeaderArr, start=0):
        if index != 0:
            ChannelColorArr[item_] = ChannelsData.iloc[:,next((i for i, item in enumerate(ChannelsHeaderArr.columns) if item == item_), -1)].tolist()[0]

    StackedPlotContribution = pd.read_excel (client_data.data,sheet_name='Stacked Plot Contribution')
    StackedPlotContributionHeaderArr = pd.read_excel (client_data.data,sheet_name='Stacked Plot Contribution',nrows=0)  
    StackedPlotContributionData = {}
    for item_header in StackedPlotContributionHeaderArr: 
        if  item_header == 'Base Revenue':
            StackedPlotContributionData[item_header] = []
            StackedPlotContributionData[item_header] = StackedPlotContribution.iloc[:,next((i for i, item in enumerate(StackedPlotContributionHeaderArr.columns) if item == item_header), -1)].tolist() 
        if item_header == 'Display':
            StackedPlotContributionData[item_header] = []  
            StackedPlotContributionData[item_header] = StackedPlotContribution.iloc[:,next((i for i, item in enumerate(StackedPlotContributionHeaderArr.columns) if item == item_header), -1)].tolist()    
        if 'Facebook' in item_header:
            StackedPlotContributionData[item_header] = []
            StackedPlotContributionData[item_header] = StackedPlotContribution.iloc[:,next((i for i, item in enumerate(StackedPlotContributionHeaderArr.columns) if item == item_header), -1)].tolist()
        if 'Google PLA' in item_header:
            StackedPlotContributionData[item_header] = []
            StackedPlotContributionData[item_header] = StackedPlotContribution.iloc[:,next((i for i, item in enumerate(StackedPlotContributionHeaderArr.columns) if item == item_header), -1)].tolist()
        if item_header == 'Google Search':
            StackedPlotContributionData[item_header] = []
            StackedPlotContributionData[item_header] = StackedPlotContribution.iloc[:,next((i for i, item in enumerate(StackedPlotContributionHeaderArr.columns) if item == item_header), -1)].tolist()
        if item_header == 'Microsoft':
            StackedPlotContributionData[item_header] = []
            StackedPlotContributionData[item_header] = StackedPlotContribution.iloc[:,next((i for i, item in enumerate(StackedPlotContributionHeaderArr.columns) if item == item_header), -1)].tolist()
   
    labels = StackedPlotContribution.iloc[:,next((i for i, item in enumerate(StackedPlotContributionHeaderArr.columns) if item == 'Day'), -1)].tolist()

    pieContrib = pd.read_excel(client_data.data,sheet_name='Pie Chart Contribution')
    totalContribution= pieContrib.iloc[:,2].tolist()
    labels3 = pieContrib.iloc[:,0].tolist()


    'Base sale Contribution Chart Data'
    BaseSaleData={}
    BaseSaleContribution = pd.read_excel (client_data.data,sheet_name='Base Sale Contribution')
    BaseSaleContributionHeaderArr = pd.read_excel (client_data.data,sheet_name='Base Sale Contribution',nrows=0)    

    for item_header in BaseSaleContributionHeaderArr:  
        if item_header == 'alpha':
            BaseSaleData[item_header] = []      
        if 'macro_gen_' in item_header:
            BaseSaleData[item_header] = []
        if 'macro_notable_' in item_header:
            BaseSaleData[item_header] = []
        if item_header == 'Unnamed: 0':
            BaseSaleData[item_header] = []
    for item_header in BaseSaleContributionHeaderArr:         
        if 'macro_gen_' in item_header:
            BaseSaleData[item_header] = BaseSaleContribution.iloc[:,next((i for i, item in enumerate(BaseSaleContributionHeaderArr.columns) if item == item_header), -1)].tolist()
        if 'macro_notable_' in item_header:
            BaseSaleData[item_header] = BaseSaleContribution.iloc[:,next((i for i, item in enumerate(BaseSaleContributionHeaderArr.columns) if item == item_header), -1)].tolist()
        if item_header == 'alpha':
            BaseSaleData[item_header] = BaseSaleContribution.iloc[:,next((i for i, item in enumerate(BaseSaleContributionHeaderArr.columns) if item == item_header), -1)].tolist()
        if item_header == 'Unnamed: 0':
            BaseSaleData[item_header] = BaseSaleContribution.iloc[:,next((i for i, item in enumerate(BaseSaleContributionHeaderArr.columns) if item == item_header), -1)].tolist()
 
    BaseSaleContributionlabels = BaseSaleContribution.iloc[:,next((i for i, item in enumerate(BaseSaleContributionHeaderArr.columns) if item == 'Day'), -1)].tolist()
    
    AdstockedHeaderArr = pd.read_excel (client_data.data,sheet_name='Adstocked Data',nrows=0)  
    HeaderArr = []
    for item_header in AdstockedHeaderArr:
        if '_adstocked' in item_header and  'spend_' in item_header:
            HeaderArr.append(((item_header.replace('spend_','')).replace('_adstocked','')).replace('_',''))
    return render_template('home/modeloutput.html',ChannelColorArr=ChannelColorArr,BaseSaleData=BaseSaleData,Tags=HeaderArr,username=us,userid=user.id, totalContribution=totalContribution, labels3 =labels3, StackedPlotContributionData=StackedPlotContributionData,labels = labels,
    Baseline_labels=BaseSaleContributionlabels)

@blueprint.route('/<template>')
@login_required
def route_template(template):

    try:

        if not template.endswith('.html'):
            template += '.html'

        # Detect the current page
        segment = get_segment(request)

        # Serve the file (if exists) from app/templates/home/FILE.html
        return render_template("home/" + template, segment=segment)

    except TemplateNotFound:
        return render_template('home/page-404.html'), 404

    except:
        return render_template('home/page-500.html'), 500


# Helper - Extract current page name from request
def get_segment(request):

    try:

        segment = request.path.split('/')[-1]

        if segment == '':
            segment = 'index'

        return segment

    except:
        return None

@blueprint.route("/index/rosa", methods=["GET", "POST"])
def rosa():
    # If the user is not an admin - inform the user of limited access
    data={}
    if request.method == 'POST':
        client_data = ClientData.query.filter_by(user_id=request.values['user_id']).first()    
        RoasChanellLine = pd.read_excel (client_data.data,sheet_name='ROAS - '+request.values['filter'])
        RoasChanellLineHeaderArr = pd.read_excel (client_data.data,sheet_name='ROAS - '+request.values['filter'],nrows=0)
        WeeklySpendLine = RoasChanellLine.iloc[:,1].tolist()
        RevenueLine = RoasChanellLine.iloc[:,next((i for i, item in enumerate(RoasChanellLineHeaderArr.columns) if item == 'Revenue'), -1)].tolist()
        RoasLine = RoasChanellLine.iloc[:,next((i for i, item in enumerate(RoasChanellLineHeaderArr.columns) if item == 'ROAS'), -1)].tolist()
        data={'WeeklySpendLine':WeeklySpendLine,'RevenueLine':RevenueLine,'RoasLine':RoasLine}
    return data;
@blueprint.route("/index/scenariocomparison", methods=["GET", "POST"])
def scenariocomparison():
    # If the user is not an admin - inform the user of limited access
    data={}
    if request.method == 'POST':
        client_data = ClientData.query.filter_by(user_id=request.values['user_id']).first()    
        ScenarioComparisonData = pd.read_excel (client_data.data,sheet_name='Scenario '+request.values['filter'] + ' Comparison')
        ScenarioComparisonHeaderArr = pd.read_excel (client_data.data,sheet_name='Scenario '+request.values['filter'] + ' Comparison',nrows=0)
        ScenarioComparisonlabel = ScenarioComparisonData.iloc[:,0].tolist()
        BaseScenarioComparison = ScenarioComparisonData.iloc[:,next((i for i, item in enumerate(ScenarioComparisonHeaderArr.columns) if item == 'Base Scenario'), -1)].tolist()
        ROASOptimizedComparison = ScenarioComparisonData.iloc[:,next((i for i, item in enumerate(ScenarioComparisonHeaderArr.columns) if item == 'ROAS Optimized'), -1)].tolist()
        DifferentComparison = ScenarioComparisonData.iloc[:,next((i for i, item in enumerate(ScenarioComparisonHeaderArr.columns) if item == 'Difference'), -1)].tolist()
        
        
        TotalData = pd.read_excel (client_data.data,sheet_name='Media Plan Recommended Totals')
        TotalDataHeaderArr = pd.read_excel (client_data.data,sheet_name='Media Plan Recommended Totals',nrows=0)
        TotalPecentage = TotalData.iloc[:,next((i for i, item in enumerate(TotalDataHeaderArr.columns) if item == 'Percent Change'), -1)].tolist()
        data={'TotalPecentage':TotalPecentage,'ScenarioComparisonlabel':ScenarioComparisonlabel,'BaseScenarioComparison':BaseScenarioComparison,'ROASOptimizedComparison':ROASOptimizedComparison,'DifferentComparison':DifferentComparison}
    return data;

@blueprint.route("/index/scenariocontribution", methods=["GET", "POST"])
def scenariocontribution():
    # If the user is not an admin - inform the user of limited access
    data={}
    if request.method == 'POST':
        client_data = ClientData.query.filter_by(user_id=request.values['user_id']).first()   
        ScenarioContribution = pd.read_excel (client_data.data,sheet_name=request.values['filter']+' Contribution')
        ScenarioContributionHeaderArr = pd.read_excel (client_data.data,sheet_name=request.values['filter']+' Contribution',nrows=0)
        
        ScenarioContributionData = {}
        for item_header in ScenarioContributionHeaderArr:  
            if item_header == 'Base Revenue':
                ScenarioContributionData[item_header] = []     
                ScenarioContributionData[item_header] = ScenarioContribution.iloc[:,next((i for i, item in enumerate(ScenarioContributionHeaderArr.columns) if item == item_header), -1)].tolist()  
            if 'revenue_' in item_header:
                ScenarioContributionData[item_header] = []
                ScenarioContributionData[item_header] = ScenarioContribution.iloc[:,next((i for i, item in enumerate(ScenarioContributionHeaderArr.columns) if item == item_header), -1)].tolist() 
        Scenariocontributionlabels = ScenarioContribution.iloc[:,next((i for i, item in enumerate(ScenarioContributionHeaderArr.columns) if item == 'Day'), -1)].tolist()
        print('===ScenarioContributionHeaderArr o')
        print(ScenarioContributionData)
        data={'ScenarioContributionData':ScenarioContributionData,'label':Scenariocontributionlabels}
       
    return data

@blueprint.route("/index/adstockedspend", methods=["GET", "POST"])
def adstockedspend():
    # If the user is not an admin - inform the user of limited access
    data={}
    if request.method == 'POST':
        client_data = ClientData.query.filter_by(user_id=request.values['user_id']).first()     
        Adsctocked = pd.read_excel (client_data.data,sheet_name='Adstocked Data')
        AdstockedHeaderArr = pd.read_excel (client_data.data,sheet_name='Adstocked Data',nrows=0)  
        HeaderArr = []
        for item_header in AdstockedHeaderArr:
            if 'spend_' in item_header:
                HeaderArr.append((item_header.replace('spend_','')).replace('_',''))
        Bar_adsctocked_Spend = Adsctocked.iloc[:,next((i for i, item in enumerate(AdstockedHeaderArr.columns) if item == 'spend_'+request.values['filter']), -1)].tolist()
        Line_adsctocked_Spend = Adsctocked.iloc[:,next((i for i, item in enumerate(AdstockedHeaderArr.columns) if item == 'spend_'+request.values['filter']+'_adstocked'), -1)].tolist()
        AdsctockedLabels = Adsctocked.iloc[:,next((i for i, item in enumerate(AdstockedHeaderArr.columns) if item == 'Day'), -1)].tolist()
        data={'Bar_adsctocked_Spend':Bar_adsctocked_Spend,'Line_adsctocked_Spend':Line_adsctocked_Spend,'AdsctockedLabels':AdsctockedLabels}
    return data;

@blueprint.route("/index/adstockedimpr", methods=["GET", "POST"])
def adstockedimpr():
    # If the user is not an admin - inform the user of limited access
    data={}
    if request.method == 'POST':
        client_data = ClientData.query.filter_by(user_id=request.values['user_id']).first()
        Adsctocked = pd.read_excel (client_data.data,sheet_name='Adstocked Data')
        AdstockedHeaderArr = pd.read_excel (client_data.data,sheet_name='Adstocked Data',nrows=0)    
        HeaderArr = []
        for item_header in AdstockedHeaderArr:
            if 'impr_' in item_header:
                HeaderArr.append((item_header.replace('impr_','')).replace('_',''))
        Bar_adsctocked_Impr = Adsctocked.iloc[:,next((i for i, item in enumerate(AdstockedHeaderArr.columns) if item == 'impr_'+request.values['filter']), -1)].tolist()  
        Line_adsctocked_Impr = Adsctocked.iloc[:,next((i for i, item in enumerate(AdstockedHeaderArr.columns) if item == 'impr_'+request.values['filter']+'_adstocked'), -1)].tolist()
        AdsctockedLabels = Adsctocked.iloc[:,next((i for i, item in enumerate(AdstockedHeaderArr.columns) if item == 'Day'), -1)].tolist()
        data={'Bar_adsctocked_Impr':Bar_adsctocked_Impr,'Line_adsctocked_Impr':Line_adsctocked_Impr,'AdsctockedLabels':AdsctockedLabels}
    return data;



@blueprint.route("/index/media-optimization2", methods=["GET", "POST"])
def profile():
    # If the user is not an admin - inform the user of limited access
    if request.method == 'POST':
        channelName = request.form["channel"]


    return render_template("home/profile.html", user=user)




#added s

@blueprint.route("/index/media-optimization", methods=["GET", "POST"])
@login_required
def media_optimization():
    request_values = request.values
    print("req: ", request_values)

    client_data = ClientData.query.filter_by(user_id=2).first()
    
    

    table_inputs_id = ["channel","start-date","end-date","inputValue","current-channel"]

    passed_values_to_tables = get_passed_values(request_values, table_inputs_id)


    (
        defaultChanellName,
        sheet_names,
        channels,
        table_input_id,
        default_roas_value,
        default_start,
        default_end,
        roi, 
        spend ,
        returns,
        avgSpend,
        avgRet,
        WeeksWithSpend,

        selectedRoiSel,
        totalSpendSel,
        totalReturnSel,
        avgRevSel,
        DifSpend,
        DifReturn,
        ToffRoi,
        Revenue,
        WeeklySpend
    ) = load_table_data(client_data.data ,passed_values_to_tables)

    return render_template(
        "home/media_optimization.html",
        WeeksWithSpend = WeeksWithSpend,
        WeeklySpend=WeeklySpend,
        Revenue=Revenue,
        user=current_user,
        channels=channels,
        defaultChanellName = defaultChanellName,
        table_input_id=table_input_id,
        default_roas_value=default_roas_value,
        default_start=default_start,
        default_end=default_end,

        totalSpend = spend,
        totalReturn = returns,
        avgSpentWeeks = avgSpend,
        avgReturnsWeeks = avgRet,
        rois=roi,
        selectedRoiSel=selectedRoiSel,
        totalSpendSel=totalSpendSel,
        totalReturnSel=totalReturnSel,
        avgRevSel=avgRevSel ,

        DifSpend=DifSpend,
        DifReturn=DifReturn,
        ToffRoi=ToffRoi,
        zip=zip,
    )
