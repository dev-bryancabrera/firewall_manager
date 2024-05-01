let eventSource = null;
let capturaPausada = false;
let pageLoaded = false;
let load_data = false;
var capturaActiva = true;

/* Boton guardar Reporte */
var btnGuardarReporte = $("#save_report");
var btnPausePlayReporte = $("#btn-play-pause");
var btnSaveReportData = $("#btn_save_report");
var nombreReporte = $("#nombreReporte");
var btnLoadReport = $("#btnLoadReport");
var btnBackFilter = $("#btnBackFilter");
var $packetTable = $("#packetTable");

var confirmDeleteModal = $("#confirmarEliminar");
var btnConfirmDeleteReport = $("#deleteReportConfirm");

var idReport = $("#reporte_id");

var loadDataSaved = false;

/* Obtener el parametro de filtro para cargar los datos */
var url = window.location.pathname; // Obtener la parte de la ruta de la URL
var parts = url.split("/"); // Dividir la URL por las barras
var baseUrl = url.split("/traffic-packets")[0];
var commandEncoded = parts[parts.length - 1]; // Obtener el valor del parámetro de ruta "filtro"
var commandFilter = decodeURIComponent(commandEncoded); // Decodificar el valor
var commandEncodedId = parts[parts.length - 2]; // Obtener el valor del parámetro de ruta "id"
var commandId = decodeURIComponent(commandEncodedId); // Decodificar el valor

$(document).ready(function () {
  btnLoadReport.css("display", "none");
  btnGuardarReporte.css("display", "none");
  btnPausePlayReporte.css("display", "none");
  btnBackFilter.prop("disabled", true);

  if (parts.length == 4) {
    btnGuardarReporte.css("display", "block");
    btnPausePlayReporte.css("display", "block");
    cargarDatosTabla();
  } else {
    loadDataSaved = true;
    btnLoadReport.css("display", "block");
    btnBackFilter.prop("disabled", false);
  }

  btnGuardarReporte.prop("disabled", true);

  $packetTable.bootstrapTable({
    showColumns: true,
    showExport: true,
    exportTypes: ["json", "xml", "txt", "excel", "pdf"],
    locale: "es-ES",
    columns: [
      {
        field: "time",
        title: "Marca de tiempo",
        sortable: true,
      },
      {
        field: "src_ip",
        title: "Dirección IP de origen",
        sortable: true,
      },
      {
        field: "src_port",
        title: "Puerto de origen",
        sortable: true,
      },
      {
        field: "dst_ip",
        title: "Dirección IP de destino",
        sortable: true,
      },
      {
        field: "dst_port",
        title: "Puerto de destino",
        sortable: true,
      },
      {
        field: "protocol",
        title: "Protocolo",
        sortable: true,
      },
      {
        field: "info",
        title: "Informacion de Captura",
        sortable: true,
      },
    ],
  });

  /* Guardar los Reportes */
  btnSaveReportData.on("click", function () {
    console.log(nombreReporte);
    if (mostrarAlerta(nombreReporte, "Debe asignar un nombre al reporte")) {
      return;
    }

    var tableData = [];
    $("#packetTable tbody tr").each(function () {
      var rowData = {};
      $(this)
        .find("td")
        .each(function (index, el) {
          rowData[$("#packetTable th").eq(index).data("field")] =
            $(this).text();
        });
      tableData.push(rowData);
    });

    btnGuardarReporte.prop("disabled", true);

    var csrfToken = document.getElementById("csrf_token").value;

    $.ajax({
      type: "POST",
      url: "/save_report",
      contentType: "application/json",
      headers: { "X-CSRFToken": csrfToken }, // Incluir el token CSRF en los headers
      data: JSON.stringify({
        nombre: nombreReporte.val(),
        filtro: commandFilter,
        tableData: tableData,
      }),
      success: function (response) {
        alertMessage(response.message);

        // Redirigir a la ruta base
        window.location.href = baseUrl + "/traffic-filter";
        sessionStorage.removeItem("datosTabla");
      },
      error: function (xhr, status, error) {
        var errorMessage = xhr.responseText; // Obtener el mensaje de error del servidor
        console.error("Error al guardar el reporte:", errorMessage);
      },
    });
  });

  function validarCampo(elemento) {
    return !elemento.prop("disabled") && elemento.val().trim() === "";
  }

  function alertMessage(response) {
    $(".alert-message-container").show("medium");
    $(".alert-message").text(response);
    setTimeout(function () {
      $(".alert-message-container").hide("medium");
    }, 2000);
  }

  function mostrarAlerta(elemento, mensaje) {
    if (validarCampo(elemento)) {
      $("#liveToast .toast-body").text(mensaje);
      $("#liveToast").toast("show");
      return true;
    }
    return false;
  }
});

function loadDataReport(registro_id) {
  resetData();

  fetch(`/load_report_data?registro_id=${registro_id}`)
    .then((response) => {
      if (!response.ok) {
        throw new Error("Network response was not ok");
      }
      // Convertir la respuesta a JSON
      return response.json();
    })
    .then((data) => {
      if (data.error) {
        console.error(data.error);
        return;
      }
      // Parsear los datos JSON y agregar cada fila a la tabla
      const jsonData = data.data;
      const parsedData = JSON.parse(jsonData);
      parsedData.forEach((row) => {
        $packetTable.bootstrapTable("append", row);
      });
      btnGuardarReporte.prop("disabled", true);
      btnPausePlayReporte.prop("disabled", true);
      capturaActiva = false;
      if (eventSource) {
        eventSource.close();
        eventSource = null;
      }
    })
    .catch((error) => {
      console.error("Hubo un problema al realizar la accion:", error);
    });
}

