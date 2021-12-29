
$(function () {
    $("#createVmButton").click(function () {
        // ===== Grab all the data from the UI =====
        var data = {}
        data["vm_name"] = $("#vmName").val()
        data["vm_template"] = $("#vmTemplate").val()

        // ===== Set the status text, then disable the create button =====
        console.log(data)
        $("#createVmOut").html("Creating vm...")
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
                $("#createVmOut").html("Success! Ip Addresses:\n" + response.ip_addrs.toString())
                $("#createVmButton").removeAttr("disabled")
            },
            error: function (response) {
                console.log(response)
                $("#createVmOut").html("Failure:\n" + response)
                $("#createVmButton").removeAttr("disabled")
            }
        });
    });
    $("#configBackupButton").click(function () {
        // ===== Set the status text, then disable the backup button =====
        $("#configBackupOut").html("Backing up configurations.....")
        $("#configBackupButton").attr("disabled", true)

        // ===== Place the REST request =====
        $.ajax({
            url: "/api/config-backup",
            type: "POST",
            success: function (response) {
                console.log(response)
                $("#configBackupOut").html("Success!")
                $("#configBackupButton").removeAttr("disabled")
            },
            error: function (response) {
                console.log(response)
                $("#configBackupOut").html("Failure:\n" + response)
                $("#configBackupButton").removeAttr("disabled")
            }
        });
    });
});
