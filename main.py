import data

rawData = data.Data()

print('----------------- Concept Tags -----------------')
print(rawData.getAllConceptTags())

print('\n\n--------------------- cDid ---------------------')
print(rawData.getAllCdid())

print('\n\n------------------ Tax Nodes -------------------')
print(rawData.getAllTaxNodes())

print('\n\n------------------- Modified -------------------')
print(rawData.getAllModified())

print('\n\n------------------- Authors --------------------')
print(rawData.getAllAuthorsRaw())

print('\n\n-------------------- Title ---------------------')
print(rawData.getAllTitle())
print(rawData.getAllTitle().loc['arxivorg:CBBFE8A2'])

