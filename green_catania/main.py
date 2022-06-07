
# Python 3.7 - scikit-learn 0.20.2 - scipy 1.2.1

from sklearn import datasets

# from sklearn import svm
# from sklearn import gaussian_process
# from sklearn import tree
# from sklearn import neighbors
# from sklearn import ensemble
# from sklearn import naive_bayes
from sklearn import discriminant_analysis

from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score


# Kneighbors 0.95726666
# Tree 0.943
# SVC 0.96207 gamma = 2
# GaussianProcess 0.952
# RandomForest 0.945 n_estimators = 10
# RandomForest 0.948 n_estimators = 20
# RandomForest 0.949 n_estimators = 40
# AdaBoost 0.92
# GaussianNB 0.951
# QuadraticDiscriminantAnalysis 0.97

#
# def main():
#     n = 700
#     iris = datasets.load_iris()
#     x = iris.data
#     y = iris.target
#
#     # classifier = svm.SVC(gamma = 2)
#     # classifier = gaussian_process.GaussianProcessClassifier()
#     # classifier = tree.DecisionTreeClassifier()
#     # classifier = neighbors.KNeighborsClassifier()
#     # classifier = ensemble.AdaBoostClassifier()
#     # classifier = ensemble.RandomForestClassifier(n_estimators=40)
#     # classifier = naive_bayes.GaussianNB()
#     classifier = discriminant_analysis.QuadraticDiscriminantAnalysis()
#
#     for j in range(4):
#         a = 0
#         print("{}/4".format(j+1))
#         for i in range(n):
#             # print(i)
#             x_train, x_test, y_train, y_test = train_test_split(x, y, test_size=.5)
#             classifier.fit(x_train, y_train)
#             predictions = classifier.predict(x_test)
#             a = a + accuracy_score(y_test, predictions)
#
#
#         print(a/n)


def darwin():
    from sklearn import ensemble
    from sklearn.model_selection import train_test_split
    from sklearn.metrics import accuracy_score

    from sklearn.metrics import classification_report, confusion_matrix

    import pandas
    import numpy
    from numpy import zeros

    df = pandas.read_csv('dataset.csv')
    print(df)

    print(df.loc[:, ['android.sensor.accelerometer#mean',
                     'android.sensor.accelerometer#min',
                     'android.sensor.accelerometer#max',
                     'android.sensor.accelerometer#std',
                     'android.sensor.gyroscope#mean',
                     'android.sensor.gyroscope#min',
                     'android.sensor.gyroscope#max',
                     'android.sensor.gyroscope#std', 'target']])

    print(type(df))

    y = zeros((len(df),), dtype=numpy.int)

    for i in range(0, len(df)):

        # Car        1
        # Still      2
        # Train      3
        # Walking    4
        # Bus        5

        if df.iloc[i]['target'] == 'Car':
            y[i] = 1
        if df.iloc[i]['target'] == 'Still':
            y[i] = 2
        if df.iloc[i]['target'] == 'Train':
            y[i] = 3
        if df.iloc[i]['target'] == 'Walking':
            y[i] = 4
        if df.iloc[i]['target'] == 'Bus':
            y[i] = 5

    print(y)

    X = df.loc[:, ['android.sensor.accelerometer#mean',
                   'android.sensor.accelerometer#min',
                   'android.sensor.accelerometer#max',
                   'android.sensor.accelerometer#std',
                   'android.sensor.gyroscope#mean',
                   'android.sensor.gyroscope#min',
                   'android.sensor.gyroscope#max',
                   'android.sensor.gyroscope#std']].values

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.20)

    model = ensemble.RandomForestClassifier(n_estimators=40)
    model.fit(X_train, y_train)
    predicted_train = model.predict(X_train)
    predicted_test = model.predict(X_test)

    print('Train accuracy')
    print(accuracy_score(y_train, predicted_train))

    print('Test score')
    accuracy = accuracy_score(y_test, predicted_test)
    print(accuracy)

    print(confusion_matrix(y_test, predicted_test))
    print(classification_report(y_test, predicted_test))


if __name__== '__main__':
    #main()
    darwin()
