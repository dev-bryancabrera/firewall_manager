/* Seleccionar Campos */
var selectRegla = $("#formSelectRegla");
var name_rule = $("#comment");
var action = $("#formSelectAction");
var ipAddrInput = $("#ipaddr");
var domain = $("#domain");
var content = $("#content");
var selectPortRange = $("#selectPortRange");
var port = $("#port");
var portStart = $("#portStart");
var portEnd = $("#portEnd");
var selectEntry = $("#selectEntry");
var selectProtocol = $("#selectProtocol");

/* Container */
var domainContainer = $("#domainContainer");
var ipContainer = $("#ipContainer");
var portContainer = $("#portContainer");
var protocolContainer = $("#protocolContainer");
var rangePortContainer = $("#rangePortContainer");
var contentContainer = $("#contentContainer");
var initPortContainer = $("#initPortContainer");
var endPortContainer = $("#endPortContainer");

var domainContainerEdit = $("#domainContainerEdit");
var ipContainerEdit = $("#ipContainerEdit");

/* Datos de tabla */
var ruleId = $("#rule_id");

/* Modales Eliminar/Editar */
var confirmarEliminarModal = $("#confirmarEliminar");
var visuzalizarReglaModal = $("#editarRegla");

/* Label */
var label = $("#puertos");
var labelEntrada = $("#puertoEntrada");
var labelSalida = $("#puertoSalida");
var btnSaveRule = $("#btnSave");

/* Botones de Modales */
var btnSeeRule = $("#editarReglaBtn");
var btnConfirmDeleteRule = $("#deleteRuleConfirm");

/* Campos del modal para visualizar la regla */
var selectFromTo = $("#editFromTo");
var ipAddrInputEdit = $("#editaripaddr");
var netmaskInput = $("#editNetmask");
var maskdest = $("#editMaskdest");
var portEdit = $("#editport");
var portStartEdit = $("#editportStart");
var portEndEdit = $("#editportLimit");
var selectEntryEdit = $("#editEntry");
var selectProtocolEdit = $("#editProtocol");
var domainEdit = $("#editDomain");

var $tablesFirewall = $(".table");

