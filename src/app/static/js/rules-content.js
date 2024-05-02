$(document).ready(function () {
  $(".ticket-type").append(
    '<button class="show-full-response">Mostrar</button>'
  );

  var selectAction = $("#selectAction");
  var selectEntry = $("#selectEntry");
  var domain = $("#domain");

  /* Modal eliminar regla */
  var confirmarEliminarModal = $("#confirmarEliminar");
  var btnConfirmDeleteRuleContent = $("#deleteRuleConfirm");

  /* Modal agregar dominio */
  var modalDomain = $("#modalDomain");
  var btnSaveDomain = $("#btnSave");

  /* Datos crear dominio */
  var ruleDetailName = $("#rule-detail-name");
  var ruleId = $("#rule_id");

  /* Datos de tabla */
  var ruleName = $("#rule_name");
  var ruleNumber = $("#rule_number");

  var tableRuleContent = $(".table");

  tableRuleContent.bootstrapTable({
    showColums: true,
    locale: "es-ES",
    columns: [
      {
        field: "number",
        title: "N° Regla",
      },
      {
        field: "name",
        title: "DOMINOS DE CONTENIDO",
        sortable: true,
      },
      {
        field: "created_date",
        title: "FECHA DE CREACION",
        sortable: true,
      },
      {
        field: "action",
        title: "ACCION DE FIREWALL",
        sortable: true,
      },
      {
        field: "protocol",
        title: "PROTOCOLO",
        sortable: true,
      },
      {
        field: "entry",
        title: "DIRECCION DE REGLA",
        sortable: true,
      },
      {
        field: "en/dis",
        title: "",
      },
      {
        field: "delete",
        title: "",
      },
    ],
  });

  modalDomain.on("show.bs.modal", function (event) {
    var button = $(event.relatedTarget);

    var reglaId = button.data("regla-id");
    var reglaNombre = button.data("regla-nombre");

    ruleDetailName.val(reglaNombre);
    ruleId.val(reglaId);
  });

  $("#formFirewall").submit(function (event) {
    event.preventDefault();

    if (
      validarSelect(selectAction, "Se debe asignar una accion para la Regla") ||
      mostrarAlerta(selectEntry, "El campo de entrada es requerido.") ||
      mostrarAlerta(domain, "El campo de dominio es requerido")
    ) {
      return;
    }

    var formData = $(this).serialize();
    btnSaveDomain.prop("disabled", true);

    $.ajax({
      type: "POST",
      url: "/add_rule_detail",
      data: formData,
      success: function (response) {
        if (response.error) {
          btnSaveDomain.prop("disabled", false);
          alertMessage(response.error, "danger");
        } else {
          alertMessage(response.message, "success");
        }
      },
      error: function (error) {
        btnSaveDomain.prop("disabled", false);
        alertMessage(error, "danger");
      },
    });
  });

  function validarSelect(elemento, mensaje) {
    if (elemento.val() === null || elemento.val().length === 0) {
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

  function validarCampo(elemento) {
    return (
      !elemento.prop("disabled") &&
      elemento.val().trim() === "" &&
      elemento.css("display") !== "none"
    );
  }

  $('button[id^="btn-regla"]').on("click", function (event) {
    event.preventDefault();

    var reglaId = $(this).attr("id").split("-", 3)[2];

    var btn_status = $(this);
    btn_status.prop("disabled", true);

    $.ajax({
      type: "GET",
      url: "/desactivar_regla",
      data: { id: reglaId },
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

  confirmarEliminarModal.on("show.bs.modal", function (event) {
    var button = $(event.relatedTarget);
    var reglaDetailId = button.data("regla-detail-id");
    var reglaNombre = button.data("regla-nombre");

    ruleName.val(reglaNombre);
    ruleNumber.val(reglaDetailId);
  });

  btnConfirmDeleteRuleContent.on("click", function () {
    var params = {
      regla: ruleNumber.val(),
      nombre: ruleName.val(),
    };
    btnConfirmDeleteRuleContent.prop("disabled", true);
    $.ajax({
      type: "GET",
      url: "/eliminar_regla",
      data: params,
      success: function (response) {
        if (response.error) {
          btnConfirmDeleteRuleContent.prop("disabled", false);
          alertMessage(response.error, "danger");
        } else {
          alertMessage(response.message, "success");
        }
      },
      error: function (error) {
        btnConfirmDeleteRuleContent.prop("disabled", false);
        alertMessage(error, "danger");
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
        location.reload();
      }
      $(".alert-message-container").hide("medium");
    }, 1500);
  }

  $(".show-full-response").on("click", function () {
    $(this).closest("table").toggleClass("full-response");
    guardarEstadoBoton();
  });

  abrirUltimoPanelAbierto();
  restaurarEstadoBoton();
  scrollPos();
});

// Obtener el ID del último panel abierto
function obtenerUltimoPanelAbierto() {
  return sessionStorage.getItem("ultimoPanelAbierto");
}

// Función para abrir el último panel abierto al cargar la página
function abrirUltimoPanelAbierto() {
  var ultimoPanelId = obtenerUltimoPanelAbierto();
  if (ultimoPanelId) {
    $("#" + ultimoPanelId).collapse("show");
    $("#btn-" + ultimoPanelId).attr("aria-expanded", "true");
  }
}

// Guardar el ID del panel abierto al mostrar un panel del acordeón
$("#accordion").on("shown.bs.collapse", function (e) {
  var idPanel = $(e.target).attr("id");
  sessionStorage.setItem("ultimoPanelAbierto", idPanel);
});

// Eliminar el ID del panel abierto al ocultar todos los paneles del acordeón
$("#accordion").on("hidden.bs.collapse", function () {
  if ($("#accordion .collapse.show").length === 0) {
    sessionStorage.removeItem("ultimoPanelAbierto");
  }
});

// Toma y Restaurar el estado del botón de expansion de la tabla
function guardarEstadoBoton() {
  var id_table = obtenerUltimoPanelAbierto().replace("collapse", "");
  var mostrarTodos = $("#tableFirewallContent_" + id_table).hasClass(
    "full-response"
  );
  sessionStorage.setItem("estadoBotonMostrarTodos", mostrarTodos);
}

function restaurarEstadoBoton() {
  var mostrarTodos = sessionStorage.getItem("estadoBotonMostrarTodos");
  if (mostrarTodos === "true") {
    var id_table = obtenerUltimoPanelAbierto().replace("collapse", "");
    $("#tableFirewallContent_" + id_table).addClass("full-response");
  }
}

// Tomar y Restaurar la posición del scroll
window.addEventListener("beforeunload", function () {
  sessionStorage.setItem("scrollPosition", window.scrollY);
});

function scrollPos() {
  var scrollPosition = sessionStorage.getItem("scrollPosition");
  if (scrollPosition !== null) {
    window.scrollTo(0, scrollPosition);
  }
}
