import pandas as pd
import numpy as np
from sklearn.impute import KNNImputer

moyenne_age_voiture=12

#Petite fonction pour traiter les variables voiture
def voiture(row):
	if row['FLAG_OWN_CAR']=='N':
		return 0
	elif row['OWN_CAR_AGE']!=row['OWN_CAR_AGE']:
		return 1/(moyenne_age_voiture+1)
	else:
		return 1/(row['OWN_CAR_AGE']+1)
    

def application(df2,train=True):
    """
    Loads application train dataset.
    Fill nan values
    Remove outliers
    Meanwhile and afterwards, feature engineering steps are implemented.
    Returns dataframe with feature engineering including new implemented features.
    """
    
    
    drop_feat=['NAME_TYPE_SUITE','WEEKDAY_APPR_PROCESS_START','HOUR_APPR_PROCESS_START','OBS_30_CNT_SOCIAL_CIRCLE',\
               'DEF_30_CNT_SOCIAL_CIRCLE',\
               'APARTMENTS_AVG','BASEMENTAREA_AVG','YEARS_BEGINEXPLUATATION_AVG','YEARS_BUILD_AVG','COMMONAREA_AVG',\
             'ELEVATORS_AVG','ENTRANCES_AVG','FLOORSMAX_AVG','FLOORSMIN_AVG','LANDAREA_AVG','LIVINGAPARTMENTS_AVG',\
             'LIVINGAREA_AVG','NONLIVINGAPARTMENTS_AVG','NONLIVINGAREA_AVG','APARTMENTS_MODE','BASEMENTAREA_MODE',\
     'YEARS_BEGINEXPLUATATION_MODE','YEARS_BUILD_MODE','COMMONAREA_MODE','ELEVATORS_MODE','ENTRANCES_MODE',\
     'FLOORSMAX_MODE','FLOORSMIN_MODE','LANDAREA_MODE','LIVINGAPARTMENTS_MODE','LIVINGAREA_MODE',\
     'NONLIVINGAPARTMENTS_MODE','NONLIVINGAREA_MODE','APARTMENTS_MEDI','BASEMENTAREA_MEDI',\
     'YEARS_BEGINEXPLUATATION_MEDI','YEARS_BUILD_MEDI','COMMONAREA_MEDI','ELEVATORS_MEDI','ENTRANCES_MEDI',\
     'FLOORSMAX_MEDI','FLOORSMIN_MEDI','LANDAREA_MEDI','LIVINGAPARTMENTS_MEDI','LIVINGAREA_MEDI',\
     'NONLIVINGAPARTMENTS_MEDI','NONLIVINGAREA_MEDI','FONDKAPREMONT_MODE','HOUSETYPE_MODE','TOTALAREA_MODE',\
     'WALLSMATERIAL_MODE','EMERGENCYSTATE_MODE']
    
    #############################On enlève les colonnes qui ne servent pas#####################################
    df=df2.drop(drop_feat,axis=1)
    
    ##################################Imputation des valeurs manquantes########################################
    #Pour EXT_SOURCE on prend la moyenne
    ext1=0.502
    ext2=0.515
    ext3=0.509
    df['EXT_SOURCE_1']=df['EXT_SOURCE_1'].fillna(ext1)
    df['EXT_SOURCE_2']=df['EXT_SOURCE_2'].fillna(ext2)
    df['EXT_SOURCE_3']=df['EXT_SOURCE_3'].fillna(ext3)
    #Pour occupation type on crée un type: Unknown
    df['OCCUPATION_TYPE']=df['OCCUPATION_TYPE'].fillna('Unknown')
    #Beaucoup de demandes au credit bureau doit etre assez signe de mauvais présage, on va conserver en les ajoutants 
    # et en mettant les nan a 0 car si rien ne revient du credit bureau c'est qu'il ne doit rien y avoir
    df['AMT_REQ_CREDIT_BUREAU']=df['AMT_REQ_CREDIT_BUREAU_YEAR'].fillna(0)+df['AMT_REQ_CREDIT_BUREAU_MON'].fillna(0)\
                        +df['AMT_REQ_CREDIT_BUREAU_QRT'].fillna(0)+df['AMT_REQ_CREDIT_BUREAU_WEEK'].fillna(0)+\
                        +df['AMT_REQ_CREDIT_BUREAU_DAY'].fillna(0)+df['AMT_REQ_CREDIT_BUREAU_HOUR'].fillna(0)
    #On enlève les autres:
    df.drop(['AMT_REQ_CREDIT_BUREAU_YEAR','AMT_REQ_CREDIT_BUREAU_MON','AMT_REQ_CREDIT_BUREAU_QRT',\
         'AMT_REQ_CREDIT_BUREAU_WEEK','AMT_REQ_CREDIT_BUREAU_DAY','AMT_REQ_CREDIT_BUREAU_HOUR'],axis=1,inplace=True)
    #OBS et DEF ont l'air d'avoir une influence minime, on va garder en imputant à 0 les valeurs manquantes car
    #cela signifie aucune observation particulière et on garde que le 60
    df['OBS_60_CNT_SOCIAL_CIRCLE']=df['OBS_60_CNT_SOCIAL_CIRCLE'].fillna(0)
    df['DEF_60_CNT_SOCIAL_CIRCLE']=df['DEF_60_CNT_SOCIAL_CIRCLE'].fillna(0)
    #CNT_FAM_MEMBERS on calcule la moyenne de la taille des ménage sans enfant (CNT_FAM-CNT_CHILD):1.7 et on y ajoute
    #Le nombre d'enfants
    df['CNT_FAM_MEMBERS']=df.apply(lambda x:1.7+x['CNT_CHILDREN']\
                                 if x['CNT_FAM_MEMBERS']!=x['CNT_FAM_MEMBERS'] else x['CNT_FAM_MEMBERS'],axis=1)
    #AMT_GOOD_PRICE est corrélé à 99% avec AMT CREDIT donc on va imputer la valeur du crédit pour les données manquantes
    df['AMT_GOODS_PRICE']=df.apply(lambda x:x['AMT_CREDIT'] if x['AMT_GOODS_PRICE']!=x['AMT_GOODS_PRICE']\
                                else x['AMT_GOODS_PRICE'],axis=1)
    #Pour amt annuity on fera un 3nn imputer à partir de income total, amt credit et cnt family members
    knn3=KNNImputer(n_neighbors=3)
    df[['AMT_INCOME_TOTAL','AMT_ANNUITY','AMT_CREDIT','CNT_FAM_MEMBERS']]=\
    knn3.fit_transform(df[['AMT_INCOME_TOTAL','AMT_ANNUITY','AMT_CREDIT','CNT_FAM_MEMBERS']])
    #On peu imaginer que le client n'a pas de portable donc on va imputer cette valeur avec le minimum de la colonne
    #On va considérer que le client n'a jamais eu de portable et on lui impute la valeur minimale (n'a jamais changé)
    df['DAYS_LAST_PHONE_CHANGE']=df['DAYS_LAST_PHONE_CHANGE'].fillna(df['DAYS_LAST_PHONE_CHANGE'].min())
    
    #Traitement des valeurs extrèmes pour DAYS_WORKED on remplace par la valeur moyenne: -2396
    df['DAYS_EMPLOYED'].replace(365243, -2400, inplace=True)
    
    ###############################Traitement des outliers pour train seulement###############################
    if train:
        #Variables catégorielles:
        #On supprime les XNA dans gender pour n'avoir plus que M and F:
        df=df[df['CODE_GENDER']!='XNA']
    
        #Variables numériques
        outliers={'CNT_CHILDREN':[0,6],'AMT_INCOME_TOTAL':[0,1000000],'AMT_CREDIT':[0,3000000],\
              'AMT_ANNUITY':[0,120000],'AMT_GOODS_PRICE':[0,3500000],'CNT_FAM_MEMBERS':[0,8],\
              'OBS_60_CNT_SOCIAL_CIRCLE':[0,15],'DEF_60_CNT_SOCIAL_CIRCLE':[0,5],'AMT_REQ_CREDIT_BUREAU':[0,15]}
        for i in outliers.keys():
            df=df[-(df[i]>outliers[i][1])]
            df=df[-(df[i]<outliers[i][0])]
    
    
    #######################################Traitement des flags##############################################
    df['FLAG_LIVING']=df['REG_REGION_NOT_LIVE_REGION']+df['REG_REGION_NOT_WORK_REGION']+df['LIVE_REGION_NOT_WORK_REGION']\
                    +df['REG_CITY_NOT_LIVE_CITY']+df['REG_CITY_NOT_WORK_CITY']+df['LIVE_CITY_NOT_WORK_CITY']
    
    df.drop(['REG_REGION_NOT_LIVE_REGION','REG_REGION_NOT_WORK_REGION','LIVE_REGION_NOT_WORK_REGION',\
          'REG_CITY_NOT_LIVE_CITY','REG_CITY_NOT_WORK_CITY','LIVE_CITY_NOT_WORK_CITY'],axis=1,inplace=True)
    
    df['FLAG_COMM']=df['FLAG_MOBIL']+df['FLAG_EMP_PHONE']+df['FLAG_WORK_PHONE']+df['FLAG_CONT_MOBILE']\
    +df['FLAG_PHONE']+df['FLAG_EMAIL']
    
    df.drop(['FLAG_MOBIL', 'FLAG_EMP_PHONE','FLAG_WORK_PHONE', 'FLAG_CONT_MOBILE', 'FLAG_PHONE', 'FLAG_EMAIL'\
         ],axis=1,inplace=True)
    
    df['Missing_docs']=df['FLAG_DOCUMENT_2']+df['FLAG_DOCUMENT_3']+df['FLAG_DOCUMENT_4']+df['FLAG_DOCUMENT_5']+\
                    df['FLAG_DOCUMENT_6']+df['FLAG_DOCUMENT_7']+df['FLAG_DOCUMENT_8']+df['FLAG_DOCUMENT_9']+\
                    df['FLAG_DOCUMENT_10']+df['FLAG_DOCUMENT_11']+df['FLAG_DOCUMENT_12']+df['FLAG_DOCUMENT_13']+\
                    df['FLAG_DOCUMENT_14']+df['FLAG_DOCUMENT_15']+df['FLAG_DOCUMENT_16']+df['FLAG_DOCUMENT_17']+\
                    df['FLAG_DOCUMENT_18']+df['FLAG_DOCUMENT_19']+df['FLAG_DOCUMENT_20']+df['FLAG_DOCUMENT_21']
    
    df.drop(['FLAG_DOCUMENT_2','FLAG_DOCUMENT_3','FLAG_DOCUMENT_4','FLAG_DOCUMENT_5','FLAG_DOCUMENT_6','FLAG_DOCUMENT_7',\
          'FLAG_DOCUMENT_8','FLAG_DOCUMENT_9','FLAG_DOCUMENT_10','FLAG_DOCUMENT_11','FLAG_DOCUMENT_12',\
          'FLAG_DOCUMENT_13','FLAG_DOCUMENT_14','FLAG_DOCUMENT_15','FLAG_DOCUMENT_16','FLAG_DOCUMENT_17',\
          'FLAG_DOCUMENT_18','FLAG_DOCUMENT_19','FLAG_DOCUMENT_20','FLAG_DOCUMENT_21'],axis=1,inplace=True)
    
    #################################Traitement des deux colonnes Cars########################################
    #Si il n'y a pas de voitures on prend 0 sinon on prend 1/année véhicule avec une imputation des valeurs
    #manquantes des items avec voitures à la moyenne c'est à dire 12:
    df['Car']=df.apply(lambda x:voiture(x),axis=1)
    df.drop(['FLAG_OWN_CAR','OWN_CAR_AGE'],axis=1,inplace=True)
    
    ##################################Traitement des variables catégorielles###################################
    
    #NAME_CONTRACT_TYPE codée en 0 ou 1: 0 pour Revolving loans et 1 pour cash loans
    df['NAME_CONTRACT_TYPE']=df['NAME_CONTRACT_TYPE'].apply(lambda x:1 if x=='Cash loans' else 0)
    #CODE_GENDER codée en 0 ou 1: 0 pour M et 1 pour F
    df['CODE_GENDER']=df['CODE_GENDER'].apply(lambda x:1 if x=='F' else 0)
    #FLAG_OWN_REALTY codée en 0 ou 1: 0 pour N et 1 pour Y
    df['FLAG_OWN_REALTY']=df['FLAG_OWN_REALTY'].apply(lambda x:1 if x=='Y' else 0)
    #Pour NAME_INCOME_TYPE, NAME_EDUCATION_TYPE, NAME_FAMILY_STATUS,NAME_HOUSING_TYPE, OCCUPATION_TYPE et 
    #ORGANIZATION_TYPE on réduit le nombre de catégorie avec les dictionnaires suivants:
    income={'Working':'Working','Commercial associate':'Commercial associate',\
           'Unemployed':'Rare', 'Student':'Rare', 'Businessman':'Rare',\
           'Maternity leave':'Rare','Pensioner':'State','State servant':'State'}
    family={'Single / not married':'Other', 'Married':'Married', 'Civil marriage':'Other', 'Widow':'Widow',
       'Separated':'Separated', 'Unknown':'Unknown'}
    housing={'House / apartment':'Other', 'Rented apartment':'Rented or with parents', 'With parents':'Rented or with parents',
           'Municipal apartment':'Municipal', 'Office apartment':'Office', 'Co-op apartment':'Other'}
    occupation={'Laborers':'Middle_skill', 'Core staff':'Skilled', 'Accountants':'Accountant',\
             'Managers':'Skilled', 'Unknown':'Unknown','Drivers':'Middle_skill', 'Sales staff':'Middle_skill',\
             'Cleaning staff':'Middle_skill', 'Cooking staff':'Middle_skill','Private service staff':'Skilled',\
             'Medicine staff':'Skilled', 'Security staff':'Middle_skill','High skill tech staff':'Skilled',\
             'Waiters/barmen staff':'Middle_skill','Low-skill Laborers':'Low_skilled',\
             'Realty agents':'Skilled', 'Secretaries':'Skilled', 'IT staff':'Skilled','HR staff':'Skilled'}
    education={'Secondary / secondary special':2, 'Higher education':4,'Incomplete higher':3, 'Lower secondary':1,\
           'Academic degree':5}
    organization_type={'Security': 'Risky','Self-employed': 'Risky', 'Trade: type 3': 'Risky',\
                       'Industry: type 3': 'Risky','Construction': 'Risky','Housing': 'Medium',\
                       'Business Entity Type 2': 'Medium','Business Entity Type 1': 'Medium',\
                       'Industry: type 11': 'Medium','Transport: type 4': 'Medium', 'Trade: type 7': 'Medium',\
                       'Business Entity Type 3': 'Medium','School': 'Low','Government': 'Low','Medicine': 'Low',\
                       'Kindergarten': 'Low','Industry: type 9': 'Low','XNA': 'Less','Military': 'Less',\
                       'Other': 'Rare'}
    df['NAME_EDUCATION_TYPE']=df['NAME_EDUCATION_TYPE'].apply(lambda x: education[x])
    df['NAME_FAMILY_STATUS']=df['NAME_FAMILY_STATUS'].apply(lambda x: family[x])
    df['NAME_HOUSING_TYPE']=df['NAME_HOUSING_TYPE'].apply(lambda x: housing[x])
    df['NAME_INCOME_TYPE']=df['NAME_INCOME_TYPE'].apply(lambda x: income[x])
    df['OCCUPATION_TYPE']=df['OCCUPATION_TYPE'].apply(lambda x: occupation[x])
    L=list(organization_type.keys())
    df['ORGANIZATION_TYPE']=df['ORGANIZATION_TYPE'].apply(lambda x: 'Rare' if x not in L else organization_type[x])
    
    #One Hot encoding des données catégorielles:
    original_columns = list(df.columns)
    categorical_columns = ['NAME_INCOME_TYPE','NAME_FAMILY_STATUS','NAME_HOUSING_TYPE','OCCUPATION_TYPE','ORGANIZATION_TYPE']
    df = pd.get_dummies(df, columns=categorical_columns)
    
    ####################################Création de nouvelles features###########################################
    df['INCOME_CREDIT_%'] = df['AMT_INCOME_TOTAL'] / df['AMT_CREDIT']
    df['INCOME_PER_PERSON'] = df['AMT_INCOME_TOTAL'] / df['CNT_FAM_MEMBERS']
    df['ANNUITY_INCOME_%'] = df['AMT_ANNUITY'] / df['AMT_INCOME_TOTAL']
    df['PAYMENT_RATE'] = df['AMT_ANNUITY'] / df['AMT_CREDIT']
    df['LOAN_VALUE_RATIO'] = df['AMT_CREDIT'] / df['AMT_GOODS_PRICE']
    df['ANNUITY_INCOME_PER_PERSON%'] = df['INCOME_PER_PERSON'] / df['AMT_ANNUITY']
    df['AGE_CREDIT_LENGTH_%']=df['AMT_CREDIT']/df['AMT_ANNUITY']*365/(-df['DAYS_BIRTH'])
    #Proportion de jours travaillé depuis 18 ans
    df['DAYS_EMPLOYED_%'] = df['DAYS_EMPLOYED'] / (df['DAYS_BIRTH']+18*365)
    
    return df

