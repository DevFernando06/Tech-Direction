# Tech Direction Design System

Base visual e de interação para uma plataforma educacional inclusiva, jovem e confiável.

## Princípios

1. **Clareza antes de decoração:** uma ação principal por contexto e linguagem direta.
2. **Leitura orientada:** mostrar a posição da pessoa na trilha e oferecer contexto para aprofundamento.
3. **Acesso não é opcional:** teclado, leitores de tela, baixa visão e redução de movimento fazem parte do componente.
4. **Energia com confiança:** azul estrutura a experiência; verde-limão sinaliza avanço e ação.

## Cores

Os tokens estão em `src/index.css`. Não use cores diretamente nos componentes.

| Papel | Token | Valor | Uso |
| --- | --- | --- | --- |
| Marca profunda | `--blue-950` | `#0A1E3F` | Texto forte, rodapé e superfícies escuras |
| Marca | `--blue-700` | `#1757AA` | Links, categorias e informação |
| Ação informativa | `--blue-600` | `#1468D4` | Progresso de leitura e destaques |
| Fundo informativo | `--blue-100` | `#DCECFF` | Tags e fundos suaves |
| Ação principal | `--lime-500` | `#B7E32B` | Botão principal e avanço |
| Destaque quente | `--coral-500` | `#FA765F` | Ilustrações e pontos de atenção não críticos |
| Texto | `--ink` | `#10213B` | Texto principal |
| Texto secundário | `--muted` | `#58677C` | Apoio e metadados |
| Borda | `--line` | `#DCE3EC` | Divisores e contornos |
| Sucesso | `--success` | `#18794E` | Confirmações, sempre com texto/ícone |
| Erro | `--danger` | `#C73532` | Erros, sempre com mensagem textual |

### Contraste e daltonismo

- Texto corrido deve atingir **4,5:1**; texto grande, **3:1**; componentes e foco, **3:1**.
- As combinações principais são branco sobre `--blue-950`, `--ink` sobre branco e `--blue-700` sobre branco.
- Verde e coral não carregam significado sozinhos. Estados incluem ícone, rótulo ou mensagem.
- Coral é reservado a elementos grandes/decorativos; não é utilizado como texto pequeno sobre fundo branco.

## Tipografia

Família: **Plus Jakarta Sans**, com fallback `sans-serif`.

| Nível | Tamanho responsivo | Peso | Uso |
| --- | --- | --- | --- |
| Display | `2.7rem–4.8rem` | 800 | Promessa principal |
| Título de página | `2.2rem–3.4rem` | 800 | Nome da área |
| Título de seção | `2rem–3rem` | 800 | Blocos de conteúdo |
| Título de card | `1.1rem–1.4rem` | 700 | Trilhas e leituras |
| Corpo destacado | `1.05rem–1.15rem` | 400 | Introduções |
| Corpo | `1rem` | 400 | Conteúdo |
| Apoio | `0.75rem–0.9rem` | 500–700 | Metadados e rótulos |

- Tamanho raiz permanece em `16px` do navegador e a escala usa `rem`.
- Corpo usa `line-height: 1.6`; títulos usam entre `1.03` e `1.15`.
- Não bloquear zoom e não inserir texto importante em imagens.

## Espaçamento, grid e responsividade

- Unidade base: **4px**; preferir múltiplos de 4 e 8.
- Espaços recorrentes: 8, 12, 16, 24, 32, 48, 64 e 96.
- Container: máximo de `76rem`, centralizado.
- Desktop: grid de 12 colunas conceituais; cards usam 3 colunas.
- Tablet: 2 colunas.
- Mobile: 1 coluna, a partir de `620px`.
- Áreas interativas têm pelo menos **44 × 44 CSS px** ou espaçamento equivalente.

## Componentes

### Botões

- **Primário:** fundo verde-limão e texto azul profundo. Uma ação principal por bloco.
- **Secundário:** fundo azul profundo e texto branco.
- **Ghost:** ação de menor hierarquia com contorno.
- Sempre usar verbo de ação e estado de foco visível. Ícone é complementar ao rótulo.

### Campos

- Rótulo persistente acima do campo; placeholder nunca substitui label.
- Obrigatoriedade indicada visualmente e pelo atributo `required`.
- Erros devem usar `aria-invalid="true"` e mensagem conectada por `aria-describedby`.
- Senha possui controle nomeado para mostrar/ocultar e autocomplete apropriado.

### Cards de trilha

- Cada trilha é uma coleção editorial composta por textos autorais, imagens, referências e links úteis.
- Ordem: categoria, título, descrição, autoria, quantidade de leituras, referências, progresso de leitura e ação.
- Card não é clicável por inteiro; a ação é um botão explícito e acessível.
- Progresso representa apenas o avanço de leitura e é expresso por barra **e** valor textual.
- Manter o vocabulário centrado em leitura, autoria, seções, fontes e exploração enquanto o produto estiver no formato editorial.

### Feedback

- Confirmações temporárias usam região `aria-live="polite"`.
- Não remover mensagens antes de tempo suficiente para leitura.
- Erros de formulário devem ser exibidos próximos ao campo e resumidos no topo em formulários longos.

## Acessibilidade e semântica

- Um `h1` por página e ordem de títulos sem saltos.
- Usar `header`, `nav`, `main`, `section`, `article`, `form` e `footer` conforme o papel.
- Imagens informativas têm `alt`; elementos decorativos usam `aria-hidden="true"`.
- Navegações possuem `aria-label`; botão de menu informa `aria-expanded`.
- O foco usa contorno verde de `0.2rem` com afastamento e não depende de sombra.
- O layout respeita `prefers-reduced-motion`.
- Ordem visual e ordem do DOM devem permanecer iguais.
- Novos fluxos devem ser testados com teclado, zoom de 200%, leitor de tela e contraste automatizado.

## Checklist antes de publicar

- [ ] Todo fluxo pode ser concluído apenas com teclado.
- [ ] O foco está sempre visível e não fica encoberto.
- [ ] Labels e mensagens de erro são anunciados pelo leitor de tela.
- [ ] Nenhuma informação depende apenas de cor, forma ou posição.
- [ ] Texto mantém legibilidade em 200% de zoom e largura de 320 CSS px.
- [ ] Contraste WCAG AA validado nos estados padrão, hover, foco e desabilitado.
- [ ] Animações não essenciais são removidas com redução de movimento.
