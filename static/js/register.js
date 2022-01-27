$("#signUp").submit(function(e) {
    e.preventDefault();
    var $form = $(this).parent();
    var error = $form.find(".error");

    var username = $("#username").val();
    var fullName = $("#fullName").val();
    var email = $("#email").val();
    var password = $("#password").val();
    var confirmPassword = $("#confirmPassword").val();

    console.log(username);
    console.log(fullName);
    console.log(email);
    console.log(password);
    console.log(confirmPassword);

    if (username.length < 1) {
        error.text("The username is Not Valid");
    } else if (fullName.length < 1) {
        error.text("The Full Name is not Valid");
    } else if (email.length < 4) {
        error.text("Invalid email");
    } else if (password != confirmPassword) {
        error.text("Password is not matching");
    } else {
        var data = $form.serialize();
        console.log(data);
        $.ajax({
            url: '/register',
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