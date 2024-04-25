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
        sortable: true,
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
        alertMessage(response.message);
      },
      error: function (xhr, status, error) {
        console.error(error);
      },
    });
  });

  function alertMessage(response) {
    $(".alert-message-container").show("medium");
    $(".alert-message").text(response);
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
