from typing import List, Tuple

import pandas as pd

import datetime

def load_data(path, sheet_name):
    return pd.read_excel(
        path,
        sheet_name=sheet_name,
        index_col=0,
        engine="openpyxl",
    )


def get_all_sheets(path) -> List[str]:
    exceldata = pd.ExcelFile(path)
    return exceldata.sheet_names


def get_roas_sheets_and_channels(path) -> Tuple[List[str], List[str]]:
    sheets = get_all_sheets(path)
    sheet_names = [sheet for sheet in sheets if "ROAS" in sheet]
    channels = [s.split("-")[1].strip() for s in sheet_names]
    print(channels)
    return sheet_names, channels


def get_default_roas_values(path):
    sheet_names, _ = get_roas_sheets_and_channels(path)
    values = [
        round(load_data(path, sheet_name)["ROAS"].max(), 2)
        for sheet_name in sheet_names
    ]
    return values

def get_default_roas_value(path,sheet_name):
    value = round(load_data(path, sheet_name)["Weekly Spend"].max(), 2)
    return value

def get_default_start_end_times(overview):
    start_date = pd.to_datetime(str(overview["Day"].min())).strftime("%Y-%m-%d")
    end_date = pd.to_datetime(str(overview["Day"].max())).strftime("%Y-%m-%d")
    return start_date, end_date


def filter_data_by_date(data, start_date, end_date):
    mask = (data["Day"] > start_date) & (data["Day"] <= end_date)
    return data.loc[mask]


def calculate_actual_roi(path, start_date, end_date, channel):
    stacked_plot_df = load_data(path, "Stacked Plot Contribution")
    overview_df = load_data(path, "Overview")

    filtered_stacked_plot_df = filter_data_by_date(
        stacked_plot_df, start_date, end_date
    )
    filtered_media_sum = filtered_stacked_plot_df[channel].sum()

    filtered_overview_df = filter_data_by_date(overview_df, start_date, end_date)
    filtered_spend_sum = filtered_overview_df[f"spend_{channel}"].sum()

    try:
        end_date = datetime.datetime.strptime(end_date, '%Y-%m-%d')
        start_date = datetime.datetime.strptime(start_date, '%Y-%m-%d')
        weeks = (end_date - start_date).days /7
        avgSpend = filtered_spend_sum/weeks
        avgRet = filtered_media_sum/weeks
        roi = filtered_media_sum / filtered_spend_sum
        return round(roi, 2), round(filtered_spend_sum, 2), round(filtered_media_sum, 2) ,round(avgSpend, 2),round(avgRet, 2)
    except ZeroDivisionError:
        return " ", " ", " "," ", " "


def calculate_actual_roiimp(RawDataDf, stacked_plot_df, start_date, end_date, channel):

    filtered_stacked_plot_df = filter_data_by_date(
        stacked_plot_df, start_date, end_date
    )
    filteredStackSum = filtered_stacked_plot_df[channel].sum()
    
    filteredRawDataDf = filter_data_by_date(RawDataDf, start_date, end_date)
    rawDataGt1 = filteredRawDataDf[filteredRawDataDf[f"spend_{channel}"] > 1]

    filtered_spend_sum = filteredRawDataDf[f"spend_{channel}"].sum()


    
    try:
        end_date = datetime.datetime.strptime(end_date, '%Y-%m-%d')
        start_date = datetime.datetime.strptime(start_date, '%Y-%m-%d')
        weeks = (end_date - start_date).days /7
        print(weeks)
        roi = filteredStackSum / filtered_spend_sum
        avgSpend = filtered_spend_sum/weeks
        avgRet = filteredStackSum/weeks
        WeeksWithSpend = f"{len(rawDataGt1)} of {round(weeks)}"
        return round(roi, 2), round(filtered_spend_sum, 2), round(filteredStackSum, 2) ,round(avgSpend, 2),round(avgRet, 2), WeeksWithSpend, round(weeks)
    except ZeroDivisionError:
        return " ", " ", " "," ", " ", " "," "

def getTotalSpend(path, start_date, end_date, channel):
    stacked_plot_df = load_data(path, "Stacked Plot Contribution")
    overview_df = load_data(path, "Overview")

    filtered_stacked_plot_df = filter_data_by_date(
        stacked_plot_df, start_date, end_date
    )
    filtered_media_sum = filtered_stacked_plot_df[channel].sum()

    filtered_overview_df = filter_data_by_date(overview_df, start_date, end_date)
    filtered_spend_sum = filtered_overview_df[f"spend_{channel}"].sum()

    try:
        print(filtered_media_sum)
        end_date = datetime.datetime.strptime(end_date, '%Y-%m-%d')
        start_date = datetime.datetime.strptime(start_date, '%Y-%m-%d')
        weeks = (end_date - start_date).days /7
        print(weeks)
        print(filtered_spend_sum)
        roi = filtered_media_sum / filtered_spend_sum
        return round(filtered_media_sum, 2) , round(filtered_media_sum, 2)
    except ZeroDivisionError:
        return " ", " "



