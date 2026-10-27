   
============================================================================= test session starts =============================================
platform win32 -- Python 3.13.12, pytest-9.1.1, pluggy-1.7.0
rootdir: D:\Users\Sara\Documents\Semestre 9 IADA\app ai\S3_projet_a_completer\projet_a_completer
configfile: pytest.ini
testpaths: tests
collected 8 items                                                                                                                                                               

tests\test_data.py ... [ 37%]
tests\test_models.py ..  [ 62%]
tests\test_train.py ...  [100%]

============================================================================== 8 passed in 5.45s ================================================


=== Comparaison des modèles ===
                      accuracy  recall  precision     f1
Modèle                                                  
LogisticRegression       0.889   0.574      0.737  0.645
HistGradientBoosting     0.881   0.574      0.697  0.629
RandomForest             0.873   0.545      0.671  0.602
KNeighbors               0.878   0.540      0.699  0.609
Dummy                    0.824   0.000      0.000  0.000

Meilleur modèle : LogisticRegression
Métrique principale : recall
Score : 0.574

Modèle sauvegardé : D:\Users\Sara\Documents\Semestre 9 IADA\app ai\S3_projet_a_completer\projet_a_completer\models\model.joblib
Métriques sauvegardées : D:\Users\Sara\Documents\Semestre 9 IADA\app ai\S3_projet_a_completer\projet_a_completer\models\metrics.json