def previous_app(df):
    """
    Loads previous_application dataset. 
    Afterwards, feature engineering and aggregations steps are implemented.
    Returns dataframe with feature engineering and aggregations implemented columns.
    
    Columns of returned dataframe include:
    On the entire table:
    - % of rejected offers amongs credits request: prev_%_rejected
    - % of applications for x-sell purchased goods prev_%_x-sell
    On the approved applications:
    - % of credits not insured: prev_%_notinsured
    - % of credit with no down-payment: prev_%_nodownpayment 
    """
    
    prev=df[['SK_ID_CURR','NAME_CONTRACT_STATUS','NAME_PRODUCT_TYPE','RATE_DOWN_PAYMENT','NFLAG_INSURED_ON_APPROVAL']].copy()
    
    #Calcul sur tableau complet
    prev['CONTRACT']=prev['NAME_CONTRACT_STATUS'].apply(lambda x:1 if x=='Rejected' else 0)
    prev['NAME_PRODUCT_TYPE']=prev['NAME_PRODUCT_TYPE'].apply(lambda x:1 if x=='x-sell' else 0)
    prev_agg_prov = prev.groupby(['SK_ID_CURR']).agg({'SK_ID_CURR':'count','CONTRACT':'sum',\
                                                    'NAME_PRODUCT_TYPE':'sum'})
    prev_agg=pd.DataFrame(index=prev_agg_prov.index)
    prev_agg['prev_%_rejected']=prev_agg_prov['CONTRACT']/prev_agg_prov['SK_ID_CURR']
    prev_agg['prev_%_x-sell']=prev_agg_prov['NAME_PRODUCT_TYPE']/prev_agg_prov['SK_ID_CURR']
    
    #Calcul sur le tableau des approved:
    prev=prev[prev.NAME_CONTRACT_STATUS=='Approved']
    prev.fillna(0,inplace=True)
    prev['RATE_DOWN_PAYMENT']=prev['RATE_DOWN_PAYMENT'].apply(lambda x:0 if x>0 else 1)
    prev['NFLAG_INSURED_ON_APPROVAL']=prev['NFLAG_INSURED_ON_APPROVAL'].apply(lambda x:1 if x!=1 else 0)
    prev_agg_prov = prev.groupby(['SK_ID_CURR']).agg({'SK_ID_CURR':'count','NFLAG_INSURED_ON_APPROVAL':'sum',\
                                                    'RATE_DOWN_PAYMENT':'sum'})
    prev_agg['prev_%_notinsured']=prev_agg_prov['NFLAG_INSURED_ON_APPROVAL']/prev_agg_prov['SK_ID_CURR']
    prev_agg['prev_%_nodownpayment']=prev_agg_prov['RATE_DOWN_PAYMENT']/prev_agg_prov['SK_ID_CURR']
    
    return prev_agg.fillna(0) 
    #les na correspondent aux clients dont tous les prets ont été refusé cancelled ou not used
    

