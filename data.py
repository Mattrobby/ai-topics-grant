import numpy as np
import pandas as pd
import requests
import matplotlib.pyplot as plt
from sklearn.linear_model import LinearRegression
import plotly.express as px


# ------------------- Key for Data Names --------------------
# This is what I renamed the values pulled from https://aitopics.org. On the left is what aitopics
# calls them and on the left is what I renamed them too (Ex: aitopics = myName)
#     - cdid = id
#     - ConceptTags = tags
#     - TaxNodes = ToDo: get a name for TaxNodes
#     - Authors = authors
#     - Title = Tile

class Data:

    def __init__(self,
                 filters='taxnodes:Technology|Information Technology|Artificial Intelligence|Cognitive '
                         'Science@@semantic-units:arXiv.org',
                 fields='concept-tagsConf,cdid,taxnodesConf,modified,authorsRaw,title',
                 sort='title_sort asc',
                 limit=1000,
                 offset=0,
                 ):

        # ToDo: put string filters here

        url = filters.find('filters=')
        if url != -1:
            filters = filters[url + 8:]
            filters = filters.replace('%7C', '|')

        self.data = pd.DataFrame(self.pullData(filters, fields, sort, limit, offset))
        self.cdid = self.createCdid()
        self.conceptTags = self.createConceptTags()
        self.taxNodes = self.createTaxNodes()
        self.modified = self.createModified()
        self.authorsRaw = self.createAuthorsRaw()
        self.title = self.createTitle()

    # --------------------- Pulling Data ----------------------
    # ToDo: Make filters passed in as array instead of string

    def pullData(self, filters, fields, sort, limit, offset):
        """
        Pulls data from AI topics Server
        You can change the filters, fields, sort, limit, offset
        """
        url = "https://aitopics.org/i2kweb/webapi/search"

        querystring = {
            "filters": filters,
            "limit": limit,
            "sort": sort,
            "offset": offset
        }

        payload = "fields=concept-tagsConf%2Ccdid%2CtaxnodesConf%2Cmodified%2CauthorsRaw%2Ctitle"
        headers = {
            'Authorization': "Basic YWl0b3BpY3MtZ3Vlc3Q6SHZHU2F1SjAwQ09nUm5HWA==",
            'Content-Type': "application/x-www-form-urlencoded"
        }

        response = requests.request("POST", url, data=payload, headers=headers, params=querystring)

        return response.json()

    def filtersToString(self, filters):
        """Takes an array of filters and formats them as a string to pull the data"""
        pass

    def fieldsToString(self, fields):
        """Takes an array of field and formats them as a string to pull the data"""
        pass

    def sortToString(self, items):
        """Takes an array of sort criteria and formates them as a string to pull data"""
        pass

    def url(self, url):
        filters_index = url.find('filters=') + 8
        filters = url[filters_index:]

        filters = filters.replace('%7C', '|')
        filters = filters.replace('%20', ' ')
        filters = filters.replace('%3A', ':')

        return filters

    # ---------------- Creates Data Structures ----------------

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

    # ------------------- Getter Functions --------------------

    def getAllTags(self):
        """Returns all Concept Tags in Dataset"""
        return self.conceptTags

    def getAllIds(self):
        """Returns all cdids in Dataset"""
        return self.cdid

    def getAllTaxNodes(self):
        """Returns all Tax Nodes in Dataset"""
        return self.taxNodes

    def getAllModified(self):
        """Returns all Modified (dates) in Dataset"""
        return self.modified

    def getAllAuthorsRaw(self):
        """Returns all Authors in Dataset"""
        return self.authorsRaw

    def getAllTitle(self):
        """Returns all Titles in Dataset"""
        return self.title

    def getAllData(self):
        """Returns the unmodified Dataset"""
        return self.data

    # --------------- Formatting Data Structures ---------------

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

    # ------------------- Accessing Functions ------------------
    # ToDo: make functions to get certain values of data

    def getTagsById(self, ids):  # ToDo: Test to see if it works
        tagsList = self.modified
        tags = []
        for id in ids.id:
            tag = tagsList.loc[tagsList.id == id].get('modified').iloc[0]
            tag = self.formatValue(tag, target='T')
            tags.append(tag)

        return tags

    def getDateById(self, ids):
        datesList = self.modified
        dates = []
        for id in ids.id:
            date = datesList.loc[datesList.id == id].get('modified').iloc[0]
            date = self.formatValue(date, target='T')
            dates.append(date)

        return dates

    def getAuthorsById(self, ids):  # ToDo: Test to see if it works
        authorsList = self.modified
        authors = []
        for id in ids.id:
            author = authorsList.loc[authorsList.id == id].get('modified').iloc[0]
            author = self.formatValue(author, target='T')
            authors.append(author)

        return authors

    def getTitleByID(self, ids):  # ToDo: Test to see if it works
        titles_list = self.modified
        titles = []
        for id in ids.id:
            title = titles_list.loc[titles_list.id == id].get('modified').iloc[0]
            title = self.formatValue(title, target='T')
            titles.append(title)

        return titles

    # ------------------------- Plots -------------------------
    def makeScatterPlotByTag(self, tag, startDate=None, endDate=None, trend='ols'):  # ToDo: This method is pretty useless
        dates = self.getChartData(tag, startDate, endDate)

        figure = px.scatter(dates, x='date', y='occurrences', trendline=trend)
        figure.update_layout(title=f'{tag} by Date',
                             xaxis_title='Article Publish Date',
                             yaxis_title='Occurrences that Day')
        return figure

    def makeLineChart(self, tag, startDate=None, endDate=None):
        dates = self.getChartData(tag, startDate, endDate)

        figure = px.line(dates, x='date', y='occurrences')
        figure.update_layout(title=f'{tag} by Date',
                             xaxis_title='Article Publish Date',
                             yaxis_title='Occurrences that Day')
        return figure

    def getChartData(self, tag, startDate, endDate):
        tags_list = self.conceptTags

        result = tags_list.loc[tags_list.tags == tag]
        dates = self.getDateById(result)

        dates = [pd.to_datetime(d) for d in dates]
        dates_df = pd.DataFrame(
            {
                "date": dates
            })
        dates_df = dates_df.groupby(dates_df['date'])

        if not(startDate is None and endDate is None):
            pass

        dates_df = dates_df.value_counts()
        dates_df = dates_df.groupby(pd.Grouper(freq='M')).sum().to_frame('occurrences').reset_index()

        return dates_df
