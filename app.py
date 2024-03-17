import streamlit as st
import cv2
import requests
from pyzbar.pyzbar import decode
import pandas as pd
from bs4 import BeautifulSoup
import webbrowser
import base64
from PIL import Image
import io

def read_qr_code(frame):
    # Converte o frame para escala de cinza
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    # Decodifica o QR Code
    decoded_objects = decode(gray)
    return decoded_objects

def extract_link_from_qr_code(decoded_objects):
    for obj in decoded_objects:
        if obj.type == 'QRCODE':
            return obj.data.decode("utf-8")
    return None

def extract_data_from_web(url):
    try:
        response = requests.get(url)
        if response.status_code == 200:
            return response.text
        else:
            st.error(f"Erro ao acessar o link: {response.status_code}")
            return None
    except Exception as e:
        st.error(f"Erro ao acessar o link: {str(e)}")
        return None

def extract_cte_data(html_content):
    # Parseia o conteúdo HTML
    soup = BeautifulSoup(html_content, 'html.parser')

    # Encontra a seção "Dados CT-e" e extrai as informações
    data_section = soup.find('section', {'id': 'dadosCTe'})
    if data_section:
        data = {}
        rows = data_section.find_all('tr')
        for row in rows:
            cells = row.find_all('td')
            if len(cells) == 2:
                key = cells[0].get_text(strip=True)
                value = cells[1].get_text(strip=True)
                data[key] = value
        return data
    else:
        st.error("Seção 'Dados CT-e' não encontrada na página.")
        return None

def save_data_to_excel(data, filename):
    try:
        df = pd.DataFrame(data.items(), columns=['Campo', 'Valor'])
        filepath = filename
        df.to_excel(filepath, index=False)
        return filepath
    except Exception as e:
        st.error(f"Erro ao salvar os dados: {str(e)}")
        return None

def main():
    st.title("Leitor de QR Code em Nota Fiscal Eletrônica")

    cap = cv2.VideoCapture(0)  # Acessa a câmera do dispositivo

    if not cap.isOpened():
        st.error("Erro ao acessar a câmera.")
        return

    st.write("Pressione o botão abaixo para capturar uma imagem:")

    if st.button("Capturar"):
        ret, frame = cap.read()

        if ret:
            # Exibe o frame na aplicação
            st.image(frame, channels="BGR")

            # Verifica se foi possível ler o QR Code
            decoded_objects = read_qr_code(frame)
            if decoded_objects:
                st.success("QR Code lido com sucesso!")
                # Extrai o link do QR Code
                link = extract_link_from_qr_code(decoded_objects)
                if link:
                    st.success("Link extraído do QR Code.")
                    # Acessa o link
                    st.write("Acessando o link...")
                    webbrowser.open(link)  # Abre o link no navegador
                    html_content = extract_data_from_web(link)
                    if html_content:
                        st.success("Link acessado com sucesso.")
                        # Extrai os dados da página
                        st.write("Extraindo dados da página...")
                        cte_data = extract_cte_data(html_content)
                        if cte_data:
                            st.success("Dados extraídos com sucesso!")
                            # Exibe os dados na tela
                            st.write("Dados extraídos da página:")
                            st.write(cte_data)
                            # Salva os dados em um arquivo Excel
                            filename = "dados_extraidos.xlsx"
                            filepath = save_data_to_excel(cte_data, filename)
                            if filepath:
                                st.success(f"Dados salvos em {filepath}.")
                                st.markdown(get_binary_file_downloader_html(filepath), unsafe_allow_html=True)
                            else:
                                st.error("Erro ao salvar os dados.")
                        else:
                            st.error("Falha ao extrair os dados da página.")
                    else:
                        st.error("Falha ao acessar o link.")
                else:
                    st.error("Falha ao extrair o link do QR Code.")
            else:
                st.error("Nenhum QR Code encontrado na imagem.")

    cap.release()

# Função auxiliar para gerar o link de download do arquivo
def get_binary_file_downloader_html(bin_file, file_label='File'):
    with open(bin_file, 'rb') as f:
        data = f.read()
    bin_str = base64.b64encode(data).decode()
    href = f'<a href="data:application/octet-stream;base64,{bin_str}" download="{bin_file}">{file_label}</a>'
    return href

if __name__ == "__main__":
    main()
