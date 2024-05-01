$(document).ready(function () {
  $(".ticket-type").append(
    '<button class="show-full-response">Mostrar</button>'
  );

  $(".show-full-response").on("click", function () {
    $(this).closest("table").toggleClass("full-response");
  });

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

    var formData = $(this).serialize();
    btnSaveDomain.prop("disabled", true);

    $.ajax({
      type: "POST",
      url: "/add_rule_detail",
      data: formData,
      success: function (response) {
        if (response.error) {
          alertMessage(response.error, "danger");
        } else {
          alertMessage(response.message, "success");
        }
      },
      error: function (xhr, status, error) {
        console.error(error);
      },
    });
  });

  function sendAjaxRequest(url, method, data, successCallback, errorCallback) {
    const xhr = new XMLHttpRequest();
    xhr.open(method, url, true);
    xhr.setRequestHeader("Content-Type", "application/json");
    xhr.onload = () => {
      if (xhr.status === 200) {
        successCallback(xhr.responseText);
      } else {
        errorCallback(xhr.statusText);
      }
    };
    xhr.onerror = () => errorCallback("Error de red");
    xhr.send(JSON.stringify(data));
  }

  $(".desactivar-btn").click(function () {
    const id = $(this).attr("id").split("-")[1];
    sendAjaxRequest(
      `/desactivar_regla?id_regla=${id}`,
      "GET",
      null,
      function (response) {
        // Actualiza el estado de la tabla después de recibir la respuesta
        const reglas = JSON.parse(response);
        // Actualiza la tabla con las nuevas reglas
      },
      function (error) {
        console.error(error);
      }
    );
  });

  $(".activar-btn").click(function () {
    const id = $(this).attr("id").split("-")[1];
    sendAjaxRequest(
      `/activar_regla?id_regla=${id}`,
      "GET",
      null,
      function (response) {
        // Actualiza el estado de la tabla después de recibir la respuesta
        const reglas = JSON.parse(response);
        // Actualiza la tabla con las nuevas reglas
      },
      function (error) {
        console.error(error);
      }
    );
  });

  function alertMessage(response, alertType) {
    var alertBox = $(".alert");
    var alertIcon = $(".alert-icon i");
    var alertMessage = $(".alert-message");

    // Oculta el contenedor de mensaje
    $(".alert-message-container").hide("medium");

    // Cambia el tipo de alerta
    if (alertType === "success") {
      alertBox.addClass("alert-success");
      alertIcon
        .removeClass("text-danger")
        .addClass("text-success")
        .addClass("fa-check-circle");
    } else if (alertType === "danger") {
      alertBox.addClass("alert-danger");
      alertIcon
        .removeClass("text-success")
        .addClass("text-danger")
        .addClass("fa-exclamation-circle");
    }

    alertMessage.text(response);

    // Muestra el contenedor de mensaje
    $(".alert-message-container").show("medium");

    // Oculta el mensaje después de 2 segundos y recarga la página
    setTimeout(function () {
      location.reload();
      $(".alert-message-container").hide("medium");
    }, 2000);
  }

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
        //alertMessage(response.message);
        location.reload();
      },
      error: function (xhr, status, error) {
        console.error(error);
      },
    });
  });
});
