Integração CFTVIP Intelbras

Este repositório reúne as ferramentas e exemplos criados para integração com o CFTVIP da Intelbras.
Aqui você vai encontrar tudo o que precisa para entender e aplicar as chamadas de API de forma rápida e prática.

📌 O que é isso?

Um espaço para documentar ferramentas criadas durante o desenvolvimento;

Um repositório de exemplos reais de chamadas à API;

Um guia prático para quem precisa usar e testar a integração com o CFTVIP.

📂 Estrutura
cftvip-intelbras/
│── docs/       → Documentação de apoio
│── examples/   → Exemplos de requisições e respostas da API
│── tools/      → Scripts e utilitários para facilitar a integração
│── README.md   → Este guia

🚀 Como começar

Clone o repositório:

git clone https://git.intelbras.com.br/Samuelzin/integracoes-cftvip.git


Entre na pasta do projeto:

# cftvip-intelbras


Explore os diretórios:

/tools → scripts prontos para usar;

/examples → chamadas de API com payloads de exemplo;

/docs → anotações e guias rápidos.

📖 Documentação da API

A documentação oficial da API será detalhada separadamente.
Este repositório funciona como apoio prático: tudo que for mostrado na documentação estará exemplificado aqui.

🤝 Como contribuir

Quer ajudar?

Faça um fork do projeto;

Crie uma branch (git checkout -b minha-feature);

Envie seu pull request.

## LPR-push (headless Linux)

O modulo `LPR-push/push-notification.py` agora roda sem interface grafica e pode ser executado em Linux.

### Dependencias

```bash
python3 -m pip install -r LPR-push/requirements.txt
```

### Execucao

```bash
python3 LPR-push/push-notification.py --host 0.0.0.0 --port 8080
```

### Opcoes uteis

- `--output-dir /caminho/para/imagens`
- `--log-level INFO`
- endpoint de saude: `GET /health`
- endpoint da camera: `POST /NotificationInfo/<action>`
