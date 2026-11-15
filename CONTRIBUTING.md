# Contributing / Como contribuir

## English

Contributions should describe the problem addressed, the resulting behavior and
the checks performed. Include reproduction steps for gameplay or display fixes.
Use UTF-8 for text files and keep the English and Brazilian Portuguese guides
consistent. The upstream GPL license text and copyright notices must be preserved.

### Public files

Commit only kit source, patches, compatibility metadata and documentation.
Do not commit ROMs, extracted data, generated game code, executables, screenshots,
audio, save states, personal logs or tool binaries. The `.local` directory is
reserved for ignored local build data.

The public file list is defined in `scripts/audit_public.py`. After reviewing a
change, update the SHA-256 entry for each changed file in `publish-manifest.json`.
Hashes use UTF-8 file bytes with LF line endings. New public files also require
an explicit entry in the allowlist and `.gitignore` exceptions. The manifest
does not include its own hash.

Stage the reviewed changes, then run:

```text
python scripts/audit_public.py
python -m unittest discover -s tests -v
bash -n scripts/run-bazzite.sh
```

The audit checks current files, the Git index and reachable history. CI runs the
same checks with synthetic test data. It does not receive a ROM, compile the game
or publish game artifacts. A change affecting translation or gameplay also needs
local validation with a compatible ROM; keep those generated files outside the
public commit.

## Português (Brasil)

As contribuições devem descrever o problema resolvido, o comportamento resultante
e as verificações realizadas. Correções de jogabilidade ou imagem devem incluir
passos para reproduzir o problema. Use UTF-8 nos arquivos de texto e mantenha os
guias em inglês e português do Brasil consistentes. O texto original da licença
GPL e os avisos de direitos autorais devem ser preservados.

### Arquivos públicos

Inclua nos commits apenas código do kit, patches, metadados de compatibilidade e
documentação. Não inclua ROMs, dados extraídos, código gerado do jogo, executáveis,
screenshots, áudio, estados salvos, logs pessoais ou binários das ferramentas.
A pasta `.local` é reservada aos dados locais de compilação e ignorada pelo Git.

A lista de arquivos públicos está em `scripts/audit_public.py`. Após revisar uma
alteração, atualize o hash SHA-256 de cada arquivo modificado em
`publish-manifest.json`. Os hashes são calculados sobre os bytes UTF-8, com finais
de linha LF. Novos arquivos públicos também exigem uma entrada explícita na lista
de arquivos permitidos e nas exceções do `.gitignore`. O manifesto não inclui
seu próprio hash.

Adicione as alterações revisadas à área de preparação do Git e execute:

```text
python scripts/audit_public.py
python -m unittest discover -s tests -v
bash -n scripts/run-bazzite.sh
```

A auditoria verifica os arquivos atuais, a área de preparação e o histórico
alcançável do Git. A integração contínua executa as mesmas verificações com dados
sintéticos. Ela não recebe uma ROM, não compila o jogo e não publica arquivos do
jogo. Mudanças na tradução do código ou na jogabilidade também exigem validação
local com uma ROM compatível; os arquivos gerados devem ficar fora do commit público.
