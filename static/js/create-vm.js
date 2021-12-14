
$(function () {
    $("#createVmButton").click(function () {
        // ===== Grab all the data from the UI =====
        var data = {}
        data["vm_name"] = $("#vmName").val()
        data["vm_template"] = $("#vmTemplate").val()

        // ===== Set the status text, then disable the create button =====
        console.log(data)
        $("#out_form").html("Creating vm...")
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
                $("#out_form").html("Success! Ip Addresses:\n" + response.ip_addrs.toString())
                $("#createVmButton").removeAttr("disabled")
            },
            error: function (response) {
                console.log(response)
                $("#out_form").html("Failure:\n" + response)
                $("#createVmButton").removeAttr("disabled")
            }
        });
    });
});
