# README - Sistema de Predição de Evasão Escolar

## Descrição do Projeto

Este sistema utiliza Machine Learning para prever quais escolas terão alta taxa de evasão no ensino médio. O projeto inclui análise de dados educacionais, modelo preditivo e dashboard interativo desenvolvido em Streamlit.

## Estrutura do Projeto 

```
ProjetoDash/
├── DadosBrutos/                    # Dados originais
│   ├── ideb/
│   ├── nivel_socioeconomico/
│   └── taxa_transicao/
├── data_preparation.py             # Script de preparação dos dados
├── model_training.py               # Script de treinamento do modelo
├── dashboard.py                    # Dashboard Streamlit
├── test_system.py                  # Testes de validação
├── Dockerfile                      # Imagem Docker 
├── auth.py                         # Regras de Usuario
├── feature_columns.pkl             # Colunas do Modelo
├── .github/workflows               # Teste do Sistema
├── .devcontainer                   # Informações sobre o sistema
├── processed_data.csv              # Dados processados
├── evasion_model.joblib            # Modelo treinado
└── README.md                       # Este arquivo
```

## Requisitos do Sistema

### Python 3.11+
### Bibliotecas necessárias:
- pandas
- scikit-learn  
- streamlit
- plotly
- joblib
- matplotlib
- seaborn
- numpy
- fpdf
- pymongo[srv]
- pymongo
- folium
- streamlit-folium
- python-dotenv
- kaleido
## Instalação e Configuração

### 1. Instalar dependências:
```bash
pip install -r requirements.txt
```

### 2. Executar preparação dos dados:
```bash
python data_preparation.py
```

### 3. Treinar o modelo:
```bash
python model_training.py
```

### 4. Executar testes:
```bash
python test_system.py
```

### 5. Iniciar o dashboard:
```bash
streamlit run dashboard.py --server.port 8501 --server.address 0.0.0.0
```

## Funcionalidades do Dashboard

### 📊 Dashboard Principal
- Métricas gerais (total de escolas, escolas em risco, taxa média de evasão, IDEB médio)
- Gráficos de distribuição por estado e rede de ensino

### 🗺️ Mapa de Risco
- Visualização geográfica do risco por estado
- Mapa coroplético com gradação de cores
- Tabela detalhada por unidade federativa

### 📈 Ranking de Fatores
- Análise de correlação dos fatores de risco
- Gráficos de distribuição das variáveis
- Identificação dos principais preditores

### 🏫 Comparativo Redes
- Análise comparativa entre rede pública e privada
- Métricas de performance por tipo de instituição

### 🎯 Simulador de Cenários
- Interface interativa para predições personalizadas
- Controles para ajuste de IDEB, nível socioeconômico, estado e rede
- Visualização em tempo real da probabilidade de risco

## Dados Utilizados

### Fontes:
1. **IDEB 2021** - Índice de Desenvolvimento da Educação Básica
2. **Nível Socioeconômico 2015** - INSE das escolas
3. **Taxa de Evasão 2021** - Dados de abandono escolar por UF/rede

### Features do Modelo:
- IDEB da escola
- Nível socioeconômico
- Taxa de evasão histórica regional
- Estado (UF)
- Rede de ensino (pública/privada)
- Latitude e Longitude
  
## Modelo de Machine Learning

- **Algoritmo:** Gradient Boosting Classifier
- **Variável alvo:** Alta evasão 

## Arquivos de Saída

1. **processed_data.csv** - Dados limpos e processados
2. **evasion_model.joblib** - Modelo treinado
3. **Dashboard interativo** - Interface web

## Como Usar

### Para análise exploratória:
1. Execute `data_preparation.py` para processar os dados
2. Analise o arquivo `processed_data.csv` gerado

### Para treinamento do modelo:
1. Execute `model_training.py`
2. O modelo será salvo como `evasion_model.joblib`

### Para usar o dashboard:
1. Execute `streamlit run dashboard.py`
2. Acesse http://localhost:8501 no navegador
3. Navegue pelas diferentes páginas usando o menu lateral

### Para fazer predições programaticamente:
```python
import pandas as pd
import joblib

# Carregar modelo
model = joblib.load('evasion_model.joblib')

# Preparar dados de entrada
data = pd.DataFrame({
    'ideb': [5.0],
    'nivel_socioeconomico': [50.0],
    'taxa_evasao_historica': [6.5],
    'sigla_uf': ['SP'],
    'rede': ['pública']
})

# Aplicar encoding
data_encoded = pd.get_dummies(data, columns=['sigla_uf', 'rede'], drop_first=True)

# Fazer predição
prediction = model.predict(data_encoded)
probability = model.predict_proba(data_encoded)[:, 1]
```

## Suporte

Para dúvidas ou problemas:
1. Verifique se todas as dependências estão instaladas
   ```python
   pip list
   ```
3. Confirme que os arquivos de dados estão no diretório correto
4. Execute os testes com `python test_system.py`
5. Ou entre em contato ao email brendofcg.2013@gmail.com

## Licença

Este projeto foi desenvolvido para fins educacionais e de pesquisa. Os dados utilizados são de domínio público do INEP/MEC.

