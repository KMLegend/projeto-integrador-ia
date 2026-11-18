# Etapa 09 — Roteiro da apresentação final

**16/12/2026** · apresentação presencial obrigatória · **todos os integrantes presentes**
Carlos Eduardo · Adryan Kevin · Eduardo Mendonça · Gabriel · Kevin Maykel

Material: `etapa_09_slides.pptx` (5 slides, o máximo permitido) + demonstração ao vivo.

---

## O que a banca vai cobrar

| Exigência do roteiro | Onde é atendida |
|---|---|
| Percurso completo: problema, dataset, modelo, otimização, integração | Slides 1 a 3 |
| Comparação mão × engenharia de prompt | Slide 4 + `etapa_08_comparacao_rodadas.md` |
| Demonstração ao vivo do notebook/modelo | Bloco B abaixo |
| Demonstração da funcionalidade das **duas rodadas** | Blocos B e C abaixo |
| Justificativa técnica das escolhas | Slides 2 e 4 + perguntas |
| Máximo 5 slides | ✅ exatamente 5 |

---

## Checklist — 15 minutos antes

```bash
open -a Docker
```

```bash
cd ~/Documents/Projetos/faculdade/projeto-integrador && docker compose up -d
```

```bash
docker compose --profile tools run --rm model_trainer
```

- [ ] `docker compose ps` mostra 4 serviços, `api_backend` e `celery_worker` em *healthy*
- [ ] `http://localhost:5173` abre com o seletor **Base de Dados** preenchido
- [ ] Notebook `Projeto_Preditivo.ipynb` aberto numa aba, já executado até o fim
- [ ] `doc-projeto/dataset_exemplo_60skus.csv` à mão para o upload
- [ ] Uma otimização de teste rodada e a aba fechada (modelo em cache)
- [ ] Capturas de tela dos resultados salvas, caso a demo falhe
- [ ] `python3.12 doc-projeto/etapa_08_equivalencia.py` roda e imprime *equivalentes*
- [ ] (se for usar a demo 3) `historico_semanal_266k.csv` já carregado — o upload leva ~6 s

---

## Divisão da fala

| Bloco | Quem | Tempo | Slide |
|---|---|---|---|
| A — Problema e percurso | | 2 min | 1 |
| B — Dataset, modelo e **notebook ao vivo** | | 4 min | 2 |
| C — Otimização e **sistema ao vivo** | | 5 min | 3 |
| D — Mão × prompt | | 4 min | 4 |
| E — Conclusão e limitações | | 2 min | 5 |

Preencham os nomes antes. O roteiro exige todos presentes — distribuam para que cada um fale.

---

## Bloco A · Problema e percurso — slide 1

> "Todo gestor de estoque decide a mesma coisa toda semana: o que repor. Comprar de menos
> custa venda; comprar demais imobiliza capital. E o dinheiro disponível quase nunca cobre
> tudo que está em falta."

> "O semestre inteiro é um único fluxo: definimos o dado, treinamos um modelo que prevê a
> demanda, e usamos computação evolutiva para decidir a compra. Machine Learning é o sensor;
> Computação Evolutiva é o motor de decisão."

---

## Bloco B · Dataset, modelo e notebook ao vivo — slide 2

Fale sobre as 5 features e o MAE, então **abra o notebook**.

**Mostrar, nesta ordem:**
1. A célula do dataset — 5 features e a variável-alvo
2. `modelo.fit(...)` e `modelo.predict(...)` — "aqui o modelo aprende, aqui ele aplica"
3. A saída do **MAE: 4.76**
4. A tabela de risco — "falta, adequado ou excesso"

> "Escolhemos regressão linear por decisão de projeto, não por limitação. Uma prova de
> conceito precisa de um modelo auditável: cada coeficiente é explicável. E o erro fica na
> escala do negócio — erra cinco unidades, frase que um gestor entende."

**Este notebook é também a Rodada 1 da comparação.** Diga isso aqui — prepara o bloco D.

---

## Bloco C · Otimização e sistema ao vivo — slide 3

Explique o fitness pelo slide, depois **vá para o navegador**.

### Demonstração 1 — o cenário do notebook

Base `historico_mensal_v1` · Orçamento **1000** · Ciclo **4** · População **60** · Gerações **100**

| Confira na tela | Valor |
|---|---|
| Custo total | **R$ 987,44** — 98,7% do orçamento |
| Atendimento | **82,2%** — 120 de 146 unidades |
| Produtos em risco | **1** |
| Fitness | **816,92** |
| Comparativo | baseline 24,7% e 236,58 contra 82,2% e 816,92 |

> "A solução ingênua divide o orçamento igualmente entre os seis produtos. Ela reserva
> dinheiro para arroz, feijão e detergente, que não precisavam de compra, gasta só R$ 314 e
> deixa o cliente sem leite e sem café. O algoritmo usa 98,7% do orçamento onde havia falta."

### Demonstração 2 — carregar uma base pela tela

Clique em **Enviar CSV** → `doc-projeto/dataset_exemplo_60skus.csv` · Orçamento **8000** · Ciclo **4**

| Confira na tela | Valor |
|---|---|
| Seletor | passa a mostrar **6240 registros, 60 SKUs** |
| Produtos no plano | **18** |
| Atendimento | **67,5%** contra **19,3%** da solução ingênua |
| Produtos em risco | **13** contra **23** |
| Erro do modelo | muda para **± 4,09** — o modelo foi retreinado nesta base |

> "Quanto mais produtos disputam o mesmo orçamento, mais valor a otimização entrega. Com
> sessenta produtos, a diferença contra a divisão igual vai de dezenove para sessenta e sete
> por cento de cobertura."

