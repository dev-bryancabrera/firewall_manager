/* Seleccionar Campos */
var selectRegla = $("#formSelectRegla");
var selectTypeRed = $("#red_type_select");
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
var typeRed = $("#type_red");

var btnCancelar = $("#btnCancelar");
var btnCreate = $("#btncreate");

/* Container */
var domainContainer = $("#domainContainer");
var redContainer = $("#redContainer");
var redTypeContainer = $("#redTypeContainer");
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
var ipAddrInputEdit = $("#editaripaddr");
var netmaskInput = $("#editNetmask");
var maskdest = $("#editMaskdest");
var portEdit = $("#editport");
var selectEntryEdit = $("#editEntry");
var selectProtocolEdit = $("#editProtocol");
var domainEdit = $("#editDomain");

var $tablesFirewall = $(".table");

$(document).ready(function () {
  /* Ocultar campos iniciales */
  domainContainer.css("display", "none");
  contentContainer.css("display", "none");
  redTypeContainer.css("display", "none");
  redContainer.css("display", "none");

  ipAddrInput.prop("disabled", true);
  selectPortRange.prop("disabled", true);
  portStart.prop("disabled", true);
  portEnd.prop("disabled", true);
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
      selectProtocol: selectProtocol,
    });
    cleanDisabledMultiselect({
      content: content,
      typeRed: typeRed,
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
      redTypeContainer: redTypeContainer,
      redContainer: redContainer,
    });

    var selectedOption = selectRegla.val();
    if (selectedOption === "direccion ip") {
      ipAddrInput.prop("disabled", false);
      selectProtocol.prop("disabled", false);

      redTypeContainer.css("display", "block");
      protocolContainer.css("display", "block");

      $("#selectEntry option[value='in']").prop("disabled", false);
    } else if (selectedOption === "puerto") {
      selectPortRange.prop("disabled", false);
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

      // $("#selectEntry option[value='in']").prop("disabled", true);
    } else if (selectedOption === "direccion ip y puerto") {
      ipAddrInput.prop("disabled", false);
      selectProtocol.prop("disabled", false);
      port.prop("disabled", false);

      redTypeContainer.css("display", "block");
      portContainer.css("display", "block");
      protocolContainer.css("display", "block");

      $("#selectEntry option[value='in']").prop("disabled", false);
    } else if (selectedOption === "dominio") {
      domain.prop("disabled", false);
      selectProtocol.prop("disabled", false);
      port.prop("disabled", false);

      domainContainer.css("display", "block");

      $("#selectEntry option[value='in']").prop("disabled", true);
    } else if (selectedOption === "contenido") {
      selectProtocol.prop("disabled", false);
      contentContainer.css("display", "block");

      $("#selectEntry option[value='in']").prop("disabled", true);
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
      portEnd.prop("disabled", false);
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

  selectTypeRed.on("change", function () {
    cleanDisabledInput({
      ipAddrInput: ipAddrInput,
    });
    cleanDisabledMultiselect({
      typeRed: typeRed,
    });
    ocultarCampos({
      ipContainer: ipContainer,
      redContainer: redContainer,
    });

    var selectedTypeOption = selectTypeRed.val();
    if (selectedTypeOption === "red_local") {
      typeRed.prop("disabled", false);

      redContainer.css("display", "block");
    } else if (selectedTypeOption === "red_externa") {
      ipAddrInput.prop("disabled", false);

      ipContainer.css("display", "block");
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
        redTypeContainer,
        selectTypeRed,
        "Seleccione que tipo de red se establecera"
      ) ||
      validarSelectContainer(
        redContainer,
        typeRed,
        "Seleccione una red para crear la regla"
      ) ||
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
        if (response.error) {
          btnSaveRule.prop("disabled", false);
          alertMessage(response.error, "danger");
        } else {
          alertMessage(response.message, "success");
        }
      },
      error: function (error) {
        btnSaveRule.prop("disabled", false);
        alertMessage(error, "danger");
      },
    });
  });

  $('button[id^="btn-regla"]').click(function (event) {
    event.preventDefault();

    var reglaId = $(this).attr("id").split("-", 3)[2];

    var btn_status = $(this);
    btn_status.prop("disabled", true);

    $.ajax({
      type: "GET",
      url: "/desactivar_regla",
      data: { id_regla: reglaId },
      success: function (response) {
        if (response.error) {
          btn_status.prop("disabled", false);
          alertMessage(response.error, "danger");
        } else {
          alertMessage(response.message, "success");
        }
      },
      error: function (textStatus, errorThrown) {
        console.error("Error en la solicitud AJAX:", textStatus, errorThrown);
        alertMessage("Ocurrió un error al procesar la solicitud.", "danger");
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
        if (response.error) {
          btnConfirmDeleteRule.prop("disabled", false);
          alertMessage(response.error, "danger");
        } else {
          alertMessage(response.message, "success");
        }
      },
      error: function (error) {
        btnConfirmDeleteRule.prop("disabled", false);
        alertMessage(error, "danger");
      },
    });
  });

  confirmarEliminarModal.on("show.bs.modal", function (event) {
    var button = $(event.relatedTarget);
    var reglaNombre = button.data("regla-id");

    ruleId.val(reglaNombre);
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

    ipAddrInputEdit.prop("disabled", true).val("");
    netmaskInput.prop("disabled", true).val("");
    maskdest.prop("disabled", true).val("");
    portEdit.prop("disabled", true).val("");
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
    var tipo_regla = fila.find(".tipo_regla").text();

    if (tipo_regla === "Dominio" || tipo_regla === "Contenido") {
      var lista_dominios = data_rule.split(",").map(function (item) {
        return item.trim();
      });
      var texto_formateado = "";
      for (var i = 0; i < lista_dominios.length; i++) {
        texto_formateado += " - " + lista_dominios[i] + "\n";
      }
    } else {
      var ip_regex = /^(\d{1,3})\.(\d{1,3})\.(\d{1,3})\.(\d{1,3})$/;
      if (/:/.test(data_rule)) {
        let data_rule_str = data_rule.split(":");
        if (data_rule_str.length > 6) {
          // Join the first 6 parts as MAC address
          let data_mac = data_rule_str.slice(0, 6).join(":");
          // Join the remaining parts as the port
          let data_port = data_rule_str.slice(6).join(":");
          ipAddrInputEdit.val(data_mac);
          portEdit.val(data_port);
        } else {
          data_rule_str = data_rule.split(":");
          data_ip = data_rule_str[0];
          data_port = data_rule_str[1];
          ipAddrInputEdit.val(data_ip);
          portEdit.val(data_port);
        }
      } else if (ip_regex.test(data_rule)) {
        ipAddrInputEdit.val(data_rule);
      } else {
        portEdit.val(data_rule);
      }
    }

    domainEdit.val(texto_formateado);

    selectProtocolEdit.val(protocolo);
    selectEntryEdit.val(entrada);
  });

  function alertMessage(response, alertType) {
    var alertBox = $(".alert");
    var alertIcon = $(".alert-icon i");
    var alertMessage = $(".alert-message");

    // Oculta el contenedor de mensaje
    $(".alert-message-container").hide("medium");

    // Cambia el tipo de alerta
    if (alertType === "success") {
      alertBox.removeClass("alert-danger").addClass("alert-success");
      alertIcon
        .removeClass("text-danger")
        .addClass("text-success")
        .addClass("fa-check-circle");
    } else if (alertType === "danger") {
      alertBox.removeClass("alert-success").addClass("alert-danger");
      alertIcon
        .removeClass("text-success")
        .addClass("text-danger")
        .addClass("fa-exclamation-circle");
    }

    alertMessage.text(response);
    $(".alert-message-container").show("medium");
    setTimeout(function () {
      if (alertType === "success") {
        location.reload();
      }
      $(".alert-message-container").hide("medium");
    }, 1500);
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
    if (elemento.val() === null || elemento.val().length === 0) {
      $("#liveToast .toast-body").text(mensaje);
      $("#liveToast").toast("show");
      return true;
    }
    return false;
  }

  function validarSelectContainer(contendor, select, mensaje) {
    if (contendor.css("display") !== "none") {
      return validarSelect(select, mensaje);
    }
    return false;
  }

  function mostrarAlerta(elemento, mensaje) {
    if (validarCampo(elemento)) {
      $("#liveToast .toast-body").text(mensaje);
      $("#liveToast").toast("show");
      return true;
    }
    return false;
  }

  scrollPos();
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
  selectProtocol.prop("disabled", true);
  port.prop("disabled", true);

  redTypeContainer.css("display", "none");
  domainContainer.css("display", "none");
  contentContainer.css("display", "none");
}

