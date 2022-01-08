function populateTable(data) {
    $("#jobsTableBody").html("")
    var tableBody = $("#jobsTableBody")[0];
    for (var i = 0; i < data.length; i++) {
        row = $(tableBody.insertRow(-1));

        var uuidCell = $("<td />");
        uuidCell.html(data[i].job_uuid);
        row.append(uuidCell);

        var startTimeCell = $("<td />");
        startTimeCell.html(data[i].start_time);
        row.append(startTimeCell);

        var endTimeCell = $("<td />");
        endTimeCell.html(data[i].end_time);
        row.append(endTimeCell);

        var statusCell = $("<td />");
        statusCell.html(data[i].status);
        row.append(statusCell);

        var resultsCell = $("<td />");
        result = data[i].result
        if (result == null)
            result = "";
        resultsCell.html(result.toString());
        row.append(resultsCell);
    }
}

function refreshJobsData() {
    $.ajax({
        url: "/api/jobs",
        contentType: "application/json",
        type: "GET",
        success: function (response) {
            populateTable(response)
        },
        error: function (response) {
            console.log("Failure to get jobs")
            console.log(response)
        },
        complete: function () {
            setTimeout(refreshJobsData, 5000);
        }
    });
}

function appendToConsoleText(msg) {
    var current = $("#consoleText").val();
    $("#consoleText").val(current + "\n" + msg);
}

$(function () {
    $("#createVmButton").click(function () {
        // ===== Grab all the data from the UI =====
        var data = {}
        data["vm_name"] = $("#vmName").val()
        data["vm_template"] = $("#vmTemplate").val()

        // ===== Set the status text, then disable the create button =====
        console.log(data)
        $("#createVmButton").attr("disabled", true)

        // ===== Place the REST request =====
        $.ajax({
            url: "/api/create-vm",
            contentType: "application/json",
            data: JSON.stringify(data),
            dataType: "json",
            type: "POST",
            success: function (response) {
                console.log(response)
                appendToConsoleText("Started job " + response.job_uuid)
                $("#createVmButton").removeAttr("disabled")
            },
            error: function (response) {
                console.log(response)
                appendToConsoleText("Failure:\n" + response)
                $("#createVmButton").removeAttr("disabled")
            }
        });
    });
    $("#configBackupButton").click(function () {
        // ===== Set the status text, then disable the backup button =====
        $("#configBackupButton").attr("disabled", true)

        // ===== Place the REST request =====
        $.ajax({
            url: "/api/config-backup",
            type: "POST",
            success: function (response) {
                console.log(response)
                appendToConsoleText("Started job " + response.job_uuid)
                $("#configBackupButton").removeAttr("disabled")
            },
            error: function (response) {
                console.log(response)
                appendToConsoleText("Failure:\n" + response)
                $("#configBackupButton").removeAttr("disabled")
            }
        });
    });
    $("#refreshButton").click(refreshJobsData)
    refreshJobsData();
});
