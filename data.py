import pandas as pd
import requests
import plotly.express as px
import urllib.parse as encode


# ------------------- Key for Data Names --------------------
# This is what I renamed the values pulled from https://aitopics.org. On the left is what aitopics
# calls them and on the left is what I renamed them too (Ex: aitopics = myName)
#     - cdid = id
#     - ConceptTags = tags
#     - TaxNodes = taxNodes
#     - Authors = authors
#     - Title = Tile
#     - Modified = date

class Data:

    def __init__(self,
                 filters=None,  # todo: Figure out why this cannot be None
                 fields='concept-tagsConf,cdid,taxnodesConf,modified,authorsRaw,title',
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
            'Authorization': "Basic YWl0b3BpY3MtZ3Vlc3Q6SHZHU2F1SjAwQ09nUm5HWA==",
            'Content-Type': "application/x-www-form-urlencoded"
        }

        if url is None:
            payload = encode.urlencode(payload_data)
        else:
            payload = url.replace('https://aitopics.org/search?', '')
            payload = payload.replace('fileds', 'fields')

        response = requests.request("POST", base_url, data=payload, headers=headers, params=params)
        self.data = pd.DataFrame(response.json())
        print(self.data)

        self.cdid = self.createCdid()
        self.tags = self.createConceptTags()
        self.taxNodes = self.createTaxNodes()
        self.dates = self.createModified()
        self.authors = self.createAuthorsRaw()
        self.titles = self.createTitle()

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

    def formatValue(self, value, target='::'):
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
        targets = []
        for id in ids.id:
            target = data.loc[data.id == id].get('modified').iloc[0]
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
    def makeScatterPlot(self, data, trend='ols', plot_layout=None):
        figure = px.scatter(data, x='date', y='occurrences', color='target', trendline=trend)
        figure.update_layout(plot_layout)
        return figure

    def makeLineChart(self, data, plot_layout=None):
        figure = px.line(data, x='date', y='occurrences', color='target')
        figure.update_layout(plot_layout)
        return figure

    def getPlotData(self, data, target, start_date, end_date):
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
            'occurrences').reset_index()  # todo: REsample by month or 30 day

        dates_df['target'] = target  # ToDo: Generalize this

        if (start_date is not None) and (end_date is not None):  # There is a start & and date
            return dates_df[(dates_df['date'] > start_date) & (dates_df['date'] < end_date)]
        elif (start_date is None) and (end_date is not None):  # Only an end date
            return dates_df[dates_df['date'] < end_date]
        elif (start_date is not None) and (end_date is None):  # Only a start date
            return dates_df[(dates_df['date'] > start_date)]
        else:
            return dates_df

    def updatePlotLayout(self, plot, layout):
        plot.update_layout(layout)
        return layout

    def getTopX(self, data, count):
        tags_count = data[data.columns[1]].value_counts()
        top_x = tags_count.nlargest(count).keys()

        return top_x

    def plotTopX(self, data, count, plot_type=None, start_date=None, end_date=None):
        top_x = self.getTopX(data, count)

        chart_data = []
        for target in top_x:
            chart_data.append(self.getPlotData(data, target, start_date, end_date))
        top_x_data = pd.concat(chart_data)

        match plot_type:
            case 'line':
                plot_top_x = self.makeLineChart(top_x_data)
            case 'scatter':
                plot_top_x = self.makeScatterPlot(top_x_data)
            case _:
                plot_top_x = self.makeLineChart(top_x_data)

        return plot_top_x

    # def lineTopX(self, data, count, start_date=None, end_date=None):
