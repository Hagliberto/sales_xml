import streamlit as st
import cv2
from pyzbar.pyzbar import decode
import webbrowser

def read_qr_code(frame):
    # Converte o frame para escala de cinza
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    # Decodifica o QR Code
    decoded_objects = decode(gray)
    return decoded_objects

def main():
    st.title("Leitor de QR Code")

    cap = cv2.VideoCapture(0)  # Acessa a câmera do dispositivo

    if not cap.isOpened():
        st.error("Erro ao acessar a câmera.")
        return

    st.write("Pressione o botão abaixo para capturar uma imagem:")

    if st.button("Capturar"):
        ret, frame = cap.read()

        if ret:
            # Verifica se foi possível ler o QR Code
            decoded_objects = read_qr_code(frame)
            if decoded_objects:
                st.success("QR Code lido com sucesso!")
                # Extrai o link do QR Code
                for obj in decoded_objects:
                    if obj.type == 'QRCODE':
                        link = obj.data.decode("utf-8")
                        st.write(f"Link extraído do QR Code: {link}")
                        # Abrir o link no navegador
                        st.write("Abrindo o link no navegador...")
                        webbrowser.open(link)  # Abre o link no navegador
                        break
            else:
                st.error("Nenhum QR Code encontrado na imagem.")

    cap.release()

if __name__ == "__main__":
    main()
