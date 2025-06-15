# test_system.py

import pandas as pd
import joblib
import numpy as np
from sklearn.metrics import classification_report, confusion_matrix
import matplotlib.pyplot as plt
import seaborn as sns


def test_model_performance():
    print("=== TESTE DE PERFORMANCE DO MODELO ===")

    df = pd.read_csv("https://storage.googleapis.com/bigdataatividade/processed_data.csv")
    model = joblib.load("evasion_model.joblib")
    feature_cols = joblib.load("feature_columns.pkl")

    X = df.drop(columns=[
        "id_escola", "alta_evasao", "id_escola_nome", "id_municipio_nome",
        "sigla_uf_nome", "id_municipio", "inse_classificacao_2014", "inse_classificacao_2015", "taxa_evasao_historica"
    ])
    y = df["alta_evasao"]

    X_encoded = pd.get_dummies(X, columns=["sigla_uf", "rede"], drop_first=False)

    # Garantir que todas as colunas do treino estejam presentes no teste
    for col in feature_cols:
        if col not in X_encoded.columns:
            X_encoded[col] = 0
    X_encoded = X_encoded[feature_cols]

    # Imputar valores ausentes com média
    numeric_cols = X_encoded.select_dtypes(include=["float64", "int64"]).columns
    X_encoded[numeric_cols] = X_encoded[numeric_cols].fillna(X_encoded[numeric_cols].mean())

    y_pred = model.predict(X_encoded)
    y_prob = model.predict_proba(X_encoded)[:, 1]

    print("\nRelatório de Classificação:")
    print(classification_report(y, y_pred))
    print("\nMatriz de Confusão:")
    print(confusion_matrix(y, y_pred))

    accuracy = (y_pred == y).mean()
    print(f"\nAcurácia: {accuracy:.4f}")
    print(f"\nDistribuição das Probabilidades:")
    print(f"Mínima: {y_prob.min():.4f}, Máxima: {y_prob.max():.4f}, Média: {y_prob.mean():.4f}, Mediana: {np.median(y_prob):.4f}")

    return True


def test_data_quality():
    print("\n=== TESTE DE QUALIDADE DOS DADOS ===")

    df = pd.read_csv("https://storage.googleapis.com/bigdataatividade/processed_data.csv")

    print(f"Registros: {len(df)} | Colunas: {len(df.columns)}")
    print("Valores ausentes:")
    print(df.isnull().sum())

    print("\nDistribuição 'alta_evasao':")
    print(df["alta_evasao"].value_counts(normalize=True))

    print("\nEstatísticas descritivas:")
    print(df[["ideb", "nivel_socioeconomico", "taxa_evasao_historica"]].describe())

    return True


def test_dashboard_functionality():
    print("\n=== TESTE DE FUNCIONALIDADE DO DASHBOARD ===")

    try:
        import streamlit as st
        df = pd.read_csv("https://storage.googleapis.com/bigdataatividade/processed_data.csv")
        model = joblib.load("evasion_model.joblib")
        feature_cols = joblib.load("feature_columns.pkl")

        sample_data = pd.DataFrame({
            "ideb": [5.0],
            "nivel_socioeconomico": [50.0],
            "taxa_evasao_historica": [df["taxa_evasao_historica"].mean()],
            "sigla_uf": ["SP"],
            "rede": ["pública"]
        })

        sample_encoded = pd.get_dummies(sample_data, columns=["sigla_uf", "rede"], drop_first=False)

        # Adicionar colunas ausentes com zero
        for col in feature_cols:
            if col not in sample_encoded.columns:
                sample_encoded[col] = 0

        # Reordenar as colunas
        sample_encoded = sample_encoded[feature_cols]

        # Imputar valores ausentes (caso existam)
        numeric_cols = sample_encoded.select_dtypes(include=["float64", "int64"]).columns
        sample_encoded[numeric_cols] = sample_encoded[numeric_cols].fillna(sample_encoded[numeric_cols].mean())

        prediction = model.predict(sample_encoded)[0]
        probability = model.predict_proba(sample_encoded)[0][1]

        print(f"✓ Predição teste: Risco={prediction}, Probabilidade={probability:.4f}")
        return True

    except Exception as e:
        print(f"✗ Erro no dashboard: {str(e)}")
        return False



def generate_test_report():
    print("=== RELATÓRIO DE TESTES DO SISTEMA ===")
    print("Data/Hora:", pd.Timestamp.now().strftime("%Y-%m-%d %H:%M:%S"))

    results = {
        "Performance do Modelo": test_model_performance(),
        "Qualidade dos Dados": test_data_quality(),
        "Funcionalidade do Dashboard": test_dashboard_functionality()
    }

    print("\n=== RESUMO ===")
    for nome, status in results.items():
        print(f"{nome}: {'✓ PASSOU' if status else '✗ FALHOU'}")

    return all(results.values())


if __name__ == "__main__":
    sucesso = generate_test_report()
    if not sucesso:
        exit(1)

