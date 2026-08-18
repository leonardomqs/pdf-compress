# pdf-compress

Compressão de PDFs via Ghostscript, com notebooks de apoio para processar lotes de arquivos e juntá-los em um único PDF.

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

### Linha de comando

```powershell
uv run pdf-compress arquivo.pdf -o saida.pdf -c 3
```

Níveis de compressão (`-c`): `0` default, `1` prepress, `2` printer (padrão), `3` ebook, `4` screen.

Sem `-o`, o arquivo original é sobrescrito — use `-b` para guardar um `_BACKUP.pdf` antes.

### Notebooks

```powershell
uv run jupyter lab
```

Os notebooks importam `from pdf_compressor import *` e devem ser executados a partir da raiz do
projeto. No VS Code, selecione o interpretador `.venv\Scripts\python.exe`.

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
| `pdf_compressor.py` | Wrapper do Ghostscript (`compress()` + CLI). Original de [Theeko74](https://github.com/theeko74/pdfc), licença MIT. |
| `ementas.ipynb` | Comprime as ementas em lote e junta tudo em `atas.pdf`. |
| `executa.ipynb` | Compressão avulsa de um arquivo. |
| `*_2024.ipynb` | Execuções de demandas anteriores, mantidas como histórico. |
| `pyproject.toml` | Metadados e dependências do projeto. |
| `.python-version` | Versão do Python usada pelo uv. |
