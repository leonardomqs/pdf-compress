# pdf-compress

Compressão de PDFs via Ghostscript, com junção e rotação em lote. Sem notebooks: tudo pela linha de comando.

O projeto usa [uv](https://docs.astral.sh/uv/) para gerenciar o Python e as dependências.

## Pré-requisitos

### 1. uv

```powershell
winget install astral-sh.uv
```

### 2. Ghostscript (dependência de sistema, não vem pelo uv)

A compressão é feita pelo executável do Ghostscript, que precisa ser instalado à parte:

```powershell
winget install ArtifexSoftware.GhostScript
```

O executável precisa estar no `PATH` — o script procura por `gs`, `gswin32` ou `gswin64`.
O instalador acrescenta o `bin` da instalação (algo como `C:\Program Files\gs\gs10.07.1\bin`) ao
`PATH` da máquina, mas **terminais já abertos não enxergam a mudança**: feche e reabra o terminal
depois de instalar.

Para conferir:

```powershell
gswin64c --version
```

## Instalação

```powershell
uv sync
```

Esse comando baixa o Python 3.12 (definido em `.python-version`), cria o `.venv` e instala as
dependências exatamente nas versões travadas em `uv.lock`. Não é preciso ativar o venv: use `uv run`.

## Uso

### Pastas `input/` e `output/` (modo recomendado)

Coloque em `input/` o que quiser comprimir — um PDF solto, vários PDFs, ou pastas com PDFs — e rode:

```powershell
uv run pdf-compress
```

Todo PDF encontrado em `input/` é comprimido para `output/`, **preservando a estrutura de pastas**:

```
input/                          output/
├── contrato.pdf        ──>     ├── contrato.pdf
└── lote_agosto/                └── lote_agosto/
    ├── ata_01.pdf                  ├── ata_01.pdf
    └── ata_02.pdf                  └── ata_02.pdf
```

Os arquivos de `input/` nunca são alterados. Para escolher o nível de compressão:

```powershell
uv run pdf-compress -c 3
```

Níveis de compressão (`-c`): `0` default, `1` prepress, `2` printer (padrão), `3` ebook, `4` screen.

> As duas pastas são versionadas vazias (via `.gitkeep`) e todo o conteúdo delas é ignorado pelo
> git — os PDFs que você processar não sobem para o GitHub. Veja [Nenhum PDF no repositório](#nenhum-pdf-no-repositório).

### Juntar e rotacionar

Para juntar tudo o que foi comprimido em um PDF único, use `-m` com o nome do arquivo final:

```powershell
uv run pdf-compress -c 3 -m atas.pdf
```

O resultado sai em `output/atas.pdf`, na mesma ordem em que os arquivos aparecem em `input/`.

Para girar todas as páginas (útil quando o scanner inverte a folha), use `-r` com um múltiplo de 90:

```powershell
uv run pdf-compress -c 3 -r 180
```

As duas opções se combinam — comprime, gira e junta em uma passada:

```powershell
uv run pdf-compress -c 3 -r 180 -m atas.pdf
```

### Arquivo avulso

Passando um caminho explícito, o comportamento antigo continua valendo:

```powershell
uv run pdf-compress arquivo.pdf -o saida.pdf -c 3
```

Sem `-o`, o arquivo original é sobrescrito — use `-b` para guardar um `_BACKUP.pdf` antes.

## Nenhum PDF no repositório

Este repositório é público e **nenhum PDF deve ser versionado**. A garantia é feita em duas camadas:

1. **`.gitignore`** — `*.pdf` e `*.PDF` são ignorados em qualquer diretório, então um `git add .`
   nunca pega um PDF por acidente.
2. **Hook `pre-commit`** — mesmo um `git add -f` é barrado na hora do commit. O hook vive em
   `.githooks/pre-commit`, versionado junto do projeto.

O hook é ativado por `core.hooksPath`, que é uma configuração local. **Depois de clonar o
repositório, rode uma vez:**

```powershell
git config core.hooksPath .githooks
```

Sem esse comando, apenas o `.gitignore` protege. Para conferir que está ativo:

```powershell
git config core.hooksPath      # deve responder: .githooks
```

Trabalhe sempre pelas pastas `input/` e `output/` e nenhuma das duas camadas será acionada.

## Gerenciando dependências

```powershell
uv add <pacote>              # adiciona ao projeto e atualiza o lock
uv add --dev <pacote>        # adiciona ao grupo de desenvolvimento
uv remove <pacote>           # remove
uv lock --upgrade            # atualiza as versões travadas
uv run python -c "..."       # roda qualquer comando dentro do ambiente
```

O arquivo `uv.lock` é versionado no git para garantir builds reproduzíveis.

## Estrutura

| Arquivo | Descrição |
| --- | --- |
| `input/` | Entrada: PDFs ou pastas de PDFs a comprimir. Versionada vazia. |
| `output/` | Saída: resultado da compressão, espelhando a estrutura de `input/`. Versionada vazia. |
| `.githooks/pre-commit` | Hook que bloqueia commits contendo PDFs. |
| `pdf_compressor.py` | Todo o código: `compress()`, `merge()`, `rotate()` e a CLI. Baseado em [Theeko74](https://github.com/theeko74/pdfc), licença MIT. |
| `pyproject.toml` | Metadados e dependências do projeto. |
| `.python-version` | Versão do Python usada pelo uv. |
