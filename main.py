import data

rawData = data.Data()

print('----------------- Concept Tags -----------------')
print(rawData.getAllTags())

print('\n\n--------------------- cDid ---------------------')
print(rawData.getAllIds())

print('\n\n------------------ Tax Nodes -------------------')
print(rawData.getAllTaxNodes())

print('\n\n------------------- Modified -------------------')
print(rawData.getAllModified())

print('\n\n------------------- Authors --------------------')
print(rawData.getAllAuthorsRaw())

print('\n\n-------------------- Title ---------------------')
print(rawData.getAllTitle())



