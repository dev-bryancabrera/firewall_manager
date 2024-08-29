// ---------Responsive-navbar-active-animation-----------
function test() {
  var tabsNewAnim = $(".collapse");
  var activeItemNewAnim = tabsNewAnim.find(".active");
  if (activeItemNewAnim.length) {
    var activeWidthNewAnimHeight = activeItemNewAnim.innerHeight();
    var activeWidthNewAnimWidth = activeItemNewAnim.innerWidth();
    var itemPosNewAnimTop = activeItemNewAnim.position().top;
    var itemPosNewAnimLeft = activeItemNewAnim.position().left;
    $(".hori-selector").css({
      top: itemPosNewAnimTop + "px",
      left: itemPosNewAnimLeft + "px",
      height: activeWidthNewAnimHeight + "px",
      width: activeWidthNewAnimWidth + "px",
    });
  }

  $(".collapse").on("click", ".nav-item", function (e) {
    $(".collapse .nav-item").removeClass("active");
    $(this).addClass("active");
    var activeWidthNewAnimHeight = $(this).innerHeight();
    var activeWidthNewAnimWidth = $(this).innerWidth();
    var itemPosNewAnimTop = $(this).position().top;
    var itemPosNewAnimLeft = $(this).position().left;
    $(".hori-selector").css({
      top: itemPosNewAnimTop + "px",
      left: itemPosNewAnimLeft + "px",
      height: activeWidthNewAnimHeight + "px",
      width: activeWidthNewAnimWidth + "px",
    });
  });
}

function logout() {
  $.ajax({
    url: "/logout",
    type: "GET",
    success: function (response) {
      location.reload();
    },
    error: function (xhr, status, error) {
      console.error(error);
    },
  });
}

$(window).on("resize", function () {
  setTimeout(function () {
    test();
  }, 500);
});

$(".navbar-toggler").click(function () {
  $(".navbar-collapse").slideToggle(300);
  setTimeout(function () {
    test();
  });
});

// ---------Notification and Dropdown Handling-----------
function loadNotifications() {
  $.ajax({
    url: "/load_notifications", // Ruta para cargar notificaciones y configuración de correo
    method: "GET",
    success: function (response) {
      // Accede al array de notificaciones y a la configuración del correo
      var notifications = response.notifications;
      var $notificationList = $(".notification-list");
      var $notificationCount = $(".label");
      var $notificationCountNav = $(".notification-count");
      var $solidBellIcon = $(".fa-solid.fa-bell");
      var $regularBellIcon = $(".fa-regular.fa-bell");

      // Vaciar la lista antes de agregar nuevas notificaciones
      $notificationList.empty();

      var unreadCount = 0;

      // Agregar las notificaciones al DOM
      notifications.forEach(function (notification) {
        var readClass = notification.leido ? "read" : "unread";

        if (notification.leido === 0) {
          unreadCount++;
        }

        var unreadIndicator =
          notification.leido === 0
            ? '<span class="unread-indicator"></span>'
            : "";

        $notificationList.append(`
          <li class="notification-list-item ${readClass}" data-id="${notification.id}">
            <div class="item-header">
              ${unreadIndicator}
              <p class="message">${notification.mensaje}</p>
              <button class="btn btn-danger delete-notification">
                <i class="fa-solid fa-trash-can"></i>
              </button>
            </div>
            <div class="item-footer">
              <span class="from">Firewall</span>
              <span class="date">${notification.fecha}</span>
            </div>
          </li>
        `);
      });

      // Actualizar el conteo de notificaciones no leídas
      $notificationCount.text(unreadCount);
      $notificationCountNav.text(unreadCount);

      // Mostrar el ícono correcto
      if (unreadCount > 0) {
        $solidBellIcon.addClass("active");
        $regularBellIcon.removeClass("active");
      } else {
        $solidBellIcon.removeClass("active");
        $regularBellIcon.addClass("active");
      }

      if (response.email_config_exists) {
        // Establecer los valores en el formulario
        $("#email-server")
          .val(response.email_server || "")
          .change()
          .selectpicker("refresh");
        $("#email-sender")
          .val(response.mail_username || "")
          .change();
        $("#email-password")
          .val(response.mail_password || "")
          .change();
        $("#email-receiver")
          .val(response.mail_default_sender || "")
          .change();

        // Ocultar los campos vacíos
        // Mostrar u ocultar el contenedor del selectpicker según el valor
        $("#email-server")
          .closest(".form-group")
          .toggle(!!response.email_server);

        // Mostrar u ocultar los otros campos
        $("#email-sender")
          .closest(".form-group")
          .toggle(!!response.mail_username);
        $("#email-password")
          .closest(".form-group")
          .toggle(!!response.mail_password);
        $("#email-receiver")
          .closest(".form-group")
          .toggle(!!response.mail_default_sender);
      }
    },
    error: function (error) {
      console.error("Error al cargar las notificaciones:", error);
    },
  });
}