function formatoDireccionIP(input) {
  // Eliminar cualquier carácter que no sea un número o un punto
  input.value = input.value.replace(/[^\d.]/g, "");

  // Dividir la dirección IP en partes separadas por puntos
  var partes = input.value.split(".");

  // Verificar si el usuario ha ingresado suficientes números antes de agregar puntos
  if (partes.length === 1 && partes[0].length > 2) {
    // Agregar un punto después de los primeros tres caracteres
    input.value = partes[0].substring(0, 3) + "." + partes[0].substring(3);
  } else if (partes.length === 2 && partes[1].length > 2) {
    // Agregar un punto después del cuarto carácter
    input.value =
      partes[0] +
      "." +
      partes[1].substring(0, 3) +
      "." +
      partes[1].substring(3);
  } else if (partes.length === 3 && partes[2].length > 2) {
    // Agregar un punto después del séptimo carácter
    input.value =
      partes[0] +
      "." +
      partes[1] +
      "." +
      partes[2].substring(0, 3) +
      "." +
      partes[2].substring(3);
  }
}

function formatoPuerto(input) {
  input.value = input.value.replace(/[^\d]/g, "");
}

function formatoNombreRegla(input) {
  input.value = input.value.replace(/-/g, "");
}

// LimpiarFormulario cuando se presiona cualquier boton
btnCancelar.on("click", limpiarFormulario);
btnCreate.on("click", limpiarFormulario);

window.addEventListener("beforeunload", function () {
  sessionStorage.setItem("scrollPositionFirewall", window.scrollY);
});

// Restaurar la posición del scroll al cargar la página
function scrollPos() {
  var scrollPosition = sessionStorage.getItem("scrollPositionFirewall");
  if (scrollPosition !== null) {
    window.scrollTo(0, scrollPosition);
  }
}