**Aponte a curva de convergência** desenhando ao vivo: "o worker publica o progresso a cada
dez gerações por WebSocket. A curva nunca desce — isso é o elitismo."

### Demonstração 3 (opcional) — escala real

Se sobrar tempo e quiserem mostrar que o sistema aguenta volume de produção:

**Enviar CSV** → `historico_semanal_266k.csv` (19 MB · 266.600 registros · **1.333 SKUs**) ·
Orçamento **50000** · Ciclo **4**

| Confira | Valor |
|---|---|
| Upload | ~6 s |
| Otimização | **~40 s** · 113 produtos no plano |
| Cobertura | 13,9% contra 2,6% da divisão igual |

> **Atenção — o fitness aparece negativo (−3.021).** Isso não é erro: os pesos da função
> foram calibrados para 6 produtos. O prêmio é limitado a +1.000, mas a penalidade é
> `produtos_em_risco × 5`, que com 1.333 SKUs chega a −6.665. A comparação contra a solução
> ingênua continua válida (−3.219 contra −3.021), mas o número absoluto confunde.
>
> **Se não quiserem explicar isso ao vivo, pulem esta demonstração.** Ela está documentada
> na decisão D-20. Se perguntarem sobre escala sem vocês mostrarem, a resposta é: "roda em
> 40 segundos com 1.333 SKUs; o que não escala são os pesos do fitness, e isso está
> registrado como limitação conhecida."

---

## Bloco D · Mão × engenharia de prompt — slide 4

Este é o bloco que a banca introduziu nas atividades 06 a 08. Seja direto e honesto.

> "Implementamos a mesma função duas vezes. Na Rodada 1, o grupo escreveu o fitness e o
> algoritmo genético à mão, no notebook que vocês acabaram de ver. Na Rodada 2, refizemos a
> mesma coisa como sistema completo, sem digitar código — só orquestrando um agente por prompt."

### Demonstração 4 — a prova de equivalência

```bash
python3.12 doc-projeto/etapa_08_equivalencia.py
```

Roda as duas implementações lado a lado. Saída esperada: **fitness 816,9178 nas duas** e
**0 divergências em 3.000 planos sorteados**.

> "Não é a mesma lógica reescrita por cima: são dois códigos independentes que produzem o
> mesmo número em três mil casos."

### Os três pontos a dizer

1. **O que a Rodada 2 entregou:** 4.342 linhas de backend, 175 testes, 96% de cobertura no
   domínio, Docker e CI — volume que não escreveríamos à mão no prazo.
2. **Onde o agente errou:** 21 defeitos registrados. Declarou conclusão duas vezes com
   defeitos abertos; ignorava o orçamento enviado pela tela; e inventou fatos no próprio
   relatório, citando um produto que não existe no catálogo.
3. **A nota conclusiva:** o trabalho não sumiu, mudou de lugar. Saiu de digitar e foi para
   **especificar antes e verificar depois**. O agente produz código mais rápido do que
   produz confiança.

> **Se perguntarem do tempo:** sejam honestos. "Não cronometramos a Rodada 1 durante os
> encontros, então não temos o número. Comparamos o que era mensurável no repositório."
> Admitir vale mais que inventar — e está registrado assim no documento da Etapa 08.

---

## Bloco E · Conclusão — slide 5

> "O Machine Learning previu, a Computação Evolutiva decidiu — e a rodada escrita à mão nos
> deu o número com o qual conferir a rodada escrita por prompt."

Liste as limitações sem rodeios: preço de venda usado como custo de compra, sem lead time,
sem validade de perecíveis, sem autenticação, dado de referência simulado. **Saber o que
falta é parte da engenharia** — e desarma metade das perguntas difíceis.

---

## Perguntas prováveis

**Por que algoritmo genético e não programação linear?**
O AG aceita restrições não-lineares sem reformular o problema — desconto por volume, espaço
de caminhão, validade. Honestamente: neste cenário de seis produtos um guloso simples também
acharia o ótimo, e usamos esse fato como teste de validação do AG.

**O que mudou de fato usando IA para codificar?**
O controle saiu do editor e foi para a especificação escrita — 25 documentos que impedem o
agente de inventar regra de negócio. E a verificação virou o gargalo: precisa ser
independente do agente, porque o relatório dele não é confiável.

**Vocês entenderam o código que o agente escreveu?**
Sim, e a prova é que encontramos 21 defeitos nele — incluindo um crítico que duas revisões
anteriores não pegaram. Para achar esses defeitos é preciso entender o que o código deveria
fazer. O notebook da Rodada 1 é o que nos deu esse entendimento.

**O dataset é simulado. Isso invalida o resultado?**
Não para uma prova de conceito. A estrutura respeita o padrão de um ERP de varejo, e
acabamos de demonstrar o sistema consumindo uma base externa de 60 produtos carregada pela
tela.

**Um MAE de 4,76 é bom?**
Para itens que vendem de 30 a 100 unidades por semana, errar cinco é pequeno. Para um item
de baixo giro, o mesmo erro pesa mais — por isso comparamos sempre com a média do alvo.

---

## Plano B

| Se acontecer | Faça |
|---|---|
| Docker não sobe | Apresente pelo notebook — os números do Bloco C vêm dele |
| A tela não carrega | `docker compose restart frontend` e recarregue |
| A otimização trava | `docker compose logs celery_worker --tail=20`; se persistir, use as capturas |
| O upload falha | Siga com a base embutida e explique o schema pelo botão "Ver colunas obrigatórias" |

A prova de equivalência (`etapa_08_equivalencia.py`) **não depende de Docker** — roda com
Python puro. Em último caso, ela sozinha sustenta o bloco D.
