let eventSource = null;
let capturaPausada = false;
let pageLoaded = false;
let load_data = false;
var capturaActiva = true;

/* Boton guardar Reporte */
var btnGuardarReporte = $("#save_report");
var btnPausePlayReporte = $("#btn-play-pause");
var nombreReporte = $("nombreReporte");
var $packetTable = $("#filterPacketTable");
var btnCreateFilter = $("#btn-create-filter");

$(document).ready(function () {
  var filterName = $("#filter_name");
  filterName.removeData("tagsinput");
  var selectFilterType = $("#selectFilterType");

  var filter_id = $("#filter_number");

  // Botones para captura de trafico
  var btnCaptureModal = $(".btn-capture-modal");
  var btnCapture = $(".btn-capture");

  if (sessionStorage.getItem("datosTabla")) {
    btnCaptureModal.css("display", "block");
  } else {
    btnCapture.css("display", "block");
  }

  var filterIp = $("#selectFilterIp");
  var filterDomain = $("#selectFilterDomain");
  var filterContent = $("#selectFilterContent");
  var filterMac = $("#selectFilterMac");
  var filterPort = $("#selectFilterPort");
  var filterProtocolRed = $("#selectFilterProtocolRed");
  var ipAddr = $("#ipaddr");
  var ipDest = $("#ipdest");
  var domainDst = $("#domaindst");
  var contentDst = $("#contentdst");
  var macAddr = $("#macaddr");
  var macDest = $("#macdest");
  var portSrc = $("#portSrc");
  var portDst = $("#portDst");
  var protocolRedSrc = $("#protocolRedSrc");
  var protocolRedDst = $("#protocolRedDst");
  var generalIp = $("#generalip");
  var generalDomain = $("#generaldomain");
  var generalContent = $("#generalcontent");
  var generalPort = $("#generalport");
  var generalProtocolRed = $("#generalProtocolRed");
  var protocol = $("#selectProtocol");

  // Containers
  var ipSrcContainer = $("#ipAddrContainer");
  var ipDstContainer = $("#ipDstContainer");
  var domainDstContainer = $("#domainDstContainer");
  var contentDstContainer = $("#contentDstContainer");
  var macSrcContainer = $("#macSrcContainer");
  var macDstContainer = $("#macDstContainer");
  var portSrcContainer = $("#portSrcContainer");
  var portDstContainer = $("#portDstContainer");
  var protocolRedSrcContainer = $("#protocolRedSrcContainer");
  var protocolRedDstContainer = $("#protocolRedDstContainer");
  var generalIpContainer = $("#generalIpContainer");
  var generalDomainContainer = $("#generaldomainContainer");
  var generalContentContainer = $("#generalContentContainer");
  var generalPortContainer = $("#generalPortContainer");
  var generalProtocolRedContainer = $("#generalProtocolRedContainer");

  // Block Containers
  var ipsContainer = $("#ipsContainer");
  var domainsContainer = $("#domainsContainer");
  var contentsContainer = $("#contentsContainer");
  var portsContainer = $("#portsContainer");
  var protoportsContainer = $("#protoportsContainer");
  var protocolsContainer = $("#protocolsContainer");

  // Filters
  var filterOperatorIp = $("#filterOperatorIp");
  var filterOperatorMac = $("#filterOperatorMac");
  var filterOperatorMacPort = $(".filterOperatorMacPort");
  var filterOperatorProtoRedProto = $(".filterOperatorProtoRedProto");

  // Logical Comparators
  var logicOperatorMacPort = $("#logicOperatorMacPort");
  var logicOperatorProtoRedProto = $("#logicOperatorProtoRedProto");
  var logicOperatorIp = $("#logicOperatorIp");
  var logicOperatorMac = $("#logicOperatorMac");

  // Función para inicializar la página
  var elementosOcultos = [
    ipSrcContainer,
    ipDstContainer,
    contentDstContainer,
    domainDstContainer,
    macSrcContainer,
    macDstContainer,
    portSrcContainer,
    portDstContainer,
    protocolRedSrcContainer,
    protocolRedDstContainer,
    generalIpContainer,
    generalDomainContainer,
    generalContentContainer,
    generalPortContainer,
    generalProtocolRedContainer,
    filterOperatorIp,
    filterOperatorMac,
    filterOperatorMacPort,
    filterOperatorProtoRedProto,

    ipsContainer,
    domainsContainer,
    contentsContainer,
    portsContainer,
    protoportsContainer,
    protocolsContainer,
  ];

  disableElements(
    btnCreateFilter,
    btnGuardarReporte,
    btnPausePlayReporte,
    generalIp,
    generalDomain,
    generalContent,
    generalPort,
    generalProtocolRed,
    ipAddr,
    ipDest,
    domainDst,
    contentDst,
    macAddr,
    macDest,
    portSrc,
    portDst,
    protocolRedSrc,
    protocolRedDst
  );

  // Función para ocultar elementos
  function hideElements() {
    elementosOcultos.forEach((element) => $(element).css("display", "none"));
  }

  // Función para deshabilitar elementos
  function disableElements(...elements) {
    elements.forEach((element) => $(element).prop("disabled", true));
  }

  hideElements();

  /* Dialog */
  var modalDialog = document.getElementById("modal-filter");
  function validaModal() {
    var inputOcultos = true;
    var entryDataPort = 0;
    var entryDataProtocol = 0;

    for (var i = 0; i < 15; i++) {
      if ($(elementosOcultos[i]).css("display") !== "none") {
        var nombreElemento = $(elementosOcultos[i]).attr("id");
        inputOcultos = false;
        if (nombreElemento.startsWith("port")) {
          entryDataPort++;
        } else if (nombreElemento.startsWith("protocol")) {
          entryDataProtocol++;
        }
        // break;
      }
    }

    var filtrosOcultos = true;
    for (var j = 15; j < 19; j++) {
      if ($(elementosOcultos[j]).css("display") !== "none") {
        filtrosOcultos = false;
        break;
      }
    }

    if (
      inputOcultos ||
      (!inputOcultos &&
        filtrosOcultos &&
        entryDataPort < 2 &&
        entryDataProtocol < 2)
    ) {
      modalDialog.style.setProperty("max-width", "625px", "important");
    } else {
      modalDialog.style.setProperty("max-width", "1125px", "important");
    }
  }

  function cleanDisabledInput(elements) {
    $.each(elements, function (key, value) {
      value.val("");
      value.tagsinput("removeAll");
      value.prop("disabled", true);
    });
  }

  function disabledBtn(element) {
    element.prop("disabled", true);
  }

  function cleanDisabledSelect(elements) {
    $.each(elements, function (key, value) {
      value.prop("selectedIndex", 0);
    });
  }

  function cleanDisabledMultiselect(elements) {
    $.each(elements, function (key, value) {
      value.val([]);
      value.prop("disabled", true);
      value.selectpicker("refresh");
    });
  }

  function ocultarCampos(campos) {
    $.each(campos, function (key, value) {
      value.css("display", "none");
    });
  }

  /* Habilitar campos para el filtro */
  selectFilterType.on("change", function () {
    var selectedType = selectFilterType.val();

    cleanDisabledInput({
      generalIp: generalIp,
      ipDest: ipDest,
      ipAddr: ipAddr,
      generalDomain: generalDomain,
      domainDst: domainDst,
      generalPort: generalPort,
      portDst: portDst,
      portSrc: portSrc,
    });
    cleanDisabledMultiselect({
      generalContent: generalContent,
      contentDst: contentDst,
      generalProtocolRed: generalProtocolRed,
      protocolRedSrc: protocolRedSrc,
      protocolRedDst: protocolRedDst,
    });
    cleanDisabledSelect({
      logicOperatorIp: logicOperatorIp,
      protocol: protocol,
      filterIp: filterIp,
      filterDomain: filterDomain,
      filterContent: filterContent,
      filterMac: filterMac,
      filterPort: filterPort,
      filterProtocolRed: filterProtocolRed,
      filterOperatorMacPort: filterOperatorMacPort,
      filterOperatorProtoRedProto: filterOperatorProtoRedProto,
    });
    ocultarCampos({
      ipsContainer: ipsContainer,
      contentsContainer: contentsContainer,
      domainsContainer: domainsContainer,
      protoportsContainer: protoportsContainer,
      portsContainer: portsContainer,
      protocolsContainer: protocolsContainer,

      /* IPS */
      generalIpContainer: generalIpContainer,
      filterOperatorIp: filterOperatorIp,
      ipSrcContainer: ipSrcContainer,
      ipDstContainer: ipDstContainer,

      /* DOMINIOS */
      generalDomainContainer: generalDomainContainer,
      domainDstContainer: domainDstContainer,

      /* CONTENIDO */
      generalContentContainer: generalContentContainer,
      contentDstContainer: contentDstContainer,

      /* PUERTOS */
      generalPortContainer: generalPortContainer,
      portSrcContainer: portSrcContainer,
      portDstContainer: portDstContainer,

      /* PROTOCOL PUERTO */
      generalProtocolRedContainer: generalProtocolRedContainer,
      protocolRedSrcContainer: protocolRedSrcContainer,
      protocolRedDstContainer: protocolRedDstContainer,
    });
    if (selectedType === "content") {
      contentsContainer.css("display", "flex");
    } else if (selectedType === "domain") {
      domainsContainer.css("display", "flex");
    } else if (selectedType === "ipAndport") {
      ipsContainer.css("display", "flex");
      portsContainer.css("display", "flex");
      protoportsContainer.css("display", "flex");
      protocolsContainer.css("display", "flex");
    }
    validaModal();
    if (validarSelectsVacios()) {
      btnCreateFilter.prop("disabled", true);
    } else {
      btnCreateFilter.prop("disabled", false);
    }
  });

  function validarSelectsVacios() {
    var filterIp = $("#selectFilterIp").val();
    var filterDomain = $("#selectFilterDomain").val();
    var filterContent = $("#selectFilterContent").val();
    var filterMac = $("#selectFilterMac").val();
    var filterPort = $("#selectFilterPort").val();
    var filterProtocolRed = $("#selectFilterProtocolRed").val();

    return (
      !filterIp &&
      !filterDomain &&
      !filterContent &&
      !filterMac &&
      !filterPort &&
      !filterProtocolRed
    );
  }

  /* Verifica el cambio que se hace con el select */
  filterIp.on("change", function () {
    disabledBtn(btnCreateFilter);
    cleanDisabledInput({
      generalIp: generalIp,
      ipDest: ipDest,
      ipAddr: ipAddr,
    });
    cleanDisabledSelect({
      logicOperatorIp: logicOperatorIp,
    });
    ocultarCampos({
      generalIpContainer: generalIpContainer,
      filterOperatorIp: filterOperatorIp,
      ipSrcContainer: ipSrcContainer,
      ipDstContainer: ipDstContainer,
    });

    var selecteFilterIp = filterIp.val();
    if (selecteFilterIp === "IP de Origen") {
      ipAddr.prop("disabled", false);

      ipSrcContainer.css("display", "block");
    } else if (selecteFilterIp === "IP de Destino") {
      ipDest.prop("disabled", false);

      ipDstContainer.css("display", "block");
    } else if (selecteFilterIp === "IP de Origen y Destino") {
      ipAddr.prop("disabled", false);
      ipDest.prop("disabled", false);

      filterOperatorIp.css("display", "block");
      ipDstContainer.css("display", "block");
      ipSrcContainer.css("display", "block");
    } else if (selecteFilterIp === "IP General (Origen y Destino)") {
      generalIp.prop("disabled", false);

      generalIpContainer.css("display", "block");
    }
    validaModal();

    if (validarSelectsVacios()) {
      btnCreateFilter.prop("disabled", true);
    } else {
      btnCreateFilter.prop("disabled", false);
    }
  });

  filterDomain.on("change", function () {
    cleanDisabledInput({
      generalDomain: generalDomain,
      domainDst: domainDst,
    });
    ocultarCampos({
      generalDomainContainer: generalDomainContainer,
      domainDstContainer: domainDstContainer,
    });

    var selecteFilterDomain = filterDomain.val();
    if (selecteFilterDomain === "Dominio de Destino") {
      domainDst.prop("disabled", false);

      domainDstContainer.css("display", "block");
    } else if (selecteFilterDomain === "Dominio General (Origen y Destino)") {
      generalDomain.prop("disabled", false);

      generalDomainContainer.css("display", "block");
    }
    validaModal();

    if (validarSelectsVacios()) {
      btnCreateFilter.prop("disabled", true);
    } else {
      btnCreateFilter.prop("disabled", false);
    }
  });

  filterContent.on("change", function () {
    cleanDisabledMultiselect({
      generalContent: generalContent,
      contentDst: contentDst,
    });
    ocultarCampos({
      generalContentContainer: generalContentContainer,
      contentDstContainer: contentDstContainer,
    });
    var selecteFilterContent = filterContent.val();

    if (selecteFilterContent === "Contenido de Destino") {
      contentDst.prop("disabled", false);
      contentDst.selectpicker("refresh");

      contentDstContainer.css("display", "block");
    } else if (
      selecteFilterContent === "Contenido General (Origen y Destino)"
    ) {
      generalContent.prop("disabled", false);
      generalContent.selectpicker("refresh");

      generalContentContainer.css("display", "block");
    }
    validaModal();

    if (validarSelectsVacios()) {
      btnCreateFilter.prop("disabled", true);
    } else {
      btnCreateFilter.prop("disabled", false);
    }
  });

  filterMac.on("change", function () {
    cleanDisabledInput({
      macDest: macDest,
      macAddr: macAddr,
    });
    cleanDisabledSelect({
      logicOperatorMac: logicOperatorMac,
    });
    ocultarCampos({
      filterOperatorMac: filterOperatorMac,
      macSrcContainer: macSrcContainer,
      macDstContainer: macDstContainer,
    });
    var selecteFilterMac = filterMac.val();
    if (selecteFilterMac === "Solo MAC de Origen") {
      macAddr.prop("disabled", false);

      macSrcContainer.css("display", "block");
    } else if (selecteFilterMac === "Solo MAC de Destino") {
      macAddr.val("");
      $("#macaddr").tagsinput("removeAll");
      macAddr.prop("disabled", false);

      macDstContainer.css("display", "block");
    } else if (selecteFilterMac === "MAC de Origen y Destino") {
      macAddr.prop("disabled", false);
      macDest.prop("disabled", false);

      filterOperatorMac.css("display", "block");
      macSrcContainer.css("display", "block");
      macDstContainer.css("display", "block");
    }
    validaModal();

    if (validarSelectsVacios()) {
      btnCreateFilter.prop("disabled", true);
    } else {
      btnCreateFilter.prop("disabled", false);
    }
  });

  filterPort.on("change", function () {
    cleanDisabledInput({
      generalPort: generalPort,
      portDst: portDst,
      portSrc: portSrc,
    });
    ocultarCampos({
      generalPortContainer: generalPortContainer,
      portSrcContainer: portSrcContainer,
      portDstContainer: portDstContainer,
    });
    var selecteFilterPort = filterPort.val();
    if (selecteFilterPort === "Puerto de Origen") {
      portSrc.prop("disabled", false);

      portSrcContainer.css("display", "block");
    } else if (selecteFilterPort === "Puerto de Destino") {
      portDst.prop("disabled", false);

      portDstContainer.css("display", "block");
    } else if (selecteFilterPort === "Puertos de Origen y Destino") {
      portSrc.prop("disabled", false);
      portDst.prop("disabled", false);

      portSrcContainer.css("display", "block");
      portDstContainer.css("display", "block");
    } else if (selecteFilterPort === "Puerto General (Origen y Destino)") {
      generalPort.prop("disabled", false);

      generalPortContainer.css("display", "block");
    }
    validaModal();

    if (validarSelectsVacios()) {
      btnCreateFilter.prop("disabled", true);
    } else {
      btnCreateFilter.prop("disabled", false);
    }
  });

  filterProtocolRed.on("change", function () {
    cleanDisabledMultiselect({
      generalProtocolRed: generalProtocolRed,
      protocolRedSrc: protocolRedSrc,
      protocolRedDst: protocolRedDst,
    });
    ocultarCampos({
      generalProtocolRedContainer: generalProtocolRedContainer,
      protocolRedSrcContainer: protocolRedSrcContainer,
      protocolRedDstContainer: protocolRedDstContainer,
    });
    var selecteFilterProtocolRed = filterProtocolRed.val();

    if (selecteFilterProtocolRed === "Protocolo de Red de Origen") {
      protocolRedSrc.prop("disabled", false);
      protocolRedSrc.selectpicker("refresh");

      protocolRedSrcContainer.css("display", "block");
    } else if (selecteFilterProtocolRed === "Protocolo de Red de Destino") {
      protocolRedDst.prop("disabled", false);
      protocolRedDst.selectpicker("refresh");

      protocolRedDstContainer.css("display", "block");
    } else if (
      selecteFilterProtocolRed === "Protocolo de Red de Origen y Destino"
    ) {
      protocolRedSrc.prop("disabled", false);
      protocolRedDst.prop("disabled", false);
      protocolRedSrc.selectpicker("refresh");
      protocolRedDst.selectpicker("refresh");

      protocolRedSrcContainer.css("display", "block");
      protocolRedDstContainer.css("display", "block");
    } else if (
      selecteFilterProtocolRed === "Protocolo de Red General (Origen y Destino)"
    ) {
      generalProtocolRed.prop("disabled", false);

      generalProtocolRed.selectpicker("refresh");
      generalProtocolRedContainer.css("display", "block");
    }
    validaModal();

    if (validarSelectsVacios()) {
      btnCreateFilter.prop("disabled", true);
    } else {
      btnCreateFilter.prop("disabled", false);
    }
  });

  /* Verifica Entrada de Texto en el Input */
  $(".ips").on("input change keypress", function () {
    if (
      ipAddr.val().trim() !== "" ||
      ipDest.val().trim() !== "" ||
      generalIp.val().trim() !== "" ||
      macAddr.val().trim() !== "" ||
      macDest.val().trim() !== ""
    ) {
      filterOperatorMacPort.css("display", "block");
    } else {
      logicOperatorMacPort.prop("selectedIndex", 0);
      filterOperatorMacPort.css("display", "none");
    }
  });

  $(".ports").on("input change keypress", function (e) {
    if (
      portSrc.val().trim() !== "" ||
      portDst.val().trim() !== "" ||
      generalPort.val().trim() !== "" ||
      !validarMultiselectVacio(protocolRedSrc) ||
      !validarMultiselectVacio(protocolRedDst) ||
      !validarMultiselectVacio(generalProtocolRed)
    ) {
      filterOperatorProtoRedProto.css("display", "block");
    } else {
      logicOperatorProtoRedProto.prop("selectedIndex", 0);
      filterOperatorProtoRedProto.css("display", "none");
    }
  });

  function showLoading() {
    $("#loading-overlay").css("display", "flex");
    $("body").addClass("no-scroll");
  }

  function hideLoading() {
    $("#loading-overlay").css("display", "none");
    $("body").removeClass("no-scroll");
  }

  $packetTable.bootstrapTable({});

  $("#clean-data").click(function () {
    sessionStorage.removeItem("countPackets");
  });

  $(".cleanDataTable").click(function () {
    sessionStorage.removeItem("datosTabla");
    sessionStorage.removeItem("countPackets");

    alertMessage("Se han limpiado los datos de tráfico correctamente.");
  });

  /* Aplicar el fitro para los paquetes */
  $("#formFilter").submit(function (event) {
    event.preventDefault();

    if (
      mostrarAlerta(filterName, "Asignar un nombre al filtro.") ||
      mostrarAlertaSelect(selectFilterType, "Seleccionar un tipo de filtro.") ||
      mostrarAlerta(ipAddr, "El campo de dirección IP es requerido.") ||
      mostrarAlerta(domainDst, "El campo de dominio es requerido.") ||
      mostrarAlerta(generalDomain, "El campo de dominio es requerido.") ||
      validarSelectFilter(
        ipAddr,
        ipDest,
        logicOperatorIp,
        "Seleccione como se relizara la comparacion entre IPs"
      ) ||
      mostrarAlerta(
        ipDest,
        "El campo de dirección IP de destino es requerido."
      ) ||
      mostrarAlerta(
        generalIp,
        "El campo de dirección IP general es requerido."
      ) ||
      mostrarAlertaSelect(
        contentDst,
        "El campo de contenido de destino es requerido."
      ) ||
      mostrarAlertaSelect(
        generalContent,
        "El campo de contenido es requerido."
      ) ||
      mostrarAlerta(macAddr, "El campo de dirección MAC es requerido.") ||
      validarSelectFilter(
        macAddr,
        macDest,
        logicOperatorMac,
        "Seleccione como se relizara la comparacion entre MACS"
      ) ||
      mostrarAlerta(
        macDest,
        "El campo de dirección MAC de destino es requerido."
      ) ||
      validarSelectOne(
        filterOperatorMacPort,
        logicOperatorMacPort,
        filterPort,
        filterProtocolRed,
        protocol,
        "Debe asignar un valor al siguiente elemento 1"
      ) ||
      mostrarAlerta(portSrc, "El campo de puerto de origen es requerido.") ||
      mostrarAlerta(portDst, "El campo de puerto de destino es requerido.") ||
      mostrarAlerta(generalPort, "El campo de puerto general es requerido.") ||
      mostrarAlertaSelect(
        protocolRedSrc,
        "El campo de protocolo de red de origen es requerido."
      ) ||
      mostrarAlertaSelect(
        protocolRedDst,
        "El campo de protocolo de red de destino es requerido."
      ) ||
      mostrarAlertaSelect(
        generalProtocolRed,
        "El campo de protocolo de red general es requerido."
      ) ||
      validarSelectTwo(
        filterOperatorProtoRedProto,
        logicOperatorProtoRedProto,
        protocol,
        "Debe asignar un valor al siguiente elemento 2"
      )
    ) {
      return;
    }

    var formData = $(this).serialize();

    btnCreateFilter.prop("disabled", true);

    showLoading();

    $.ajax({
      type: "POST",
      url: "/save_filter",
      data: formData,
      success: function (response) {
        //$("#modal-filter").find(".close").trigger("click");
        if (response.error) {
          btnCreateFilter.prop("disabled", false);
          alertMessage(response.error, "danger");
        } else {
          alertMessage(response.message, "success");
        }
      },
      error: function (xhr, status, error) {
        btnCreateFilter.prop("disabled", false);

        alertMessage(error, "danger");
      },
    });
  });

  $(".deletefilterConfirm").on("click", function (event) {
    console.log("entru");
    event.preventDefault();

    var btn_delete = $(this);
    btn_delete.prop("disabled", true);

    showLoading();

    $.ajax({
      type: "GET",
      url: "/eliminar_filtro",
      data: { id_filtro: filter_id.val() },
      success: function (response) {
        if (response.error) {
          btn_delete.prop("disabled", false);
          alertMessage(response.error, "danger");
        } else {
          alertMessage(response.message, "success");
        }
      },
      error: function (textStatus, errorThrown) {
        btn_delete.prop("disabled", false);

        console.error("Error en la solicitud AJAX:", textStatus, errorThrown);
        alertMessage("Ocurrió un error al procesar la solicitud.", "danger");
      },
    });
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
        hideLoading();
        location.reload();
      } else {
        hideLoading();
      }
      $(".alert-message-container").hide("medium");
    }, 2000);
  }

  function validarMultiselectVacio(elemento) {
    return elemento.val() === null || elemento.val().length === 0;
  }

  function validarSelectOne(
    contenedor,
    elemento1,
    elemento2,
    elemento3,
    elemento4,
    mensaje
  ) {
    if (
      (contenedor.css("display") !== "none" &&
        validarMultiselectVacio(elemento1) &&
        (!validarMultiselectVacio(elemento2) ||
          !validarMultiselectVacio(elemento3) ||
          !validarMultiselectVacio(elemento4))) ||
      (contenedor.css("display") !== "none" &&
        !validarMultiselectVacio(elemento1) &&
        validarMultiselectVacio(elemento2) &&
        validarMultiselectVacio(elemento3) &&
        validarMultiselectVacio(elemento4))
    ) {
      $("#liveToast .toast-body").text(mensaje);
      $("#liveToast").toast("show");
      return true;
    }
    return false;
  }

  function validarSelectTwo(contenedor, elemento1, elemento2, mensaje) {
    if (
      contenedor.css("display") !== "none" &&
      ((!validarMultiselectVacio(elemento1) &&
        validarMultiselectVacio(elemento2)) ||
        (validarMultiselectVacio(elemento1) &&
          !validarMultiselectVacio(elemento2)))
    ) {
      $("#liveToast .toast-body").text(mensaje);
      $("#liveToast").toast("show");
      return true;
    }
    return false;
  }

  function validarSelectFilter(elemento1, elemento2, select, mensaje) {
    if (
      !elemento1.prop("disabled") &&
      !elemento2.prop("disabled") &&
      validarMultiselectVacio(select)
    ) {
      $("#liveToast .toast-body").text(mensaje);
      $("#liveToast").toast("show");
      return true;
    }
    return false;
  }

  function validarCampo(elemento) {
    return !elemento.prop("disabled") && elemento.val().trim() === "";
  }

  function validarCampoSelect(elemento) {
    return !elemento.prop("disabled") && validarMultiselectVacio(elemento);
  }

  function mostrarAlertaSelect(elemento, mensaje) {
    if (validarCampoSelect(elemento)) {
      $("#liveToast .toast-body").text(mensaje);
      $("#liveToast").toast("show");
      return true;
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
});

$(".delete-btn").click(function () {
  const filterId = $(this).data("id");
  $("#ruleNumberInput").val(filterId);
});

function formatoNombreRegla(input) {
  input.value = input.value.replace(/-/g, "");
}
