$(document).ready(function () {
  // Variables
  var $automationForm = $("#form-automation");
  var $communityTable = $("#community-table");

  var automationName = $("#automation-name");
  var automationType = $("#automation-type");
  var automationAction = $("#automation-action");
  var domain = $("#domain");
  var contentType = $("#content-type");
  var domainPlataform = $("#domain-plataform");
  var intialTime = $("#initial-time");
  var finalTime = $("#final-time");
  var diasHorario = "";
  var daysSelected = $(".weekday");

  var btnCreateComunnity = $("#btn-create-comunnity");
  var btnDeleteCommunity = $("#delete-btn");

  /* localIp.prop("disabled", true);
  localIp.selectpicker("refresh");

  initialIp.prop("disabled", true);
  finalIp.prop("disabled", true); */

  /* Obtener el parametro de filtro para cargar los datos */
  var url = window.location.pathname; // Obtener la parte de la ruta de la URL
  var parts = url.split("/"); // Dividir la URL por las barras
  var baseUrl = url.split("/firewall_automation")[0];
  var commandEncodedId = parts[parts.length - 1]; // Obtener el valor del parámetro de ruta "id"
  var commandId = decodeURIComponent(commandEncodedId); // Decodificar el valor

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

          // Agregar la opción al select
          domainPlataform.append(option);
        });

        // Refrescar la vista del selectpicker
        domainPlataform.selectpicker("refresh");
      },
      error: function (xhr, status, error) {
        // Manejar errores
        console.error(error);
      },
    });
  });

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

  /*  automationType.on("change", function () {
    cleanDisabledInput({
      initialIp: initialIp,
      finalIp: finalIp,
    });
    cleanDisabledMultiselect({
      localIp: localIp,
    });
    var selectedOption = automationType.val();

    if (selectedOption === "red_local") {
      localIp.prop("disabled", false);
      localIp.selectpicker("refresh");
    } else if (selectedOption === "rango_red") {
      initialIp.prop("disabled", false);
      finalIp.prop("disabled", false);
    }
  }); */

  $communityTable.bootstrapTable({});

  /* Seleccionar los dias que se aplicaran la automatizacion */
  daysSelected.change(function () {
    var days = []; // Array para almacenar los días seleccionados

    // Iterar sobre los checkboxes
    daysSelected.each(function () {
      if ($(this).prop("checked")) {
        // Si el checkbox está marcado, agregar el valor al array
        days.push($(this).next("label").text());
      }
    });

    // Convertir el array en una cadena de texto separada por comas
    diasHorario = days.join(", ");
  });

  $automationForm.submit(function (event) {
    event.preventDefault();

    /* if (
      mostrarAlerta(communityName, "Asignar un nombre a la comunidad.") ||
      mostrarAlertaSelect(communityType, "Seleccionar un tipo de comunidad.") ||
      mostrarAlertaSelect(localIp, "Selecciona la o las IPs necesarias.") ||
      mostrarAlerta(initialIp, "Asigne un valor a la IP de inicio.") ||
      mostrarAlerta(finalIp, "Asigne un valor a la IP final.")
    ) {
      return;
    } */

    // var formData = $(this).serialize();

    var name = automationName.val();
    var type = automationType.val();
    var csrfToken = $("#csrf_token").val();
    var horario =
      diasHorario + "  " + intialTime.val() + " - " + finalTime.val();

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

    btnCreateComunnity.prop("disabled", true);

    $.ajax({
      type: "POST",
      url: "/add_automation",
      data: $.param(formData, true),
      headers: {
        "X-CSRFToken": csrfToken,
      },
      success: function (response) {
        //$("#modal-filter").find(".close").trigger("click");
        alertMessage(response.message);
      },
      error: function (xhr, status, error) {
        console.error("Respuesta del servidor:", xhr.responseText);
      },
    });
  });

  btnDeleteCommunity.click(function () {
    console.log("fsdfsf");
    // Mostrar el mensaje en la alerta
    $(".alert-message").text("¡Comunidad eliminada correctamente!");
    $(".alert-message-container").show("medium");
    setTimeout(function () {
      $(".alert-message-container").hide("medium");
    }, 5000);
  });

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