confirmDeleteModal.on("show.bs.modal", function (event) {
  var button = $(event.relatedTarget);
  var reporteId = button.data("reporte-id");

  idReport.val(reporteId);
});

btnConfirmDeleteReport.on("click", function () {
  var params = {
    reporte_id: idReport.val(),
  };
  btnConfirmDeleteReport.prop("disabled", true);
  $.ajax({
    type: "GET",
    url: "/eliminar_reporte",
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

function guardarDatosTabla() {
  if (!loadDataSaved) {
    const datosTabla = [];
    sessionStorage.removeItem("datosTabla");

    $("#packetTable tbody tr").each(function () {
      var rowData = {};
      $(this)
        .find("td")
        .each(function (index, el) {
          rowData[$("#packetTable th").eq(index).data("field")] =
            $(this).text();
        });
      datosTabla.push(rowData);
    });

    sessionStorage.setItem("datosTabla", JSON.stringify(datosTabla));
  }
}

function cargarDatosTabla() {
  // Obtener los datos del sessionStorage
  const datosTabla = JSON.parse(sessionStorage.getItem("datosTabla"));

  if (datosTabla) {
    // Iterar sobre los datos y agregar cada fila a la tabla
    datosTabla.forEach(function (fila) {
      const tr = $("<tr>");
      Object.values(fila).forEach(function (value) {
        const td = $("<td>").text(value);
        tr.append(td);
      });
      $("#packetTable tbody").append(tr);
    });
  }
}

$("#btnBackFilter").click(function () {
  guardarDatosTabla();
  window.location.href = baseUrl + "/traffic-filter";
});

function loadPacketFilter() {
  const urlWithFilter = `/packetdata?command_id=${commandId}&command_filter=${commandFilter}`;

  load_data = true;
  eventSource = new EventSource(urlWithFilter);

  btnPausePlayReporte.prop("disabled", true);

  eventSource.onmessage = function (event) {
    const packetData = event.data;

    if (packetData.length !== 0) {
      $("#play-icon").hide();
      $("#pause-icon").show();

      btnPausePlayReporte.prop("disabled", false);
    }

    const packetInfo = packetData.split(" ");
    const time = packetInfo[0] + " " + packetInfo[1];
    const src_ip = packetInfo[2].split(":")[0];
    const src_port = packetInfo[2].split(":")[1];
    const dst_ip = packetInfo[4].split(":")[0];
    const dst_port = packetInfo[4].split(":")[1];
    const protocol = packetInfo[5];
    const info = packetInfo.slice(6).join(" ");

    const row = {
      time: time,
      src_ip: src_ip,
      src_port: src_port,
      dst_ip: dst_ip,
      dst_port: dst_port,
      protocol: protocol,
      info: info,
    };

    $packetTable.bootstrapTable("append", row);
  };
}

function preLoadData() {
  if (!pageLoaded) {
    pageLoaded = true;
    console.log("Cargando datos por primera vez...");
    eventSource = new EventSource("/pre_start_capture");

    eventSource.onmessage = function (event) {
      const packetData = event.data;

      if (packetData.length !== 0) {
        btnPausePlayReporte.prop("disabled", false);
      }

      const packetInfo = packetData.split(" ");
      const time = packetInfo[0] + " " + packetInfo[1];
      const src_ip = packetInfo[2].split(":")[0];
      const src_port = packetInfo[2].split(":")[1];
      const dst_ip = packetInfo[4].split(":")[0];
      const dst_port = packetInfo[4].split(":")[1];
      const protocol = packetInfo[5];
      const info = packetInfo.slice(6).join(" ");

      const row = {
        time: time,
        src_ip: src_ip,
        src_port: src_port,
        dst_ip: dst_ip,
        dst_port: dst_port,
        protocol: protocol,
        info: info,
      };

      $packetTable.bootstrapTable("append", row);
    };
  }
}

function stopPlayData() {
  var isPaused = $("#pause-icon").is(":visible");

  if (eventSource) {
    btnGuardarReporte.prop("disabled", false);
    btnBackFilter.prop("disabled", false);
    if (isPaused) {
      capturaActiva = false; // Desactivar la captura
      pageLoaded = false;
      eventSource.close(); // Cierra la conexión del EventSource
      eventSource = null; // Limpia la variable eventSource
      $("#play-icon").show();
      $("#pause-icon").hide();
    }
  } else {
    loadPacketFilter();

    btnGuardarReporte.prop("disabled", true);
    btnBackFilter.prop("disabled", true);

    $("#play-icon").hide();
    $("#pause-icon").show();
    if (load_data) {
      loadData();
    } else {
      capturaActiva = true; // Reactivar la captura
      preLoadData();
    }
    capturaPausada = false;
  }
}

async function resetData() {
  btnPausePlayReporte.prop("disabled", false);
  sessionStorage.removeItem("datosTabla");
  /* if (!eventSource) {
    capturaActiva = true;
    preLoadData();
  } */
  load_data = true;
  $packetTable.bootstrapTable("removeAll");
}

$("#btn-clean").on("click", function () {
  $("#pause-icon").hide();
  $("#play-icon").show();
  load_data = false;
  resetData();
});
