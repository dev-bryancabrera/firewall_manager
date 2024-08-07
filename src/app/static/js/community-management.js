$(document).ready(function () {
  // Variables
  var $communityForm = $("#form-community");
  var $communityTable = $("#community-table");

  var communityName = $("#community-name");
  var communityType = $("#community-type");
  var localIp = $("#local-ip");
  var initialIp = $("#initial-ip");
  var finalIp = $("#final-ip");

  var btnCreateComunnity = $("#btn-create-comunnity");
  var btnDeleteCommunity = $("#delete-btn");

  localIp.prop("disabled", true);
  localIp.selectpicker("refresh");

  initialIp.prop("disabled", true);
  finalIp.prop("disabled", true);

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

  communityType.on("change", function () {
    cleanDisabledInput({
      initialIp: initialIp,
      finalIp: finalIp,
    });
    cleanDisabledMultiselect({
      localIp: localIp,
    });
    var selectedOption = communityType.val();

    if (selectedOption === "red_local") {
      localIp.prop("disabled", false);
      localIp.selectpicker("refresh");
    } else if (selectedOption === "rango_red") {
      initialIp.prop("disabled", false);
      finalIp.prop("disabled", false);
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

  $communityTable.bootstrapTable({});

  $communityForm.submit(function (event) {
    event.preventDefault();

    if (
      mostrarAlerta(communityName, "Asignar un nombre a la comunidad.") ||
      mostrarAlertaSelect(communityType, "Seleccionar un tipo de comunidad.") ||
      mostrarAlertaSelect(localIp, "Selecciona la o las IPs necesarias.") ||
      mostrarAlerta(initialIp, "Asigne un valor a la IP de inicio.") ||
      mostrarAlerta(finalIp, "Asigne un valor a la IP final.")
    ) {
      return;
    }

    var formData = $(this).serialize();

    btnCreateComunnity.prop("disabled", true);

    showLoading();

    $.ajax({
      type: "POST",
      url: "/add_community",
      data: formData,
      success: function (response) {
        //$("#modal-filter").find(".close").trigger("click");

        if (response.error) {
          btnCreateComunnity.prop("disabled", false);
          alertMessage(response.error, "danger");
        } else {
          alertMessage(response.message, "success");
        }
      },
      error: function (xhr, status, error) {
        btnCreateComunnity.prop("disabled", false);

        console.error(error);
        alertMessage("Ocurrió un error al procesar la solicitud.", "danger");
      },
    });
  });

  $('button[id^="delete-community"]').on("click", function (event) {
    event.preventDefault();

    var comunidadId = $(this).attr("id").split("-", 3)[2];

    var btn_status = $(this);
    btn_status.prop("disabled", true);

    showLoading();

    $.ajax({
      type: "GET",
      url: "/eliminar_comunidad",
      data: { id: comunidadId },
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
