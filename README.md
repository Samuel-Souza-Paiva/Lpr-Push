# Tollgate Dashboard
# Intelbras LPR push notification

Aplicação desktop que recebe notificações de câmeras IP, salva as imagens recebidas, exibe pré-visualização e mantém um histórico em tabela. Possui também indicador de dispositivos conectados e exibe o IP do último dispositivo.

## Funcionalidades

* Indicador de status de conexão (bolinha vermelha/verde) e exibição do IP do dispositivo conectado.
* Recebimento de notificações via endpoint Flask (`/NotificationInfo/<action>`).
* Salvamento automático de imagens em `Desktop/Tollgate_Images`.
* Pré-visualização da imagem recebida dentro da interface Qt.
* Histórico de notificações em tabela com data/hora, placa e caminho do arquivo.
* Pop-up não modal que fecha automaticamente ao exibir nova notificação.
* Configuração de ícone do aplicativo (`assets/icon.ico`) e logo no cabeçalho (`assets/logo.png`).

## Requisitos

* Python 3.7+
* PySide6
* Flask
* Werkzeug
* (Opcional) PyInstaller para gerar executável

## Instalação

1. Clone este repositório:

   ```bash
   git clone <URL_DO_REPO>
   cd <PASTA_DO_REPO>
   ```
2. Instale as dependências:

   ```bash
   python -m pip install --upgrade pip
   pip install flask werkzeug PySide6
   ```

## Estrutura de pastas

```
├── assets/
│   ├── icon.ico       # Ícone do aplicativo
│   └── logo.png       # Logomarca exibida no cabeçalho
├── README.md
└── push-notification.py
```

## Uso

Execute o script principal:

```bash
python push-notification.py
```

Depois, acesse o servidor HTTP criado pelo Flask em:

```
http://<IP_DO_SERVIDOR>:8080
```

Qualquer dispositivo que enviar POST JSON para `/NotificationInfo/<action>` verá sua imagem salva e sinalizada na interface.

## Gerando um executável

Para empacotar tudo em um único `.exe` (Windows) com ícone e pasta de assets embutida, use o PyInstaller:

```bash
python -m PyInstaller `
  --name TollgateDashboard `
  --onefile `
  --windowed `
  --icon assets/icon.ico `
  --add-data "assets;assets" `
  push-notification.py
```

* `--name`: nome do executável gerado.
* `--onefile`: empacota em um único arquivo.
* `--windowed`: cria aplicação sem console.
* `--icon`: ícone do app.
* `--add-data "assets;assets"`: inclui a pasta de `assets` no bundle.

O executável resultante ficará em `push-notification.py`.

## Contribuições

Pull requests são bem-vindos. Para mudanças complexas, abra uma issue primeiro para discutirmos o roteiro.

## Licença

MIT License © \ Samuel Vasconcelos De Souza Paiva
