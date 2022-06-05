import requests
import json

def format_tag(tag):
    end = tag.find('::')
    return (tag[0:end])

data = {
  'filters': 'taxnodes:Technology|Information Technology|Artificial Intelligence|Cognitive Science@@semantic-units:arXiv.org',
  'fields': 'concept-tagsConf',
  'sort': 'title_sort asc'
}

response = requests.post('https://aitopics.org/i2kweb/webapi/search', data=data, auth=('aitopics-guest', 'HvGSauJ00COgRnGX'))

response_data = response.json()

tag_count = {}

for article in response_data:
    tags = article.get('concept-tagsConf')
    
    for tag in tags or []:
        tag = format_tag(tag)

        if tag in tag_count:
            tag_count[tag] += 1
        else:
            tag_count[tag] = 1
print(tag_count)
largest = max(zip(tag_count.values(), tag_count.keys()))[1]
print(largest)

# Do an insert and sort
largest_to_smallest = []
# for tag in tag_count.values():
#    if 
