# -*- coding: utf-8 -*-
from flask import Flask, render_template, jsonify, request
import json
import requests
import pandas as pd
import numpy as np
import json
from sklearn.neighbors import KDTree
import pickle 

#chargement du classifieur
with open('./data/model.pkl', 'rb') as file : 
    model = pickle.load(file)
#chargement du scaler
with open('./data/scaler.pkl', 'rb') as file : 
    scaler = pickle.load(file)

app = Flask(__name__)

# 1. PREPARATION DES DONNEES

#Chargement des données prétraitées clients
client_id=None
n_rows=10000 # On limite les données à 10000 clients

data=pd.read_csv('./data/data.csv',index_col=0,nrows=n_rows)
data.set_index('SK_ID_CURR',inplace=True)
#On enlève les colonnes inutiles:
drop_list=['AMT_GOODS_PRICE','REGION_RATING_CLIENT','bb_annuités_max','bb_duration_max','CC_Monthly_draw_max',\
           'CC_Monthly_pay_max','POS_cnt_instalment_future_max','POS_cnt_instalment_future_min',\
           'INST_payment_perc_max']
data.drop(drop_list,axis=1,inplace=True)

#extraction de la liste de clients
client_list=data.index.tolist()

#Extraction des données générales clients et conservation des seules features qui nous intéressent.
clients=pd.read_csv('./data/clients.csv',index_col='SK_ID_CURR')
clients=clients[clients.index.isin(client_list)]
cols_keep = ['DAYS_BIRTH', 'DAYS_EMPLOYED','CODE_GENDER','CNT_FAM_MEMBERS',\
             'CNT_CHILDREN','NAME_EDUCATION_TYPE',\
             'AMT_CREDIT','AMT_ANNUITY', 'AMT_GOODS_PRICE','EXT_SOURCE_1','EXT_SOURCE_2','EXT_SOURCE_3',\
             'OWN_CAR_AGE','FLAG_OWN_CAR']
clients=clients[cols_keep]
clients['AGE'] = (clients['DAYS_BIRTH']/-365).astype(int)
clients['YEARS EMPLOYED'] = round((clients['DAYS_EMPLOYED']/-365), 0)
clients.drop(['DAYS_BIRTH', 'DAYS_EMPLOYED'], axis=1, inplace=True)
clients.columns=['GENDER','FAMILY SIZE','CHILDREN','EDUCATION','CREDIT','ANNUITY','PRICE',\
             'EXT_1','EXT_2','EXT_3','CAR AGE','CAR','AGE','YEARS EMPLOYED']
             
#recherche de voisins pour les catégories (éducation, occupation type, income type, family status, gender, children)
cols=['OCCUPATION_TYPE_Accountant','OCCUPATION_TYPE_Low_skilled',\
 'OCCUPATION_TYPE_Middle_skill','OCCUPATION_TYPE_Skilled','OCCUPATION_TYPE_Unknown',\
 'NAME_INCOME_TYPE_Commercial associate','NAME_INCOME_TYPE_Rare','NAME_INCOME_TYPE_State',\
 'NAME_INCOME_TYPE_Working','NAME_FAMILY_STATUS_Married','NAME_FAMILY_STATUS_Other',\
 'NAME_FAMILY_STATUS_Separated','NAME_FAMILY_STATUS_Unknown','NAME_FAMILY_STATUS_Widow',\
 'CODE_GENDER','CNT_CHILDREN','NAME_EDUCATION_TYPE']
data_plus=data[cols].fillna(0)
tree=KDTree(data_plus)
           	
#page de saisie de l'ID client
@app.route('/client', methods=['GET'])
def get_id():
    # saisie Id_client
    return render_template("saisie.html")	

@app.route('/api/dashboard/',methods=['post'])
def dashboard():
	global client_id
	client_id=int(request.form['client_id'])
	return render_template("dashboardp7.html")

#renvoi les ID clients disponibes
@app.route('/client/ids')
def ids_client():
	return jsonify(client_list)

