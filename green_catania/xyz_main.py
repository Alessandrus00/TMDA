import math
import pandas
import csv




if __name__ == '__main__':


    df2= pandas.read_csv('accelerazioni.csv')
    df2.fillna(0, inplace=True)


    print(df2)

    X2 = df2.loc[:, ['X',
                     'Y',
                     'Z'
                    ]].values

    S= df2.loc[:, ['IDMATRICOLA',
                   'VIAGGIO',
                   'DATA',
                   'TIPO',
                   'TIMESTAMP'
                   ]].values

    ID=[row[0] for row in S]
    Viaggio=[row[1] for row in S]
    Data=[row[2] for row in S]
    Tipo=[row[3] for row in S]
    Timestamp=[row[4] for row in S]



    result=[]
    l=len(X2)

    for row in range (l):
        x = X2.item((row,0))
        y = X2.item((row,1))
        z = X2.item((row,2))
        A = math.sqrt((x**2)+(y**2)+(z**2))
        result.append(A)


    with open('test_not_ord.csv', 'w') as csvfile:
        filewriter = csv.writer(csvfile, delimiter=',',
                                quotechar='|', quoting=csv.QUOTE_MINIMAL)
        filewriter.writerow(['IDMATRICOLA', 'VIAGGIO','DATA','TIPO','ACCELEROMETRO','TIMESTAMP'])
        for i in range(l):
            filewriter.writerow([ID[i],Viaggio[i],Data[i],Tipo[i],result[i],Timestamp[i]])

