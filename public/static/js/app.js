(function () {
  var botaoMenu = document.querySelector("[data-menu]");
  if (botaoMenu) {
    botaoMenu.addEventListener("click", function () {
      var menu = document.getElementById("menu");
      var aberto = menu.classList.toggle("aberto");
      botaoMenu.setAttribute("aria-expanded", aberto ? "true" : "false");
    });
  }

  document.querySelectorAll("[data-fechar]").forEach(function (botao) {
    botao.addEventListener("click", function () {
      botao.closest(".mensagem").remove();
    });
  });

  document.querySelectorAll("form[data-confirmar]").forEach(function (form) {
    form.addEventListener("submit", function (evento) {
      if (!window.confirm(form.getAttribute("data-confirmar"))) {
        evento.preventDefault();
      }
    });
  });

  function formatarMoeda(valor) {
    return valor.toLocaleString("pt-BR", { style: "currency", currency: "BRL" });
  }

  var checkout = document.querySelector("[data-checkout]");
  if (checkout) {
    var endereco = checkout.querySelector("[data-endereco]");
    var cartao = checkout.querySelector("[data-cartao]");
    var celulaTaxa = checkout.querySelector("[data-taxa]");
    var celulaTotal = checkout.querySelector("[data-total]");
    var taxa = parseFloat(celulaTaxa.getAttribute("data-taxa")) || 0;
    var subtotal = parseFloat(celulaTotal.getAttribute("data-subtotal")) || 0;

    function atualizar() {
      var entrega = checkout.querySelector("input[name=forma_entrega]:checked").value === "entrega";
      var pagamento = checkout.querySelector("input[name=forma_pagamento]:checked").value;
      endereco.hidden = !entrega;
      cartao.hidden = pagamento !== "cartao";
      var taxaAtual = entrega ? taxa : 0;
      celulaTaxa.textContent = taxaAtual ? formatarMoeda(taxaAtual) : "Grátis";
      celulaTotal.textContent = formatarMoeda(subtotal + taxaAtual);
    }

    checkout.querySelectorAll("input[name=forma_entrega], input[name=forma_pagamento]").forEach(function (opcao) {
      opcao.addEventListener("change", atualizar);
    });
    atualizar();

    var cep = checkout.querySelector("input[name=cep]");
    cep.addEventListener("input", function () {
      var digitos = cep.value.replace(/\D/g, "").slice(0, 8);
      cep.value = digitos.length > 5 ? digitos.slice(0, 5) + "-" + digitos.slice(5) : digitos;
    });

    var validade = checkout.querySelector("input[name=validade]");
    validade.addEventListener("input", function () {
      var digitos = validade.value.replace(/\D/g, "").slice(0, 4);
      validade.value = digitos.length > 2 ? digitos.slice(0, 2) + "/" + digitos.slice(2) : digitos;
    });
  }

  var seletorCor = document.querySelector("[data-cor]");
  var previa = document.querySelector("[data-previa]");
  if (seletorCor && previa) {
    seletorCor.addEventListener("input", function () {
      previa.style.setProperty("--fundo", seletorCor.value);
      var cobertura = previa.querySelectorAll("path")[2];
      if (cobertura) {
        cobertura.setAttribute("fill", seletorCor.value);
      }
    });
  }
})();
