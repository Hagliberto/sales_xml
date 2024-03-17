import xml.etree.ElementTree as ET
import streamlit as st
import pandas as pd
import io

st.set_page_config(layout=("wide"))

def extract_cte_info(xml_file):
    try:
        # Carregar o XML
        tree = ET.parse(xml_file)
        root = tree.getroot()

        # Namespace
        ns = {'cte': 'http://www.portalfiscal.inf.br/cte'}

        # Chave de Acesso do CTe
        chave_acesso = root.find('.//cte:infProt/cte:chCTe', ns).text

        # Emitente
        emitente = {
            'Nome': root.find('.//cte:emit/cte:xNome', ns).text,
            'CNPJ': root.find('.//cte:emit/cte:CNPJ', ns).text,
            'IE': root.find('.//cte:emit/cte:IE', ns).text,
            'Endereço': {
                'Logradouro': root.find('.//cte:emit/cte:enderEmit/cte:xLgr', ns).text,
                'Número': root.find('.//cte:emit/cte:enderEmit/cte:nro', ns).text,
                'Bairro': root.find('.//cte:emit/cte:enderEmit/cte:xBairro', ns).text,
                'CEP': root.find('.//cte:emit/cte:enderEmit/cte:CEP', ns).text,
                'Município': root.find('.//cte:emit/cte:enderEmit/cte:xMun', ns).text,
                'UF': root.find('.//cte:emit/cte:enderEmit/cte:UF', ns).text,
            }
        }

        # Destinatário
        destinatario = {
            'Nome': root.find('.//cte:dest/cte:xNome', ns).text,
            'CNPJ': root.find('.//cte:dest/cte:CNPJ', ns).text,
            'IE': root.find('.//cte:dest/cte:IE', ns).text,
            'Endereço': {
                'Logradouro': root.find('.//cte:dest/cte:enderDest/cte:xLgr', ns).text,
                'Número': root.find('.//cte:dest/cte:enderDest/cte:nro', ns).text,
                'Bairro': root.find('.//cte:dest/cte:enderDest/cte:xBairro', ns).text,
                'CEP': root.find('.//cte:dest/cte:enderDest/cte:CEP', ns).text,
                'Município': root.find('.//cte:dest/cte:enderDest/cte:xMun', ns).text,
                'UF': root.find('.//cte:dest/cte:enderDest/cte:UF', ns).text,
            }
        }

        # Informações sobre os produtos
        produtos = []
        for prod in root.findall('.//cte:infCarga/cte:infQ', ns):
            produto = {
                'Unidade de Medida': prod.find('cte:cUnid', ns).text,
                'Tipo de Medida': prod.find('cte:tpMed', ns).text,
                'Quantidade': prod.find('cte:qCarga', ns).text
            }
            produtos.append(produto)

        # Totais da operação
        total = {
            'Valor Total da Prestação': root.find('.//cte:vTPrest', ns).text,
            'Valor Total Recebido': root.find('.//cte:vRec', ns).text
        }

        # Impostos
        impostos = {
            'ICMS': {
                'Base de Cálculo': root.find('.//cte:imp/cte:ICMS/cte:ICMS00/cte:vBC', ns).text,
                'Alíquota': root.find('.//cte:imp/cte:ICMS/cte:ICMS00/cte:pICMS', ns).text,
                'Valor': root.find('.//cte:imp/cte:ICMS/cte:ICMS00/cte:vICMS', ns).text
            },
            'ICMSUFFim': {
                'Base de Cálculo': root.find('.//cte:imp/cte:ICMSUFFim/cte:vBCUFFim', ns).text,
                'Alíquota': root.find('.//cte:imp/cte:ICMSUFFim/cte:pICMSUFFim', ns).text,
                'Valor': root.find('.//cte:imp/cte:ICMSUFFim/cte:vICMSUFFim', ns).text
            }
        }

        return chave_acesso, emitente, destinatario, produtos, total, impostos

    except Exception as e:
        st.error(f"Erro ao processar o arquivo XML: {e}")

