$(document).ready(function () {
  // Variables
  var $automationForm = $("#form-automation");
  var $automationTable = $("#automation-table");

  var automationName = $("#automation-name");
  var community = $("#community");

  // Servicios a restringir
  var serviceType = $("#service-type");
  var actionType = $("#action-type");

  // Contenedores
  var mysqlContainer = $("#mysql-container");
  var sshContainer = $("#ssh-container");
  var ftpContainer = $("#ftp-container");
  var apacheContainer = $("#apache-container");

  // MySQL
  var restrictionMysql = $("#restricion-msyql");
  var maxConnections = $("#max-connections");
  var userName = $("#user-name");
  var accessType = $("#access-type");
  var maxDurationMysql = $("#mysql-max-duration");

  // SSH
  var actionSshType = $("#actionssh-type");
  var commands = $("#commands");
  var networkUsage = $("#network-usage");
  var sessionDuration = $("#session-duration");
  var maxDurationSsh = $("#ssh-max-duration");

  // FTP
  var actionFtpType = $("#actionftp-type");
  var uploadDirectory = $("#upload-directory");
  var fileTypesFtp = $("#file-types");
  var downloadDirectory = $("#download-directory");
  var deleteDirectory = $("#delete-directory");
  var maxTransferSize = $("#max-transfer-size");

  // Apache
  var actionApacheType = $("#actionapache-type");

  maxConnections.prop("disabled", true);
  userName.prop("disabled", true);
  maxDurationMysql.prop("disabled", true);
  commands.prop("disabled", true);
  networkUsage.prop("disabled", true);
  sessionDuration.prop("disabled", true);
  maxDurationSsh.prop("disabled", true);
  uploadDirectory.prop("disabled", true);
  fileTypesFtp.prop("disabled", true);
  downloadDirectory.prop("disabled", true);
  deleteDirectory.prop("disabled", true);
  maxTransferSize.prop("disabled", true);

  // Configurar horario de restriccion
  var intialTime = $("#initial-time");
  var finalTime = $("#final-time");
  var daySchedule = $("#daypicker");

  var btnCreateAutomation = $("#btn-create-automation");

  var communityList = $("#community-list");

  /* Obtener el parametro de filtro para cargar los datos */
  var url = window.location.pathname; // Obtener la parte de la ruta de la URL
  var parts = url.split("/"); // Dividir la URL por las barras
  var baseUrl = url.split("/firewall_automation")[0];
  var commandEncodedId = parts[parts.length - 1]; // Obtener el valor del parámetro de ruta "id"
  var commandId = decodeURIComponent(commandEncodedId); // Decodificar el valor

  if (isNaN(commandId)) {
    communityList.css("display", "flex");
  }

  /* Configuracion para el timer */
  var defaults = {
    calendarWeeks: true,
    showClear: true,
    showClose: true,
    allowInputToggle: true,
    useCurrent: false,
    ignoreReadonly: true,
    // minDate: new Date(),

    toolbarPlacement: "top",
    locale: "nl",
    icons: {
      time: "fa fa-clock-o",
      date: "fa fa-calendar",
      up: "fa fa-angle-up",
      down: "fa fa-angle-down",
      previous: "fa fa-angle-left",
      next: "fa fa-angle-right",
      today: "fa fa-dot-circle-o",
      clear: "fa fa-trash",
      close: "fa fa-times",
    },
  };

  var optionsTime = $.extend({}, defaults, { format: "HH:mm" });

  $(".timepicker").datetimepicker(optionsTime);

  /* Manejar selector de dias */
  function togglePopup() {
    const popup = $("#daysPopup");
    if (popup.css("display") === "none") {
      popup.css("display", "flex");
    } else {
      popup.css("display", "none");
    }
  }

  function updateInput() {
    const selectedDays = [];
    $(".weekday:checked").each(function () {
      selectedDays.push($(this).next("label").text());
    });
    $("#daypicker").val(selectedDays.join(", "));
  }

  $("#daypicker, #icon-day").on("click", togglePopup);
  $(".weekday").on("change", updateInput);

  $(document).on("click", function (event) {
    if (!$(event.target).closest("#daypicker, #icon-day, #daysPopup").length) {
      $("#daysPopup").hide();
    }
  });

  function cleanDisabledInput(elements) {
    $.each(elements, function (key, value) {
      value.val("");
      // value.tagsinput("removeAll");
      value.prop("disabled", true);
    });
  }

  function cleanMultiselect(elements) {
    $.each(elements, function (key, value) {
      value.val([]);
      value.selectpicker("refresh");
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

  serviceType.on("change", function () {
    cleanDisabledInput({
      maxConnections: maxConnections,
      userName: userName,
      maxDurationMysql: maxDurationMysql,
      commands: commands,
      networkUsage: networkUsage,
      sessionDuration: sessionDuration,
      maxDurationSsh: maxDurationSsh,
      uploadDirectory: uploadDirectory,
      fileTypesFtp: fileTypesFtp,
      downloadDirectory: downloadDirectory,
      deleteDirectory: deleteDirectory,
      maxTransferSize: maxTransferSize,
    });
    cleanMultiselect({
      restrictionMysql: restrictionMysql,
      actionSshType: actionSshType,
      actionFtpType: actionFtpType,
    });
    cleanDisabledMultiselect({
      accessType: accessType,
    });
    ocultarCampos({
      mysqlContainer: mysqlContainer,
      sshContainer: sshContainer,
      ftpContainer: ftpContainer,
      apacheContainer: apacheContainer,
    });

    var selectedOption = serviceType.val();

    if (selectedOption === "mysql") {
      mysqlContainer.css("display", "flex");
    } else if (selectedOption === "ssh") {
      sshContainer.css("display", "flex");
    } else if (selectedOption === "ftp") {
      ftpContainer.css("display", "flex");
    } else if (selectedOption === "apache") {
      apacheContainer.css("display", "flex");
    }
  });

  restrictionMysql.on("change", function () {
    cleanDisabledInput({
      maxConnections: maxConnections,
      userName: userName,
      maxDurationMysql: maxDurationMysql,
    });
    cleanDisabledMultiselect({
      accessType: accessType,
    });

    var selectedOption = restrictionMysql.val();

    if (selectedOption === "limit-connections") {
      maxConnections.prop("disabled", false);
    } else if (selectedOption === "restrict-db-access") {
      userName.prop("disabled", false);
      accessType.prop("disabled", false);
      maxDurationMysql.prop("disabled", false);

      accessType.selectpicker("refresh");
    }
  });

  actionSshType.on("change", function () {
    cleanDisabledInput({
      commands: commands,
      networkUsage: networkUsage,
      sessionDuration: sessionDuration,
      maxDurationSsh: maxDurationSsh,
    });

    var selectedOption = actionSshType.val();

    if (selectedOption === "limit-commands") {
      commands.prop("disabled", false);
    } else if (selectedOption === "limit-network-usage") {
      networkUsage.prop("disabled", false);
    } else if (selectedOption === "limit-session-duration") {
      sessionDuration.prop("disabled", false);
    } else if (selectedOption === "process-max-duration") {
      maxDurationSsh.prop("disabled", false);
    }
  });

  ftpContainer.on("change", function () {
    cleanDisabledInput({
      uploadDirectory: uploadDirectory,
      fileTypesFtp: fileTypesFtp,
      downloadDirectory: downloadDirectory,
      // deleteDirectory: deleteDirectory,
      maxTransferSize: maxTransferSize,
    });

    var selectedOption = ftpContainer.val();

    if (selectedOption === "upload-files") {
      uploadDirectory.prop("disabled", false);
      fileTypesFtp.prop("disabled", false);
    } else if (selectedOption === "download-files") {
      downloadDirectory.prop("disabled", false);
      fileTypesFtp.prop("disabled", false);
    } else if (selectedOption === "max-transfer-bytes") {
      maxTransferSize.prop("disabled", false);
    }
  });

  $automationTable.bootstrapTable({});

  $automationForm.submit(function (event) {
    event.preventDefault();

    if (
      mostrarAlerta(automationName, "Asignar un nombre a la automatizacion.") ||
      validarSelectContainer(
        communityList,
        community,
        "Seleccione una comunidad a asignar la automatizacion"
      ) ||
      mostrarAlertaSelect(serviceType, "Seleccionar un tipo de restriccion.")
    ) {
      return;
    }

    // Crear un objeto con los datos que deseas enviar
    var formData = $(this).serialize();

    btnCreateAutomation.prop("disabled", true);

    $.ajax({
      type: "POST",
      url: "/add_service_automation",
      data: formData,
      success: function (response) {
        //$("#modal-filter").find(".close").trigger("click");
        alertMessage(response.message);
      },
      error: function (xhr, status, error) {
        console.error("Respuesta del servidor:", xhr.responseText);
      },
    });
  });

  $('button[id^="btn-automatizacion"]').on("click", function (event) {
    event.preventDefault();

    var automatizacionId = $(this).attr("id").split("-", 3)[2];

    var btn_status = $(this);
    btn_status.prop("disabled", true);

    $.ajax({
      type: "GET",
      url: "/desactivar_automatizacion",
      data: { id: automatizacionId },
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

  $('button[id^="delete-automatizacion"]').on("click", function (event) {
    event.preventDefault();

    var automatizacionId = $(this).attr("id").split("-", 3)[2];

    var btn_status = $(this);
    btn_status.prop("disabled", true);

    $.ajax({
      type: "GET",
      url: "/eliminar_automatizacion",
      data: { id: automatizacionId },
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

  function validarSelectContainer(contenedor, elemento, mensaje) {
    if (
      contenedor.css("display") !== "none" &&
      validarMultiselectVacio(elemento)
    ) {
      $("#liveToast .toast-body").text(mensaje);
      $("#liveToast").toast("show");
      return true;
    }
    return false;
  }

  function alertMessage(response) {
    $(".alert-message-container").show("medium");
    $(".alert-message").text(response);
    setTimeout(function () {
      location.reload();
      $(".alert-message-container").hide("medium");
    }, 2000);
  }

  function validarMultiselectVacio(elemento) {
    return elemento.val() === null || elemento.val().length === 0;
  }

  function mostrarAlerta(elemento, mensaje) {
    if (validarCampo(elemento)) {
      $("#liveToast .toast-body").text(mensaje);
      $("#liveToast").toast("show");
      return true;
    }
    return false;
  }

  function mostrarAlertaSelect(elemento, mensaje) {
    if (validarCampoSelect(elemento)) {
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
});