def CCB(df):
    """
    Loads credit_card_balance dataset. 
    Afterwards, feature engineering and aggregations steps are implemented.
    Returns dataframe with feature engineering and aggregations implemented columns.
    
    Columns of returned dataframe include:
    - Nb of active contract at the time of the loan: CC_Active
    - Montant de crédit at the time of the loan: CC_AMT
    - Percentage of CREDIT_LIMIT at the time of the loan: CC_AMT_% 
    - Min, Max and Mean monthly drawings over the last 6 months: CC_Monthly_draw_min,max,mean
    - Min, Max and Mean monthly payment over the last 6 months: CC_Monthly_pay_min,max,mean
    - Percentage of months with DPD for all contracts: CC_DPD
    - Percentage of months with DPD_DEF for all contracts: CC_DPD_DEF
    """
    
    cc_agg=pd.DataFrame()
    #Calcul des DPD
    cc=df[['SK_ID_CURR','MONTHS_BALANCE','SK_DPD','SK_DPD_DEF']].copy()  
    cc['SK_DPD_DEF']=cc['SK_DPD_DEF'].apply(lambda x: 1 if x>0 else 0)
    cc['SK_DPD']=cc['SK_DPD'].apply(lambda x: 1 if x>0 else 0)
    cc_agg_prov = cc.groupby(['MONTHS_BALANCE','SK_ID_CURR']).agg({'SK_ID_CURR':'first','SK_DPD':'max','SK_DPD_DEF':'max'}).unstack()
    cc_agg['CC_DPD']=cc_agg_prov['SK_DPD'].sum()/cc_agg_prov['SK_DPD'].count()
    cc_agg['CC_DPD_DEF']=cc_agg_prov['SK_DPD_DEF'].sum()/cc_agg_prov['SK_DPD_DEF'].count()
    
    #Calcul de CC_Active, CC_AMT et CC_AMT_%:
    cc=df[['SK_ID_CURR','MONTHS_BALANCE','AMT_BALANCE','AMT_CREDIT_LIMIT_ACTUAL','NAME_CONTRACT_STATUS']].copy()
    cc=cc[cc['MONTHS_BALANCE']==-1]
    cc['NAME_CONTRACT_STATUS']=cc['NAME_CONTRACT_STATUS'].apply(lambda x: 1 if x in \
                                ['Active','Demand', 'Signed', 'Sent proposal','Approved'] else 0)
    
    cc_agg1=cc.groupby('SK_ID_CURR').agg({'AMT_BALANCE':'sum','AMT_CREDIT_LIMIT_ACTUAL':'sum','NAME_CONTRACT_STATUS':'sum'})
    cc_agg1['AMT_CREDIT_LIMIT_ACTUAL']=cc_agg1['AMT_BALANCE']/cc_agg1['AMT_CREDIT_LIMIT_ACTUAL']
    cc_agg1.columns=['CC_AMT','CC_AMT_%','CC_Active']
    
    cc_agg=pd.merge(cc_agg,cc_agg1,left_index=True,right_index=True,how='left')
    
    del cc_agg1#,cc_agg3
    
    #Calcul des Min, Max et Mean monthly drawings et payments
    cc=df[['SK_ID_CURR','MONTHS_BALANCE','AMT_DRAWINGS_CURRENT','AMT_PAYMENT_TOTAL_CURRENT']].copy()
    cc=cc[cc['MONTHS_BALANCE']>=-6]
    cc_agg_prov =cc.groupby(['MONTHS_BALANCE','SK_ID_CURR']).agg(\
    {'SK_ID_CURR':'first','AMT_DRAWINGS_CURRENT':'sum','AMT_PAYMENT_TOTAL_CURRENT':'sum'}).unstack()
    cc_agg['CC_Monthly_draw_min']=cc_agg_prov['AMT_DRAWINGS_CURRENT'].min()
    cc_agg['CC_Monthly_draw_max']=cc_agg_prov['AMT_DRAWINGS_CURRENT'].max()
    cc_agg['CC_Monthly_draw_mean']=cc_agg_prov['AMT_DRAWINGS_CURRENT'].mean()
    cc_agg['CC_Monthly_pay_min']=cc_agg_prov['AMT_PAYMENT_TOTAL_CURRENT'].min()
    cc_agg['CC_Monthly_pay_max']=cc_agg_prov['AMT_PAYMENT_TOTAL_CURRENT'].max()
    cc_agg['CC_Monthly_pay_mean']=cc_agg_prov['AMT_PAYMENT_TOTAL_CURRENT'].mean()
    
    del cc,cc_agg_prov
    
    return cc_agg.fillna(0)
    