def get_weekly_spend_closest(data, value):
    closest_value = data.iloc[(data["Weekly Spend"] - value).abs().argsort()[:2]]["Revenue"]
    return max(closest_value.values)


def get_revenue_closest(data, value):
    return data.iloc[(data["ROAS"] - float(value)).abs().argsort()[0]]["Revenue"]


def calculate_overspend(path, sheet_name, start_date, end_date, value):
    value = float(value)
    channel = sheet_name.split("-")[1].strip()
    overview_df = load_data(path, "Overview")
    roas_df = load_data(path, sheet_name)
    weekly_spend = get_weekly_spend_closest(roas_df, value)

    filtered_overview_df = filter_data_by_date(overview_df, start_date, end_date)
    filtered_spend_sum = filtered_overview_df[f"spend_{channel}"].sum()

    try:
        overspend = filtered_spend_sum - (weekly_spend * len(filtered_overview_df))
        totalReturn = value * len(filtered_overview_df)
        selectRoi = overspend/totalReturn

        return round(overspend)
    except:
        return " "

def calculate_overspend_revenue(path, sheet_name, start_date, end_date, value):
    value = float(value)
    channel = sheet_name.split("-")[1].strip()
    stacked_plot_df = load_data(path, "Stacked Plot Contribution")
    overview_df = load_data(path, "Overview")
    roas_df = load_data(path, sheet_name)
    revenue = get_revenue_closest(roas_df, value)

    filtered_stacked_plot_df = filter_data_by_date(
        stacked_plot_df, start_date, end_date
    )
    filtered_media_sum = filtered_stacked_plot_df[channel].sum()

    filtered_overview_df = filter_data_by_date(overview_df, start_date, end_date)

    try:
        overspend_revenue = filtered_media_sum - (revenue * len(filtered_overview_df))
        return round(overspend_revenue)
    except:
        return " "


def _calculate_roi_overspend(overspend: int, overspend_revenue: int):
    return round((overspend_revenue / overspend), 2)


def calculate_roi_overspend(overspend: int, overspend_revenue: int):
    try:
        # if any of the values is not available return not available as well
        if isinstance(overspend, str) or isinstance(overspend_revenue, str):
            return " "
        # otherwise calculate_roi_overspend
        roi_overspend = _calculate_roi_overspend(overspend, overspend_revenue)
        return roi_overspend
    except ZeroDivisionError:
        return " "


def split_ids(id_):
    split_ids_by_dash = id_.split("-")
    input_index = split_ids_by_dash.index("input")
    new_table_id = split_ids_by_dash[:input_index]
    return "_".join(new_table_id)


def get_passed_values(request_values, table_inputs_id):
    passed_values_to_tables = {}

    for table_id in table_inputs_id:
        passed_values_to_tables[table_id] = request_values.get(table_id)
    return passed_values_to_tables


def has_values(passed_values_to_tables):
    for key in passed_values_to_tables:
        if passed_values_to_tables[key] is None:
            return False
    return True


def get_overspend_revenue(
    path,
    channels,
    passed_values_to_tables,
    table_inputs_id,
    sheet_names,
    default_roas_values,
    default_start,
    default_end,
):

    if has_values(passed_values_to_tables):
        start_date = passed_values_to_tables["start_date"]
        end_date = passed_values_to_tables["end_date"]
        values_sheets = {
            sheet_name: passed_values_to_tables[table_id]
            for sheet_name, table_id in zip(sheet_names, table_inputs_id)
        }
        rois = []
        totalSpend = []
        totalReturn = []
        AvgSpentWeeks = []
        AvgReturnsWeeks = []
        for channel in channels:
            roi, spend , returns,avgSpend,avgRet = calculate_actual_roi(path, start_date, end_date, channel)
            rois.append(roi)
            totalSpend.append(spend)
            totalReturn.append(returns)
            AvgSpentWeeks.append(avgSpend)
            AvgReturnsWeeks.append(avgRet)


        print(rois)
        overspends = [
            calculate_overspend(path, sheet_name, start_date, end_date, val)
            for sheet_name, val in values_sheets.items()
        ]
        overspend_revenues = [
            calculate_overspend_revenue(path, sheet_name, start_date, end_date, val)
            for sheet_name, val in values_sheets.items()
        ]
        roi_overspends = [
            calculate_roi_overspend(overspend, overspend_revenue)
            for overspend, overspend_revenue in zip(overspends, overspend_revenues)
        ]

        return rois, overspends, overspend_revenues, roi_overspends
    else:
        values_sheets = {
            sheet_name: val for sheet_name, val in zip(sheet_names, default_roas_values)
        }
        rois = []
        totalSpend = []
        totalReturn = []
        AvgSpentWeeks = []
        AvgReturnsWeeks = []
        for channel in channels:
            roi, spend , returns,avgSpend,avgRet = calculate_actual_roi(path, default_start, default_end, channel)
            rois.append(roi)
            totalSpend.append(spend)
            totalReturn.append(returns)
            AvgSpentWeeks.append(avgSpend)
            AvgReturnsWeeks.append(avgRet)

        overspends = [
            calculate_overspend(path, sheet_name, default_start, default_end, val)
            for sheet_name, val in values_sheets.items()
        ]
        overspend_revenues = [
            calculate_overspend_revenue(
                path, sheet_name, default_start, default_end, val
            )
            for sheet_name, val in values_sheets.items()
        ]
        roi_overspends = [
            calculate_roi_overspend(overspend, overspend_revenue)
            for overspend, overspend_revenue in zip(overspends, overspend_revenues)
        ]

        return totalSpend,totalReturn, AvgSpentWeeks, AvgReturnsWeeks,rois, overspends, overspend_revenues, roi_overspends


