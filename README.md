# Paritários SPPrev — Consulta e Gerenciamento

> **Aplicativo desktop para Windows para consulta e gerenciamento de dados de servidores inativos e pensionistas.**

---

## 📖 História do Projeto

O **Paritários SPPrev** nasceu da necessidade de modernizar o acesso e a gestão dos dados de servidores inativos e pensionistas da SPPrev (Secretaria Pública da Previdência), especificamente da categoria **Paritários** — servidores com vínculo na área de ensino superior. Antes deste sistema, o acesso a informações como CPF, RG, matrícula, status, processos judiciais e lista APEO era feito manualmente em planilhas soltas, sem controle de versão, sem backup estruturado e com risco de inconsistências.

### Como tudo começou
O projeto foi iniciado com um protótipo simples em Python utilizando **CustomTkinter** para a interface e **SQLite** como armazenamento local. A primeira versão já permitia:
- Buscar registros por CPF
- Importar planilhas Excel (.xlsx)
- Exportar e restaurar backups
- Um painel administrativo protegido por senha

### Evolução e refinamentos

| Versão | Principais mudanças |
|--------|---------------------|
| **v1.0** | Protótipo inicial com interface básica e funcionalidades CRUD |
| **v1.1** | Correção de bugs e pequenos ajustes de usabilidade |
| **v1.2** | Otimização de importação com batch inserts e progress bar |
| **v1.3** | Refino de interface com toggle de tema claro/escuro |
| **v2.0** | Redesign completo da interface — inspiração clean, Apple-like, com cards, arredondamentos e tipografia refinada |

---

## ✨ Funcionalidades

- **Consulta por CPF**: busca instantânea com exibição completa de todos os campos e detalhamento dos processos
- **Importação de Planilhas**: suporte a arquivos Excel (.xlsx) com mapeamento automático das colunas e inserção em lote otimizada
- **Painel Administrativo**: edição e exclusão de registros com proteção por senha
- **Backup e Restauração**: exportação em Excel ou JSON, restauração completa do banco
- **Interface com Toggle de Tema**: alterne entre tema escuro e claro
- **Interface Refinada**: cards com cantos arredondados, tipografia clara e espaçamentos generosos

---

## 🗂️ Estrutura do Projeto

```
paritarios-app/
├── main.py                 # Ponto de entrada — configura tema e inicializa a janela
├── requirements.txt        # Dependências Python
├── build.spec             # Configuração PyInstaller para gerar .exe
├── instalar.bat           # Script de instalação automática (Windows)
├── build.bat              # Script de geração do executável (Windows)
├── .gitignore             # Arquivos ignorados pelo Git
├── DOCUMENTACAO.md        # Este arquivo — documentação completa
├── database/
│   └── db_manager.py      # Gerenciador SQLite — CRUD, backup, restore, batch insert
├── excel_io/
│   └── excel_handler.py   # Import/export Excel e backup JSON
├── ui/
│   ├── main_window.py     # Janela principal — topo, abas e toggle de tema
│   ├── consulta_tab.py    # Aba de consulta — busca, cards de dados e processos
│   ├── admin_tab.py       # Aba administrativa — login, formulário de edição
│   └── backup_tab.py      # Aba de backup — exportar, restaurar, limpar
└── data/
    └── paritarios.db      # Banco SQLite (criado automaticamente)
```

---

## 🛠️ Tecnologias

| Tecnologia | Propósito |
|------------|-----------|
| **Python 3.9+** | Linguagem principal |
| **CustomTkinter** | Interface gráfica moderna (GUI) |
| **SQLite3** | Banco de dados relacional embutido |
| **pandas** | Leitura e manipulação de planilhas Excel |
| **openpyxl** | Motor de escrita/leitura de arquivos .xlsx |
| **PyInstaller** | Empacotamento em executável (.exe) |

---

## 📦 Instalação

### Opção 1: Instalação Automática (Windows)

1. **Baixe o projeto** para uma pasta no seu PC
2. **Execute o instalador automático**:
   - Dê dois cliques no arquivo `instalar.bat`
   - O script verifica se o Python está instalado, atualiza o `pip` e instala todas as dependências automaticamente
3. **Execute o aplicativo**:
```bash
python main.py
```

### Opção 2: Instalação Manual

1. **Instale o Python** (versão mínima 3.9):
   - Baixe em: https://www.python.org/downloads/
   - **IMPORTANTE**: durante a instalação, marque a opção **"Add Python to PATH"**

2. **Instale as dependências**:
```bash
pip install -r requirements.txt
```

3. **Execute o aplicativo**:
```bash
python main.py
```

---

## 📦 Distribuição (Gerar .exe)

### Usando o Script Automático

1. Execute o arquivo `build.bat`
2. Aguarde o processo de build (alguns minutos na primeira vez)
3. O executável será gerado em `dist/ParitariosSPPrev.exe`

### Instalação em Outro PC

1. Copie a pasta `dist/` para o PC de destino
2. Execute `ParitariosSPPrev.exe`
3. O aplicativo cria automaticamente o banco de dados na pasta `data/`