def installments(df):
    """
    Loads installments_payments dataset. 
    Afterwards, feature engineering and aggregations steps are implemented.
    Returns dataframe with feature engineering and aggregations implemented columns.

    Returns differences between payment due and real instalments and days due and days of payment
    Takes 'max', 'mean', 'sum', 'var' for thoses
    """
    
    df=df[['SK_ID_CURR','AMT_PAYMENT','AMT_INSTALMENT','DAYS_ENTRY_PAYMENT','DAYS_INSTALMENT']].copy()
    
    # Percentage and difference paid in each installment (amount paid and installment value)
    df['PAYMENT_PERC'] = df['AMT_PAYMENT'] / df['AMT_INSTALMENT']
    df['PAYMENT_DIFF'] = df['AMT_INSTALMENT'] - df['AMT_PAYMENT']
    # Differences in days paid and expected
    df['DAYS_DIFF'] = df['DAYS_ENTRY_PAYMENT'] - df['DAYS_INSTALMENT']
    # Features: Perform aggregations
    aggregations = {
        'DAYS_DIFF': ['max', 'mean', 'sum','var'],
        'PAYMENT_PERC': ['max', 'mean', 'sum', 'var'],
        'PAYMENT_DIFF': ['max', 'mean', 'sum', 'var'],
        }
    ins_agg = df.groupby('SK_ID_CURR').agg(aggregations)
    ins_agg.columns = pd.Index(['INST_' + e[0].lower() + "_" + e[1].lower() for e in ins_agg.columns.tolist()])
    del df
    return ins_agg
    

