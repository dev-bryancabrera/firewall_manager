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

    $.ajax({
      type: "POST",
      url: "/add_community",
      data: formData,
      success: function (response) {
        //$("#modal-filter").find(".close").trigger("click");
        alertMessage(response.message);
      },
      error: function (xhr, status, error) {
        console.error(error);
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