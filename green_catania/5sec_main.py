import pandas
import csv
import numpy as np



def diocleziano():

    df3 = pandas.read_csv('test.csv')

    R = df3.loc[:, ['IDMATRICOLA',
                    'VIAGGIO',
                    'DATA',
                    'TIPO',
                    'ACCELEROMETRO',
                    'TIMESTAMP'
                    ]].values

    #
    #
    # lista_val = []
    #
    # tipo_fatto = []
    #
    # tot_i = 0;
    # tipo_rif = ""
    # index = 0;
    #
    # value_rif = df3.iloc[0]['TIMESTAMP']
    #
    # while len(tipo_fatto) != 4:
    #
    #     while
    #
    #     tipo = df3.iloc[tot_i]['TIPO']
    #     if tipo not in tipo_fatto:
    #         value_rif = df3.iloc[tot_i]['TIMESTAMP']
    #         tipo_rif = tipo
    #
    #     while True:
    #         value = df3.iloc[tot_i]['TIMESTAMP']
    #
    #         if value <= value_rif + 5000 :
    #             print(value)
    #             tot_i+=1
    #         else: break
    #
    #
    #
    #
    # print("i = {}".format(tot_i))







    # for j in range(100):
    #     value = df3.iloc[j]['ACCELEROMETRO']
    #     lista.append(value)
    #
    # MAX = max(lista)
    # MIN = min(lista)
    # MEAN = np.mean(lista)
    # STD = np.std(lista)
    # print(MAX, MIN, MEAN, STD)
    #
    # with open('test_1.csv', 'w') as csvfile:
    #
    #     filewriter = csv.writer(csvfile, delimiter=',',
    #                             quotechar='|', quoting=csv.QUOTE_MINIMAL)
    #     filewriter.writerow(
    #         ['IDMATRICOLA', 'VIAGGIO', 'DATA', 'TIPO', 'ACCELEROMETRO#mean', 'ACCELEROMETRO#max', 'ACCELEROMETRO#min',
    #          'ACCELEROMETRO#std', 'TIMESTAMP#start', 'TIMESTAMP#end'])
    #     filewriter.writerow(
    #         [df3.iloc[0]['IDMATRICOLA'], df3.iloc[0]['VIAGGIO'], df3.iloc[0]['DATA'], df3.iloc[0]['TIPO'], MEAN, MAX, MIN,
    #          STD, df3.iloc[0]['TIMESTAMP'], df3.iloc[0]['TIMESTAMP'] + 5090])



if __name__ == '__main__':
    diocleziano()