def POScash(df,previous_application):
    """
    Loads POS_cash dataset and previous_application dataset. 
    Afterwards, feature engineering and aggregations steps are implemented.
    Returns dataframe with feature engineering and aggregations implemented columns.

    Returns 
    - Percentage of months with DPD for all contracts: POS_DPD
    - Percentage of months with DPD_DEF for all contracts: POS_DPD_DEF
    After agregation with Previous_applications returns
    - Amount left to pay (total of credit remaining) POS_AMT
    - Annuity min max and mean POS_CNT_INSTALMENT_FUTURE_min,max,mean   
    """
    pos=df[['SK_ID_CURR','MONTHS_BALANCE','SK_DPD','SK_DPD_DEF']].copy()
    actuel=df[df.MONTHS_BALANCE.isin([-1,0])].copy()
    actuel=pd.merge(actuel,previous_application[['SK_ID_PREV','AMT_CREDIT','AMT_ANNUITY','DAYS_DECISION']],on='SK_ID_PREV')
    
    del df,previous_application
    
    #Calcul des DPD
    pos_agg=pd.DataFrame()
    pos['SK_DPD_DEF']=pos['SK_DPD_DEF'].apply(lambda x: 1 if x>0 else 0)
    pos['SK_DPD']=pos['SK_DPD'].apply(lambda x: 1 if x>0 else 0)
    pos_agg_prov = pos.groupby(['MONTHS_BALANCE','SK_ID_CURR']).agg({'SK_ID_CURR':'first','SK_DPD':'max','SK_DPD_DEF':'max'}).unstack()
    pos_agg['POS_DPD']=pos_agg_prov['SK_DPD'].sum()/pos_agg_prov['SK_DPD'].count()
    pos_agg['POS_DPD_DEF']=pos_agg_prov['SK_DPD_DEF'].sum()/pos_agg_prov['SK_DPD_DEF'].count()
    
    del pos
    
    # Calcul des montants restants et des mensualités restantes
    
    #Traitement des valeurs manquantes
    actuel['CNT_INSTALMENT']=actuel.apply(lambda x : x['AMT_CREDIT']/x['AMT_ANNUITY']\
                                        if x['CNT_INSTALMENT']!=x['CNT_INSTALMENT'] else x['CNT_INSTALMENT'],axis=1)
    actuel['CNT_INSTALMENT_FUTURE']=actuel.apply(lambda x : x['CNT_INSTALMENT']-x['DAYS_DECISION']//30\
                                        if x['CNT_INSTALMENT_FUTURE']!=x['CNT_INSTALMENT_FUTURE']\
                                               else x['CNT_INSTALMENT_FUTURE'],axis=1)
    
    #Calcul des features
    actuel['POS_AMT']=actuel['AMT_CREDIT']*actuel['CNT_INSTALMENT_FUTURE']/actuel['CNT_INSTALMENT']
    actuel.groupby('SK_ID_CURR').agg({})
    aggregations = {
        'POS_AMT': ['sum'],
        'CNT_INSTALMENT_FUTURE': ['min', 'max', 'mean'],
        }
    
    pos_agg2 = actuel.groupby('SK_ID_CURR').agg(aggregations)
    pos_agg2.columns = pd.Index(['POS_' + e[0].lower() + "_" + e[1].lower() for e in pos_agg2.columns.tolist()])
    
    del actuel
    #On retourne le merging des deux à gauche sur le premier en remplissant les valeurs manquantes à 0
    return pd.merge(pos_agg,pos_agg2,left_index=True,right_index=True,how='left').fillna(0)
    

