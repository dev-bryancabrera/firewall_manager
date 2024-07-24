/* Seleccionar Campos */
var selectRegla = $("#selectRegla");
var selectTypeRed = $("#red_type_select");
var selectLocalTypeSelect = $("#red_local_type_select");
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
var typeIpRed = $("#type_ip_red");
var typeMacRed = $("#type_mac_red");
var typeRed = $("#type_red");
var newEntry = $("#newEntry");

var btnCancelar = $("#btnCancelar");
var btnCreate = $("#btncreate");

/* Container */
var domainContainer = $("#domainContainer");
var redContainer = $("#redContainer");
var redTypeContainer = $("#redTypeContainer");
var redLocalTypeContainer = $("#redLocalTypeContainer");
var redIpContainer = $("#redIpContainer");
var redMacContainer = $("#redMacContainer");
var directionContainer = $("#directionContainer");
var ipContainer = $("#ipContainer");
var portContainer = $("#portContainer");
var protocolContainer = $("#protocolContainer");
var rangePortContainer = $("#rangePortContainer");
var contentContainer = $("#contentContainer");
var initPortContainer = $("#initPortContainer");
var endPortContainer = $("#endPortContainer");
var newEntryGroupContainer = $("#newEntryGroup");

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
  $(".ticket-type").append(
    '<button class="show-full-response">Mostrar</button>'
  );

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
      selectEntry: selectEntry,
    });
    cleanDisabledMultiselect({
      content: content,
      typeRed: typeRed,
    });
    ocultarCampos({
      domainContainer: domainContainer,
      contentContainer: contentContainer,
      directionContainer: directionContainer,
      ipContainer: ipContainer,
      portContainer: portContainer,
      rangePortContainer: rangePortContainer,
      contentContainer: contentContainer,
      initPortContainer: initPortContainer,
      endPortContainer: endPortContainer,
      protocolContainer: protocolContainer,
      redTypeContainer: redTypeContainer,
      redLocalTypeContainer: redLocalTypeContainer,
      redContainer: redContainer,
    });

    var selectedOption = selectRegla.val();
    if (selectedOption === "direccion ip") {
      ipAddrInput.prop("disabled", false);
      selectProtocol.prop("disabled", false);
      selectEntry.prop("disabled", false);

      redTypeContainer.css("display", "block");
      protocolContainer.css("display", "block");
      directionContainer.css("display", "block");

      $("#selectEntry option[value='in']").prop("disabled", false);
    } else if (selectedOption === "puerto") {
      selectPortRange.prop("disabled", false);
      selectProtocol.prop("disabled", false);
      selectEntry.prop("disabled", false);
      port.prop("disabled", false);

      label.textContent = "Rango de Puertos";
      labelEntrada.textContent = "Puerto Inicial";
      labelSalida.textContent = "Puerto Final";

      portContainer.css("display", "block");
      rangePortContainer.css("display", "block");
      initPortContainer.css("display", "block");
      endPortContainer.css("display", "block");
      protocolContainer.css("display", "block");
      directionContainer.css("display", "block");
    } else if (selectedOption === "direccion ip y puerto") {
      ipAddrInput.prop("disabled", false);
      selectProtocol.prop("disabled", false);
      port.prop("disabled", false);
      selectEntry.prop("disabled", false);

      redTypeContainer.css("display", "block");
      portContainer.css("display", "block");
      protocolContainer.css("display", "block");
      directionContainer.css("display", "block");

      $("#selectEntry option[value='in']").prop("disabled", false);
    } else if (selectedOption === "dominio") {
      domain.prop("disabled", false);
      selectProtocol.prop("disabled", false);
      port.prop("disabled", false);

      redLocalTypeContainer.css("display", "block");
      domainContainer.css("display", "block");

      $("#selectEntry option[value='in']").prop("disabled", true);
    } else if (selectedOption === "contenido") {
      selectProtocol.prop("disabled", false);

      redLocalTypeContainer.css("display", "block");
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

  selectLocalTypeSelect.on("change", function () {
    /* cleanDisabledInput({
      ipAddrInput: ipAddrInput,
    }); */
    cleanDisabledMultiselect({
      typeIpRed: typeIpRed,
      typeMacRed: typeMacRed,
    });
    ocultarCampos({
      redIpContainer: redIpContainer,
      redMacContainer: redMacContainer,
    });

    var selectedTypeLocalOption = selectLocalTypeSelect.val();
    if (selectedTypeLocalOption === "red_local_ip") {
      typeIpRed.prop("disabled", false);

      redIpContainer.css("display", "block");
    } else if (selectedTypeLocalOption === "red_externa_mac") {
      typeMacRed.prop("disabled", false);

      redMacContainer.css("display", "block");
    }
  });

  let currentSelect = null;

  // AGREGAR UN NUEVO REGISTRO EN EL SELECT
  $(".selectpicker").on(
    "changed.bs.select",
    function (e, clickedIndex, isSelected, previousValue) {
      var selectedValue = $(this).val();
      if (selectedValue === "addNewOption") {
        currentSelect = $(this);
        newEntryGroupContainer.css("display", "flex");
        $("#newEntry").focus();
      } else {
        newEntryGroupContainer.css("display", "none");
      }
    }
  );

  function addNewEntry() {
    var newEntry = $("#newEntry").val();
    if (newEntry && currentSelect) {
      // Inserta antes de la opción "Agregar nueva"
      var newOption = new Option(newEntry, newEntry);
      currentSelect.find("option[value='addNewOption']").before(newOption);

      currentSelect.selectpicker("refresh");
      currentSelect.selectpicker("val", newEntry);

      $("#newEntry").val("");
      newEntryGroupContainer.css("display", "none");
    }
  }

  $("#newEntry").keypress(function (event) {
    if (event.which === 13) {
      addNewEntry();
      event.preventDefault();
    }
  });

  // Agrega el nuevo dato al hacer clic en el botón
  $("#addEntryButton").click(function () {
    addNewEntry();
  });

  $tablesFirewall.bootstrapTable({});

  $("#formFirewall").submit(function (event) {
    event.preventDefault();

    if (
      mostrarAlerta(name_rule, "Se debe asignar un nombre a la Regla") ||
      validarSelect(selectRegla, "Seleccione que tipo de regla desea crear") ||
      validarSelect(action, "Se debe asignar una accion para la Regla") ||
      mostrarAlerta(selectEntry, "El campo de entrada es requerido.") ||
      validarCampoInput(
        ipAddrInput,
        ipContainer,
        "El campo de dirección IP es requerido."
      ) ||
      validarSelectContainer(
        redTypeContainer,
        selectTypeRed,
        "Seleccione que tipo de red se establecera."
      ) ||
      validarCampoInput(
        newEntry,
        newEntryGroupContainer,
        "Ingrese el nuevo dato para la lista de ip o mac."
      ) ||
      validarEntryContainer(
        newEntryGroupContainer,
        "Presione enter o el + para agregar el valor a la lista"
      ) ||
      validarCampoInput(
        domain,
        domainContainer,
        "El campo de dominio es requerido"
      ) ||
      validarSelectContainer(
        redLocalTypeContainer,
        selectLocalTypeSelect,
        "Seleccione que tipo de red se establecera."
      ) ||
      validarSelectContainer(
        redContainer,
        typeRed,
        "Seleccione una red para crear la regla."
      ) ||
      validarSelectContainer(
        redIpContainer,
        typeIpRed,
        "Seleccione una direccion IP del equipo al que se realizara la restriccion."
      ) ||
      validarSelectContainer(
        redMacContainer,
        typeMacRed,
        "Seleccione una direccion MAC del equipo al que se realizara la restriccion."
      ) ||
      validarSelectContainer(
        contentContainer,
        content,
        "Seleccione un tipo de contenido"
      ) ||
      validarCampoInput(
        port,
        portContainer,
        "El campo de puerto es requerido."
      ) ||
      /*  mostrarAlerta(portStart, "El campo de puerto de inicio es requerido.") ||
      mostrarAlerta(portEnd, "El campo de puerto de fin es requerido.") || */
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
    var reglaNombre = button.data("reglaNombre");
    var filaTabla = button.data("reglaFila");
    var tablaId = button.data("tablaId");

    var nameCommentlb = $("#editComment");

    console.log(button.data());

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

    var tabla = $("#" + tablaId);

    if (tabla.find("tr").eq(filaTabla).length) {
      fila = tabla.find("tr").eq(filaTabla);
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

  function validarCampoInput(elemento, contenedor, mensaje) {
    if (
      !elemento.prop("disabled") &&
      elemento.val().trim() === "" &&
      contenedor.css("display") !== "none"
    ) {
      $("#liveToast .toast-body").text(mensaje);
      $("#liveToast").toast("show");
      return true;
    }
    return false;
  }

  function validarEntryContainer(contenedor, mensaje) {
    if (contenedor.css("display") !== "none") {
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

  // Toma y Restaurar el estado del botón de expansión de la tabla
  $(".show-full-response").on("click", function () {
    const $table = $(this).closest("div").find("table");
    const tableId = $table.attr("id");
    const statusExpand = $table
      .toggleClass("full-response")
      .hasClass("full-response");

    // Guardar el estado en sessionStorage
    const datos = obtenerDatosAlmacenados();
    datos.tablas = datos.tablas || {};
    datos.tablas[tableId] = statusExpand;
    guardarDatosAlmacenados(datos);
  });

  abrirUltimoPanelAbierto();
  restaurarEstadoBoton();
  $(window).on("load", function () {
    setTimeout(scrollPos, 600);
  });
});

// Obtener los datos almacenados en sessionStorage y combinarlos en un solo objeto
function obtenerDatosAlmacenados() {
  const estadoGeneral = sessionStorage.getItem("estadoFirewall");
  return estadoGeneral ? JSON.parse(estadoGeneral) : {};
}

// Guardar los datos en sessionStorage bajo una sola clave
function guardarDatosAlmacenados(datos) {
  sessionStorage.setItem("estadoFirewall", JSON.stringify(datos));
}

// Función para obtener el ID del último panel abierto
function obtenerUltimoPanelAbierto() {
  const datos = obtenerDatosAlmacenados();
  return datos.ultimoPanelAbierto || null;
}

// Función para abrir el último panel abierto al cargar la página
function abrirUltimoPanelAbierto() {
  const ultimoPanelId = obtenerUltimoPanelAbierto();
  if (ultimoPanelId) {
    $("#" + ultimoPanelId).collapse("show");
    $("#btn-" + ultimoPanelId).attr("aria-expanded", "true");
  }
}

// Guardar el ID del panel abierto y el estado de las tablas al mostrar un panel del acordeón
$("#accordion").on("shown.bs.collapse", function (e) {
  const idPanel = $(e.target).attr("id");
  const datos = obtenerDatosAlmacenados();
  datos.ultimoPanelAbierto = idPanel;
  guardarDatosAlmacenados(datos);
});

// Eliminar el ID del panel abierto al ocultar todos los paneles del acordeón
$("#accordion").on("hidden.bs.collapse", function () {
  if ($("#accordion .collapse.show").length === 0) {
    const datos = obtenerDatosAlmacenados();
    delete datos.ultimoPanelAbierto;
    guardarDatosAlmacenados(datos);
  }
});

// Restaurar el estado de los botones de expansión de las tablas
function restaurarEstadoBoton() {
  const datos = obtenerDatosAlmacenados();
  if (datos.tablas) {
    for (const [tableId, statusExpand] of Object.entries(datos.tablas)) {
      if (statusExpand) {
        $("#" + tableId).addClass("full-response");
      }
    }
  }
}

// Tomar y Restaurar la posición del scroll
window.addEventListener("beforeunload", function () {
  const datos = obtenerDatosAlmacenados();
  datos.scrollPositionFirewall = window.scrollY;
  guardarDatosAlmacenados(datos);
});

function scrollPos() {
  const datos = obtenerDatosAlmacenados();
  if (datos.scrollPositionFirewall !== undefined) {
    window.scrollTo(0, datos.scrollPositionFirewall);
  }
}

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

function formatoIpAdded(input) {
  // Reemplaza cualquier carácter que no sea dígito, guion o punto
  input.value = input.value.replace(/[^0-9.-]/g, "");
}

function formatoNombreRegla(input) {
  input.value = input.value.replace(/-/g, "");
}

// LimpiarFormulario cuando se presiona cualquier boton
btnCancelar.on("click", limpiarFormulario);
btnCreate.on("click", limpiarFormulario);
