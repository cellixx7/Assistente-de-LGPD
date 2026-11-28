# Re-teste v3: o que foi conferido (container Linux, sem Ollama)

Fonte da comparação: números do `artigo.pdf` (v2 entregue) x `saidas/tabelas_v3_container.txt` (rodada atual).

| Item | Artigo (v2) | v3 | Mudou? |
|---|---|---|---|
| Guarda, 15 perguntas | 13/15 | 13/15 | não |
| Guarda, 20 novas | 16/20 | 16/20 | não |
| 10 casos: sem incerteza / com / sem rede | 9 / 10 / 7 | 9 / 10 / 7 | não |
| TF-IDF acerto@3 (7 / 15 novas) | 7/7, 10/15 | 7/7, 10/15 | não |
| Embeddings acerto@3 (7 / 15 novas) | 6/7, 13/15 | 6/7, 13/15 | não |
| Erros do TF-IDF nas novas | d09,d23,d25,d08,d18 | idem | não |
| Erros dos embeddings | d14 (aval.), d23 e d03 (novas) | idem | não |
| Limiar: maior nota fora do domínio / menor a responder | 0,357 / 0,315 | 0,357 / 0,315 | não |
| Respostas marcadas qwen (fiel/sem suporte/recusa) | 5/2/3 | 5/2/3 | não |
| Respostas marcadas llama (fiel/sem suporte/recusa) | 6/0/4 | 6/0/4 | não |

Não conferido (precisa do Ollama): tempos médios (6,68 s e 7,47 s), Tabela 3 do artigo
(modelo sem documentos), exigência E (9/36 sem defesa, 7/36 com).
Observação: a tabela 5 só conta o CSV `respostas_marcadas.csv`; ela não gera respostas novas.