#Les constantes de change
change2=6.6
change3=3.8
change4=3.1
#Les moyennes des rembousements de prets pour les valeurs manquantes
index_moyenne=['Another type of loan', 'Car loan', 'Cash loan (non-earmarked)','Consumer credit',\
 'Credit card', 'Loan for business development','Loan for purchase of shares (margin lending)',\
 'Loan for the purchase of equipment','Loan for working capital replenishment', 'Microloan',\
 'Mobile operator loan', 'Mortgage', 'Real estate loan','Unknown type of loan']
moyennes=pd.DataFrame([ 248.49180581, 1383.10632738,  361.78123681,  493.91495511,248.64115538, 2351.27258935,\
                       3011.09588376, 1623.57282767,1540.87681125, 1051.60324189, 8132.53012048, 1087.71447291,\
                       3979.01876471,  542.43629699],index=index_moyenne,columns=['quot'])

def creditsom(row):
    """ Fonctions pour imputation de AMT_CREDIT_SUM"""
    if row['AMT_CREDIT_SUM']==row['AMT_CREDIT_SUM']:
        return row['AMT_CREDIT_SUM']
    elif row['AMT_ANNUITY']!=row['AMT_ANNUITY']:
        return row['AMT_CREDIT_SUM_DEBT']
    else:
        return row['AMT_ANNUITY']*row['DAYS_CREDIT_ENDDATE']/365

