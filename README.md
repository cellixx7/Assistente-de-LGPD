# Assistente de LGPD para pequenas empresas (N2: RAG com modelos locais)

Assistente de suporte que responde dúvidas de donos de pequenos negócios sobre a Lei Geral de Proteção de Dados (LGPD, Lei 13.709/2018). Uma guarda especialista decide se a pergunta pode ser respondida, se deve ser recusada ou se deve ser encaminhada (a um advogado, ou ao encarregado e à ANPD em caso de incidente). Só quando a guarda libera, o documento encontrado segue para um modelo de linguagem local.

**Disciplina:** Inteligência Artificial, Sistemas de Informação, 8º semestre. **Avaliação:** N2.

## Estado desta versão (inscrição, 12/11/2026)

| Parte | Situação |
| :-- | :-- |
| FAQ do domínio | 25 documentos em `corpus/`, origem em `corpus/fontes.md` |
| Rede semântica | 13 relações (8 sinônimos e 5 de herança) em `codigo/rede_semantica.py` |
| Guarda | 7 regras, com cadeia de duas (R2 deduz o fato que R3 usa), decisão e rastro em `codigo/guarda.py` |
| Busca | Provisória, por palavras em comum (cosseno entre conjuntos de palavras), em `codigo/busca_palavras.py` |
| TF-IDF e embeddings | Próxima etapa (versão parcial, 19/11) |
| Modelos locais e prompt | Próxima etapa (versão parcial, 19/11) |

## Como rodar

Na raiz do projeto, só com a biblioteca padrão do Python (3.10 ou mais novo):

```bash
python codigo/main.py                      # demonstração com 8 perguntas
python codigo/main.py "Pequena empresa precisa de DPO?"   # uma pergunta
python codigo/main.py ""                   # pergunta vazia (a guarda recusa, não quebra)
```

## Como funciona (fluxo implementado)

1. `rede_semantica.expandir_pergunta` acrescenta à pergunta os sinônimos e os termos acima na herança (por exemplo, autorização acrescenta consentimento).
2. `busca_palavras.buscar` traz os 3 documentos mais parecidos, com a nota e as palavras em comum.
3. `guarda.extrair_fatos` transforma pergunta e busca em fatos (tema LGPD, incidente em curso, pedido jurídico, documento acima do limiar).
4. `guarda.decidir` aplica as regras em ordem de cautela e devolve a decisão com o rastro de cada regra testada.
5. `assistente.tratar_pergunta` liga as três etapas, e `main.py` imprime tudo.

O limiar de similaridade é `LIMIAR_SIMILARIDADE = 0.15` em `guarda.py`. É um valor provisório, escolhido nesta versão a partir das notas observadas, e será refeito com a busca TF-IDF e embeddings e as 15 perguntas de avaliação.

## Estrutura

```text
codigo/
├── main.py             # execução e impressão
├── assistente.py       # liga rede, busca e guarda
├── rede_semantica.py   # relações e expansão da pergunta
├── busca_palavras.py   # carrega o corpus e busca por palavras (provisória)
├── guarda.py           # fatos, regras, decisão e rastro
└── texto.py            # normalização, radical e palavras vazias
corpus/
├── d01.txt ... d25.txt # um documento por arquivo
└── fontes.md           # origem de cada documento
```

## Declaração de uso de IA

Foi usada a IA Claude (Anthropic) para gerar o código inicial desta versão e o texto dos documentos do corpus (parágrafos que parafraseiam a lei e as resoluções da ANPD). O grupo é responsável por entender e explicar todo o material entregue.
