# Cadillacs and Dinosaurs Build Kit

[English](README.md) | **Português (Brasil)**

Ferramentas para compilar um port não oficial de **Cadillacs and Dinosaurs** para
Windows x64, com cenário ampliado para 16:9 e menu de cheats durante a partida.
O executável gerado também funciona no Bazzite pelo Proton, incluindo o ROG Ally.

**Versão: 0.1.0 · ROM compatível: dino — World 930201**

O repositório disponibiliza scripts de compilação e modificações no código-fonte.
Não distribui a ROM, o executável do jogo, imagens ou áudio. A compilação exige
uma ROM compatível obtida separadamente e utilizada com os direitos necessários.
Todo o processamento da ROM ocorre localmente; o script não envia dados do jogo
para serviços externos.

## Recursos

- Cenário ampliado para 16:9, sem esticar a imagem original.
- Exibição dos inimigos e limites de movimento adaptados à tela ampliada.
- Ajustes de widescreen na abertura, nas transições, nas telas de história e no final.
- Menu de pausa com **Infinite Ammo** e **Infinite Health**, configuráveis
  separadamente como **No / Yes**.
- Menus em inglês e configurações salvas junto ao jogo.
- Geração local de pacotes para Windows e Bazzite/Proton.

As extensões do cenário usam elementos gráficos do próprio jogo, com repetições
quando necessário. São adaptações, e não imagens ocultas recuperadas além da tela
original. O programa do jogo é traduzido para C++ nativo durante a compilação.
O CPS2Recomp fornece o comportamento da placa, do vídeo e do som; o executável
final não recorre a um interpretador de CPU quando falta código traduzido.

## Requisitos

- Windows x64 para compilar.
- Python 3.11 ou mais recente e Git para Windows, disponíveis no `PATH`.
- Conexão com a internet para baixar as dependências de compilação.
- Vários GB de espaço livre em disco.
- ROM **dino World 930201**, em um arquivo ZIP.

O compilador e as demais ferramentas são baixados para a pasta de trabalho,
sem necessidade de instalação global. A versão 0.1.0 não inclui um script de
compilação para Linux. No Bazzite, o pacote gerado no Windows é executado pelo Proton.

## Compilação

Clone o repositório ou baixe e extraia o arquivo de código-fonte. Recomenda-se
um caminho curto, como `C:\dino-kit`. Abra o PowerShell nessa pasta e execute:

```powershell
python build.py --rom "D:\ROMs\dino.zip"
```

Substitua o caminho do exemplo pelo local da ROM compatível. O script verifica os
arquivos exigidos, baixa e confere as dependências nas versões fixadas, aplica as
alterações de código, traduz o programa do jogo, compila o port e executa um teste
breve de funcionamento nativo.

Ao concluir, serão gerados:

```text
.local/output/Cadillacs-Dinosaurs-Windows-0.1.0/
.local/output/Cadillacs-Dinosaurs-Bazzite-0.1.0/
.local/output/Cadillacs-Dinosaurs-Bazzite-0.1.0.tar.gz
```

No Windows, execute **PLAY.cmd** na pasta do pacote correspondente.

Os pacotes gerados contêm uma cópia da ROM fornecida e o executável produzido a
partir dela. São resultados da compilação local, não releases distribuídas por
este projeto. Não os anexe ao repositório, aos relatos de problemas ou às releases.

### Verificação da ROM

```powershell
python build.py --rom "D:\ROMs\dino.zip" --verify-rom
```

Esse comando verifica a ROM sem baixar ferramentas nem compilar o jogo.
Os 16 arquivos necessários são conferidos por tamanho e hash. A compressão e as
datas do ZIP não afetam a verificação. Versões americanas, japonesas, bootlegs e
ROMs modificadas não são aceitas. Conjuntos incompatíveis ou incompletos são
recusados antes do download das dependências.

### Opções de compilação e solução de problemas

Por padrão, são usadas até oito tarefas simultâneas de compilação. Em computadores
com pouca memória, reduza esse número com `--jobs 2`. Os logs ficam em
`.local/logs` quando se usa a pasta de trabalho padrão.

