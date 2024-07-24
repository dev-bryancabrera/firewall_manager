$(document).ready(function () {
  $(".ticket-type").append(
    '<button class="show-full-response">Mostrar</button>'
  );

  var automationName = $("#automation-name");
  var domainPlataform = $("#siteRestriction");

  var intialTime = $("#initial-time");
  var finalTime = $("#final-time");
  var daySchedule = $("#daypicker");

  var btnCreateAutomation = $("#btn-create-automation");
  var btnDeleteAutomation = $("#btn-delete-automation");

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

  var selectAction = $("#selectAction");
  var domain = $("#domain");

  /* Modal eliminar regla */
  var confirmarEliminarModal = $("#confirmarEliminar");
  var btnConfirmDeleteRuleContent = $("#deleteRuleConfirm");

  /* Modal agregar dominio */
  var modalDomain = $(".modalForm");
  var btnSaveDomain = $("#btnSave");

  /* Datos crear dominio */
  var ruleDetailName = $(".name-rule");
  var ruleId = $(".id-rule");

  /* Datos de tabla */
  var ruleName = $("#rule_name");
  var ruleNumber = $("#rule_number");

  var tableRuleContent = $(".table");

  tableRuleContent.bootstrapTable({});

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

  $("#formAutomation").submit(function (event) {
    event.preventDefault();

    if (
      mostrarAlerta(automationName, "Indique un nombre a al automatizacion") ||
      mostrarAlertaSelect(
        domainPlataform,
        "Selecciona el o los dominos a restringir."
      ) ||
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
    var csrfToken = $("#csrf_token").val();
    var horario =
      daySchedule.val() + "  " + intialTime.val() + " - " + finalTime.val();

    var formData = {
      automationName: name,
      domainPlataform: domainPlataform.val(),
      horario: horario,
      id_regla: ruleId.val(),
      nombre_regla: ruleDetailName.val(),
    };
    btnCreateAutomation.prop("disabled", true);

    $.ajax({
      type: "POST",
      url: "/add_automation_content",
      data: $.param(formData, true),
      headers: {
        "X-CSRFToken": csrfToken,
      },
      success: function (response) {
        if (response.error) {
          btnCreateAutomation.prop("disabled", false);
          alertMessage(response.error, "danger");
        } else {
          alertMessage(response.message, "success");
        }
      },
      error: function (error) {
        btnCreateAutomation.prop("disabled", false);
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

  // confirmarEliminarModal.on("show.bs.modal", function (event) {
  //   var button = $(event.relatedTarget);
  //   var reglaId = button.data("regla-id");
  //   var reglaDetailId = button.data("regla-detail-id");
  //   var reglaNombre = button.data("regla-nombre");

  //   if (reglaDetailId) {
  //     ruleNumber.val(reglaDetailId);
  //   } else {
  //     ruleNumber.val(reglaId);
  //   }
  //   ruleName.val(reglaNombre);
  // });

  // btnConfirmDeleteRuleContent.on("click", function () {
  //   var params = {
  //     regla: ruleNumber.val(),
  //     nombre: ruleName.val(),
  //   };
  //   btnConfirmDeleteRuleContent.prop("disabled", true);
  //   $.ajax({
  //     type: "GET",
  //     url: "/eliminar_regla",
  //     data: params,
  //     success: function (response) {
  //       if (response.error) {
  //         btnConfirmDeleteRuleContent.prop("disabled", false);
  //         alertMessage(response.error, "danger");
  //       } else {
  //         alertMessage(response.message, "success");
  //       }
  //     },
  //     error: function (error) {
  //       btnConfirmDeleteRuleContent.prop("disabled", false);
  //       alertMessage(error, "danger");
  //     },
  //   });
  // });

  $("#confirmarEliminar").on("show.bs.modal", function (event) {
    var button = $(event.relatedTarget); // Botón que abrió el modal

    var ruleNameAccordion = button.data("regla-nombre-accordion");
    var reglaId = button.data("regla-id");
    var reglaDetailId = button.data("regla-detail-id");
    var reglaNombre = button.data("regla-nombre");
    var automatizacionNombre = button.data("automation-nombre");
    var actionType = button.data("action-type");

    var modal = $(this);
    var confirmacionModalLabel = modal.find("#confirmacionModalLabel");
    var confirmDelete = modal.find("#confirmDelete");
    var deleteRuleConfirm = modal.find("#deleteRuleConfirm");

    if (actionType === "deleteRule") {
      confirmacionModalLabel.text("Confirmar Eliminación");
      confirmDelete.text("¿Estás seguro de que deseas eliminar la regla?");
      deleteRuleConfirm.text("Eliminar");
    } else if (actionType === "deleteAutomation") {
      confirmacionModalLabel.text("Confirmar Automatización");
      confirmDelete.text(
        "¿Estás seguro de que deseas eliminar la automatización para " +
          ruleNameAccordion +
          "?"
      );
      deleteRuleConfirm.text("Eliminar");
    }

    if (reglaDetailId) {
      ruleNumber.val(reglaDetailId);
    } else {
      ruleNumber.val(reglaId);
    }
    ruleName.val(reglaNombre);

    deleteRuleConfirm.off("click").on("click", function () {
      if (actionType === "deleteRule") {
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
      } else if (actionType === "deleteAutomation") {
        console.log("ascdsf");
        var params = {
          regla_id: ruleNumber.val(),
          regla_nombre: ruleName.val(),
          automatizacion_nombre: automatizacionNombre,
        };
        btnDeleteAutomation.prop("disabled", true);
        $.ajax({
          type: "GET",
          url: "/eliminar_automatizacion_content",
          data: params,
          success: function (response) {
            if (response.error) {
              btnDeleteAutomation.prop("disabled", false);
              alertMessage(response.error, "danger");
            } else {
              alertMessage(response.message, "success");
            }
          },
          error: function (error) {
            btnDeleteAutomation.prop("disabled", false);
            alertMessage(error, "danger");
          },
        });
      }
    });
  });

  // btnDeleteAutomation.on("click", function () {
  //   var params = {
  //     regla_id: ruleId.val(),
  //     regla_nombre: ruleDetailName.val(),
  //   };
  //   btnDeleteAutomation.prop("disabled", true);
  //   $.ajax({
  //     type: "GET",
  //     url: "/eliminar_automatizacion_content",
  //     data: params,
  //     success: function (response) {
  //       if (response.error) {
  //         btnDeleteAutomation.prop("disabled", false);
  //         alertMessage(response.error, "danger");
  //       } else {
  //         alertMessage(response.message, "success");
  //       }
  //     },
  //     error: function (error) {
  //       btnDeleteAutomation.prop("disabled", false);
  //       alertMessage(error, "danger");
  //     },
  //   });
  // });

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

  function mostrarAlertaSelect(elemento, mensaje) {
    if (validarCampoSelect(elemento)) {
      $("#liveToast .toast-body").text(mensaje);
      $("#liveToast").toast("show");
      return true;
    }
    return false;
  }

  function validarCampoSelect(elemento) {
    return !elemento.prop("disabled") && validarMultiselectVacio(elemento);
  }

  function validarMultiselectVacio(elemento) {
    return elemento.val() === null || elemento.val().length === 0;
  }

  $(".set-automation").on("click", function () {
    // Obtener el índice de la fila desde el atributo data-row-index
    var rowIndex = $(this).data("row-index");

    // Encontrar la tabla correspondiente
    var table = $("#tableFirewallContent_" + rowIndex);

    var rows = table.find("tbody tr");

    var sites = $("#siteRestriction");
    sites.empty();

    // Iterar sobre cada fila y obtener el valor de la celda "Sitio restringido"
    rows.each(function () {
      var row = $(this);
      var sitiosRestringidos = row.find(".site-blocked").text().trim();
      if (sitiosRestringidos) {
        sites.append(
          '<option value="' +
            sitiosRestringidos +
            '">' +
            sitiosRestringidos +
            "</option>"
        );
      }
      sites.find("option").prop("selected", true);
      sites.selectpicker("refresh");
    });

    // Abrir el modal
    $("#modalAutomation").modal("show");
  });

  $(".show-full-response").on("click", function () {
    $(this).closest("table").toggleClass("full-response");
    guardarEstadoBoton();
  });

  abrirUltimoPanelAbierto();
  restaurarEstadoBoton();
  $(window).on("load", function () {
    setTimeout(scrollPos, 500);
  });
});

// Obtener el objeto estado general desde sessionStorage
function obtenerEstadoGeneral() {
  var estadoGeneral = sessionStorage.getItem("estadoGeneral");
  return estadoGeneral ? JSON.parse(estadoGeneral) : {};
}

// Guardar el objeto estado general en sessionStorage
function guardarEstadoGeneral(estado) {
  sessionStorage.setItem("estadoGeneral", JSON.stringify(estado));
}

// Obtener el ID del último panel abierto
function obtenerUltimoPanelAbierto() {
  var estadoGeneral = obtenerEstadoGeneral();
  return estadoGeneral.ultimoPanelAbierto;
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
  var estadoGeneral = obtenerEstadoGeneral();
  estadoGeneral.ultimoPanelAbierto = idPanel;
  guardarEstadoGeneral(estadoGeneral);
});

// Eliminar el ID del panel abierto al ocultar todos los paneles del acordeón
$("#accordion").on("hidden.bs.collapse", function () {
  if ($("#accordion .collapse.show").length === 0) {
    var estadoGeneral = obtenerEstadoGeneral();
    delete estadoGeneral.ultimoPanelAbierto;
    guardarEstadoGeneral(estadoGeneral);
  }
});

// Guardar el estado del botón de expansión de la tabla
function guardarEstadoBoton() {
  var id_table = obtenerUltimoPanelAbierto().replace("collapse", "");
  var mostrarTodos = $("#tableFirewallContent_" + id_table).hasClass(
    "full-response"
  );
  var estadoGeneral = obtenerEstadoGeneral();
  estadoGeneral.estadoBotonMostrarTodos = mostrarTodos;
  guardarEstadoGeneral(estadoGeneral);
}

// Restaurar el estado del botón de expansión de la tabla
function restaurarEstadoBoton() {
  var estadoGeneral = obtenerEstadoGeneral();
  var mostrarTodos = estadoGeneral.estadoBotonMostrarTodos;
  if (mostrarTodos === true) {
    var id_table = obtenerUltimoPanelAbierto().replace("collapse", "");
    $("#tableFirewallContent_" + id_table).addClass("full-response");
  }
}

// Tomar y Restaurar la posición del scroll
window.addEventListener("beforeunload", function () {
  var estadoGeneral = obtenerEstadoGeneral();
  estadoGeneral.scrollPosition = window.scrollY;
  guardarEstadoGeneral(estadoGeneral);
});

function scrollPos() {
  var estadoGeneral = obtenerEstadoGeneral();
  var scrollPosition = estadoGeneral.scrollPosition;
  if (scrollPosition !== undefined) {
    window.scrollTo(0, scrollPosition);
  }
}

function formatoNombre(input) {
  input.value = input.value.replace(/-/g, "");
}
