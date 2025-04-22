import pandas as pd
import streamlit as st
from io import BytesIO

# === Carregar dados ===
df = pd.read_csv('eleitorado_mensal.csv', encoding='latin1', sep=';')

# Limpar espaços nos nomes das colunas
df.columns = df.columns.str.strip()

# Aproveitar faixa etária já existente
df['Faixa_Etaria'] = df['Faixa etária']

# === Streamlit App ===
st.title('Cotas de Eleitorado por Faixa Etária e Sexo')

# Seleção de Estado e Município
estado = st.selectbox('Selecione o Estado:', sorted(df['UF'].unique()))
municipio = st.selectbox('Selecione o Município:', sorted(df[df['UF'] == estado]['Município'].unique()))

# Filtrar base pelo estado e município selecionados
df_filtrado = df[(df['UF'] == estado) & (df['Município'] == municipio)]

# Inserir cota desejada
cota = st.number_input('Digite a Cota:', min_value=1, value=50)

# Agrupar por faixa etária e gênero
distribuicao = df_filtrado.groupby(['Faixa_Etaria', 'Gênero'])['Quantidade de eleitor'].sum().reset_index()

# Calcular proporção
total = distribuicao['Quantidade de eleitor'].sum()
distribuicao['Proporcao'] = distribuicao['Quantidade de eleitor'] / total
distribuicao['Qtd_Cota'] = (distribuicao['Proporcao'] * cota).round(0).astype(int)

# Exibir resultados
st.subheader('Distribuição Proporcional:')
st.dataframe(distribuicao[['Faixa_Etaria', 'Gênero', 'Qtd_Cota']])

# === Função para converter o DataFrame para Excel em memória ===
def to_excel(df):
    output = BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Rateio')
    processed_data = output.getvalue()
    return processed_data

# Botão de download
arquivo_excel = to_excel(distribuicao[['Faixa_Etaria', 'Gênero', 'Qtd_Cota']])
st.download_button(
    label="📥 Baixar Resultado em Excel",
    data=arquivo_excel,
    file_name=f"rateio_{municipio}.xlsx",
    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
)
