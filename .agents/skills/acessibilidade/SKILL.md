---
name: acessibilidade
description: >-
  Guia prático e checklist de acessibilidade e semântica para o Tech Direction,
  baseado no DESIGN_SYSTEM.md. Use esta skill ao criar, revisar ou refatorar
  templates HTML, componentes de interface, formulários, estilos CSS ou fluxos
  de interação no frontend.
---

# Acessibilidade — Tech Direction

Use estas diretrizes ao construir ou auditar qualquer tela, componente ou fluxo em `templates/` e `static/`, garantindo conformidade com o `DESIGN_SYSTEM.md`.

## 1. Semântica e Estrutura do Documento

1. **Um único `<h1>` por página** e hierarquia de títulos (`h1` -> `h2` -> `h3`) sem saltos de nível.
2. **Landmarks HTML5:** utilizar `header`, `nav`, `main`, `section`, `article`, `form` e `footer` de acordo com o papel de cada bloco.
3. **Ordem de leitura:** a ordem visual deve corresponder exatamente à ordem do DOM.
4. **Imagens e ícones:**
   - Imagens informativas devem possuir `alt` descritivo; nunca inserir texto importante dentro de imagens.
   - Ícones e elementos puramente decorativos devem usar `aria-hidden="true"`.

## 2. Contraste, Cores e Tipografia

1. **Contraste WCAG AA:**
   - Texto corrido: mínimo **4,5:1**.
   - Texto grande, componentes de interface e indicadores de foco: mínimo **3:1**.
   - Combinações principais do projeto: branco sobre `--blue-950` (`#0A1E3F`), `--ink` (`#10213B`) sobre branco e `--blue-700` (`#1757AA`) sobre branco.
2. **Independência de cor:** verde (`--success` / `--lime-500`) e coral (`--coral-500`) nunca devem carregar significado sozinhos. Estados de sucesso, erro ou progresso precisam de ícone, rótulo ou mensagem textual.
3. **Uso do coral:** `--coral-500` (`#FA765F`) é reservado para ilustrações e elementos grandes; não usar como texto pequeno sobre fundo branco.
4. **Tipografia e zoom:** manter tamanho raiz em `16px`, usar escala em `rem`, `line-height: 1.6` no corpo e não bloquear o zoom do navegador (garantir legibilidade em **200% de zoom** e largura de **320 CSS px**).

## 3. Navegação por Teclado, Foco e Áreas de Toque

1. **Fluxo 100% via teclado:** toda ação interativa (menus, modais, formulários, cards) deve ser operável via `Tab`, `Shift+Tab`, `Enter` e `Espaço`.
2. **Foco visível:** usar contorno verde de `0.2rem` com afastamento (`outline` / `focus-visible`), sem depender apenas de sombra e sem deixar o foco encoberto por elementos fixos.
3. **Alvos interativos:** botões, links de ação e controles devem ter área mínima de **44 × 44 CSS px** (ou espaçamento equivalente).
4. **Redução de movimento:** respeitar `prefers-reduced-motion`, removendo ou suavizando animações não essenciais.

## 4. Padrões de Componentes Acessíveis

- **Navegações e menus:** cada `<nav>` deve ter `aria-label` descritivo; botões que abrem/fecham menus ou painéis devem informar `aria-expanded`.
- **Botões:** usar sempre verbo de ação e manter o texto visível ou `aria-label` claro; ícone é complementar ao rótulo.
- **Cards de conteúdo/trilha:** o card inteiro não deve ser clicável; a navegação deve ocorrer por meio de botão ou link explícito e acessível.
- **Campos de formulário:**
  - Rótulo (`<label>`) persistente acima do campo — `placeholder` nunca substitui `<label>`.
  - Campos obrigatórios indicados visualmente e com atributo `required`.
  - Campos de senha devem oferecer controle nomeado para mostrar/ocultar e `autocomplete` apropriado.
  - Erros de validação devem usar `aria-invalid="true"` e conectar a mensagem de erro via `aria-describedby`.
- **Mensagens e feedback:**
  - Confirmações temporárias (flash/toasts) devem usar região `aria-live="polite"` e permanecer visíveis por tempo suficiente para leitura.
  - Em formulários longos, exibir erros próximos aos campos e um resumo no topo.

## 5. Checklist de Verificação antes de Concluir

Ao finalizar alterações de interface, valide todos os itens abaixo:

- [ ] Todo o fluxo pode ser concluído apenas com o teclado.
- [ ] O foco está sempre visível e nunca fica encoberto.
- [ ] Todos os `<label>`, botões, navegações e mensagens de erro são anunciados corretamente por leitores de tela.
- [ ] Nenhuma informação depende exclusivamente de cor, forma ou posição.
- [ ] O layout e o texto permanecem legíveis em 200% de zoom e largura de 320px.
- [ ] O contraste WCAG AA é atendido nos estados padrão, hover, foco e desabilitado.
- [ ] Animações não essenciais são desativadas quando `prefers-reduced-motion` está ativo.
