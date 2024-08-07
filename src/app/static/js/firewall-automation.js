$(document).ready(function () {
  // Variables
  var $automationForm = $("#form-automation");
  var $automationTable = $("#automation-table");

  var automationName = $("#automation-name");
  var automationType = $("#automation-type");
  var community = $("#community");
  var automationAction = $("#automation-action");
  var domain = $("#domain");
  var contentType = $("#content-type");
  var domainPlataform = $("#domain-plataform");
  var intialTime = $("#initial-time");
  var finalTime = $("#final-time");
  var daySchedule = $("#daypicker");

  var btnCreateAutomation = $("#btn-create-automation");

  var communityList = $("#community-list");

  contentType.prop("disabled", true);
  contentType.selectpicker("refresh");
  domainPlataform.prop("disabled", true);
  domainPlataform.selectpicker("refresh");

  domain.prop("disabled", true);

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

  // Ventana de carga
  function showLoading() {
    $("#loading-overlay").css("display", "flex");
    $("body").addClass("no-scroll");
  }

  function hideLoading() {
    $("#loading-overlay").css("display", "none");
    $("body").removeClass("no-scroll");
  }

  /* Agregar los dominios personalizado de cada plataforma */
  contentType.change(function () {
    var plataformaSeleccionada = $(this).val();

    $.ajax({
      url: "/domain_plataform",
      type: "GET",
      data: { key_plataform: plataformaSeleccionada },
      success: function (response) {
        domainPlataform.empty();

        // Iterar sobre los datos en la respuesta y agregar opciones al select
        $.each(response, function (index, value) {
          // Crear una nueva opción
          var option = $("<option>").val(value).text(value);

          domainPlataform.append(option);
        });

        // Agregar la opción "Añadir nuevo..." al final
        var addNewOption = $("<option>")
          .val("add_new")
          .html("&#x2795; Añadir dominio");
        domainPlataform.append(addNewOption);

        domainPlataform.find("option").slice(0, -1).prop("selected", true);

        domainPlataform.selectpicker("refresh");
      },
      error: function (xhr, status, error) {
        console.error(error);
      },
    });
  });

  domainPlataform.on(
    "changed.bs.select",
    function (e, clickedIndex, isSelected, previousValue) {
      var selectedValue = $(this).find("option").eq(clickedIndex).val();

      if (selectedValue === "add_new") {
        // Prompt user for new item
        var newItem = prompt("Ingrese el nuevo dominio:");

        if (newItem) {
          // Remove "Añadir dominio" option
          $(this).find('option[value="add_new"]').remove();

          // Add the new item to the select options
          $(this).append(new Option(newItem, newItem, true, true));

          // Add "Añadir dominio" option at the end
          var addNewOption = $("<option>")
            .val("add_new")
            .html("&#x2795; Añadir dominio");
          $(this).append(addNewOption);

          $(this).selectpicker("refresh");
        }

        // Unselect the "Añadir dominio" option
        $(this).find('option[value="add_new"]').prop("selected", false);
        $(this).selectpicker("refresh");
      }
    }
  );

  /* domainPlataform.on(
    "changed.bs.select",
    function (e, clickedIndex, isSelected, previousValue) {
      var selectedValue = $(this).find("option").eq(clickedIndex).val();

      if (selectedValue === "add_new") {
        // Mostrar el input para ingresar el nuevo dominio
        $("#new-domain-input").show();

        // Manejar clic en el botón para añadir el nuevo dominio
        $("#add-domain-btn").on("click", function () {
          console.log("fsdfdsfsd");
          var newItem = $("#new-domain").val();
          if (newItem) {
            // Remove "Añadir dominio" option
            $(this).find('option[value="add_new"]').remove();

            // Add the new item to the select options
            $(this).append(new Option(newItem, newItem, true, true));

            // Add "Añadir dominio" option at the end
            var addNewOption = $("<option>")
              .val("add_new")
              .html("&#x2795; Añadir dominio");
            $(this).append(addNewOption);

            $(this).selectpicker("refresh");
          }

          // Unselect the "Añadir dominio" option
          $(this).find('option[value="add_new"]').prop("selected", false);
          $(this).selectpicker("refresh");
          // Ocultar el input para ingresar el nuevo dominio
          $("#new-domain-input").hide();
          // Desmarcar la opción "Añadir dominio"
          $(this).selectpicker("deselectAll");
        });
      }
    }
  ); */

  function cleanDisabledInput(elements) {
    $.each(elements, function (key, value) {
      value.val("");
      value.tagsinput("removeAll");
      value.prop("disabled", true);
    });
  }

  function cleanDisabledMultiselect(elements) {
    $.each(elements, function (key, value) {
      value.val([]);
      value.prop("disabled", true);
      value.selectpicker("refresh");
    });
  }

  automationType.on("change", function () {
    cleanDisabledInput({
      domain: domain,
    });
    cleanDisabledMultiselect({
      contentType: contentType,
      domainPlataform: domainPlataform,
    });
    var selectedOption = automationType.val();

    if (selectedOption === "contenido") {
      contentType.prop("disabled", false);
      domainPlataform.prop("disabled", false);

      contentType.selectpicker("refresh");
      domainPlataform.selectpicker("refresh");
    } else if (selectedOption === "dominio") {
      domain.prop("disabled", false);
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
      mostrarAlertaSelect(
        automationType,
        "Seleccionar un tipo de restriccion."
      ) ||
      mostrarAlertaSelect(contentType, "Selecciona un tipo de contenido.") ||
      mostrarAlertaSelect(
        domainPlataform,
        "Selecciona el o los dominos a restringir."
      ) ||
      mostrarAlerta(domain, "Asigne un valor del dominio a restringir.") ||
      mostrarAlerta(daySchedule, "Asigne el o los dias a restringir.") ||
      mostrarAlerta(
        intialTime,
        "Asigne una hora de inicio a la restriccion."
      ) ||
      mostrarAlerta(finalTime, "Asigne una hora de fin a la restriccion.")
    ) {
      return;
    }

    var name = automationName.val();
    var type = automationType.val();
    var csrfToken = $("#csrf_token").val();
    var horario =
      daySchedule.val() + "  " + intialTime.val() + " - " + finalTime.val();

    if (isNaN(commandId)) {
      commandId = community.val();
    }

    // Crear un objeto con los datos que deseas enviar
    var formData = {
      automationName: name,
      automationType: type,
      automationAction: automationAction.val(),
      domain: domain.val(),
      contentType: contentType.val(),
      domainPlataform: domainPlataform.val(),
      idComunnity: commandId,
      horario: horario,
    };

    btnCreateAutomation.prop("disabled", true);

    showLoading();

    $.ajax({
      type: "POST",
      url: "/add_automation",
      data: $.param(formData, true),
      headers: {
        "X-CSRFToken": csrfToken,
      },
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
        console.error("Respuesta del servidor:", xhr.responseText);
        btnCreateAutomation.prop("disabled", false);
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