# Título e descrição da aplicação
st.title("Extração de Informações de Conhecimento de Transporte Eletrônico (CT-e)")
st.write("Faça upload do arquivo XML do CT-e para extrair informações.")

# Upload do arquivo XML
xml_file = st.file_uploader("Faça upload do arquivo XML", type=['xml'])

# Verificar se um arquivo foi enviado
if xml_file is not None:
    # Extrair informações do XML
    chave_acesso, emitente, destinatario, produtos, total, impostos = extract_cte_info(xml_file)

    # Formatar endereço do emitente
    endereco_emitente = (
        f"{emitente['Endereço']['Logradouro']}, {emitente['Endereço']['Número']}\n"
        f"Bairro: {emitente['Endereço']['Bairro']}\n"
        f"CEP: {emitente['Endereço']['CEP']} - {emitente['Endereço']['Município']} / {emitente['Endereço']['UF']}"
    )

    # Formatar endereço do destinatário
    endereco_destinatario = (
        f"{destinatario['Endereço']['Logradouro']}, {destinatario['Endereço']['Número']}\n"
        f"Bairro: {destinatario['Endereço']['Bairro']}\n"
        f"CEP: {destinatario['Endereço']['CEP']} - {destinatario['Endereço']['Município']} / {destinatario['Endereço']['UF']}"
    )

    # Formatar informações dos produtos em DataFrame
    produtos_data = []
    for produto in produtos:
        produtos_data.append({
            'Unidade de Medida': produto['Unidade de Medida'],
            'Tipo de Medida': produto['Tipo de Medida'],
            'Quantidade': produto['Quantidade']
        })
    df_produtos = pd.DataFrame(produtos_data)

    # Formatar informações dos impostos em DataFrame
    impostos_data = {
        'ICMS': {
            'Base de Cálculo': impostos['ICMS']['Base de Cálculo'],
            'Alíquota': impostos['ICMS']['Alíquota'],
            'Valor': impostos['ICMS']['Valor']
        },
        'ICMSUFFim': {
            'Base de Cálculo': impostos['ICMSUFFim']['Base de Cálculo'],
            'Alíquota': impostos['ICMSUFFim']['Alíquota'],
            'Valor': impostos['ICMSUFFim']['Valor']
        }
    }
    df_impostos = pd.DataFrame(impostos_data)

    # Exibir as informações em um DataFrame
    data = {
        'Chave de Acesso': [chave_acesso],
        'Emitente': [emitente['Nome']],
        'CNPJ Emitente': [emitente['CNPJ']],
        'IE Emitente': [emitente['IE']],
        'Endereço Emitente': [endereco_emitente],  # Usando a string formatada do endereço
        'Destinatário': [destinatario['Nome']],
        'CNPJ Destinatário': [destinatario['CNPJ']],
        'IE Destinatário': [destinatario['IE']],
        'Endereço Destinatário': [endereco_destinatario],  # Usando a string formatada do endereço
        'Produtos': [df_produtos.to_string(index=False)],  # Convertendo o DataFrame de produtos em string
        'Total da Prestação': [total['Valor Total da Prestação']],
        'Valor Total Recebido': [total['Valor Total Recebido']],
        'Impostos': [df_impostos.to_string(index=False)]  # Convertendo o DataFrame de impostos em string
    }

    df = pd.DataFrame(data)

    # Mostrar o DataFrame
    st.write("Informações do CT-e:")
    st.write(df)

    # Botão para baixar o DataFrame como arquivo XLSX
    buffer = io.BytesIO()
    with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False, sheet_name='CTe Info')
    buffer.seek(0)
    st.write("Baixe o arquivo XLSX abaixo:")
    st.download_button("Baixar XLSX", buffer, file_name='cte_info.xlsx', mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
