# 🎬 Tubys Neshy Pro - YouTube Downloader

<p align="center">
<img src="https://i.ibb.co/chwqh0hm/program.png" width="400" alt="Tubys Neshy Pro Screenshot">
</p>

Tubys Neshy Pro é um aplicativo desktop para baixar vídeos e áudios do YouTube com interface amigável e recursos avançados.

## ✨ Recursos

- 🎥 Download de vídeos em diversos formatos (MP4, MP3, WhatsApp)
- 📶 Suporte para múltiplas resoluções (de 144p até 4K)
- 📋 Sistema de fila de downloads
- 🔍 Visualização de informações do vídeo (thumbnail, título, duração, etc.)
- ⏱️ Monitoramento de progresso com velocidade de download e tempo restante
- 🎨 Interface moderna com animações

## 🛠️ Requisitos do Sistema

- 🐍 Python 3.7 ou superior
- 📦 Pacotes Python listados em `requirements.txt`
- 🌐 Conexão com a internet

## ⚙️ Instalação

1. Clone este repositório ou faça o download do código fonte:
   ```bash
   git clone https://github.com/delrlo/tubys-neshy-pro.git
   cd tubys-neshy-pro
Crie e ative um ambiente virtual (opcional mas recomendado):

bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate    # Windows
Instale as dependências:

bash
pip install -r requirements.txt
🚀 Como Usar
Execute o aplicativo:

bash
python main.py
Na interface:

📋 Cole a URL do vídeo do YouTube no campo indicado

🖇️ Selecione o formato desejado (MP4, MP3 ou WhatsApp)

🎚️ Escolha a qualidade (quando aplicável)

📁 Selecione a pasta de destino

⬇️ Clique em "Adicionar à Fila" ou "INICIAR DOWNLOADS"

Para baixar múltiplos vídeos:

➕ Adicione várias URLs à fila

🚦 Inicie os downloads quando estiver pronto

🎛️ Comandos Adicionais
🔍 Buscar Info: Obtém informações do vídeo antes do download

📥 Adicionar à Fila: Adiciona o vídeo atual à lista de downloads pendentes

🗑️ Remover/Limpar: Gerencia itens na fila de downloads

❌ Cancelar: Interrompe os downloads em andamento

📦 Dependências
As principais dependências são:

yt-dlp (fork moderno do youtube-dl)

tkinter (para a interface gráfica)

Pillow (para manipulação de imagens)

ffmpeg (para conversão de formatos - deve estar no PATH do sistema)

🚨 Solução de Problemas
Erros de download:

📡 Verifique sua conexão com a internet

🔗 Certifique-se de que a URL é válida

⚠️ Alguns vídeos podem ter restrições de download

Problemas com thumbnails:

🔒 Pode ser bloqueado por firewall/proxy

🔄 Tente novamente mais tarde

Conversão de formatos:

⚙️ Certifique-se de que o FFmpeg está instalado e no PATH do sistema

📜 Licença
Este projeto está licenciado sob a licença MIT - veja o arquivo LICENSE para mais detalhes.

🤝 Contribuição
Contribuições são bem-vindas! Sinta-se à vontade para abrir issues ou enviar pull requests.


Desenvolvido com ❤️ por [DELIRIO OU YSNESHY]