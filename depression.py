import json
import io
import re
import os
import copy
import operator
import math


def rootLogLikelihoodRatio(a, b, c, d):
	e1 = c*(a+b)/(c+d)
	e2 = d*(a+b)/(c+d)
	if a == 0 and b == 0:
		result = 2 * (a * math.log(a / e1 + 1) + b * math.log(b / e2 + 1))
	elif a == 0 and not b == 0:
		result = 2 * (a * math.log(a / e1 + 1) + b * math.log(b / e2 + 0))
	elif not a == 0 and b == 0:
		result = 2 * (a * math.log(a / e1 + 0) + b * math.log(b / e2 + 1))
	else:
		result = 2 * (a * math.log(a / e1 + 0) + b * math.log(b / e2 + 0))
	result = math.sqrt(result)
	if (a/c)<(b/d):
		result = -result
	return result


regex = re.compile('[^a-zA-Z]')

"Numero de palabras sin repetir en Norvig"
numNoRepNorvig = 0
"Numero de palabras totales en Norvig (suma de freq)"
numNorvig = 0
"Numero de palabras sin repetir en Depression"
numNoRepDepression = 0
"Numero de palabras totales en Depression"
numDepression = 0
"Palabras repetidas de Depression"
palabrasDepression = []
"Frecuencia de corte"
freqCorte = 0

dictNorvig = {}
dictDepression = {}
dictCommons = {}
dictRootLLR = {}


"Se abre el archivo norvig.txt con todas las palabras de Norvig"
with io.open("norvig.txt", mode="r", encoding="utf-8") as fnorvig:
	keys = []
	values = []
	for line in fnorvig:
		palabras = line.split()
		for p in palabras:
			if re.search('\d+', p):
				values.append(int(p))
				numNorvig += int(p)
			else:
				keys.append(p)
		numNoRepNorvig += 1

	for i in range(numNoRepNorvig):
		"Dictionary Norvig con freq absolutas"
		dictNorvig[keys[i]] = values[i]

fnorvig.close()


"Se abre el archivo depression.json con las 10.000 entradas de depression"
with open('depression.json') as json_file:
	data = json.load(json_file)
data= data['data']


"Se escriben los datos sin limpiar en depression.txt"
with io.open("depression.txt", mode="w", encoding="utf-8") as fdepression:
	for elemento in data:
		if 'selftext' in elemento:
			fdepression.write(elemento['title'] + " " + elemento['selftext'] + " ")
		else:
			fdepression.write(elemento['title'] + " ")
fdepression.close()


"Se eliminan URLs y sustituyen los caracteres no alfabeticos por espacios"
with io.open("depression.txt", mode="r", encoding="utf-8") as fdepression:
	with io.open("depressionAux.txt", mode="w", encoding="utf-8") as fdepressionAux:
		for line in fdepression:
			palabras = line.split()
			for p in palabras:
				if not "www." in p and not "http" in p:
					if not p.isalpha():
						pnew = re.sub('[^a-zA-Z]+', ' ', p)
						fdepressionAux.write(pnew.lower() + ' ')
					else:
						fdepressionAux.write(p.lower() + ' ')
			fdepressionAux.write("\n")
	fdepressionAux.close()
fdepression.close()


"Se eliminan los espacios multiples"
with io.open("depressionAux.txt", mode="r", encoding="utf-8") as fdepressionAux:
	with io.open("depressionClean.txt", mode="w", encoding="utf-8") as fdepressionClean:
		for line in fdepressionAux:
			palabras = line.split()
			for p in palabras:
				fdepressionClean.write(p + '\n')
				palabrasDepression.append(p)
				numDepression += 1
	fdepressionClean.close()
fdepressionAux.close()
os.remove("depressionAux.txt")


"Dictionary Depression freq absolutas"
for k in palabrasDepression:
	if k not in dictDepression:
		dictDepression[k] = 1
		numNoRepDepression += 1
	else:
		dictDepression[k] += 1
dictCommons = copy.deepcopy(dictDepression)


"Dictionary de palabras comunes en Depression y Norvig freq absolutas"
for k in dictNorvig:
	if k not in dictCommons:
		dictCommons[k] = 0


"Se guarda dictCommons en el archivo commons"
with io.open("commons.txt", mode="w", encoding="utf-8") as fcommons:
	for key,value in sorted(dictCommons.items(), key=operator.itemgetter(1), reverse=True):
		fcommons.write(key+"\t"+str(value)+"\n")
fcommons.close()


"Obtencion de la freq de corte"
freqCorte = dictNorvig[keys[numNoRepNorvig-1]]/numNorvig

"Dictionary dictRootLLR comprobando si la palabra esta en Norvig o supera la freq de corte impuesta"
for k in dictCommons:
	if k not in dictRootLLR:
		if k in dictNorvig:
			res = rootLogLikelihoodRatio(dictCommons[k], dictNorvig[k], numDepression, numNorvig)
			dictRootLLR[k] = res
		elif dictCommons[k]>freqCorte:
			res = rootLogLikelihoodRatio(dictCommons[k], 0, numDepression, numNorvig)
			dictRootLLR[k] = res


"Se guarda el Dictionary rootLLR en el archivo rootLLR"
with io.open("rootLLR.txt", mode="w", encoding="utf-8") as frootLLR:
	for key, value in sorted(dictRootLLR.items(), key=operator.itemgetter(1), reverse=True):
		frootLLR.write(key + "\t" + str(value) + "\n")
frootLLR.close()