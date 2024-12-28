
CREATE MATERIALIZED VIEW VISTAMATERIALITZADA
BUILD IMMEDIATE 
REFRESH COMPLETE
AS 
SELECT 
    D.NAME AS DATASET,
    C.NOMCURT AS CLASSIFICADOR,
    P.VALORS AS PARAMETERS,
    E.DATA AS DATA_EXPERIMENT,
    ROUND(AVG(E.ACCURACY), 2) AS AVG_ACCURACY,
    ROUND(AVG(E.F_SCORE), 2) AS AVG_F_SCORE
FROM
    DATASET D, CLASSIFICADOR C, PARAMETERS P, EXPERIMENT E, REPETICIO R
WHERE 
    D.id = R.id_dataset
    AND R.id_dataset= E.id_dataset
    AND R.NUM = E.num_repeticio
    AND E.nom_curt_classificador = P.nom_curt_classificador
    AND P.VALORS = e.valors_parametres
    AND P.nom_curt_classificador = C.NOMCURT
GROUP BY D.NAME, C.NOMCURT, P.VALORS, e.data;

CREATE OR REPLACE VIEW VISTA_FINAL AS
SELECT
    vm.Dataset,
    vm.Classificador,
    vm.Parameters,
    vm.Avg_Accuracy AS Avg_Accuracy,
    ROUND(SQRT(SUM(POWER((SELECT MAX(E.ACCURACY)
                                       FROM EXPERIMENT E
                                       WHERE E.NOM_CURT_CLASSIFICADOR = vm.Classificador) - vm.Avg_Accuracy, 2)) / COUNT(*)), 2) AS Desviacion_Tipica_Accuracy,
    vm.F_Score AS Avg_F_Score,
    ROUND(SQRT(SUM(POWER((SELECT MAX(E.F_SCORE)
                                 FROM EXPERIMENT E
                                 WHERE E.NOM_CURT_CLASSIFICADOR = vm.Classificador) - vm.F_Score, 2)) / COUNT(*)), 2) AS Desviacion_Tipica_F_Score
FROM
    VISTAMATERIALITZADA vm,
    EXPERIMENT E
WHERE
    vm.Classificador = E.NOM_CURT_CLASSIFICADOR
    AND vm.Dataset = (SELECT NAME FROM DATASET WHERE ID = E.ID_DATASET)
GROUP BY
    vm.Dataset, vm.Classificador, vm.Parameters, vm.Avg_Accuracy, vm.F_Score;