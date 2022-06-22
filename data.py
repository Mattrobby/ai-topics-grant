import numpy as np
import pandas as pd
import requests
import matplotlib.pyplot as plt


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
                 offset=0):

        # TODO: put string filters here

        self.data = pd.DataFrame(self.pullData(filters, fields, sort, limit, offset))
        self.cdid = self.createCdid()
        self.conceptTags = self.createConceptTags()
        self.taxNodes = self.createTaxNodes()
        self.modified = self.createModified()
        self.authorsRaw = self.createAuthorsRaw()
        self.title = self.createTitle()

    # --------------------- Pulling Data ----------------------
    # TODO: Make filters passed in as array instead of string

    def pullData(self, filters, fields, sort, limit, offset):
        """
        Pulls data from AI topics Server
        You can change the filters, fields, sort, limit, offset
        """
        data = {
            'filters': filters,
            'fields': fields,
            'sort': sort,
            'limit': limit,
            'offset': offset
        }

        response = requests.post('https://aitopics.org/i2kweb/webapi/search', data=data,
                                 auth=('aitopics-guest', 'HvGSauJ00COgRnGX'))  # TODO: Setup ENV Variables

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
        taxNodes = self.makeMultiIndex('taxnodesConf', 'tax-node')
        return taxNodes

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

    def formatValue(self, value):
        """Removes all characters after '::' in a string"""
        end = value.find('::')
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
    # TODO: make functions to get certain values of data

    def getTagsById(self, id):
        pass

    def getDateById(self, id):
        pass

    def getAuthorsById(self, id):
        pass

    def getTitleByID(self, id):
        pass

    ## ------------------------- Plots -------------------------
    def makeScatterPlotByTag(self, tag):
        datesList = self.modified
        tagsList = self.conceptTags

        result = tagsList.loc[tagsList.tags == tag]

        dates = []
        for id in result.id:
            date = datesList.loc[datesList.id == id].get('modified').iloc[0]
            dates.append(date)

        dates = [pd.to_datetime(d) for d in dates]
        return plt.scatter(dates, result.id, s=10, c='red')