$(document).ready(function () {
  /* Ocultar campos iniciales */
  domainContainer.css("display", "none");
  contentContainer.css("display", "none");

  ipAddrInput.prop("disabled", true);
  selectPortRange.prop("disabled", true);
  portStart.prop("disabled", true);
  portEnd.prop("disabled", true);
  selectEntry.prop("disabled", true);
  selectProtocol.prop("disabled", true);
  port.prop("disabled", true);

  function cleanDisabledInput(elements) {
    $.each(elements, function (key, value) {
      value.val("");
      value.prop("disabled", true);
    });
  }

  function cleanDisabledSelect(elements) {
    $.each(elements, function (key, value) {
      value.prop("selectedIndex", 0);
      value.prop("disabled", true);
    });
  }

  function ocultarCampos(campos) {
    $.each(campos, function (key, value) {
      value.css("display", "none");
    });
  }

  function cleanDisabledMultiselect(elements) {
    $.each(elements, function (key, value) {
      value.val([]);
      value.selectpicker("refresh");
    });
  }

  selectRegla.on("change", function () {
    cleanDisabledInput({
      ipAddrInput: ipAddrInput,
      port: port,
      portStart: portStart,
      portEnd: portEnd,
      domain: domain,
    });
    cleanDisabledSelect({
      selectPortRange: selectPortRange,
      selectEntry: selectEntry,
      selectProtocol: selectProtocol,
    });
    cleanDisabledMultiselect({
      content: content,
    });
    ocultarCampos({
      domainContainer: domainContainer,
      contentContainer: contentContainer,
      ipContainer: ipContainer,
      portContainer: portContainer,
      rangePortContainer: rangePortContainer,
      contentContainer: contentContainer,
      initPortContainer: initPortContainer,
      endPortContainer: endPortContainer,
      protocolContainer: protocolContainer,
    });

    var selectedOption = selectRegla.val();
    if (selectedOption === "direccion ip") {
      ipAddrInput.prop("disabled", false);
      selectEntry.prop("disabled", false);
      selectProtocol.prop("disabled", false);

      ipContainer.css("display", "block");
      protocolContainer.css("display", "block");

      $("#selectEntry option[value='in']").prop("disabled", false);
    } else if (selectedOption === "puerto") {
      selectPortRange.prop("disabled", false);
      selectEntry.prop("disabled", false);
      selectProtocol.prop("disabled", false);
      port.prop("disabled", false);

      label.textContent = "Rango de Puertos";
      labelEntrada.textContent = "Puerto Inicial";
      labelSalida.textContent = "Puerto Final";

      portContainer.css("display", "block");
      rangePortContainer.css("display", "block");
      initPortContainer.css("display", "block");
      endPortContainer.css("display", "block");
      protocolContainer.css("display", "block");

      $("#selectEntry option[value='in']").prop("disabled", true);
    } else if (selectedOption === "direccion ip y puerto") {
      ipAddrInput.prop("disabled", false);
      selectEntry.prop("disabled", false);
      selectProtocol.prop("disabled", false);
      port.prop("disabled", false);

      ipContainer.css("display", "block");
      portContainer.css("display", "block");
      protocolContainer.css("display", "block");

      $("#selectEntry option[value='in']").prop("disabled", false);
    } else if (selectedOption === "dominio") {
      domain.prop("disabled", false);
      selectEntry.prop("disabled", false);
      selectProtocol.prop("disabled", false);
      port.prop("disabled", false);

      domainContainer.css("display", "block");
    } else if (selectedOption === "contenido") {
      selectEntry.prop("disabled", false);
      selectProtocol.prop("disabled", false);
      contentContainer.css("display", "block");
    }
  });

  selectPortRange.on("change", function () {
    cleanDisabledInput({
      port: port,
      portStart: portStart,
      portEnd: portEnd,
    });
    cleanDisabledSelect({
      selectProtocol: selectProtocol,
    });
    var selectedPort = selectPortRange.val();
    var selectedOption = selectRegla.val();

    if (selectedPort === "yes" && selectedOption !== "port") {
      portStart.prop("disabled", false);
    } else if (selectedPort === "yes" && selectedOption === "port") {
      portStart.prop("disabled", false);
      portEnd.prop("disabled", false);

      $("#selectProtocol option[value='in']").prop("disabled", false);
    } else if (selectedPort === "no") {
      port.prop("disabled", false);
      selectProtocol.prop("disabled", false);

      $("#selectProtocol option[value='in']").prop("disabled", false);
    } else {
      port.prop("disabled", false);
      selectProtocol.prop("disabled", false);
    }
  });

  $tablesFirewall.bootstrapTable({});

  $("#formFirewall").submit(function (event) {
    event.preventDefault();

    if (
      validarSelect(selectRegla, "Seleccione que tipo de regla desea crear") ||
      mostrarAlerta(name_rule, "Se debe asignar un nombre a la Regla") ||
      validarSelect(action, "Se debe asignar una accion para la Regla") ||
      mostrarAlerta(ipAddrInput, "El campo de dirección IP es requerido.") ||
      mostrarAlerta(selectEntry, "El campo de entrada es requerido.") ||
      mostrarAlerta(domain, "El campo de dominio es requerido") ||
      validarSelectContainer(
        contentContainer,
        content,
        "Seleccione un tipo de contenido"
      ) ||
      validarCampoDomain(port, "El campo de puerto es requerido.") ||
      validarCampoDomain(
        portStart,
        "El campo de puerto de inicio es requerido."
      ) ||
      validarCampoDomain(portEnd, "El campo de puerto de fin es requerido.") ||
      validarSelectContainer(
        protocolContainer,
        selectProtocol,
        "El campo de protocolo es requerido."
      )
    ) {
      return;
    }

    var formData = $(this).serialize();
    btnSaveRule.prop("disabled", true);

    $.ajax({
      type: "POST",
      url: "/add_rule",
      data: formData,
      success: function (response) {
        alertMessage(response.message);
      },
      error: function (xhr, status, error) {
        console.error(error);
      },
    });
  });

  btnConfirmDeleteRule.on("click", function () {
    var params = {
      id_regla: ruleId.val(),
    };
    btnConfirmDeleteRule.prop("disabled", true);
    $.ajax({
      type: "GET",
      url: "/eliminar_regla",
      data: params,
      success: function (response) {
        //alertMessage(response.message);
        location.reload();
      },
      error: function (xhr, status, error) {
        console.error(error);
      },
    });
  });

  confirmarEliminarModal.on("show.bs.modal", function (event) {
    var button = $(event.relatedTarget);
    var reglaNombre = button.data("regla-id");

    ruleId.val(reglaNombre);
    console.log(ruleId.val());
  });

  /* Carga los datos al modal para visualizar */
  visuzalizarReglaModal.on("show.bs.modal", function (event) {
    var button = $(event.relatedTarget);
    var reglaNombre = button.data("regla-nombre");
    var filaTablaEntrada = button.data("regla-fila-in");
    var filaTablaSalida = button.data("regla-fila-out");

    var nameCommentlb = $("#editComment");

    nameCommentlb.text(reglaNombre);

    domainContainerEdit.css("display", "none");
    ipContainerEdit.css("display", "block");

    selectFromTo.prop("disabled", true).val("");
    ipAddrInputEdit.prop("disabled", true).val("");
    netmaskInput.prop("disabled", true).val("");
    maskdest.prop("disabled", true).val("");
    portEdit.prop("disabled", true).val("");
    portStartEdit.prop("disabled", true).val("");
    portEndEdit.prop("disabled", true).val("");
    selectEntryEdit.prop("disabled", true).val("");
    selectProtocolEdit.prop("disabled", true).val("");
    domainEdit.prop("disabled", true).val("");

    if (filaTablaEntrada) {
      var fila = $("#tableFirewallIn").find("tr").eq(filaTablaEntrada);
    } else {
      var fila = $("#tableFirewallOut").find("tr").eq(filaTablaSalida);
    }

    var protocolo = fila.find(".protocolo").text();
    var entrada = fila.find(".entrada").text();
    var data_rule = fila.find(".dominio").text();

    var lista_dominios = data_rule.split("|").map(function (item) {
      return item.trim();
    });
    var texto_formateado = "";
    for (var i = 0; i < lista_dominios.length; i++) {
      texto_formateado += " - " + lista_dominios[i] + "\n";
    }

    domainEdit.val(texto_formateado);

    selectProtocolEdit.val(protocolo);
    selectEntryEdit.val(entrada);
  });

  function alertMessage(response) {
    $(".alert-message-container").show("medium");
    $(".alert-message").text(response);
    setTimeout(function () {
      location.reload();
      $(".alert-message-container").hide("medium");
    }, 2000);
  }

  function validarCampo(elemento) {
    return (
      !elemento.prop("disabled") &&
      elemento.val().trim() === "" &&
      elemento.css("display") !== "none"
    );
  }

  function validarCampoDomain(elemento, mensaje) {
    if (
      !elemento.prop("disabled") &&
      elemento.val().trim() === "" &&
      domainContainer.css("display") === "none"
    ) {
      $("#liveToast .toast-body").text(mensaje);
      $("#liveToast").toast("show");
      return true;
    }
    return false;
  }

  function validarSelect(elemento, mensaje) {
    if (
      elemento.val() === null ||
      (elemento.val().length === 0 && elemento.css("display") !== "none")
    ) {
      $("#liveToast .toast-body").text(mensaje);
      $("#liveToast").toast("show");
      return true;
    }
    return false;
  }

  function validarSelectContainer(elemento, select, mensaje) {
    if (elemento.css("display") !== "none") {
      validarSelect(select, mensaje);
    }
  }

  function mostrarAlerta(elemento, mensaje) {
    if (validarCampo(elemento)) {
      $("#liveToast .toast-body").text(mensaje);
      $("#liveToast").toast("show");
      return true;
    }
    return false;
  }
});

// Función para limpiar el formulario
function limpiarFormulario() {
  var formulario = document.getElementById("formFirewall");
  formulario.reset();

  ipContainer.css("display", "block");
  portContainer.css("display", "block");
  rangePortContainer.css("display", "block");
  initPortContainer.css("display", "block");
  endPortContainer.css("display", "block");

  ipAddrInput.prop("disabled", true);
  selectPortRange.prop("disabled", true);
  portStart.prop("disabled", true);
  portEnd.prop("disabled", true);
  selectEntry.prop("disabled", true);
  selectProtocol.prop("disabled", true);
  port.prop("disabled", true);
  domainContainer.css("display", "none");
}

// LimpiarFormulario cuando se presiona cualquier boton
$("#btnCancelar").on("click", limpiarFormulario);

$("#btncreate").on("click", limpiarFormulario);
