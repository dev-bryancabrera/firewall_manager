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
  var maxConnectionsType = $("#max-connection-type");
  var maxConnections = $("#max-connections");
  var userName = $("#user-name");
  var accessType = $("#access-type");
  var databaseType = $("#database-type");
  var tablesSelect = $("#tables-type");

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

  // function populateSelect(elementId, max) {
  //   const select = document.getElementById(elementId);
  //   for (let i = 0; i <= max; i++) {
  //     const option = document.createElement("option");
  //     option.value = i < 10 ? `0${i}` : i; // Asegura formato de dos dígitos
  //     option.text = option.value;
  //     select.appendChild(option);
  //   }
  //   // Actualiza selectpicker después de agregar opciones
  //   $(select).selectpicker("refresh");
  // }

  // // Poblar las horas, minutos y segundos
  // populateSelect("hours", 23);
  // populateSelect("minutes", 59);
  // populateSelect("seconds", 59);

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
      maxConnectionsType: maxConnectionsType,
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
    });
    cleanDisabledMultiselect({
      accessType: accessType,
      maxConnectionsType: maxConnectionsType,
    });

    var selectedOption = restrictionMysql.val();

    if (selectedOption === "limitar conexiones") {
      maxConnectionsType.prop("disabled", false);

      maxConnectionsType.selectpicker("refresh");
    } else if (selectedOption === "restringir acceso a base de datos") {
      userName.prop("disabled", false);
      accessType.prop("disabled", false);

      accessType.selectpicker("refresh");
    }
  });

  maxConnectionsType.on("change", function () {
    cleanDisabledInput({
      maxConnections: maxConnections,
      userName: userName,
    });

    var selectedOption = maxConnectionsType.val();

    if (selectedOption === "todos los usuarios") {
      maxConnections.prop("disabled", false);
    } else if (selectedOption === "usuarios especificos") {
      userName.prop("disabled", false);
      maxConnections.prop("disabled", false);
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

    if (selectedOption === "limitar comandos") {
      commands.prop("disabled", false);
    } else if (selectedOption === "limitar uso de red") {
      networkUsage.prop("disabled", false);
    } else if (selectedOption === "limitar duracion de la sesion") {
      sessionDuration.prop("disabled", false);
    } else if (selectedOption === "duracion de procesos") {
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

    if (selectedOption === "subir archivos") {
      uploadDirectory.prop("disabled", false);
      fileTypesFtp.prop("disabled", false);
    } else if (selectedOption === "descargar archivos") {
      downloadDirectory.prop("disabled", false);
      fileTypesFtp.prop("disabled", false);
    } else if (selectedOption === "transferencia maxima de bytes") {
      maxTransferSize.prop("disabled", false);
    }
  });

  // Ventana de carga
  function showLoading() {
    $("#loading-overlay").css("display", "flex");
    $("body").addClass("no-scroll");
  }

  function hideLoading() {
    $("#loading-overlay").css("display", "none");
    $("body").removeClass("no-scroll");
  }

  databaseType.change(function () {
    var databaseSelected = $(this).val();

    $.ajax({
      url: "/get_tables",
      type: "GET",
      data: { database: databaseSelected },
      success: function (response) {
        tablesSelect.empty(); // Limpiar las opciones anteriores

        tablesSelect.append(
          $("<option>").val("all-tables").text("Aplicar a todas las tablas")
        );

        // Iterar sobre las tablas recibidas en la respuesta y agregar opciones al select
        $.each(response, function (index, value) {
          var option = $("<option>").val(value).text(value);
          tablesSelect.append(option);
        });

        // Refrescar el selectpicker para que se reflejen los cambios
        tablesSelect.selectpicker("refresh");
      },
      error: function (xhr, status, error) {
        console.error(error);
      },
    });
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
      mostrarAlertaSelect(
        serviceType,
        "Seleccionar un servicio para aplicar la restriccion."
      ) ||
      mostrarAlertaSelect(actionType, "Seleccione un tipo de acción.") ||
      validarSelectContainer(
        mysqlContainer,
        restrictionMysql,
        "Asignar una restricción MySQL."
      ) ||
      mostrarAlerta(
        maxConnections,
        "Asignar un valor a las conexiones máximas."
      ) ||
      mostrarAlerta(userName, "Asignar un nombre de usuario MySQL.") ||
      mostrarAlertaSelect(accessType, "Asignar un tipo de acceso MySQL.") ||
      mostrarAlertaSelect(
        maxConnectionsType,
        "Asignar un valor para la limitacion de conexiones."
      ) ||
      validarSelectContainer(
        sshContainer,
        actionSshType,
        "Seleccione un tipo de acción SSH."
      ) ||
      // mostrarAlerta(commands, "Asignar comandos SSH.") ||
      mostrarAlerta(networkUsage, "Asignar un uso de red para SSH.") ||
      mostrarAlerta(sessionDuration, "Asignar una duración de sesión SSH.") ||
      // mostrarAlerta(maxDurationSsh, "Asignar una duración máxima para SSH.") ||
      validarSelectContainer(
        ftpContainer,
        actionFtpType,
        "Seleccione un tipo de acción FTP."
      ) ||
      mostrarAlerta(uploadDirectory, "Asignar un directorio de carga FTP.") ||
      mostrarAlerta(fileTypesFtp, "Asignar tipos de archivos FTP.") ||
      mostrarAlerta(
        downloadDirectory,
        "Asignar un directorio de descarga FTP."
      ) ||
      mostrarAlerta(
        maxTransferSize,
        "Asignar un tamaño máximo de transferencia FTP."
      )
    ) {
      return;
    }

    // Crear un objeto con los datos que deseas enviar
    var formData = $(this).serialize();

    btnCreateAutomation.prop("disabled", true);

    showLoading();

    $.ajax({
      type: "POST",
      url: "/add_service_automation",
      data: formData,
      success: function (response) {
        //$("#modal-filter").find(".close").trigger("click");

        if (response.error) {
          btnCreateAutomation.prop("disabled", false);
          alertMessage(response.error, "danger");
        } else {
          alertMessage(response.message, "success");
        }
      },
      error: function (xhr, status, error) {
        btnCreateAutomation.prop("disabled", false);
        console.error("Respuesta del servidor:", xhr.responseText);
        alertMessage(error, "danger");
      },
    });
  });

  $('button[id^="btn-automatizacion"]').on("click", function (event) {
    event.preventDefault();

    var automatizacionId = $(this).attr("id").split("-", 3)[2];

    var btn_status = $(this);
    btn_status.prop("disabled", true);

    showLoading();

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
        btn_status.prop("disabled", false);

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

    showLoading();

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
        btn_status.prop("disabled", false);

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
    }, 1500);
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
