#coding=utf-8
import json
provices = {}
with open('cities','r+',encoding='utf-8') as f:
    for line in f:
        number = line.split(' ')[0]
        name = line.split(' ')[len(line.split(' '))-1].strip().replace('　','')
        provices[name] = number 
f.close()
json.dump(provices,open('city2code.json','w',encoding='utf-8'))
#w = open('cities.js','w')
#w.write(json.dumps(provices,encoding='utf-8',ensure_ascii=False))
#w.close()