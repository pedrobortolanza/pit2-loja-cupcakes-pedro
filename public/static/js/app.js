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

    var agendamento = checkout.querySelector("[data-agendamento]");
    var prazo = checkout.querySelector("[data-prazo]");

    function atualizar() {
      var entrega = checkout.querySelector("input[name=forma_entrega]:checked").value === "entrega";
      var pagamento = checkout.querySelector("input[name=forma_pagamento]:checked").value;
      var quando = checkout.querySelector("input[name=quando]:checked");
      endereco.hidden = !entrega;
      cartao.hidden = pagamento !== "cartao";
      if (agendamento) {
        agendamento.hidden = !quando || quando.value !== "agendado";
      }
      if (prazo) {
        prazo.textContent = "(" + prazo.getAttribute(entrega ? "data-prazo-entrega" : "data-prazo-retirada") + ")";
      }
      var taxaAtual = entrega ? taxa : 0;
      celulaTaxa.textContent = taxaAtual ? formatarMoeda(taxaAtual) : "Grátis";
      celulaTotal.textContent = formatarMoeda(subtotal + taxaAtual);
    }

    checkout.querySelectorAll("input[name=forma_entrega], input[name=forma_pagamento], input[name=quando]").forEach(function (opcao) {
      opcao.addEventListener("change", atualizar);
    });
    atualizar();

    var cep = checkout.querySelector("input[name=cep]");
    var statusCep = checkout.querySelector("[data-cep-status]");
    var ultimoCepBuscado = "";

    function avisarCep(texto) {
      if (statusCep) {
        statusCep.textContent = texto;
      }
    }

    function buscarCep(digitos) {
      if (digitos === ultimoCepBuscado || !window.fetch) {
        return;
      }
      ultimoCepBuscado = digitos;
      avisarCep("Buscando o endereço...");
      fetch("https://viacep.com.br/ws/" + digitos + "/json/")
        .then(function (resposta) {
          if (!resposta.ok) {
            throw new Error("falha");
          }
          return resposta.json();
        })
        .then(function (dados) {
          if (dados.erro) {
            avisarCep("CEP não encontrado. Confira os números ou preencha o endereço à mão.");
            return;
          }
          var campos = { logradouro: dados.logradouro, bairro: dados.bairro, cidade: dados.localidade };
          Object.keys(campos).forEach(function (nome) {
            if (campos[nome]) {
              checkout.querySelector("input[name=" + nome + "]").value = campos[nome];
            }
          });
          avisarCep("Endereço encontrado. Confira e informe o número.");
          checkout.querySelector("input[name=numero]").focus();
        })
        .catch(function () {
          ultimoCepBuscado = "";
          avisarCep("Não foi possível buscar o CEP agora. Preencha o endereço à mão.");
        });
    }

    cep.addEventListener("input", function () {
      var digitos = cep.value.replace(/\D/g, "").slice(0, 8);
      cep.value = digitos.length > 5 ? digitos.slice(0, 5) + "-" + digitos.slice(5) : digitos;
      if (digitos.length === 8) {
        buscarCep(digitos);
      }
    });

    var validade = checkout.querySelector("input[name=validade]");
    validade.addEventListener("input", function () {
      var digitos = validade.value.replace(/\D/g, "").slice(0, 4);
      validade.value = digitos.length > 2 ? digitos.slice(0, 2) + "/" + digitos.slice(2) : digitos;
    });
  }

  var seletorCor = document.querySelector("[data-cor]");
  var previa = document.querySelector("[data-previa]");
  var campoFoto = document.querySelector("[data-foto]");
  if (campoFoto && previa) {
    var desenhoOriginal = previa.innerHTML;
    campoFoto.addEventListener("change", function () {
      var link = campoFoto.value.trim();
      if (/^https:\/\/\S+$/.test(link)) {
        var imagem = document.createElement("img");
        imagem.className = "cupcake-foto";
        imagem.alt = "Prévia da foto";
        imagem.src = link;
        previa.replaceChildren(imagem);
      } else {
        previa.innerHTML = desenhoOriginal;
      }
    });
  }
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