#renvoi les infos générales client à renseigner en direct
@app.route('/info/client/')
def info_client():
	#je récupère les données générales
	data_client=clients[clients.index==client_id]
	client=data[data.index==client_id].copy()
	client.drop('TARGET',axis=1,inplace=True)
	#J'ajoute la probabilité d'obtention du pret
	data_client['score']=(model.predict_proba(scaler.transform(client))[0][0]*100-44)/43*50
	#j'y ajoute les données des autres prets
	data_client=data_client.join(client[['CC_AMT_%','INST_days_diff_max','PAYMENT_RATE','LOAN_VALUE_RATIO','bb_debt']])
	infos=data_client.loc[client_id,:]
	info_json = json.loads(infos.to_json())
	#j'ajoute l'id
	info_json['client_id']=client_id
	return jsonify({'data': info_json})
	
#renvoi les infos pour le diagramme source 1
@app.route('/info/ext1/')
def source1():
	df=clients[['EXT_1']].copy()
	df['quant_1']=df['EXT_1'].apply(lambda x:x//0.025)
	groupe=df.groupby(by='quant_1').count()
	data=[]
	for i in range(1,41):
		if i in groupe.index:
			data.append([float(i),float(groupe.loc[i]['EXT_1'])])
		else:		
			data.append([float(i),float(0)])
	print(client_id)
	return jsonify({'status': 'ok','data': data,'ext':clients.fillna(0).loc[client_id]['EXT_1']})

#renvoi les infos pour le diagramme source 2
@app.route('/info/ext2/')
def source2():
	df=clients[['EXT_2']].copy()
	df['quant_2']=df['EXT_2'].apply(lambda x:x//0.025)
	groupe=df.groupby(by='quant_2').count()
	data2=[]
	for i in range(1,41):
		if i in groupe.index:
			data2.append([float(i),float(groupe.loc[i]['EXT_2'])])
		else:
			data2.append([float(i),float(0)])
	print(client_id)
	return jsonify({'status': 'ok','data': data2,'ext':clients.fillna(0).loc[client_id]['EXT_2']})

#renvoi les infos pour le diagramme source 3
@app.route('/info/ext3/')
def source3():
	df=clients[['EXT_3']].copy()
	df['quant_3']=df['EXT_3'].apply(lambda x:x//0.025)
	groupe=df.groupby(by='quant_3').count()
	data3=[]
	for i in range(1,41):
		if i in groupe.index:
			data3.append([float(i),float(groupe.loc[i]['EXT_3'])])
		else:
			data3.append([float(i),float(0)])
	print(client_id)
	return jsonify({'status': 'ok','data': data3,'ext':clients.fillna(0).loc[client_id]['EXT_3']})

@app.route('/info/loan/')
def loan_neighbors():
	#on récupère les indices des 50 voisins les plus proches
	indices=tree.query(data_plus[data_plus.index==client_id].fillna(0), k=50)[1][0]
	#on extrait les données de data qui nous intéressent:
	moyennes=data.iloc[indices][['TARGET','PAYMENT_RATE','LOAN_VALUE_RATIO']]
	ratio=moyennes.groupby('TARGET').mean()['LOAN_VALUE_RATIO']
	client=data[data.index==client_id].copy()		
	zero=float(ratio.values[0])
	un=float(ratio.values[1])
	value=float(client['LOAN_VALUE_RATIO'])
	d={'acc': zero,'ref': un,'cli':value}
	return jsonify({'status': 'ok','data':d})

@app.route('/info/rate/')
def rate_neighbors():
	#on récupère les indices des 50 voisins les plus proches
	indices=tree.query(data_plus[data_plus.index==client_id].fillna(0), k=50)[1][0]
	#on extrait les données de data qui nous intéressent:
	moyennes=data.iloc[indices][['TARGET','PAYMENT_RATE','LOAN_VALUE_RATIO']]
	rate=moyennes.groupby('TARGET').mean()['PAYMENT_RATE']
	client=data[data.index==client_id].copy()
	zero=round(float(rate.values[0])*10000)/100
	un=round(float(rate.values[1])*10000)/100
	value=round(float(client['PAYMENT_RATE'])*10000)/100
	d={'acc': zero,'ref': un,'cli':value}
	return jsonify({'status': 'ok','data':d})	
	
if __name__ == "__main__":
    app.run(debug=True)
