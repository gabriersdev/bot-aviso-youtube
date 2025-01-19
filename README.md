# Bot de Notificação de Novo Vídeo no Discord

## Descrição

Este bot notifica automaticamente em um canal do Discord quando um novo vídeo é postado em um canal do YouTube.

## Funcionamento

- Verifica se o último vídeo do canal já foi anunciado.
- Se não foi, envia uma mensagem no Discord.
- Caso já tenha sido anunciado, aguarda a postagem de um novo vídeo.

## Requisitos

- Python 3.12+ com `pip`.
- Bibliotecas: `discord.py`, `pytz`, `google-api-python-client`.
- Conta no Discord e Google, acesso ao Discord Developer Portal e ao Google Cloud Console.
- Servidor do Discord com canal configurado.
- Editor de texto ou IDE.

## Configuração

1. **Preparação**  
   Crie uma pasta com os arquivos:

- `Main.py`: Código principal.
- `logs.txt`: Registro de logs.
- `credentials.py`: Credenciais.
- `history_ids.json`: Histórico de vídeos notificados.

2. **Configuração no Discord**

- Crie um app no [Discord Developer Portal](https://discord.com/developers/applications).
- Configure escopos e permissões (veja no código).
- Adicione o bot ao servidor usando a URL gerada.

3. **API do YouTube**

- Crie um projeto no [Google Cloud Console](https://console.cloud.google.com/).
- Ative a YouTube Data API v3 e gere uma chave de API.

4. **Definição de Credenciais**  
   Insira no `credentials.py`:
   ```python
   credentials = {
       'DISCORD_TOKEN': '#',
       'YOUTUBE_API_KEY': '123',
       'YOUTUBE_CHANNEL_ID': '123',
       'YOUTUBE_CHANNEL_NAME': 'youtube',
       'DISCORD_CHANNEL_ID': 123
   }
   ```

5. **Execução**

- Execute o Main.py.
- Mensagens no console:
- Sucesso: [DATETIME] Bot conectado como [BOTNAME#1234].
- Sem novos vídeos: Novos vídeos do [YOUTUBE_CHANNEL_NAME] não foram encontrados.

## Docker (Opcional)

- Crie os arquivos:
  requirements.txt:
  ```
  pytz~=2024.2
  discord.py~=2.4.0
  google-api-python-client~=2.153.0
  ```

  Dockerfile:
  ```
  FROM python:3.9-slim-buster
  WORKDIR /app
  COPY requirements.txt .
  RUN pip install -r requirements.txt
  COPY . .
  EXPOSE 8001
  CMD ["python", "Main.py"]
  ```

## Configurações Opcionais

- Alterar frequência de verificação no get_loop_minutes.
- Personalizar mensagens no fluxo de envio.

## Tecnologias Utilizadas

- Python
- Discord Developer Portal
- Google Cloud Console
- Docker
- Git/GitHub
- PyCharm