Para tentar novamente após uma falha, escolha uma nova pasta de trabalho.
O cache de downloads anterior pode ser reutilizado; seus arquivos serão
verificados novamente antes do uso:

```powershell
python build.py --rom "D:\ROMs\dino.zip" --work-dir "C:\dino-build-2" --cache-dir ".local\cache" --jobs 4
```

## Execução no Bazzite / ROG Ally

1. Copie o `.tar.gz` gerado para o aparelho e extraia o conteúdo em uma pasta
   dentro do diretório pessoal.
2. Instale a Steam e uma versão compatível do Proton. O iniciador procura
   Proton 11.0, Proton Experimental e Proton 10.0, nessa ordem.
3. Adicione **jogar.sh**, do pacote extraído, à Steam como um jogo não Steam.
4. Inicie pela Steam. Mantenha desativada a opção de forçar compatibilidade nesse
   atalho, pois o próprio script já inicia o Proton.

Se a permissão de execução tiver sido perdida na extração, execute
`chmod +x jogar.sh` na pasta do pacote. Para usar outra instalação do Proton,
defina `DINO_PROTON` com o caminho completo do executável `proton` antes de
iniciar o script.

O pacote mantém o ambiente do Proton, os logs e as configurações do jogo em sua
própria pasta.

## Menu de pausa e cheats

Durante a partida, pressione **Start** para abrir **Paused** e selecione **Cheats**.

| Comando | Ação |
| --- | --- |
| Direcional para cima/baixo | Selecionar um item |
| A | Abrir um item ou alterar seu valor |
| Direcional para esquerda/direita | Alternar No / Yes |
| B | Voltar ao menu anterior |
| Start | Retomar a partida |

**Infinite Ammo** mantém a munição ao disparar uma arma de fogo equipada.
Não cria armas, não recarrega uma arma já vazia, não afeta granadas e não impede
o desgaste de armas de combate corpo a corpo.

**Infinite Health** protege personagens vivos contra dano e contra o custo de
saúde dos golpes especiais. Não revive um personagem derrotado nem elimina todos
os limites de tempo e mortes previstas pelo roteiro. As duas opções são salvas
independentemente.

Fora de uma partida ativa, Start mantém sua função normal de iniciar ou continuar
o jogo. Movimento, ataque e pulo usam os controles normais do jogo.

## Estado do projeto e relatos de problemas

A versão 0.1.0 é experimental. Foram testadas a compilação no Windows e a execução
no Bazzite/Proton do ROG Ally, incluindo áudio e controles. Há um relato de
fechamento inesperado durante uma partida cuja causa ainda não foi identificada.

Quadros inteiramente pretos nas transições e áreas escuras pertencentes à arte
original continuam fazendo parte da apresentação. Os ajustes de widescreen
corrigem lacunas no cenário e bordas indevidas, sem remover todo pixel preto.

Ao relatar um problema, informe a versão do kit, o sistema operacional, a versão
do Proton quando aplicável, a fase afetada e os passos para reproduzir a falha.
Revise os logs para remover informações pessoais antes de compartilhá-los.
Não anexe ROMs, dados extraídos do jogo, estados salvos ou executáveis gerados.

## Código-fonte e licença

O kit aplica `patches/port.patch` ao [CPS2Recomp v1.5.0](https://github.com/tmcleroy/cps2recomp),
no commit `eea67d13bd2eccab1712db063ebf2eda06853f2b`.
As versões das dependências, os endereços de download e os hashes SHA-256 estão
registrados em `sources.lock.json`.

O software do kit e suas modificações de código usam a licença **GPL-3.0-only**.
Essa licença não abrange a ROM, as imagens, o áudio ou as marcas do jogo original.
Consulte [LICENSE](LICENSE) e [NOTICE.md](NOTICE.md). O projeto não é afiliado
nem endossado pela Capcom ou pelos demais titulares de direitos do jogo.

As verificações para contribuições e as regras de publicação estão em
[CONTRIBUTING.md](CONTRIBUTING.md).
