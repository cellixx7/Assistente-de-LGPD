# Assistente de LGPD para pequenas empresas (N2: RAG com modelos locais)

Assistente de suporte que responde dúvidas de donos de pequenos negócios sobre a Lei Geral de Proteção de Dados (LGPD, Lei 13.709/2018). Uma guarda especialista decide se a pergunta pode ser respondida, se deve ser recusada ou se deve ser encaminhada a um humano (advogado, ou encarregado e ANPD em caso de incidente). Só quando a guarda libera, o documento encontrado segue para um modelo de linguagem local.

**Disciplina:** Inteligência Artificial, Sistemas de Informação, 8º semestre. **Avaliação:** N2.

## Estado desta versão (inscrição, 12/11/2026)

| Parte | Situação |
| :-- | :-- |
| FAQ do domínio | 25 documentos em `corpus/`, origem em `corpus/fontes.md` |
| Rede semântica | 15 triplas em `codigo/rede_semantica.py`: 8 `sinonimo_de` e 7 `e_um`, com herança de propriedade (`pode_exibir`) |
| Guarda (exercício 5 da Aula 06) | 8 regras SE/ENTÃO, encadeamento para frente, ordem de cautela e incerteza em `codigo/guarda.py` |
| Casos de teste | 10 casos com decisão esperada em `codigo/casos_teste.py`, avaliados por `codigo/avaliacao.py` |
| Busca | Provisória, por palavras em comum (cosseno entre conjuntos de palavras), em `codigo/busca_palavras.py` |
| TF-IDF e embeddings | Próxima etapa (versão parcial, 19/11) |
| Modelos locais e prompt | Próxima etapa (versão parcial, 19/11) |

## Como rodar

Na raiz do projeto, só com a biblioteca padrão do Python (3.10 ou mais novo):

```bash
python codigo/avaliacao.py                 # 10 casos: acurácia sem e com incerteza, efeito da rede, rastro
python codigo/main.py                      # os 10 casos e uma pergunta vazia, passo a passo
python codigo/main.py "Pequena empresa precisa de DPO?"   # uma pergunta
python codigo/main.py ""                   # pergunta vazia (a guarda recusa, não quebra)
```

## Como funciona

1. `rede_semantica.expandir` acrescenta à pergunta os sinônimos da rede (autorização acrescenta consentimento).
2. `busca_palavras.buscar` traz os 3 documentos mais parecidos, com a nota e as palavras em comum.
3. `guarda.perceber` transforma pergunta, rede e busca em **fatos** (sensores): `menciona_dado_pessoal` (herdado pela rede), `pede_exibicao`, `cita_incidente`, `marca_ocorrencia`, `pede_orientacao_juridica`, `sem_termo_do_dominio` e `documento_encontrado` (maior similaridade acima do limiar 0,15).
4. `guarda.encadear_para_frente` dispara as regras até não surgir fato novo. Há três cadeias de duas regras: R1 e R2 (dado pessoal pedido, vazamento, recusar), R3 e R4 (incidente em curso, encaminhar) e R6 e R7 (fora do domínio, recusar).
5. `guarda.decidir` escolhe a ação mais cautelosa entre as concluídas: **recusar** vence **encaminhar_humano**, que vence **responder**. Sem nenhuma ação, um humano decide.
6. **Incerteza:** cada fato tem confiança, e uma conclusão vale a menor confiança de suas condições. O gatilho fraco "qual" dá 0,5 ao pedido de exibição. Se a ação ficar abaixo de 0,7, o assistente encaminha a um humano.
7. `guarda.explicar` escreve a explicação da decisão a partir das regras que dispararam (o rastro).

### Regras

| Regra | SE | ENTÃO |
| :-- | :-- | :-- |
| R1 | menciona_dado_pessoal e pede_exibicao | vazamento_de_dado |
| R2 | vazamento_de_dado | recusar |
| R3 | cita_incidente e marca_ocorrencia | incidente_em_curso |
| R4 | incidente_em_curso | encaminhar_humano |
| R5 | pede_orientacao_juridica | encaminhar_humano |
| R6 | sem_termo_do_dominio | fora_do_dominio |
| R7 | fora_do_dominio | recusar |
| R8 | documento_encontrado | responder |

Nenhuma regra reconhece uma pergunta inteira: todas trabalham sobre fatos.

## PEAS do assistente

- **P (desempenho):** acurácia da guarda nos casos de teste, sem e com incerteza; acerto@3 da busca; respostas fiéis ao documento; nenhuma exibição de dado pessoal; tempo médio por resposta.
- **E (ambiente):** perguntas em português de donos de pequenos negócios sobre LGPD, e um FAQ fixo de 25 documentos.
- **A (atuadores):** responder com a fonte, recusar ou encaminhar a um humano (advogado, encarregado e ANPD).
- **S (sensores):** o texto da pergunta, as notas de similaridade da busca e os fatos percebidos pelas regras de percepção.

## Limites e risco de ajustar as regras só aos casos de teste

Os 10 casos foram escritos junto com as regras, por uma IA a pedido do grupo, então um 10/10 não prova que a guarda acerta perguntas novas. O defeito do gatilho "qual", achado na primeira avaliação, mostrou que o erro está na percepção: palavras que ninguém listou (como "forneça" ou "divulgue") passam despercebidas. Ajustar listas e regras até acertar esses 10 casos é decorar o teste, e por isso nenhuma regra reconhece uma frase inteira. Três casos só acertam por causa da rede, que também foi escrita por pessoas. Para medir de verdade, é preciso testar perguntas novas, escritas por outra pessoa, antes de mexer nas listas.

## Estrutura

```text
codigo/
├── main.py             # execução e impressão passo a passo
├── avaliacao.py        # 10 casos, acurácias, efeito da rede e explicação
├── casos_teste.py      # perguntas e decisões esperadas
├── assistente.py       # liga rede, busca e guarda
├── rede_semantica.py   # triplas, herança de propriedades e expansão
├── busca_palavras.py   # carrega o corpus e busca por palavras (provisória)
├── guarda.py           # sensores, regras, motor, incerteza e explicação
└── texto.py            # normalização, radical e palavras vazias
corpus/
├── d01.txt ... d25.txt # um documento por arquivo
└── fontes.md           # origem de cada documento
```

## Declaração de uso de IA

Foi usada a IA Claude (Anthropic) para gerar o código desta versão, os 10 casos de teste e o texto dos documentos do corpus (parágrafos que parafraseiam a lei e as resoluções da ANPD). O grupo é responsável por entender e explicar todo o material entregue.
