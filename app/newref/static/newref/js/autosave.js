export function autosaveForm(form, alertbox) {
  var timeleft;
  var downloadTimer;
  var all_data;
  var form_ini;

  form_ini = form + "";
  form = $("#" + form);
  statusBox("OK");

  // form.bind("change paste keyup", function () {
  $("#" + form_ini + " :input").on("input", function () {
    setTimer();
  });

  function setTimer() {
    statusBox("PENDING");
    clearInterval(downloadTimer);
    timeleft = 2;
    downloadTimer = setInterval(function () {
      timeleft--;
      if (timeleft <= 0) {
        clearInterval(downloadTimer);
        sendUpdate();
      }
    }, 1000);
  }

  function sendUpdate() {
    all_data = form.serialize();
    $.ajax({
      url: form.attr("action"),
      type: "POST",
      data: all_data,
      success: function (data) {
        if (timeleft == 0) {
          if (data["success"]) {
            statusBox("OK");
          } else {
            statusBox("DATANOK");
          }
        }
      },
      error: function () {
        statusBox("NOK");
      },
    });
  }

  function statusBox(status) {
    if (status == "OK") {
      alertbox.html("Tous les changements sont enregistrés");
      alertbox.attr("class", "alert alert-success mt-4 mb-4");
    } else if (status == "PENDING") {
      alertbox.html("Modifications en cours d'enregistrement...");
      alertbox.attr("class", "alert alert-warning mt-4 mb-4");
    } else if (status == "NOK") {
      alertbox.html("Erreur lors de l'enregistrement des modifications");
      alertbox.attr("class", "alert alert-danger mt-4 mb-4");
    } else if (status == "DATANOK") {
      alertbox.html(
        "Echec de l'enregistrement : des champs obligatoires ne sont pas correctement remplis"
      );
      alertbox.attr("class", "alert alert-danger mt-4 mb-4");
    }
  }
}