// Mostrar el formulario de correo al hacer clic en "Configurar Correo"
$("#configuracionCorreo").click(function (e) {
  e.preventDefault();

  $("#email-sender").prop("disabled", true);
  $("#email-password").prop("disabled", true);
  $("#email-receiver").prop("disabled", true);

  $(".formulario").hide();
  $("#formCorreo").show();
});

// Mostrar el formulario de red al hacer clic en "Configurar Red"
$("#configuracionRed").click(function (e) {
  e.preventDefault();
  $(".formulario").hide();
  $("#formRed").show();
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

$(document).ready(function () {
  var $notificacionForm = $("#form-notification");
  var btnSaveReceiver = $("btn-save-receiver");

  $notificacionForm.submit(function (event) {
    event.preventDefault();

    // if (
    //   mostrarAlerta(automationName, "Asignar un nombre a la automatizacion.") ||
    //   validarSelectContainer(
    //     communityList,
    //     community,
    //     "Seleccione una comunidad a asignar la automatizacion"
    //   ) ||
    //   mostrarAlertaSelect(
    //     serviceType,
    //     "Seleccionar un servicio para aplicar la restriccion."
    //   )
    // ) {
    //   return;
    // }

    // Crear un objeto con los datos que deseas enviar
    var formData = $(this).serialize();

    btnSaveReceiver.prop("disabled", true);

    showLoading();

    $.ajax({
      type: "POST",
      url: "/add_notification_email",
      data: formData,
      success: function (response) {
        //$("#modal-filter").find(".close").trigger("click");

        if (response.error) {
          btnSaveReceiver.prop("disabled", false);
          alertMessage(response.error, "danger");
        } else {
          alertMessage(response.message, "success");
        }
      },
      error: function (xhr, status, error) {
        btnSaveReceiver.prop("disabled", false);
        console.error("Respuesta del servidor:", xhr.responseText);
        alertMessage(error, "danger");
      },
    });
  });

  // Abrir el comentario del icono de pregunta
  var tooltipTriggerList = [].slice.call(
    document.querySelectorAll('[data-bs-toggle="tooltip"]')
  );
  var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
    return new bootstrap.Tooltip(tooltipTriggerEl);
  });

  setTimeout(function () {
    test();
  });

  /* --------------Add active class-on another-page move---------- */
  var path = window.location.pathname;

  if (path == "/") {
    path = "/home";
  }

  // Encontrar el enlace de navegación que coincide con la ruta actual
  var target = $('.navbar-nav li a[href="' + path + '"]');

  $(".navbar-nav li").removeClass("active");
  target.parent().addClass("active");

  loadNotifications();

  $("#settingsIcon").click(function () {
    $("#modalSettings").modal("show");
  });

  // Manejar el clic en el enlace que activa el dropdown de notificaciones
  $(document).on("click", ".notification.menu-link", function (e) {
    e.preventDefault();

    // Agregar overlay para cerrar el dropdown al hacer clic fuera de él
    $("body").prepend(
      '<div id="dropdownOverlay" style="background: transparent; height:100%; width:100%; position:fixed;"></div>'
    );

    var container = $(e.currentTarget).closest(".dropdown-container");
    var dropdown = container.find(".dropdown");

    // Centrar el dropdown
    var containerWidth = container.width();
    dropdown.css({
      right: containerWidth / 2 + "px",
    });

    container.toggleClass("expanded");

    loadNotifications();
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
    }, 1500);
  }

  // Cerrar dropdowns al hacer clic en el overlay
  $(document).on("click", "#dropdownOverlay", function () {
    $("#dropdownOverlay").remove();
    $(".dropdown-container.expanded").removeClass("expanded");
  });

  // Manejar el clic en las pestañas del dropdown
  $(".notification-tab").click(function (e) {
    var notificationGroup = $(e.currentTarget).parent();

    // Alternar la clase expanded en el grupo de notificaciones
    if (notificationGroup.hasClass("expanded")) {
      notificationGroup.removeClass("expanded");
    } else {
      $(".notification-group").removeClass("expanded");
      notificationGroup.addClass("expanded");
    }
  });

  // Manejar la eliminación de una notificación
  $(document).on("click", ".delete-notification", function (event) {
    event.preventDefault();
    event.stopPropagation();

    var csrfToken = $("#csrf_token").val();

    var $notificationItem = $(this).closest(".notification-list-item");
    var notificationId = $notificationItem.data("id");

    $.ajax({
      type: "DELETE",
      url: "/delete_notification",
      contentType: "application/json",
      data: JSON.stringify({ id_notificacion: notificationId }),
      headers: {
        "X-CSRFToken": csrfToken, // Enviar el token CSRF en los encabezados
      },
      success: function () {
        loadNotifications();
      },
      error: function (error) {
        console.error("Error al eliminar la notificación:", error);
      },
    });
  });

  $(document).on("click", ".notification-list-item", function (event) {
    event.preventDefault();

    var $notificationItem = $(this).closest(".notification-list-item");

    if ($notificationItem.hasClass("read")) {
      return;
    }

    var notificationId = $notificationItem.data("id");

    $.ajax({
      type: "GET",
      url: "/mark_as_read",
      data: { id_notificacion: notificationId },
      success: function (response) {
        loadNotifications();
      },
      error: function (textStatus, errorThrown) {
        console.error("Error en la solicitud AJAX:", textStatus, errorThrown);
      },
    });
  });

  // Configuración del socket para recibir notificaciones en tiempo real
  var socket = io.connect("http://" + document.domain + ":" + location.port);

  socket.on("block_notification", function (data) {
    loadNotifications();
  });

  // socket.on("block_notification", function (data) {
  //   var message = data.message;
  //   var $notificationList = $(".notification-list");
  //   var $notificationCount = $(".label");
  //   var $notificationCountNav = $(".notification-count");
  //   var $solidBellIcon = $(".fa-solid.fa-bell");
  //   var $regularBellIcon = $(".fa-regular.fa-bell");

  //   // Crear y agregar una nueva notificación
  //   $notificationList.prepend(`
  //     <li class="notification-list-item unread" data-id="${data.id}">
  //       <div class="item-header">
  //         <p class="message">${message}</p>
  //         <button class="btn btn-danger delete-notification">
  //           <i class="fa-solid fa-trash-can"></i>
  //         </button>
  //       </div>
  //       <div class="item-footer">
  //         <span class="from">Firewall</span>
  //         <span class="date">Ahora mismo</span>
  //       </div>
  //     </li>
  //   `);

  //   // Actualizar el conteo de notificaciones
  //   var count = $notificationList.children().length;
  //   $notificationCount.text(count);
  //   $notificationCountNav.text(count);

  //   if (count > 0) {
  //     $solidBellIcon.addClass("active");
  //     $regularBellIcon.removeClass("active");
  //   } else {
  //     $solidBellIcon.removeClass("active");
  //     $regularBellIcon.addClass("active");
  //   }
  // });
});
