$(document).ready(function () {
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

    $.ajax({
      type: "POST",
      url: "/add_vpn_server",
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

    $.ajax({
      type: "POST",
      url: "/add_vpn_client",
      data: formData,
      xhrFields: {
        responseType: "blob", // Esto es importante para manejar la respuesta del archivo
      },
      success: function (blob, status, xhr, response) {
        //$("#modal-filter").find(".close").trigger("click");
        alertMessage("Usuario creado correctamente");

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
        console.error("Respuesta del servidor:", xhr.responseText);
      },
    });
  });

  $("#deleteClientConfirm").on("click", function () {
    var params = {
      client_name: $("#client_vpn_delete").val(),
      secret_vpn: $("#secret_vpn").val(),
    };

    $.ajax({
      type: "GET",
      url: "/eliminar_clientevpn",
      data: params,
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

  $.ajax({
    type: "GET",
    url: "/status_openvpn",
    success: function (response) {
      if (response.file_exists) {
        $(".form-servervpn").hide();
        $(".container-accordion").show();
      }

      $("#estado_vpn").text("Estado: " + response.status);

      if (response.status === "En ejecucion") {
        response.credentials.forEach(function (credential) {
          $("#nombre_vpn").text("Nombre: " + credential.vpn_name);
          $("#asociacion_vpn").text("Asociacion: " + credential.vpn_asociation);
          $(".secretvpn").val(credential.vpn_secret_key);
        });

        // Mostrar puerta de enlace si está disponible
        if (response.gateway) {
          $("#gateway_vpn").text("Puerta de enlace: " + response.gateway);
        }
      }
    },
    error: function (xhr, status, error) {
      console.error("Error al obtener el estado del servidor VPN:", error);
    },
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