---

## 🎮 Uso

### Consulta
1. Acesse a aba **Consulta**
2. Digite o CPF no campo de busca e pressione Enter ou clique em **Buscar**
3. Visualize todos os campos em um card organizado, incluindo processos na fazenda e outros processos
4. Use o toggle de tema no topo para alternar entre escuro e claro

### Importação de Dados
1. Clique no botão **Importar Planilha** no topo da janela
2. Selecione o arquivo Excel com os dados
3. Uma barra de progresso mostra o andamento da importação
4. O sistema adiciona ou atualiza os registros no banco

> **Dica de performance**: A importação usa inserção em lote (batch insert) em uma única transação com otimizações de SQLite, tornando-a muito mais rápida mesmo com planilhas grandes.

### Administração
1. Acesse a aba **Administrativo**
2. Digite a senha de admin (padrão: `admin123`)
3. Busque um CPF para editar ou excluir
4. Altere os campos desejados e clique em **Salvar Alterações**

### Backup
- **Exportar Backup (Excel)**: gera um arquivo .xlsx com todos os dados
- **Exportar Backup (JSON)**: gera um arquivo .json para backup completo
- **Restaurar Backup (JSON)**: importa um backup JSON anterior (substitui todos os dados)
- **Limpar Todos os Dados**: remove todos os registros do banco

### Alternância de Tema
- Use o interruptor **Tema** no topo da janela para alternar entre tema **escuro** e **claro**
- A preferência padrão é o tema escuro

---

## 🔒 Segurança

- **Senha de Administrador**: `admin123` (pode ser alterada no painel administrativo)
- **Proteção de dados**: todas as operações de exclusão e restauração exigem confirmação prévia

---

## 🗄️ Arquitetura do Banco de Dados

| Característica | Detalhe |
|----------------|---------|
| **Motor** | SQLite3 (embutido) |
| **Arquivo** | `data/paritarios.db` |
| **Chave primária** | CPF (único por registro) |
| **Modo WAL** | Ativado para maior confiabilidade e concorrência |
| **Tabelas** | `pessoas` (dados dos servidores) e `config` (configurações) |

### Otimizações de Performance
- **Batch insert**: uso de `executemany` em uma única transação em vez de inserts individuais
- **PRAGMA synchronous = OFF** e **PRAGMA journal_mode = MEMORY** durante importação para acelerar escrita
- **WAL mode** para melhorar leitura/escrita concorrente

---

## 🧪 CPFs para Teste

Use os CPFs abaixo para testar a funcionalidade de consulta (dados reais no banco de exemplo):

| CPF | Nome |
|-----|------|
| `00001362801` | IRAIDES POLIMENO GIL |
| `00005812836` | IOLANDA GUIMARAES ALVES |
| `00007890893` | JURACI VIEIRA PEREIRA TOLEDO |
| `00009367829` | SANDRA NOELI TONSIG M ALMEIDA |

### CPFs adicionais (sem zeros iniciais)

| CPF | Nome |
|-----|------|
| `10004590805` | MARIA GRACAS BERNARDO B FELIX |
| `10006939880` | IVONE LUCINDA BARBOSA DA SILVA |
| `10007719892` | MARLY LOPES SANTOS AZEVEDO |
| `10024795844` | ANAUMI RODRIGUES S RUCHINSQUE |
| `10025632833` | LUIZA MARIA F P S PINHEIRO |
| `10025771876` | ANA MARIA SOARES PEREZ RAMOS |

---

## 📁 Formato da Planilha de Importação

A planilha Excel deve conter as seguintes colunas (maiúsculas ou minúsculas, espaços serão removidos automaticamente):

| Coluna | Descrição |
|--------|-----------|
| `nome` | Nome completo |
| `rg` | Número do RG |
| `cpf` | CPF (11 dígitos) |
| `matricula` | Número da matrícula |
| `status` | Situação do servidor |
| `origem_info` | Origem da informação |
| `lista_apeo` | Lista APEO (se aplicável) |
| `especificidade` | Especificidade |
| `processos_fazenda` | Descrição dos processos na fazenda |
| `processos_outros` | Outros processos |
| `qtdade_processos_fazenda` | Quantidade (inteiro) |
| `qtdade_processos_outros` | Quantidade (inteiro) |
| `qtdade_total_processos` | Quantidade total (inteiro) |
| `status_coleta_processos` | Status da coleta |

---

## 🛠️ Manutenção e Desenvolvimento

### Requisitos de Desenvolvimento
- Python 3.9+
- Windows 10/11 (recomendado)
- PyInstaller (para gerar .exe): `pip install pyinstaller`

### Comandos Úteis
```bash
# Executar em modo desenvolvimento
python main.py

# Gerar executável
pyinstaller build.spec --clean --noconfirm

# Instalar dependências
pip install -r requirements.txt
```

---

## 📄 Licença

Este projeto é desenvolvido para uso interno da SPPrev — Secretaria Pública da Previdência.