def currency(row,i):
    """Fonction de conversion des lignes en la devise principale"""
    if row['CREDIT_CURRENCY']=='currency 2':
        return row[i]/change2
    elif row['CREDIT_CURRENCY']=='currency 3':
        return row[i]/change3
    elif row['CREDIT_CURRENCY']=='currency 4':
        return row[i]/change4
    else:
        return row[i]

 
    

def bureau_et_balance(bb,bureau):
    """
    Loads applications bureau and bureau balance
    Fill nan values
    Remove outliers
    Meanwhile and afterwards, feature engineering steps are implemented.
    Returns dataframe with feature engineering including new implemented features.
    """
    ###########################################################################################################
    #############################     Traitement de Bureau_Balance            #################################
    ###########################################################################################################
    
    #On cherche les contrats avec des DPDs
    bb['DPD']=bb['STATUS'].apply(lambda x: 1 if x in ['1', '2', '3', '5', '4'] else 0)
    #On compte le nombre de DPD par contrat
    bb_agg = bb.groupby('SK_ID_BUREAU').agg({'DPD':'sum'})
    
    ###########################################################################################################
    #############################             Traitement de Bureau            #################################
    ###########################################################################################################
    
    ####################################       Prétraitement   ################################################
    
    #Conversion des montants en autres devises:
    for i in ['AMT_CREDIT_MAX_OVERDUE','AMT_CREDIT_SUM','AMT_CREDIT_SUM_DEBT',\
              'AMT_CREDIT_SUM_LIMIT','AMT_CREDIT_SUM_OVERDUE','AMT_ANNUITY']:
        bureau[i]=bureau.apply(lambda x:currency(x,i),axis=1)
    #récupération des infos des tableaux précédents
    bureau=pd.merge(bureau,bb_agg,left_on='SK_ID_BUREAU',right_index=True, how='left')
    
    #nettoyage mémoire
    del bb, bb_agg
    
    #On crée donc 2 nouvelles colonnes:
    bureau['actif']=bureau.apply(lambda x:1 if x['CREDIT_ACTIVE']=='Active' else 0,axis=1)
    bureau['anomalies']=bureau.apply(lambda x:1 if x['CREDIT_ACTIVE']=='Bad debt' or x['CREDIT_DAY_OVERDUE']>0 or\
                           x['AMT_CREDIT_MAX_OVERDUE']>0 or x['AMT_CREDIT_SUM_OVERDUE']>0 \
                           or x['DPD']>0 else 0,axis=1)
    
    #On supprime les colonnes inutiles
    bureau.drop(['CREDIT_CURRENCY','CREDIT_ACTIVE','DPD','AMT_CREDIT_SUM_OVERDUE','CREDIT_DAY_OVERDUE'],axis=1,inplace=True)
    
    #Séparation prets actifs et en cours
    actif=bureau[bureau['actif']==1].copy()
    closed=bureau[bureau['actif']==0].copy()
    
    del bureau
    
    ################# Imputation des valeurs manquantes des crédits actifs ######################################
    
    ########## AMT_CREDIT_SUM
    
    actif['AMT_CREDIT_SUM']=actif.apply(lambda row: creditsom(row),axis=1) 
    
    ######### DAYS_CREDIT_ENDDATE
    
    def creditend(row):
        """ Fonction pour le remplissage des données manquantes pour le calcul de la fin du crédit """
        #On va mettre une durée maximale de crédit à 30 ans pour les nan
        #si les crédits qui sont créés et cloturés le même jour ou de montant nul ou avec un days enddate fact:
        #On met à 0
        if row['DAYS_CREDIT']==row['DAYS_CREDIT_ENDDATE'] or row['AMT_CREDIT_SUM']<=1 or \
        row['DAYS_ENDDATE_FACT']==row['DAYS_ENDDATE_FACT']:
            return 0
        #si nan:
        elif row['DAYS_CREDIT_ENDDATE']!=row['DAYS_CREDIT_ENDDATE']:
            #Je récupère tous les crédit de la personne en question
            emprunteur=actif[actif['SK_ID_CURR']==row['SK_ID_CURR']][['DAYS_CREDIT','DAYS_CREDIT_ENDDATE','AMT_CREDIT_SUM','CREDIT_TYPE','DAYS_CREDIT_UPDATE']]
            #Je ne garde que les valeurs non nulles de end_date
            df=emprunteur[-emprunteur['DAYS_CREDIT_ENDDATE'].isnull()]
            #J'enlève éventuellement les crédit qui sont cloturés les mêmes jours
            df=df[-df['DAYS_CREDIT']==df['DAYS_CREDIT_ENDDATE']]
            #Je filtre sur le type d'emprunt et ne conserve que les emprunt positifs
            emprunttype=df[df['CREDIT_TYPE']==row['CREDIT_TYPE']]
            emprunttype=emprunttype[emprunttype['AMT_CREDIT_SUM']>0]
            #SI je n'ai aucun type d'emprunt similaire je prends la moyenne globale de ce type d'emprunt
            if len(emprunttype)==0:
                #Je renvois le montant divisé par la somme moyenne auquel j'enlève les jours écoulés
                return min(row['AMT_CREDIT_SUM']/moyennes.loc[row['CREDIT_TYPE']]['quot']+row['DAYS_CREDIT'],11000)
            else: 
                #Je calcule la moyenne
                moyennequot=(emprunttype['AMT_CREDIT_SUM']/(emprunttype['DAYS_CREDIT_ENDDATE']-emprunttype['DAYS_CREDIT'])).mean()
                return min((row['AMT_CREDIT_SUM']/moyennequot)+row['DAYS_CREDIT'],11000)
        else:
            return row['DAYS_CREDIT_ENDDATE']
    
    actif['DAYS_CREDIT_ENDDATE']=actif.apply(lambda x: creditend(x),axis=1)
    
    #Mise à jour DAYS_CREDIT_END_DATE et DAYS_CREDIT avec DAYS_CREDIT_UPDATE:
    actif['DAYS_CREDIT_ENDDATE']+=actif['DAYS_CREDIT_UPDATE']
    actif['DAYS_CREDIT']+=actif['DAYS_CREDIT_UPDATE']
    
    #Mise à jour des crédits closes et actifs en fonction des nouvelles dates:
    closed=closed.append(actif[actif['DAYS_CREDIT_ENDDATE']<=0])
    actif=actif[actif['DAYS_CREDIT_ENDDATE']>0]
    
    ########### AMT_ANNUITY
    actif['AMT_ANNUITY']=actif.apply(lambda x: x['AMT_ANNUITY'] if x['AMT_ANNUITY']==x['AMT_ANNUITY']\
                                       else x['AMT_CREDIT_SUM']/(x['DAYS_CREDIT_ENDDATE']-x['DAYS_CREDIT']),axis=1)
    
    
    ########## AMT_CREDIT_SUM_DEBT
    actif['AMT_CREDIT_SUM_DEBT']=actif.apply(lambda x: x['AMT_CREDIT_SUM_DEBT'] if \
                                         x['AMT_CREDIT_SUM_DEBT']==x['AMT_CREDIT_SUM_DEBT']\
                                       else x['AMT_CREDIT_SUM']*x['DAYS_CREDIT_ENDDATE']/\
                                         (x['DAYS_CREDIT_ENDDATE']-x['DAYS_CREDIT']),axis=1)
    
    
    ###############################   Création de nouvelles features     #######################################
    
    ######### Sur les crédits en cours
    
    bb_agg=actif.groupby('SK_ID_CURR').agg({'AMT_CREDIT_SUM_DEBT':['count','sum'],'AMT_ANNUITY':['max','mean'],
                                        'DAYS_CREDIT_ENDDATE':['max','mean'],'anomalies':'sum',\
                                       'AMT_CREDIT_MAX_OVERDUE':['max']})
    
    del actif
    
    bb_agg.columns=pd.Index(['bb_credits','bb_debt','bb_annuités_max','bb_annuités_mean','bb_duration_max',\
                             'bb_duration_mean','bb_%_anomalies','bb_max_overdue_active'])
    bb_agg['bb_%_anomalies']=bb_agg['bb_%_anomalies']/bb_agg['bb_credits']
    
    ######### Sur les crédits cloturés
    
    clos=closed[['SK_ID_CURR','anomalies','AMT_CREDIT_MAX_OVERDUE']].groupby('SK_ID_CURR').agg({'anomalies':['count','sum'],\
                                                                       'AMT_CREDIT_MAX_OVERDUE':['max']})
    clos['%_anomalies_past_credits']=clos[('anomalies','sum')]/clos[('anomalies','count')]
    clos.columns=pd.Index(['count','sum','bb_max_overdue_closed','bb_%_anomalies_past_credits'])
    
    del closed
    
    return pd.merge(bb_agg,clos[['bb_%_anomalies_past_credits','bb_max_overdue_closed']],left_index=True,right_index=True,how='outer').fillna(0)
    

