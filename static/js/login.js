$("#login").submit(function(e) {
    e.preventDefault();
    var $form = $(this).parent();
    var error = $form.find(".error");

    var username = $("#username").val();
    var password = $("#password").val();

    console.log(username);
    console.log(password);

    if (username.length < 1) {
        error.text("The username is Not Valid");
    } else {
        var data = $form.serialize();

        $.ajax({
            url: '/login',
            type: "POST",
            data: data,
            dataType: "json",
            success: function(resp) {
                console.log(resp);
            },
            error: function(resp) {
                console.log(resp);
            }
        });
    }
});