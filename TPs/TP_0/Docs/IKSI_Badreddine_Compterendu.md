============================================================= test session starts ==============================================================
platform darwin -- Python 3.13.12, pytest-9.1.1, pluggy-1.7.0
rootdir: /Users/iksi/Documents/S3_projet_a_completer/projet_a_completer
configfile: pytest.ini
testpaths: tests
collected 8 items                                                                                                                              

tests/test_data.py ...                                                                                                                   [ 37%]
tests/test_models.py ..                                                                                                                  [ 62%]
tests/test_train.py ...                                                                                                                  [100%]

============================================================== 8 passed in 3.62s ===============================================================
(S3_projet_a_completer) iksi@Iksis-Mac projet_a_completer % uv run python -m monprojet.train
warning: `VIRTUAL_ENV=/Users/iksi/Documents/S3_projet_a_completer/.venv` does not match the project environment path `.venv` and will be ignored; use `--active` to target the active environment instead

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

Modèle sauvegardé : /Users/iksi/Documents/S3_projet_a_completer/projet_a_completer/models/model.joblib
Métriques sauvegardées : /Users/iksi/Documents/S3_projet_a_completer/projet_a_completer/models/metrics.json


============================================================= test session starts ==============================================================
platform darwin -- Python 3.13.12, pytest-9.1.1, pluggy-1.7.0
rootdir: /Users/iksi/Documents/S3_projet_a_completer/projet_a_completer
configfile: pytest.ini
testpaths: tests
collected 8 items                                                                                                                              

tests/test_data.py ...                                                                                                                   [ 37%]
tests/test_models.py ..                                                                                                                  [ 62%]
tests/test_train.py ...                                                                                                                  [100%]

============================================================== 8 passed in 1.98s ===============================================================
(S3_projet_a_completer) iksi@Iksis-Mac projet_a_completer % uv run python -m monprojet.train
warning: `VIRTUAL_ENV=/Users/iksi/Documents/S3_projet_a_completer/.venv` does not match the project environment path `.venv` and will be ignored; use `--active` to target the active environment instead

=== Comparaison des modèles ===
                         mae    rmse     r2
Modèle                                     
Ridge                 22.623  28.545  0.880
RandomForest          31.845  41.540  0.746
KNeighbors            36.212  46.037  0.688
HistGradientBoosting  39.015  51.049  0.616
Dummy                 70.271  88.416 -0.151

Meilleur modèle : Ridge
Métrique principale : mae
Score : 22.623

Modèle sauvegardé : /Users/iksi/Documents/S3_projet_a_completer/projet_a_completer/models/model.joblib
Métriques sauvegardées : /Users/iksi/Documents/S3_projet_a_completer/projet_a_completer/models/metrics.json