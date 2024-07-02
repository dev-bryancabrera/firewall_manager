$(document).ready(function () {
  // Variables
  var $vpnserverForm = $("#form-servervpn");
  var $vpnclientForm = $("#form-clientvpn");
  var $servervpnTable = $("#servervpn-table");

  var servervpnName = $("#servervpn-name");
  var servervpnAssociation = $("#servervpn-association");
  var servervpnSecret = $("#servervpn-secret");

  var btnCreateServervpn = $("#btn-create-servervpn");

  /* contentType.prop("disabled", true);
  contentType.selectpicker("refresh");
  domainPlataform.prop("disabled", true);
  domainPlataform.selectpicker("refresh"); */

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

  /* automationType.on("change", function () {
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
  }); */

  $servervpnTable.bootstrapTable({});

  $vpnserverForm.submit(function (event) {
    event.preventDefault();

    if (
      mostrarAlerta(servervpnName, "Asignar un nombre a la automatizacion.") ||
      mostrarAlerta(
        servervpnAssociation,
        "Asigne un valor del dominio a restringir."
      ) ||
      mostrarAlerta(servervpnSecret, "Asigne el o los dias a restringir.")
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

    // if (
    //   mostrarAlerta(servervpnName, "Asignar un nombre a la automatizacion.") ||
    //   mostrarAlerta(
    //     servervpnAssociation,
    //     "Asigne un valor del dominio a restringir."
    //   ) ||
    //   mostrarAlerta(servervpnSecret, "Asigne el o los dias a restringir.")
    // ) {
    //   return;
    // }

    // Crear un objeto con los datos que deseas enviar
    var formData = $(this).serialize();

    // btnCreateServervpn.prop("disabled", true);

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

  $.ajax({
    type: "GET",
    url: "/status_openvpn",
    success: function (response) {
      // Mostrar estado del servidor VPN
      $("#estado_vpn").text("Estado VPN: " + response.status);

      // Mostrar credenciales si el estado es "running"
      if (response.status === "running") {
        response.credentials.forEach(function (credential) {
          $("#nombre_vpn").text("VPN Nombre: " + credential.vpn_name);
          $("#asociacion_vpn").text(
            "VPN Asociacion: " + credential.vpn_asociation
          );
          $("#secret_vpn").val(credential.vpn_secret_key);
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
