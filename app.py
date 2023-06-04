#importación de paquetes
from flask import Flask, jsonify, request
import json
from pulp import *
import pandas as pd

app=Flask(__name__)

import os, json

## se pretende leer todos los archivos json de la carpeta example_payloads
archivos_json=[]
path_to_json_files = 'C:\powerplant-coding-challenge\example_payloads'
#lista de todos los archivos JSON
json_file_names = [filename for filename in os.listdir(path_to_json_files) if filename.endswith('.json')]

#creamos bucle que va rellenando la lista (archivos_json=[]) con el contenido de los archivos
for json_file_name in json_file_names:
    with open(os.path.join(path_to_json_files, json_file_name)) as json_file:
        json_text = json.load(json_file)
        print(json_file_name, json_text) 
        archivos_json.append(json_text)

##se pregunta que num de archivo desea leerse
integer = int(input("¿Qué archivo de payload.json desea cargar? (indique un número entero)"))
data=archivos_json[integer]

#descomponemos el diccionario de cada JSON en sus distintos apartados
load=data['load'] ##es un diccionario
fuels=data['fuels']  ##es un diccionario
powerplants=data['powerplants']  ##es una lista

#elaboramos una lista con las fuels de todas las plantas menos las eólicas, ya que estas, al no tener costes se tratan diferentemente
lista_fuels=['gas(euro/MWh)','gas(euro/MWh)','kerosine(euro/MWh)','co2(euro/ton)']

#definimos las variables que deseamos parametrizar: potenciales generaciones de energía. Se establece su valor mínimo y máximo junto al tipo contínuo.
x1=LpVariable("Producción gasfiredbig1",powerplants[0]['pmin'],powerplants[0]['pmax'],LpContinuous)
x2=LpVariable("Producción gasfiredbig2",powerplants[1]['pmin'],powerplants[1]['pmax'],LpContinuous)
x3=LpVariable("Producción gasfiredsomewhatsmaller",powerplants[2]['pmin'],powerplants[2]['pmax'],LpContinuous)
x4=LpVariable("Producción tj1",powerplants[3]['pmin'],powerplants[3]['pmax'],LpContinuous)
x5=LpVariable("Producción windpark1",powerplants[4]['pmin'],powerplants[4]['pmax'],LpContinuous)
x6=LpVariable("Producción windpark2",powerplants[5]['pmin'],powerplants[5]['pmax'],LpContinuous)


#definimos el modelo
modelo=LpProblem("Producción_energia", LpMinimize)

#establecemos la ecuación a optimizar
lista_var=[x1,x2,x3,x4]
rango=len(lista_fuels)
modelo+=lpSum([(fuels[lista_fuels[i]]/powerplants[i]['efficiency'])*lista_var[i] for i in range(rango)])+x5*0+x6*0

#restricciones
modelo += x1+x2+x3+x4+x5+x6 == load
modelo += x5<=powerplants[4]['pmax']*powerplants[4]['efficiency']
modelo += x6<=powerplants[5]['pmax']*powerplants[5]['efficiency']


# El problema se resuelve mediante el Solver de Pulp


modelo.solve()
lista_planta_prod=[]
output={}
separador="_"

#Mediante un bucle, se crea una lista con diccionarios en la que se guarda la planta y su produccion
for v in modelo.variables():
    planta=v.name.split(separador)[1]
    produccion=round(v.varValue)
    #print(planta)
    #print(planta, "=", produccion)
    elemento=({"name":planta, "p":produccion})
    #print(elemento)
    lista_planta_prod.append(elemento)
    #print(list)
    
#ponemos bonito el formato de impresión
output_final = json.dumps(lista_planta_prod)# indent=2)
print(output_final)

with open("output_final.json", "w") as outfile:
    outfile.write(output_final)

@app.route('/productionplan',methods=['GET'])
def return_output():
    #return jsonify(json.dumps(output_final))
    import json

    

@app.route('/productionplan',methods=['POST'])
def capture_data():
    info = {
        'load':request.json['load'],
        'fuels':request.json['fuels'],
        'powerplants':request.json['powerplants']
    }
    #print(info)
    #print(request.json)
    return(info)
    



if __name__=='__main__':
    app.run(debug=True,port=8888)