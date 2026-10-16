# Tela branca no endereço local — 15/10/2026

## Sintoma e causa

`http://127.0.0.1:8000/` respondia 200, mas JavaScript e CSS retornavam 404. O servidor mantinha `index.html` em cache enquanto um novo build do Vite substituía os assets. A página apontava para nomes antigos; o React não iniciava.

## Correção

Em `config/settings.py`, o ambiente `DEBUG` usa loaders de templates sem cache. O servidor local foi reiniciado para aplicar a configuração. Produção mantém o comportamento de cache do Django.

## Verificação e diagnóstico

- Comparar o HTML servido com `frontend/dist/index.html`.
- Conferir no navegador, em Rede/Network, as URLs de JavaScript e CSS: devem retornar 200.
- Validar a renderização da interface; uma resposta 200 apenas no HTML não garante seu funcionamento.
- A porta 8000 foi identificada como pertencente ao Django deste projeto. Não alterar a porta antes de conferir o processo responsável.

## Prevenção

Para desenvolvimento contínuo do React, usar Vite na porta 5173 com Django na 8000. Para testar o pacote compilado na 8000, executar o build e recarregar a página. Alterações na configuração Python exigem reiniciar o servidor quando iniciado com `--noreload`.

Nenhum banco, resposta ou credencial foi alterado nesta correção.
