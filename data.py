import pandas as pd
import requests
import plotly.express as px
import urllib.parse as encode
import os
from datetime import datetime, timedelta

# ------------------------------------------------- Key for Data Names -------------------------------------------------
# This is what I renamed the values pulled from https://aitopics.org. On the left is what aitopics
# calls them and on the left is what I renamed them too (Ex: aitopics = myName)
#   - cdid = id
#   - ConceptTags = tags
#   - TaxNodes = taxNodes
#   - Authors = authors
#   - Title = title
#   - Modified = date

AUTHORIZATION = os.environ['AUTHORIZATION']
CONTENT_TYPE = os.environ['CONTENT_TYPE']


class Data:

    def __init__(self,
                 filters=None,  # todo: Figure out why this cannot be None
                 fields='concept-tagsConf,cdid,taxnodesConf,modified,title,authorsRaw',
                 limit=1000,
                 offset=0,
                 url=None
                 ):

        # ToDo: Add url encoding

        base_url = "https://aitopics.org/i2kweb/webapi/search"
        params = {
            "limit": limit,
            "offset": offset
        }

        payload_data = {
            "fields": fields,
            "filters": filters
        }

        headers = {
            'Authorization': AUTHORIZATION,
            'Content-Type': CONTENT_TYPE
        }

        if url is None:
            payload = encode.urlencode(payload_data)

        else:
            payload = "fields=" + encode.quote(fields) + '&' + url.replace('https://aitopics.org/search?', '')

        response = requests.request("POST", base_url, data=payload, headers=headers, params=params)
        self.data = pd.DataFrame(response.json())

        self.cdid = self.createCdid()
        self.tags = self.createConceptTags()
        self.taxNodes = self.createTaxNodes()
        self.dates = self.createModified()
        self.titles = self.createTitle()

        try:
            self.authors = self.createAuthorsRaw()
        except:
            self.authors = None

    # --------------------------------------------- Creates Data Structures --------------------------------------------

    def createConceptTags(self):
        """Creates the Concept Tags Dataset"""
        tags = self.makeMultiIndex('concept-tagsConf', 'tags')
        return tags

    def createCdid(self):
        """Creates the cdid Dataset"""
        cdid = self.data.get('cdid')
        return cdid

    def createTaxNodes(self):  # ToDo: Make this a hierarchical data structure
        """Creates the Tax Nodes Dataset"""
        tax_nodes = self.makeMultiIndex('taxnodesConf', 'tax-node')
        return tax_nodes

    def createModified(self):
        """Creates the Modified Dataset"""
        modified = self.makeIndex('modified', 'modified')
        return modified

    def createAuthorsRaw(self):
        """Creates the Authors Dataset"""
        authors = self.makeMultiIndex('authorsRaw', 'authors')
        return authors

    def createTitle(self):
        """Creates the title Dataset"""
        title = self.makeIndex('title', 'title')
        return title

    # ------------------------------------------------ Getter Functions ------------------------------------------------

    def getAllTags(self):
        """Returns all Concept Tags in Dataset"""
        return self.tags

    def getAllIds(self):
        """Returns all cdids in Dataset"""
        return self.cdid

    def getAllTaxNodes(self):
        """Returns all Tax Nodes in Dataset"""
        return self.taxNodes

    def getAllDates(self):
        """Returns all Modified (dates) in Dataset"""
        return self.dates

    def getAllAuthorsRaw(self):
        """Returns all Authors in Dataset"""
        return self.authors

    def getAllTitle(self):
        """Returns all Titles in Dataset"""
        return self.titles

    def getAllData(self):
        """Returns the unmodified Dataset"""
        return self.data

    # ------------------------------------------- Formatting Data Structures -------------------------------------------

    @staticmethod
    def formatValue(value, target='::'):
        """Removes all characters after the given target in a string"""
        end = value.find(target)
        return value[0:end]

    def makeMultiIndex(self, target, name):
        """Creates a Pandas MultiIndex from a Pandas Dataframe with a list inside"""
        result = []
        for index in self.data.index:
            cdid = self.cdid[index]
            value = self.data.get(target)[index]

            if isinstance(value, list):
                for item in value:
                    item = self.formatValue(item)
                    result.append((cdid, item))

        multi = pd.DataFrame(result, columns=['id', name])
        multi.set_index(['id'], inplace=True)
        # multi.set_index([multi.index, name], inplace=True)
        multi.sort_index()

        return multi.reset_index()

    def makeIndex(self, target, name):
        """Matches the correct cdid with the target item"""
        result = []
        for index in self.data.index:
            cdid = self.cdid[index]
            value = self.data.get(target)[index]
            result.append((cdid, value))

        index = pd.DataFrame(result, columns=['id', name])
        return index

    # ---------------------------------------------------- Get by ID ---------------------------------------------------
    # ToDo: make functions to get certain values of data

    def getXByID(self, data, ids):
        """Searches a set of data for the ID"""
        targets = []
        for item in ids.id:
            target = data.loc[data.id == item].get('modified').iloc[0]
            target = self.formatValue(target, target='T')
            targets.append(target)
        return targets

    def getTagsById(self, ids):  # ToDo: Test to see if it works
        return self.getXByID(self.tags, ids)

    def getDateById(self, ids):
        return self.getXByID(self.dates, ids)

    def getAuthorsById(self, ids):  # ToDo: Test to see if it works
        return self.getXByID(self.authors, ids)

    def getTitleByID(self, ids):  # ToDo: Test to see if it works
        return self.getXByID(self.titles, ids)

    # ----------------------------------------------------- Plots ------------------------------------------------------
    @staticmethod
    def makeScatterPlot(data, trend='lowess', trend_options=None, plot_layout=None):
        figure = px.scatter(data, x='date', y='occurrences', color='target',
                            trendline=trend, trendline_options=trend_options)
        figure.update_layout(plot_layout)
        return figure

    @staticmethod
    def makeLineChart(data, plot_layout=None):
        figure = px.line(data, x='date', y='occurrences', color='target')
        figure.update_layout(plot_layout)

        return figure

    @staticmethod
    def makeRadarChart(data, plot_layout=None):
        figure = px.line_polar(data, r='occurrences', theta='target', line_close=True)
        figure.update_traces(fill='toself')
        figure.update_layout(plot_layout)

        return figure

    @staticmethod
    def makeBarChart(data, plot_layout=None):
        figure = px.bar(data)
        figure.update_layout(plot_layout)

        return figure

    # ---------------------------------------------- Plot Helper Functions ---------------------------------------------

    def getPlotDataByDate(self, data, target, start_date=None, end_date=None):
        result = data.loc[data[data.columns[1]] == target]
        dates = self.getDateById(result)

        dates = [pd.to_datetime(d) for d in dates]
        dates_df = pd.DataFrame(
            {
                "date": dates
            })
        dates_df = dates_df.groupby(dates_df['date'])

        dates_df = dates_df.value_counts()
        dates_df = dates_df.groupby(pd.Grouper(freq='M')).sum().to_frame(
            'occurrences').reset_index()

        dates_df['target'] = target

        if end_date is None:  # ToDo: Do the better way to subtract datetime
            end_date = datetime.today() - timedelta(30)

        if (start_date is not None) and (end_date is not None):  # There is a start & and date
            return dates_df[(dates_df['date'] > start_date) & (dates_df['date'] < end_date)]
        elif (start_date is None) and (end_date is not None):  # Only an end date
            return dates_df[dates_df['date'] < end_date]
        elif (start_date is not None) and (end_date is None):  # Only a start date
            return dates_df[(dates_df['date'] > start_date)]
        else:
            return dates_df

    def getPlotDataByOccurrences(self, data, target, start_date=None, end_date=None):
        """Takes a dataset and returns data sorted by the given target and the number of occurrences that target has
        in the """
        plot_data = self.getPlotDataByDate(data, target, start_date=start_date, end_date=end_date)
        occurrences = plot_data['occurrences'].sum()

        result = pd.DataFrame({
            'target': [target],
            'occurrences': [occurrences]
        })

        return result

    @staticmethod
    def updatePlotLayout(plot, layout):
        plot.update_layout(layout)

        return layout

    @staticmethod
    def getTopX(data, count):
        tags_count = data[data.columns[1]].value_counts()
        top_x = tags_count.nlargest(count).keys()

        return top_x

    def plotTopX(self, data, count, plot_type, plot_layout=None, trend='lowess', trend_options=None,
                 start_date=None, end_date=None):
        global plot_top_x
        top_x = self.getTopX(data, count)

        match plot_type:
            case 'radar':
                chart_data = []
                for target in top_x:
                    chart_data.append(
                        self.getPlotDataByOccurrences(data, target, start_date=start_date, end_date=end_date))
                top_x_data = pd.concat(chart_data).reset_index(drop=True)
            case _:
                chart_data = []
                for target in top_x:
                    chart_data.append(self.getPlotDataByDate(data, target, start_date=start_date, end_date=end_date))
                top_x_data = pd.concat(chart_data)

        match plot_type:
            case 'line':
                plot_top_x = self.makeLineChart(top_x_data, plot_layout=plot_layout)
            case 'scatter':
                plot_top_x = self.makeScatterPlot(top_x_data, plot_layout=plot_layout,
                                                  trend=trend, trend_options=trend_options)
            case 'radar':
                plot_top_x = self.makeRadarChart(top_x_data, plot_layout=plot_layout)
            case _:
                pass

        return plot_top_x

    def weeksTrendingTags(self):
        start = end_date = datetime.today() - timedelta(7)
        end = datetime.today()

        plot = self.plotTopX(self.tags, 5, 'scatter', start_date=start, end_date=end)

        return plot

    # --------------------------------------------- Trend Line Calculations --------------------------------------------

    @staticmethod
    def getTrendLineData(plot):
        """Takes a plot and returns the trend line data"""
        data = plot.to_dict().get('data')

        trend_line_data = []
        for item in data:
            title = item.get('hovertemplate')

            if 'trendline' in title:
                name = item.get('name')
                line = item.get('y')

                series = pd.Series(line, name=name)

                trend_line_data.append(series)

        return pd.concat(trend_line_data, axis=1)

    def minMaxScaled(self, plot):
        """Takes in a plot and applies min max scaling to the trend"""

        data = self.getTrendLineData(plot)

        answer = []
        for column in data.columns:
            result = (data[column] - data[column].min()) / (data[column].max() - data[column].min())
            answer.append(result)

        return pd.concat(answer, axis=1)

    def zScore(self, plot):
        """Takes in a plot and applies Z Score to the trend"""

        data = self.getTrendLineData(plot)

        answer = []
        for column in data:
            result = (data - data[column].mean()) / data[column].std()
            answer.append(result)

        return pd.concat(answer, axis=1)

    def maxScaled(self, plot):
        """Takes in a plot and applies max scaling to the trend"""

        data = self.getTrendLineData(plot)

        answer = []
        for column in data:
            result = data[column] / data[column].abs().max()
            answer.append(result)

        return pd.concat(answer, axis=1)


