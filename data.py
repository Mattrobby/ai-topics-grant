import numpy as np
import pandas as pd
import requests


class Data:

    def __init__(self):
        self.data = pd.DataFrame(self.pullData())
        self.cdid = self.createCdid()
        self.conceptTags = self.createConceptTags()
        self.taxNodes = self.createTaxNodes()
        self.modified = self.createModified()
        self.authorsRaw = self.createAuthorsRaw()
        self.title = self.createTitle()

    def pullData(self,
                 filters='taxnodes:Technology|Information Technology|Artificial Intelligence|Cognitive Science@@semantic-units:arXiv.org',
                 fields='concept-tagsConf,cdid,taxnodesConf,modified,authorsRaw,title',
                 sort='title_sort asc',
                 limit=2000,
                 offset=0):  # TODO: add filters to change fields and use env variables for authentication
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
                                 auth=('aitopics-guest', 'HvGSauJ00COgRnGX'))

        return response.json()

    # ---------------- Creates Data Structures ----------------

    def createConceptTags(self):
        """Creates the Concept Tags Dataset"""
        tags = self.makeMultiIndex('concept-tagsConf', 'tag')
        return tags

    def createCdid(self):
        """Creates the cdid Dataset"""
        cdid = self.data.get('cdid')
        return cdid

    def createTaxNodes(self):
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

    def getAllConceptTags(self):
        """Returns all Concept Tags in Dataset"""
        return self.conceptTags

    def getAllCdid(self):
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
            value = self.data.get(target)[0]

            for item in value:
                item = self.formatValue(item)
                result.append((cdid, item))

        multi = pd.DataFrame(result, columns=['id', name])
        multi.set_index(['id', name], inplace=True)
        multi.sort_index(inplace=True)

        return multi

    def makeIndex(self, target, name):
        """Matches the correct cdid with the target item"""
        result = []
        for index in self.data.index:
            cdid = self.cdid[index]
            value = self.data.get(target)[index]
            result.append((cdid, value))

        index = pd.DataFrame(result, columns=['id', name])
        return index