def get_data_utils(path):
    sheet_names, channels = get_roas_sheets_and_channels(path)
    channels_with_dash = [channel.replace(" ", "-") for channel in channels]
    print(channels_with_dash)
    channels = [channel for channel in channels]
    tab_ids = [f"{channel.lower()}-tab" for channel in channels_with_dash]
    section_ids = [f"{channel.lower()}-section" for channel in channels_with_dash]
    section_targets = [f"#{id_}" for id_ in section_ids]
    channel_plot_ids = [f"{channel.lower()}-plot" for channel in channels_with_dash]
    table_inputs_id = [
        f"{channel.lower()}-input-value" for channel in channels_with_dash
    ]
    default_roas_values = get_default_roas_values(path)
    default_start, default_end = get_default_start_end_times(path)
    return (
        sheet_names,
        channels,
        tab_ids,
        section_ids,
        section_targets,
        channel_plot_ids,
        table_inputs_id,
        default_roas_values,
        default_start,
        default_end,
    )
def load_table_data(path,passed_values_to_tables):
    sheet_names, channels = get_roas_sheets_and_channels(path)
    channels_with_dash = [channel.replace(" ", "-") for channel in channels]

    table_input_ids = [
        f"{channel.lower()}-input-value" for channel in channels_with_dash
    ]
    overview = load_data(path, "Overview")
    stacked_plot_df = load_data(path, "Stacked Plot Contribution")
    RawDataDf = load_data(path, "Raw Data")
    default_start, default_end = get_default_start_end_times(overview)
    
   

    if has_values(passed_values_to_tables):
        print(passed_values_to_tables)
        if passed_values_to_tables["channel"] != "hide":
            channelName = passed_values_to_tables["channel"]
        else:
            channelName = passed_values_to_tables["current-channel"]
            
        defaultChanell = "ROAS - " + channelName
        channel_with_dash = channelName.replace(" ", "-")
        table_input_id = f"{channel_with_dash.lower()}-input-value"
        default_start = passed_values_to_tables["start-date"]
        default_end = passed_values_to_tables["end-date"]
        defaultChanellName = defaultChanell.split("-")[1].strip()
        default_roas_value = get_default_roas_value(path,defaultChanell)
        roi, spend , returns,avgSpend,avgRet, WeeksWithSpend ,weeksNum= calculate_actual_roiimp(RawDataDf, stacked_plot_df, default_start, default_end, channelName)
        val = float(passed_values_to_tables["inputValue"])


        RoasChanell = load_data(path,defaultChanell)
        WeeklySpend = RoasChanell.iloc[:,0].tolist()
        Revenue = RoasChanell.iloc[:,1].tolist()
        avgRev = get_weekly_spend_closest(RoasChanell, val)
        totalReturn = avgRev/weeksNum
        totalSpend = val * weeksNum
        selectedRoi = avgRev/totalSpend

        DifSpend = spend - totalSpend
        DifReturn = returns - totalReturn
        ToffRoi = DifReturn/DifSpend
    else:
        defaultChanell = sheet_names[0]
        firstChannel = channels[0]
        table_input_id = f"{firstChannel.lower()}-input-value"
        defaultChanellName = defaultChanell.split("-")[1].strip()
        default_roas_value = get_default_roas_value(path,defaultChanell)
        roi, spend , returns,avgSpend,avgRet, WeeksWithSpend,weeksNum = calculate_actual_roiimp(RawDataDf, stacked_plot_df, default_start, default_end, firstChannel)
        
        val = default_roas_value
        RoasChanell = load_data(path,defaultChanell)
        print(RoasChanell)
        WeeklySpend = RoasChanell.iloc[:,0].tolist()
        Revenue = RoasChanell.iloc[:,1].tolist()
        avgRev = get_weekly_spend_closest(RoasChanell, val)
        totalReturn = avgRev/weeksNum
        totalSpend = val * weeksNum
        selectedRoi = avgRev/totalSpend
        
        DifSpend = spend - totalSpend
        DifReturn = returns - totalReturn
        ToffRoi = DifReturn/DifSpend

    return (
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

        round(selectedRoi,2),
        round(totalSpend,2),
        round(totalReturn,2),
        round(avgRev,2),
        DifSpend,
        DifReturn,
        round(ToffRoi,2),

        Revenue,
        WeeklySpend

    )