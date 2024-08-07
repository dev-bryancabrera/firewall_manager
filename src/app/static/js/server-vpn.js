$(document).ready(function () {
  obtenerEstadoVPN();

  // Variables
  var $vpnserverForm = $("#form-servervpn");
  var $vpnclientForm = $("#form-clientvpn");
  var $servervpnTable = $("#servervpn-table");

  var servervpnName = $("#servervpn-name");
  var servervpnAssociation = $("#servervpn-association");
  var servervpnSecret = $("#servervpn-secret");

  var clientName = $("#client-name");
  var clientvpnRestriction = $("#client_key");
  var restrictionClt = $("#restriction-type");

  var btnCreateServervpn = $("#btn-create-servervpn");
  var btnCreateClientvpn = $("#btn-create-clientvpn");
  var btndeleteClientConfirm = $("#deleteClientConfirm");
  clientvpnRestriction.prop("disabled", true);
  $(".container-accordion").hide();

  function cleanDisabledInput(elements) {
    $.each(elements, function (key, value) {
      value.val("");
      value.prop("disabled", true);
    });
  }

  restrictionClt.on("change", function () {
    cleanDisabledInput({
      clientvpnRestriction: clientvpnRestriction,
    });

    var selectedOption = restrictionClt.val();

    if (selectedOption === "yes") {
      clientvpnRestriction.prop("disabled", false);
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

  $servervpnTable.bootstrapTable({});

  $vpnserverForm.submit(function (event) {
    event.preventDefault();

    if (
      mostrarAlerta(servervpnName, "Asignar un nombre al servidor vpn.") ||
      mostrarAlerta(
        servervpnAssociation,
        "Asigne un valor del asociacion CA."
      ) ||
      mostrarAlerta(
        servervpnSecret,
        "Asigne una clave secreta para el servidor."
      )
    ) {
      return;
    }

    // Crear un objeto con los datos que deseas enviar
    var formData = $(this).serialize();

    btnCreateServervpn.prop("disabled", true);

    showLoading();

    $.ajax({
      type: "POST",
      url: "/add_vpn_server",
      data: formData,
      success: function (response) {
        //$("#modal-filter").find(".close").trigger("click");

        if (response.error) {
          btnCreateServervpn.prop("disabled", false);
          alertMessage(response.error, "danger");
        } else {
          alertMessage(response.message, "success");
        }
      },
      error: function (xhr, status, error) {
        btnCreateServervpn.prop("disabled", false);

        console.error("Respuesta del servidor:", xhr.responseText);
        alertMessage(error, "danger");
      },
    });
  });

  $vpnclientForm.submit(function (event) {
    event.preventDefault();

    if (
      mostrarAlerta(clientName, "Asignar un nombre al usuario.") ||
      mostrarAlertaSelect(
        restrictionClt,
        "Escoja una opcion sobre la restriccion del usuario."
      ) ||
      mostrarAlerta(
        clientvpnRestriction,
        "Asigne un valor a la clave del usuario."
      )
    ) {
      return;
    }

    // Crear un objeto con los datos que deseas enviar
    var formData = $(this).serialize();

    btnCreateClientvpn.prop("disabled", true);

    showLoading();

    $.ajax({
      type: "POST",
      url: "/add_vpn_client",
      data: formData,
      xhrFields: {
        responseType: "blob", // Esto es importante para manejar la respuesta del archivo
      },
      success: function (blob, status, xhr, response) {
        //$("#modal-filter").find(".close").trigger("click");

        alertMessage("Usuario creado correctamente", "success");
        if (xhr.getResponseHeader("Content-Disposition")) {
          var a = document.createElement("a");
          var url = window.URL.createObjectURL(blob);
          a.href = url;
          a.download = xhr
            .getResponseHeader("Content-Disposition")
            .split("filename=")[1];
          document.body.append(a);
          a.click();
          a.remove();
          window.URL.revokeObjectURL(url);
        } else {
          // Manejar una respuesta JSON en caso de error o mensaje
          var reader = new FileReader();
          reader.onload = function (event) {
            var response = JSON.parse(event.target.result);
            alertMessage(response.message || response.error);
          };
          reader.readAsText(blob);
        }
      },
      error: function (xhr, status, error) {
        btnCreateClientvpn.prop("disabled", false);

        console.error("Respuesta del servidor:", xhr.responseText);
        alertMessage(error, "danger");
      },
    });
  });

  $("#deleteClientConfirm").on("click", function () {
    var params = {
      client_name: $("#client_vpn_delete").val(),
      secret_vpn: $("#secret_vpn").val(),
    };

    btndeleteClientConfirm.prop("disabled", true);
    showLoading();

    $.ajax({
      type: "GET",
      url: "/eliminar_clientevpn",
      data: params,
      success: function (response) {
        if (response.error) {
          btndeleteClientConfirm.prop("disabled", false);
          alertMessage(response.error, "danger");
        } else {
          alertMessage(response.message, "success");
        }
      },
      error: function (textStatus, errorThrown) {
        btndeleteClientConfirm.prop("disabled", false);

        console.error("Error en la solicitud AJAX:", textStatus, errorThrown);
        alertMessage("Ocurrió un error al procesar la solicitud.", "danger");
      },
    });
  });

  function obtenerEstadoVPN() {
    showLoading();
    $.ajax({
      type: "GET",
      url: "/status_openvpn",
      success: function (response) {
        if (response.file_exists) {
          $(".form-servervpn").hide();
          $(".container-accordion").show();
        }

        $("#estado_vpn").text("Estado: " + response.status);

        if (response.status === "En ejecución") {
          response.credentials.forEach(function (credential) {
            $("#nombre_vpn").text("Nombre: " + credential.vpn_name);
            $("#asociacion_vpn").text(
              "Asociación: " + credential.vpn_asociation
            );
            $(".secretvpn").val(credential.vpn_secret_key);
          });

          // Mostrar puerta de enlace si está disponible
          if (response.gateway) {
            $("#gateway_vpn").text("Puerta de enlace: " + response.gateway);
          }
        }
        hideLoading();
      },
      error: function (xhr, status, error) {
        console.error("Error al obtener el estado del servidor VPN:", error);
        alertMessage(status, "danger");
      },
    });
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
